#!/usr/bin/env python3
"""Generate the self-contained profile SVGs. Run: python3 tools/generate_profile.py.

Only the build helper uses Python; GitHub renders the committed SVGs directly.
Each of the 28 letters has a stable identity and a continuous pickup/reset route.
The crane and carried letter use the same timed coordinates (no reveal trick).
"""
from __future__ import annotations

import random
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS = ("frontend", "image", "interactive", "game")
DURATION = 30.0
START = 0.6
STEP = 0.75
HOME = (108.0, 57.0)
PARK = (389.0, 57.0)
GRIP_OFFSET = 16.0
RAIL_Y = 41.0
LIFT_Y = 57.0
RELEASE = 0.96
THROW = 27.0
SETTLE = 29.5
TITLE = "ivgtr — frontend / image / interactive / game"
DESCRIPTION = (
    "A small crane picks up 28 scattered letters, one at a time, and assembles "
    "frontend, image, interactive and game. It pauses so the profile can be read, "
    "then presses its own reset button and scatters the same letters again."
)
STYLE = """    :root { --ink: #59636e; --soft: #d6dce2; --paper: #ffffff; --letter: #8d5f3d; }
    @media (prefers-color-scheme: dark) {
      :root { --ink: #b4bec8; --soft: #333e49; --paper: #0d1117; --letter: #dfb98f; }
    }
    .ink { fill: none; stroke: var(--ink); stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
    .soft { fill: none; stroke: var(--soft); stroke-width: 1; stroke-linecap: round; }
    .paper { fill: var(--paper); }
    .solid { fill: var(--ink); }
    .letter { fill: var(--letter); font: 500 20px ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; text-anchor: middle; }
"""
MOTION_STYLE = """    /* Default to a readable profile, including in older media-query engines. */
    .motion { display: none; }
    @media (prefers-reduced-motion: no-preference) {
      .motion { display: inline; }
      .still { display: none; }
    }
"""
FRAME = """  <path class="soft" d="M41 284H443"/>
  <path class="ink" d="M65 280V38H414M71 280V44H414M54 281H83"/>
  <path class="soft" d="M79 41H406"/>
  <path class="ink" d="M139 271V280M344 271V280M130 281H148M335 281H353"/>
  <path class="soft" d="M143 276H340"/>
  <path class="ink paper" d="M393 269V263H407V269Z"/>
"""
RACK = """    <g class="rack ink">
      <path class="soft" d="M157 108H325M157 140H325M157 172H325M157 204H325"/>
      <path class="soft" d="M153 107V208M329 107V208"/>
      <path d="M85 260V269H388V260"/>
      <circle cx="241" cy="272" r="2"/>
{animation}    </g>
"""


def num(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def letters() -> list[dict]:
    """Shuffled/jittered slots keep all characters separated, in a stable layout."""
    rng = random.Random(140926)
    slots = [(97 + col * 22 + rng.randint(-2, 2),
              226 + row * 27 + rng.randint(-3, 3),
              rng.choice((-24, -18, -12, 12, 18, 24)))
             for row in range(2) for col in range(14)]
    rng.shuffle(slots)
    result = []
    for row, word in enumerate(WORDS):
        left = 241 - (len(word) - 1) * 7.5
        for col, char in enumerate(word):
            index = len(result)
            sx, sy, angle = slots[index]
            result.append(dict(index=index, char=char, word=word, col=col,
                               source=(sx, sy), angle=angle,
                               target=(left + col * 15, 97 + row * 32),
                               start=START + index * STEP))
    return result


def track(points: list[tuple], attribute: str = "transform", kind: str = "translate") -> str:
    """SMIL tracks share one clock; compact repeated hold points, not movements."""
    points = sorted(dict(points).items())
    assert points[0][0] == 0 and points[-1][0] == DURATION
    # Remove redundant middle points while preserving the beginning/end of holds.
    compact = []
    for i, point in enumerate(points):
        if 0 < i < len(points) - 1 and points[i - 1][1] == point[1] == points[i + 1][1]:
            continue
        compact.append(point)
    def value_string(value):
        return " ".join(num(v) for v in value) if isinstance(value, tuple) else num(value)
    values = ";".join(value_string(value) for _, value in compact)
    times = ";".join(num(time / DURATION) for time, _ in compact)
    element = "animateTransform" if attribute == "transform" else "animate"
    extra = f' type="{kind}"' if attribute == "transform" else ""
    return (f'<{element} attributeName="{attribute}"{extra} dur="{num(DURATION)}s" '
            f'begin="0s" repeatCount="indefinite" calcMode="linear" '
            f'keyTimes="{times}" values="{values}"/>')


def pickup(letter: dict) -> list[tuple[float, tuple]]:
    t = letter["start"]
    sx, sy = letter["source"]
    tx, ty = letter["target"]
    return [(t + STEP * .43, (sx, sy)), (t + STEP * .50, (sx, sy)),
            (t + STEP * .63, (sx, LIFT_Y + GRIP_OFFSET)),
            (t + STEP * .78, (tx, LIFT_Y + GRIP_OFFSET)),
            (t + STEP * .92, (tx, ty)), (t + STEP * RELEASE, (tx, ty))]


def reset(letter: dict) -> list[tuple[float, tuple]]:
    sx, sy = letter["source"]
    tx, ty = letter["target"]
    i = letter["index"]
    # A small kick, ballistic-looking apex, fall, and one damped bounce.
    return [(THROW, (tx, ty)),
            (27.25, (tx + (sx - tx) * .12, ty - 10)),
            (27.65, ((sx + tx) / 2, max(76, ty - 24))),
            (28.15, (sx, sy - 30)),
            (28.75 + i % 3 * .06, (sx, sy)),
            (29.06 + i % 3 * .04, (sx, sy - 5)),
            (SETTLE, (sx, sy)), (DURATION, (sx, sy))]


def letter_svg(letter: dict, moving: bool) -> str:
    i, char = letter["index"], escape(letter["char"])
    tx, ty = letter["target"]
    x = f'    <g class="letter" data-letter="{i}" data-word="{letter["word"]}" transform="translate({num(tx)} {num(ty)})">\n'
    if moving:
        points = [(0, letter["source"])] + pickup(letter) + reset(letter)
        x += "      " + track(points) + "\n"
        rotations = [(0, letter["angle"]), (pickup(letter)[0][0], letter["angle"]),
                     (pickup(letter)[1][0], 0), (THROW, 0),
                     (27.65, -45 if i % 2 else 45), (28.75, letter["angle"]),
                     (SETTLE, letter["angle"]), (DURATION, letter["angle"])]
        x += '      <g transform="rotate(0)">\n        ' + track(rotations, kind="rotate") + "\n"
        x += f'        <text y="6">{char}</text>\n      </g>\n'
    else:
        x += f'      <text y="6">{char}</text>\n'
    return x + "    </g>\n"


def crane_tracks(items: list[dict]) -> tuple[list, list]:
    positions = [(0, HOME), (START, HOME)]
    grips = [(0, 0)]
    previous = HOME
    for letter in items:
        t, (sx, sy) = letter["start"], letter["source"]
        positions += [(t, previous), (t + STEP * .14, (previous[0], LIFT_Y)),
                      (t + STEP * .30, (sx, LIFT_Y))]
        positions += [(time, (x, y - GRIP_OFFSET)) for time, (x, y) in pickup(letter)]
        grips += [(t, 0), (t + STEP * .43, 0), (t + STEP * .50, 2),
                  (t + STEP * .92, 2), (t + STEP * RELEASE, 0)]
        tx, ty = letter["target"]
        previous = (tx, ty - GRIP_OFFSET)
    positions += [(21.82, (previous[0], LIFT_Y)), (22.1, PARK), (26.1, PARK),
                  (26.3, (400, LIFT_Y)), (26.55, (400, 240)),
                  (26.8, (400, 245)), (27, (400, 245)), (27.3, (400, LIFT_Y)),
                  (28, HOME), (DURATION, HOME)]
    grips += [(DURATION, 0)]
    return positions, grips


def crane_svg(items: list[dict], moving: bool) -> str:
    positions, grips = crane_tracks(items)
    def a(points, attr="transform", kind="translate"):
        return track(points, attr, kind) if moving else ""
    xtrack = a([(t, (x, 0)) for t, (x, _) in positions])
    ytrack = a([(t, (0, y)) for t, (_, y) in positions])
    cable = a([(t, y - RAIL_Y) for t, (_, y) in positions], "y2")
    left = a([(t, (v, 0)) for t, v in grips])
    right = a([(t, (-v, 0)) for t, v in grips])
    return f'''    <g class="carriage" transform="translate({num(PARK[0])} 0)">
      {xtrack}
      <g transform="translate(0 {num(RAIL_Y)})"><line class="ink" y2="{num(PARK[1] - RAIL_Y)}">{cable}</line></g>
      <rect class="ink paper" x="-10" y="32" width="20" height="15" rx="3"/>
      <circle class="solid" cx="-5" cy="38" r="1"/><circle class="solid" cx="5" cy="38" r="1"/>
      <g class="head ink" transform="translate(0 {num(PARK[1])})">
        {ytrack}
        <rect class="paper" x="-6" y="-4" width="12" height="8" rx="1"/>
        <g>{left}<path d="M-6 4L-9 10V16H-5"/></g>
        <g>{right}<path d="M6 4L9 10V16H5"/></g>
      </g>
    </g>
'''


def scene(items: list[dict], moving: bool) -> str:
    tip = ""
    press = ""
    if moving:
        tip = '      ' + track([(0, (0, 241, 269)), (26.8, (0, 241, 269)),
                               (27, (3, 241, 269)), (27.25, (-6, 241, 269)),
                               (27.7, (2, 241, 269)), (28.3, (0, 241, 269)),
                               (DURATION, (0, 241, 269))], kind="rotate") + '\n'
        press = track([(0, (0, 0)), (26.55, (0, 0)), (26.8, (0, 5)),
                       (27, (0, 5)), (27.3, (0, 0)), (DURATION, (0, 0))])
    return (RACK.format(animation=tip)
            + f'    <g class="plunger">{press}<path class="ink" d="M400 257V264M395 256H405"/></g>\n'
            + ''.join(letter_svg(item, moving) for item in items)
            + crane_svg(items, moving))


def render(moving: bool) -> str:
    items = letters()
    style = STYLE + (MOTION_STYLE if moving else "")
    content = '  <g class="still">\n' + scene(items, False) + '  </g>\n'
    if moving:
        content += '  <g class="motion" aria-hidden="true">\n' + scene(items, True) + '  </g>\n'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="300" viewBox="0 0 480 300" role="img" aria-labelledby="title description">\n'
            f'  <title id="title">{escape(TITLE)}</title>\n'
            f'  <desc id="description">{escape(DESCRIPTION)}</desc>\n'
            '  <!-- Generated by tools/generate_profile.py. Edit the generator, not this file. -->\n'
            '  <!-- No scripts, external images, fonts, or network dependencies. -->\n'
            f'  <style>\n{style}  </style>\n' + FRAME + content + '</svg>\n')


def main() -> None:
    for name, moving in (("again.svg", True), ("again.still.svg", False)):
        path = ROOT / "assets" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(moving), encoding="utf-8")
        print(f"Wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
