"""Sprite loading, with hand-coded pixel-grid placeholders as a fallback for
whatever hasn't been drawn yet — there's no full art-asset pipeline yet (see
the project brief's Art/Visual Pipeline notes). Each build_*_sprite()
function is the one seam callers touch: they only ever consume the Surface
it returns, never caring whether that surface came from a loaded file or
hand-coded pixels, so real art can land file-by-file without any caller
changes.
"""

from pathlib import Path

import pygame

from . import constants

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# Canonical orientation for the paddle sprite: horizontal, PADDLE_WIDTH wide
# x PADDLE_THICKNESS tall, matching a bottom/top-lane paddle as drawn. A
# left/right-lane paddle rotates this 90° at draw time (see paddle.py) —
# only one sprite per player needs to be authored/drawn, orientation is
# handled once, generically, by the caller.
_PADDLE_SPRITE_PATHS = {
    1: ASSETS_DIR / "sprites" / "paddles" / "Silver_Paddle.png",
    2: ASSETS_DIR / "sprites" / "paddles" / "Onyx_Paddle.png",
}

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

# Laser turret attachment — same file-first/placeholder-fallback pattern as
# the paddle sprite, and same per-player palette so it reads as part of the
# same unit rather than a bolted-on mismatch. A standalone sprite/Surface,
# not part of the paddle's own canvas — paddle.py layers it on at draw time,
# so it never touches PADDLE_WIDTH/THICKNESS or paddle collision.
_TURRET_SPRITE_PATHS = {
    1: ASSETS_DIR / "sprites" / "paddles" / "Silver_Turret.png",
    2: ASSETS_DIR / "sprites" / "paddles" / "Onyx_Turret.png",
}

# Row-by-row pixel legend for the placeholder turret: narrow barrel tip,
# widening dome, flat mount base — small enough to sit centered on the
# paddle's existing mount notch. H/B/S/R map to the same highlight/base/
# shadow/rim keys as the paddle palette; '.' is transparent.
_TURRET_ROWS = [
    "...HH...",
    "..BHHB..",
    ".BBBBBB.",
    "RSBBBBSR",
    "RSSSSSSR",
    ".RSSSSR.",
]

_turret_sprite_cache = {}


def build_turret_sprite(player: int) -> pygame.Surface:
    """Returns the (cached) canonical turret sprite for `player`, sized
    TURRET_WIDTH x TURRET_HEIGHT. Loads
    assets/sprites/paddles/<Palette>_Turret.png if present; falls back to a
    hand-coded placeholder otherwise — same file-then-placeholder contract
    as build_paddle_sprite, so real turret art can land later with no
    caller changes."""
    cached = _turret_sprite_cache.get(player)
    if cached is not None:
        return cached

    sprite = _load_turret_sprite_file(player)
    if sprite is None:
        sprite = _build_placeholder_turret_sprite(player)
    _turret_sprite_cache[player] = sprite
    return sprite


def _load_turret_sprite_file(player: int):
    """Same contract as _load_paddle_sprite_file: loads the player's turret
    file if present, scaling to TURRET_WIDTH x TURRET_HEIGHT if needed;
    returns None (falling back to the placeholder) if missing or bad."""
    path = _TURRET_SPRITE_PATHS[player]
    if not path.is_file():
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
    except pygame.error as exc:
        print(f"sprites: failed to load {path} ({exc}); using placeholder.")
        return None

    size = (constants.TURRET_WIDTH, constants.TURRET_HEIGHT)
    if image.get_size() != size:
        print(f"sprites: {path.name} is {image.get_size()}, expected {size} — scaling to fit.")
        image = pygame.transform.scale(image, size)
    return image


def _build_placeholder_turret_sprite(player: int) -> pygame.Surface:
    """Hand-coded fallback turret: barrel tip, dome, and mount base, using
    the same palette as that player's paddle."""
    palette = _PADDLE_PALETTES[player]
    legend = {"H": palette["highlight"], "B": palette["base"], "S": palette["shadow"], "R": palette["rim"]}
    surface = pygame.Surface((constants.TURRET_WIDTH, constants.TURRET_HEIGHT), pygame.SRCALPHA)

    for y, row in enumerate(_TURRET_ROWS):
        for x, ch in enumerate(row):
            color = legend.get(ch)
            if color is not None:
                surface.set_at((x, y), color)

    return surface


def build_paddle_sprite(player: int) -> pygame.Surface:
    """Returns the (cached) canonical horizontal paddle sprite for `player`,
    sized PADDLE_WIDTH x PADDLE_THICKNESS. Loads
    assets/sprites/paddles/p<player>_paddle.png if it exists; falls back to
    a hand-coded placeholder bar otherwise, so the game runs fine before
    real art exists and picks it up automatically the moment a file lands
    at that path — no code change needed on the art side."""
    cached = _paddle_sprite_cache.get(player)
    if cached is not None:
        return cached

    sprite = _load_paddle_sprite_file(player)
    if sprite is None:
        sprite = _build_placeholder_paddle_sprite(player)
    _paddle_sprite_cache[player] = sprite
    return sprite


def _load_paddle_sprite_file(player: int):
    """Loads the player's sprite file if present, scaling it to
    PADDLE_WIDTH x PADDLE_THICKNESS if its native size doesn't already
    match (nearest-neighbor, consistent with display.py's whole-surface
    scaling — keeps art crisp instead of blurred). Returns None (letting
    the caller fall back to the placeholder) if the file is missing or
    fails to load, rather than crashing the game over missing/bad art."""
    path = _PADDLE_SPRITE_PATHS[player]
    if not path.is_file():
        return None
    try:
        image = pygame.image.load(path).convert_alpha()
    except pygame.error as exc:
        print(f"sprites: failed to load {path} ({exc}); using placeholder.")
        return None

    size = (constants.PADDLE_WIDTH, constants.PADDLE_THICKNESS)
    if image.get_size() != size:
        print(f"sprites: {path.name} is {image.get_size()}, expected {size} — scaling to fit.")
        image = pygame.transform.scale(image, size)
    return image


def _build_placeholder_paddle_sprite(player: int) -> pygame.Surface:
    """Hand-coded fallback: a beveled bar (highlight row on top, shadow/rim
    rows on the bottom, darker end caps) with a small center notch marking
    where a laser-turret attachment will eventually mount."""
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

    return surface
