"""Paddle entity: position along its lane, movement clamped to its travel
range, and rendering. Orientation follows the lane automatically —
bottom/top lanes are horizontal paddles traveling along x; left/right lanes
are vertical paddles traveling along y — so placing a paddle on a side lane
just works, no special-casing needed elsewhere. (Corner transfer tubes,
letting a paddle move *between* lanes at runtime, are still later work —
this only covers a paddle placed on a given lane for the whole game/level.)"""

import pygame

from . import constants
from .controls import Lane, lane_axis

# Fixed coordinate (perpendicular to the paddle's travel axis) for each
# lane — how far in from that lane's screen edge the paddle sits. y for the
# horizontal bottom/top lanes, x for the vertical left/right lanes.
_LANE_FIXED_COORD = {
    Lane.BOTTOM: constants.VIRTUAL_HEIGHT - 20,
    Lane.TOP: 20,
    Lane.LEFT: 20,
    Lane.RIGHT: constants.VIRTUAL_WIDTH - 20,
}

# Which direction stacking nudges a paddle, per lane — always toward the
# arena's center, away from that lane's screen edge.
_STACK_SIGN = {
    Lane.BOTTOM: -1,
    Lane.TOP: 1,
    Lane.LEFT: 1,
    Lane.RIGHT: -1,
}

# Gap used when two paddles share the same lane — per the brief, they stack
# "one above the other" (or side by side, on a vertical lane) rather than
# overlapping, same relationship regardless of which lane it is.
STACK_OFFSET = 16

_PLAYER_COLOR = {
    1: (192, 192, 192),  # P1 = silver
    2: (20, 20, 20),      # P2 = onyx black
}


class Paddle:
    def __init__(self, player: int, lane: Lane, pos: float = None, stack_order: int = 0):
        self.player = player
        self.lane = lane
        # Extent along the travel axis — "width" on a horizontal paddle,
        # but also the paddle's length when it's vertical on a side lane.
        self.length = constants.PADDLE_WIDTH
        self.thickness = constants.PADDLE_THICKNESS
        travel_range = self._travel_range()
        # Position along the travel axis (x for bottom/top, y for
        # left/right) — analogous to the old fixed "self.x", generalized to
        # whichever axis this paddle's lane actually travels along.
        self.pos = pos if pos is not None else (travel_range - self.length) / 2
        # 0 = normal lane position; 1+ nudges this paddle toward the center
        # of the arena, for when it shares a lane with another paddle.
        self.stack_order = stack_order

    def _travel_range(self) -> float:
        return constants.VIRTUAL_WIDTH if lane_axis(self.lane) == "x" else constants.VIRTUAL_HEIGHT

    def _travel_bounds(self) -> tuple[float, float]:
        """Min/max for self.pos, inset from both ends of the lane's travel
        range by CORNER_SIZE — every lane runs between two corners (e.g.
        BOTTOM spans the bottom-left and bottom-right corners), so both
        ends get the same corner dead-zone treatment. Keeps this paddle
        from ever sliding into the reserved corner squares (see arena.py),
        which is what let two perpendicular paddles cross/overlap before."""
        low = constants.CORNER_SIZE
        high = self._travel_range() - constants.CORNER_SIZE - self.length
        return low, high

    @property
    def rect(self) -> pygame.Rect:
        fixed = _LANE_FIXED_COORD[self.lane] + _STACK_SIGN[self.lane] * self.stack_order * STACK_OFFSET
        pos = round(self.pos)
        if lane_axis(self.lane) == "x":
            return pygame.Rect(pos, fixed, self.length, self.thickness)
        return pygame.Rect(fixed, pos, self.thickness, self.length)

    def move(self, delta: float):
        self.pos += delta
        low, high = self._travel_bounds()
        self.pos = max(low, min(high, self.pos))

    def draw(self, surface: pygame.Surface):
        rect = self.rect
        pygame.draw.rect(surface, _PLAYER_COLOR[self.player], rect)
        if self.player == 2:
            # Onyx black is otherwise near-invisible against the background.
            pygame.draw.rect(surface, (255, 255, 255), rect, width=1)
