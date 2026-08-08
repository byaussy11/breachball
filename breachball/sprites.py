"""Hand-authored placeholder pixel art, built as small pixel grids in code
rather than loaded from image files — there's no art-asset pipeline yet (see
the project brief's Art/Visual Pipeline notes). Each build_*_sprite()
function is the sole seam a real asset swap needs to touch later: callers
only ever consume the Surface it returns, so replacing the hand-coded pixels
with `pygame.image.load(...)` (same native size, same orientation
convention) is a one-function change, not a rewrite of the callers.
"""

import pygame

from . import constants

# Canonical orientation for the paddle sprite: horizontal, PADDLE_WIDTH wide
# x PADDLE_THICKNESS tall, matching a bottom/top-lane paddle as drawn. A
# left/right-lane paddle rotates this 90° at draw time (see paddle.py) —
# only one sprite per player needs to be authored, orientation is handled
# once, generically, by the caller.
_PADDLE_PALETTES = {
    1: {  # silver
        "highlight": (235, 235, 235),
        "base": (190, 190, 190),
        "shadow": (120, 120, 120),
        "rim": (80, 80, 80),
        "cap": (150, 150, 150),
    },
    2: {  # onyx black — widened contrast band vs. a "true black" reading of
        # onyx, since the bevel rows need enough spread to actually read at
        # 8px tall; the caller adds a 1px white outline on top regardless,
        # since onyx-on-background silhouette contrast can't be guaranteed
        # by internal palette tuning alone.
        "highlight": (95, 95, 95),
        "base": (35, 35, 35),
        "shadow": (15, 15, 15),
        "rim": (0, 0, 0),
        "cap": (55, 55, 55),
    },
}

_paddle_sprite_cache = {}


def build_paddle_sprite(player: int) -> pygame.Surface:
    """Returns the (cached) canonical horizontal paddle sprite for `player`,
    sized PADDLE_WIDTH x PADDLE_THICKNESS: a beveled bar (highlight row on
    top, shadow/rim rows on the bottom, darker end caps) with a small center
    notch marking where a laser-turret attachment will eventually mount."""
    cached = _paddle_sprite_cache.get(player)
    if cached is not None:
        return cached

    palette = _PADDLE_PALETTES[player]
    w, h = constants.PADDLE_WIDTH, constants.PADDLE_THICKNESS
    surface = pygame.Surface((w, h), pygame.SRCALPHA)

    for y in range(h):
        if y == 0:
            row_color = palette["highlight"]
        elif y == h - 1:
            row_color = palette["rim"]
        elif y == h - 2:
            row_color = palette["shadow"]
        else:
            row_color = palette["base"]
        for x in range(w):
            # Outermost 2 columns read as slightly darker end caps,
            # distinguishing the paddle's ends from its body at a glance.
            color = palette["cap"] if x < 2 or x >= w - 2 else row_color
            surface.set_at((x, y), color)

    # Center rivet/mount notch, 2px wide on the second row.
    mid = w // 2
    for x in range(mid - 1, mid + 1):
        surface.set_at((x, 1), palette["shadow"])

    _paddle_sprite_cache[player] = surface
    return surface
