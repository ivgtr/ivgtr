"""Dependency-free regression checks: python3 -m unittest discover -s tests -v."""
import math
import sys
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_profile as p

NS = {"s": "http://www.w3.org/2000/svg"}


def eased(fraction):
    """Invert the x coordinate of the shared cubic-bezier(.42,0,.58,1)."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        t = (lo + hi) / 2
        x = 3 * (1-t)**2 * t * .42 + 3 * (1-t) * t*t * .58 + t**3
        if x < fraction:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return 3 * (1-t) * t*t + t**3


def sample(points, time):
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t0 <= time <= t1:
            a = eased((time - t0) / (t1 - t0))
            return tuple(x + (y-x)*a for x, y in zip(v0, v1))
    raise AssertionError(f"Time outside track: {time}")


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.clock = p.timeline()

    def test_only_frontend_and_exactly_eight_characters(self):
        self.assertEqual(p.WORD, "frontend")
        items = p.letters()
        self.assertEqual(len(items), 8)
        self.assertEqual([item["index"] for item in items], list(range(8)))
        self.assertEqual("".join(item["char"] for item in items), "frontend")
        self.assertEqual(Counter(item["char"] for item in items), Counter("frontend"))
        for moving in (True, False):
            root = ET.fromstring(p.render(moving))
            for group in root.findall("s:g", NS):
                nodes = group.findall("s:g[@class='letter']", NS)
                self.assertEqual(len(nodes), 8)
                self.assertEqual("".join(node.find(".//s:text", NS).text for node in nodes), "frontend")

    def test_generated_files_are_reproducible(self):
        for name, moving in (("again.svg", True), ("again.still.svg", False)):
            self.assertEqual((ROOT / "assets" / name).read_text(), p.render(moving))
        self.assertEqual(p.timeline(), p.timeline())

    def test_sources_targets_and_staging_do_not_overlap(self):
        items = p.letters()
        for i, item in enumerate(items):
            sx, sy = item["source"]
            self.assertTrue(118 <= sx <= 368)
            self.assertEqual(sy, p.LETTER_Y)
            for other in items:
                self.assertGreaterEqual(math.dist(item["source"], other["target"]), 18)
            for other in items[:i]:
                self.assertGreaterEqual(math.dist(item["source"], other["source"]), 16)
                self.assertEqual(item["target"][1], other["target"][1])

    def test_crane_letter_and_easing_stay_synchronized(self):
        for item in p.letters():
            start, end = self.clock["held"][item["index"]]
            route = self.clock["routes"][item["index"]]
            for i in range(21):
                time = start + (end-start) * i / 20
                head = sample(self.clock["positions"], time)
                letter = sample(route, time)
                self.assertAlmostEqual(head[0], letter[0], places=6)
                self.assertAlmostEqual(head[1] + p.GRIP_OFFSET, letter[1], places=6)

    def test_tracks_have_valid_splines_and_seamless_endpoints(self):
        root = ET.fromstring(p.render(True))
        tracks = root.findall(".//s:animate", NS) + root.findall(".//s:animateTransform", NS)
        self.assertEqual(len(tracks), 23)  # 8 positions + 8 rotations + 7 machine tracks.
        for animation in tracks:
            times = [float(t) for t in animation.attrib["keyTimes"].split(";")]
            values = animation.attrib["values"].split(";")
            splines = animation.attrib["keySplines"].split(";")
            self.assertEqual(len(times), len(values))
            self.assertEqual(len(splines), len(times)-1)
            self.assertTrue(all(spline == p.EASE for spline in splines))
            self.assertTrue(all(a < b for a, b in zip(times, times[1:])))
            self.assertEqual((times[0], times[-1]), (0, 1))
            self.assertEqual(values[0], values[-1])
            self.assertEqual(animation.attrib["dur"], f"{self.clock['duration']}s")
            self.assertEqual(animation.attrib["begin"], "0s")
            self.assertEqual(animation.attrib["calcMode"], "spline")

    def test_five_seconds_of_complete_stillness(self):
        self.assertGreaterEqual(self.clock["park_end"]-self.clock["park_start"], 5)
        for i in range(11):
            time = self.clock["park_start"] + i * p.READ_HOLD/10
            head = sample(self.clock["positions"], time)
            self.assertEqual(head, p.PARK)
            for item in p.letters():
                route = self.clock["routes"][item["index"]] + p.reset(item, self.clock)
                self.assertEqual(sample(route, time), item["target"])

    def test_timing_is_not_the_old_rushed_letter_cycle(self):
        intervals = [self.clock["turns"][i+1][0]-self.clock["turns"][i][0] for i in range(7)]
        self.assertGreater(min(intervals), 2)
        for (t0, a), (t1, b) in zip(self.clock["positions"], self.clock["positions"][1:]):
            self.assertLessEqual(math.dist(a, b)/(t1-t0), 255)  # segment average, not peak speed
        self.assertLessEqual(self.clock["duration"], 35)

    def test_single_tray_and_original_compact_aspect_ratio(self):
        for moving in (True, False):
            root = ET.fromstring(p.render(moving))
            self.assertEqual(root.attrib["viewBox"], "0 0 480 230")
            self.assertFalse(root.findall(".//s:g[@class='rack ink']", NS))
            for group in root.findall("s:g", NS):
                self.assertEqual(len(group.findall("s:g[@class='tray ink']", NS)), 1)

    def test_reduced_motion_is_the_completed_word(self):
        root = ET.fromstring(p.render(False))
        self.assertFalse(root.findall(".//s:animate", NS))
        self.assertFalse(root.findall(".//s:animateTransform", NS))
        for node, item in zip(root.findall(".//s:g[@class='letter']", NS), p.letters()):
            x, y = item["target"]
            self.assertEqual(node.attrib["transform"], f"translate({p.num(x)} {p.num(y)})")
        self.assertIn("prefers-reduced-motion: no-preference", p.render(True))
        self.assertIn('class="still"', p.render(True))

    def test_self_contained_and_accessible(self):
        for moving in (True, False):
            root = ET.fromstring(p.render(moving))
            self.assertEqual(root.attrib["role"], "img")
            self.assertEqual(root.find("s:title", NS).text, "ivgtr — frontend")
            for label in root.attrib["aria-labelledby"].split():
                self.assertIsNotNone(root.find(f".//*[@id='{label}']"))
            for element in root.iter():
                self.assertNotIn(element.tag.split("}")[-1], ("script", "image", "foreignObject", "iframe"))
                self.assertFalse(any(name.lower().startswith("on") for name in element.attrib))
                self.assertFalse(any(name.endswith("href") for name in element.attrib))
            self.assertNotIn("@import", p.render(moving))
            self.assertNotIn("url(", p.render(moving))

    def test_readme_is_one_image_with_no_extra_profile_list(self):
        readme = (ROOT / "README.md").read_text()
        self.assertIn('width="400"', readme)
        self.assertNotIn('height=', readme)
        self.assertEqual(readme.count('<img '), 1)
        self.assertIn('ivgtr — frontend', readme)
        self.assertNotIn('interactive', readme)
        self.assertNotIn('game', readme)
        for name in ("again.svg", "again.still.svg"):
            self.assertIn(f'./assets/{name}', readme)
            self.assertTrue((ROOT / "assets" / name).is_file())
        self.assertIn('media="(prefers-reduced-motion: reduce)"', readme)


if __name__ == "__main__":
    unittest.main()
