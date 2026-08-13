"""Paddle entity: position along its lane, movement clamped to its travel
range, and rendering. Orientation follows the lane automatically —
bottom/top lanes are horizontal paddles traveling along x; left/right lanes
are vertical paddles traveling along y — so placing a paddle on a side lane
just works, no special-casing needed elsewhere. (Corner transfer tubes,
letting a paddle move *between* lanes at runtime, are still later work —
this only covers a paddle placed on a given lane for the whole game/level.)"""

import pygame

from . import arena, constants, sprites
from .controls import Lane, lane_axis

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

    @property
    def rect(self) -> pygame.Rect:
        fixed = arena.LANE_FIXED_COORD[self.lane] + _STACK_SIGN[self.lane] * self.stack_order * STACK_OFFSET
        pos = round(self.pos)
        if lane_axis(self.lane) == "x":
            return pygame.Rect(pos, fixed, self.length, self.thickness)
        return pygame.Rect(fixed, pos, self.thickness, self.length)

    def move(self, delta: float, active_lanes):
        self.pos += delta
        low, high = arena.travel_bounds(self.lane, self.length, active_lanes)
        self.pos = max(low, min(high, self.pos))

    def draw(self, surface: pygame.Surface):
        rect = self.rect
        sprite = sprites.build_paddle_sprite(self.player)
        turret = sprites.build_turret_sprite(self.player)
        if lane_axis(self.lane) != "x":
            # Side lane: rotate the canonical horizontal sprites 90° to
            # stand them up vertically. Exact rotation direction doesn't
            # matter — the bar reads the same either way — so this doesn't
            # need to special-case left vs. right.
            sprite = pygame.transform.rotate(sprite, 90)
            turret = pygame.transform.rotate(turret, 90)
        surface.blit(sprite, rect.topleft)

        # Turret is a separate sprite/blit, not part of the paddle's own
        # canvas — mounted centered on the paddle, poking out past its
        # field-facing edge. Reuses _STACK_SIGN, which already encodes
        # "which way is toward the arena's interior" per lane, so this
        # doesn't need its own per-lane direction table. Purely decorative
        # for now (fixed hardware on the chassis); the Laser skill (0.4.0)
        # will control whether it actually fires, not whether it's drawn.
        sign = _STACK_SIGN[self.lane]
        tw, th = turret.get_size()
        if lane_axis(self.lane) == "x":
            turret_pos = (rect.left + (rect.width - tw) // 2, rect.top - th if sign < 0 else rect.bottom)
        else:
            turret_pos = (rect.left - tw if sign < 0 else rect.right, rect.top + (rect.height - th) // 2)
        surface.blit(turret, turret_pos)
