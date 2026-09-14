"""Dependency-free checks: python3 -m unittest discover -s tests -v."""
import math
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_profile as profile

NS = {"s": "http://www.w3.org/2000/svg"}


def interpolate(points, time):
    points = sorted(dict(points).items())
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t0 <= time <= t1:
            alpha = (time - t0) / (t1 - t0)
            return tuple(a + (b - a) * alpha for a, b in zip(v0, v1))
    raise AssertionError(f"Time outside track: {time}")


class ProfileTests(unittest.TestCase):
    def test_exact_words_and_letter_inventory(self):
        self.assertEqual(profile.WORDS, ("frontend", "image", "interactive", "game"))
        letters = profile.letters()
        self.assertEqual(len(letters), 28)
        self.assertEqual([p["index"] for p in letters], list(range(28)))
        self.assertEqual(Counter(p["char"] for p in letters), Counter("".join(profile.WORDS)))
        for word in profile.WORDS:
            self.assertEqual("".join(p["char"] for p in letters if p["word"] == word), word)

    def test_reproducible_generated_assets(self):
        for name, moving in (("again.svg", True), ("again.still.svg", False)):
            self.assertEqual((ROOT / "assets" / name).read_text(), profile.render(moving))
        self.assertEqual(profile.letters(), profile.letters())

    def test_scattered_letters_are_separated_and_in_bounds(self):
        letters = profile.letters()
        for i, letter in enumerate(letters):
            x, y = letter["source"]
            self.assertTrue(80 < x < 390 and 210 < y < 260)
            self.assertNotEqual(letter["source"], letter["target"])
            for other in letters[:i]:
                self.assertGreaterEqual(math.dist(letter["source"], other["source"]), 18)

    def test_crane_and_carried_letter_share_the_same_route(self):
        positions, _ = profile.crane_tracks(profile.letters())
        for letter in profile.letters():
            carried = profile.pickup(letter)
            for fraction in (.50, .56, .63, .70, .78, .85, .92):
                time = letter["start"] + profile.STEP * fraction
                head = interpolate(positions, time)
                glyph = interpolate(carried, time)
                self.assertAlmostEqual(head[0], glyph[0], places=6)
                self.assertAlmostEqual(head[1] + profile.GRIP_OFFSET, glyph[1], places=6)

    def test_clock_values_and_seamless_loop(self):
        root = ET.fromstring(profile.render(True))
        tracks = root.findall(".//s:animate", NS) + root.findall(".//s:animateTransform", NS)
        self.assertEqual(len(tracks), 63)  # 28 translations, 28 rotations, 7 machine tracks.
        for animation in tracks:
            times = [float(t) for t in animation.attrib["keyTimes"].split(";")]
            values = animation.attrib["values"].split(";")
            self.assertEqual(len(times), len(values))
            self.assertEqual((times[0], times[-1]), (0, 1))
            self.assertTrue(all(a < b for a, b in zip(times, times[1:])))
            self.assertEqual(values[0], values[-1])
            self.assertEqual(animation.attrib["dur"], "30s")
            self.assertEqual(animation.attrib["begin"], "0s")
            self.assertEqual(animation.attrib["repeatCount"], "indefinite")

    def test_each_letter_remains_readable_until_reset(self):
        for letter in profile.letters():
            route = [(0, letter["source"])] + profile.pickup(letter) + profile.reset(letter)
            for time in (22.1, 23, 26.1):
                self.assertEqual(interpolate(route, time), letter["target"])
        positions, _ = profile.crane_tracks(profile.letters())
        self.assertEqual(interpolate(positions, 22.1), profile.PARK)
        self.assertEqual(interpolate(positions, 26.1), profile.PARK)

    def test_static_fallback_contains_the_completed_profile(self):
        root = ET.fromstring(profile.render(False))
        self.assertFalse(root.findall(".//s:animate", NS))
        self.assertFalse(root.findall(".//s:animateTransform", NS))
        nodes = root.findall(".//s:g[@class='letter']", NS)
        self.assertEqual(len(nodes), 28)
        for node, letter in zip(nodes, profile.letters()):
            self.assertEqual(node.find("s:text", NS).text, letter["char"])
            x, y = letter["target"]
            self.assertEqual(node.attrib["transform"], f"translate({profile.num(x)} {profile.num(y)})")
        animated = ET.fromstring(profile.render(True))
        self.assertIsNotNone(animated.find("s:g[@class='still']", NS))
        self.assertIn("prefers-reduced-motion: no-preference", profile.render(True))

    def test_self_contained_and_accessibly_named(self):
        for moving in (True, False):
            root = ET.fromstring(profile.render(moving))
            self.assertEqual(root.attrib["role"], "img")
            for label in root.attrib["aria-labelledby"].split():
                self.assertIsNotNone(root.find(f".//*[@id='{label}']"))
            self.assertIn(" / ".join(profile.WORDS), root.find("s:title", NS).text)
            for element in root.iter():
                self.assertNotIn(element.tag.split("}")[-1], ("script", "image", "foreignObject", "iframe"))
                self.assertFalse(any(name.lower().startswith("on") for name in element.attrib))
                self.assertFalse(any(name.endswith("href") for name in element.attrib))
            self.assertNotIn("@import", profile.render(moving))
            self.assertNotIn("url(", profile.render(moving))

    def test_readme_links_and_alternative_text(self):
        readme = (ROOT / "README.md").read_text()
        for word in profile.WORDS:
            self.assertIn(word, readme)
        for filename in ("again.svg", "again.still.svg"):
            self.assertIn(f'./assets/{filename}', readme)
            self.assertTrue((ROOT / "assets" / filename).is_file())
        self.assertIn('media="(prefers-reduced-motion: reduce)"', readme)
        self.assertNotIn('height="300"', readme)  # Preserve intrinsic aspect ratio on narrow screens.


if __name__ == "__main__":
    unittest.main()
