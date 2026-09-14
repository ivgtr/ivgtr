#!/usr/bin/env python3
"""Generate the quiet, single-word profile. No runtime build or dependencies.

Eight letters, one tray, one shared clock. The crane and each carried letter
use identical easing and pickup coordinates. Edit this file, not the SVGs.
"""
from __future__ import annotations

import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD = "frontend"
WIDTH, HEIGHT = 480, 230
START = .8
HOME = (108.0, 98.0)
PARK = (397.0, 98.0)
RAIL_Y = 57.0
GRIP_OFFSET = 16.0
LETTER_Y = 169.0
LIFT_Y = 98.0
READ_HOLD = 5.0
EASE = ".42 0 .58 1"
TITLE = "ivgtr — frontend"
DESCRIPTION = (
    "A little crane arranges eight scattered letters into frontend, steps aside "
    "for five seconds, then presses its own reset button and scatters them again."
)
# Four loose letters on each side; the receiving area is empty, not overlapping
# uncollected letters. All eight remain on the same tray throughout the loop.
SOURCES = ((154, -12), (118, 14), (172, -8), (136, 10),
           (350, -14), (368, 8), (314, 12), (332, -10))
STYLE = '''    :root { --ink: #59636e; --soft: #d6dce2; --paper: #ffffff; --letter: #8d5f3d; }
    @media (prefers-color-scheme: dark) {
      :root { --ink: #b4bec8; --soft: #333e49; --paper: #0d1117; --letter: #dfb98f; }
    }
    .ink { fill: none; stroke: var(--ink); stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
    .soft { fill: none; stroke: var(--soft); stroke-width: 1; stroke-linecap: round; }
    .paper { fill: var(--paper); }
    .solid { fill: var(--ink); }
    .letter { fill: var(--letter); font: 500 20px ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; text-anchor: middle; }
'''
MOTION_STYLE = '''    .motion { display: none; }
    @media (prefers-reduced-motion: no-preference) {
      .motion { display: inline; }
      .still { display: none; }
    }
'''
FRAME = '''  <path class="soft" d="M62 208H423"/>
  <path class="ink" d="M80 204V54H422M86 204V60H422M68 205H97"/>
  <path class="soft" d="M94 57H414"/>
  <path class="ink" d="M160 183V204M333 183V204M151 205H170M324 205H343"/>
  <path class="soft" d="M164 191H329"/>
  <path class="ink paper" d="M388 178V172H402V178Z"/>
'''


def num(value: float) -> str:
    return f"{value:.8f}".rstrip("0").rstrip(".") or "0"


def letters() -> list[dict]:
    """Stable character identity, including the two separate n's."""
    return [dict(index=i, char=char, source=(x, LETTER_Y), angle=angle,
                 target=(190.0 + 15 * i, LETTER_Y))
            for i, (char, (x, angle)) in enumerate(zip(WORD, SOURCES))]


def timeline() -> dict:
    """Distance-based travel avoids a long jump being squeezed into 0.1s."""
    time, previous = START, HOME
    positions = [(0.0, HOME), (START, HOME)]
    grips = [(0.0, 0.0)]
    routes, held, turns = {}, {}, {}
    for letter in letters():
        sx, sy = letter["source"]
        tx, ty = letter["target"]
        time = round(time + max(.28, abs(previous[0] - sx) / 170), 6)
        positions.append((time, (sx, LIFT_Y)))
        time = round(time + .36, 6)
        contact = time
        positions.append((time, (sx, sy - GRIP_OFFSET)))
        time = round(time + .18, 6)
        closed = time
        positions.append((time, (sx, sy - GRIP_OFFSET)))
        time = round(time + .38, 6)
        raised = time
        positions.append((time, (sx, LIFT_Y)))
        time = round(time + max(.36, abs(tx - sx) / 150), 6)
        crossed = time
        positions.append((time, (tx, LIFT_Y)))
        time = round(time + .38, 6)
        placed = time
        positions.append((time, (tx, ty - GRIP_OFFSET)))
        time = round(time + .20, 6)
        released = time
        positions.append((time, (tx, ty - GRIP_OFFSET)))
        time = round(time + .34, 6)
        positions.append((time, (tx, LIFT_Y)))
        previous = (tx, LIFT_Y)
        grips += [(contact, 0.0), (closed, 2.0), (placed, 2.0), (released, 0.0)]
        routes[letter["index"]] = [(0.0, letter["source"]), (contact, letter["source"]),
            (closed, letter["source"]), (raised, (sx, LIFT_Y + GRIP_OFFSET)),
            (crossed, (tx, LIFT_Y + GRIP_OFFSET)), (placed, letter["target"])]
        held[letter["index"]] = (closed, placed)
        turns[letter["index"]] = (contact, closed)
    completed = placed
    park_start = round(time + abs(PARK[0] - previous[0]) / 150, 6)
    park_end = round(park_start + READ_HOLD, 6)
    approach = round(park_end + .32, 6)
    button_contact = round(approach + .48, 6)
    button_down = round(button_contact + .26, 6)
    throw = round(button_down + .24, 6)
    settled = round(throw + 1.6, 6)
    duration = math.ceil(settled + .8)
    positions += [(park_start, PARK), (park_end, PARK),
        (approach, (395.0, LIFT_Y)), (button_contact, (395.0, 149.0)),
        (button_down, (395.0, 154.0)), (throw, (395.0, 154.0)),
        (throw + .42, (395.0, LIFT_Y)), (settled, HOME), (duration, HOME)]
    grips.append((duration, 0.0))
    return dict(positions=positions, grips=grips, routes=routes, held=held,
                turns=turns, completed=completed, park_start=park_start,
                park_end=park_end, contact=button_contact, down=button_down,
                throw=throw, settled=settled, duration=duration)


def track(points: list[tuple], duration: float, attribute: str = "transform",
          kind: str = "translate") -> str:
    """Smooth, shared easing; only remove redundant interior hold points."""
    points = sorted(points)
    assert points[0][0] == 0 and points[-1][0] == duration
    assert all(a[0] < b[0] for a, b in zip(points, points[1:]))
    compact = [point for i, point in enumerate(points)
               if not (0 < i < len(points) - 1
                       and points[i - 1][1] == point[1] == points[i + 1][1])]
    def values(value):
        return " ".join(num(v) for v in value) if isinstance(value, tuple) else num(value)
    element = "animateTransform" if attribute == "transform" else "animate"
    extra = f' type="{kind}"' if attribute == "transform" else ""
    return (f'<{element} attributeName="{attribute}"{extra} dur="{num(duration)}s" '
            f'begin="0s" repeatCount="indefinite" calcMode="spline" '
            f'keyTimes="{";".join(num(t / duration) for t, _ in compact)}" '
            f'keySplines="{";".join([EASE] * (len(compact) - 1))}" '
            f'values="{";".join(values(v) for _, v in compact)}"/>')


def rotated(point: tuple, angle: float) -> tuple:
    """Rotate a resting letter with the tray before its launch."""
    x, y = point[0] - 245, point[1] - 177
    a = math.radians(angle)
    return (245 + x * math.cos(a) - y * math.sin(a),
            177 + x * math.sin(a) + y * math.cos(a))


def reset(letter: dict, clock: dict) -> list[tuple]:
    sx, sy = letter["source"]
    tx, ty = letter["target"]
    t = clock["throw"]
    return [(clock["down"], (tx, ty)), (t, rotated((tx, ty), 3)),
            (t + .20, rotated((tx, ty), -10)),
            (t + .63, ((sx + tx) / 2, 126 - letter["index"] % 3 * 4)),
            (t + 1.18, (sx, sy)), (t + 1.38, (sx, sy - 3)),
            (clock["settled"], (sx, sy)), (clock["duration"], (sx, sy))]


def letter_svg(letter: dict, moving: bool, clock: dict) -> str:
    i, char = letter["index"], escape(letter["char"])
    tx, ty = letter["target"]
    x = f'    <g class="letter" data-letter="{i}" transform="translate({num(tx)} {num(ty)})">\n'
    if moving:
        x += "      " + track(clock["routes"][i] + reset(letter, clock), clock["duration"]) + "\n"
        contact, closed = clock["turns"][i]
        t = clock["throw"]
        rotations = [(0, letter["angle"]), (contact, letter["angle"]), (closed, 0),
                     (clock["down"], 0), (t, 3), (t + .20, -10),
                     (t + .63, -26 if i % 2 else 26),
                     (t + 1.18, letter["angle"]), (clock["duration"], letter["angle"])]
        x += '      <g>\n        ' + track(rotations, clock["duration"], kind="rotate") + "\n"
        x += f'        <text y="6">{char}</text>\n      </g>\n'
    else:
        x += f'      <text y="6">{char}</text>\n'
    return x + "    </g>\n"


def crane_svg(moving: bool, clock: dict) -> str:
    def a(points, attr="transform", kind="translate"):
        return track(points, clock["duration"], attr, kind) if moving else ""
    p = clock["positions"]
    xt = a([(t, (x, 0)) for t, (x, _) in p])
    yt = a([(t, (0, y)) for t, (_, y) in p])
    cable = a([(t, y - RAIL_Y) for t, (_, y) in p], "y2")
    left = a([(t, (v, 0)) for t, v in clock["grips"]])
    right = a([(t, (-v, 0)) for t, v in clock["grips"]])
    return f'''    <g class="carriage" transform="translate({num(PARK[0])} 0)">
      {xt}
      <g transform="translate(0 57)"><line class="cable ink" y2="41">{cable}</line></g>
      <rect class="ink paper" x="-10" y="48" width="20" height="15" rx="3"/>
      <circle class="solid" cx="-5" cy="54" r="1"/><circle class="solid" cx="5" cy="54" r="1"/>
      <g class="head ink" transform="translate(0 {num(PARK[1])})">
        {yt}
        <rect class="paper" x="-6" y="-4" width="12" height="8" rx="1"/>
        <g>{left}<path d="M-6 4L-9 10V16H-5"/></g>
        <g>{right}<path d="M6 4L9 10V16H5"/></g>
      </g>
    </g>
'''


def scene(moving: bool, clock: dict) -> str:
    tip, press = "", ""
    if moving:
        t, end = clock["throw"], clock["duration"]
        tip = track([(0, (0, 245, 177)), (clock["down"], (0, 245, 177)),
                     (t, (3, 245, 177)), (t + .20, (-10, 245, 177)),
                     (t + .75, (1.5, 245, 177)), (t + 1.18, (0, 245, 177)),
                     (end, (0, 245, 177))], end, kind="rotate")
        press = track([(0, (0, 0)), (clock["contact"], (0, 0)),
                       (clock["down"], (0, 5)), (t, (0, 5)),
                       (t + .42, (0, 0)), (end, (0, 0))], end)
    return (f'    <g class="tray ink">{tip}<path d="M110 169V177H380V169M114 177H376"/></g>\n'
            '    <circle class="ink paper" cx="245" cy="180" r="2"/>\n'
            f'    <g class="plunger">{press}<path class="ink" d="M395 166V173M390 165H400"/></g>\n'
            + ''.join(letter_svg(item, moving, clock) for item in letters())
            + crane_svg(moving, clock))


def render(moving: bool) -> str:
    clock = timeline()
    style = STYLE + (MOTION_STYLE if moving else "")
    content = '  <g class="still">\n' + scene(False, clock) + '  </g>\n'
    if moving:
        content += '  <g class="motion" aria-hidden="true">\n' + scene(True, clock) + '  </g>\n'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">\n'
            f'  <title id="title">{escape(TITLE)}</title>\n'
            f'  <desc id="description">{escape(DESCRIPTION)}</desc>\n'
            '  <!-- Generated by tools/generate_profile.py. Edit the generator, not this file. -->\n'
            '  <!-- Self-contained. No scripts, external images or font downloads. -->\n'
            f'  <style>\n{style}  </style>\n' + FRAME + content + '</svg>\n')


def main() -> None:
    for name, moving in (("again.svg", True), ("again.still.svg", False)):
        path = ROOT / "assets" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(moving), encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
    clock = timeline()
    print(f"Complete {clock['completed']:.2f}s; parked {clock['park_start']:.2f}–"
          f"{clock['park_end']:.2f}s; loop {clock['duration']}s")


if __name__ == "__main__":
    main()
