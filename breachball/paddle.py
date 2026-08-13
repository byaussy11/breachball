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

        # Death-animation state — see start_death_animation/
        # update_death_animation/finish_death_animation below. `dying` true
        # for the whole life-lost pause, covering both the frames actually
        # playing and the blank hold afterward once they run out.
        self.dying = False
        self._death_frames = []
        self._death_frame_index = 0
        self._death_frame_elapsed = 0.0
        self._death_blank_elapsed = 0.0

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
        if self.dying:
            if self._death_frame_index >= len(self._death_frames):
                # Frames exhausted — hold blank/invisible until respawn
                # clears `dying` (see finish_death_animation).
                return
            frame = self._death_frames[self._death_frame_index]
            if lane_axis(self.lane) != "x":
                frame = pygame.transform.rotate(frame, 90)
            fw, fh = frame.get_size()
            # Death frames are their own (larger) size, not
            # PADDLE_WIDTH/THICKNESS, so center on the paddle's rect rather
            # than blitting at its topleft.
            surface.blit(frame, (rect.centerx - fw // 2, rect.centery - fh // 2))
            return

        sprite = sprites.build_paddle_sprite(self.player)
        if lane_axis(self.lane) != "x":
            # Side lane: rotate the canonical horizontal sprite 90° to
            # stand it up vertically. Exact rotation direction doesn't
            # matter — the bar reads the same either way — so this doesn't
            # need to special-case left vs. right.
            sprite = pygame.transform.rotate(sprite, 90)
        surface.blit(sprite, rect.topleft)

    def start_death_animation(self) -> bool:
        """Begins the life-lost death animation for this paddle's player.
        Returns True if frames exist and the animation actually started
        (caller should pause play for it); False if this player has no
        death art yet, in which case nothing was started and the caller
        should skip straight to respawn with no pause."""
        frames = sprites.build_paddle_death_frames(self.player)
        if not frames:
            return False
        self._death_frames = frames
        self._death_frame_index = 0
        self._death_frame_elapsed = 0.0
        self._death_blank_elapsed = 0.0
        self.dying = True
        return True

    def update_death_animation(self, dt_ms: float) -> bool:
        """Advances the death animation by dt_ms. Frames play through
        once, then the paddle holds blank (draw() shows nothing, per
        _death_frame_index >= len(_death_frames)) for
        PADDLE_DEATH_BLANK_HOLD_MS before this returns True — the signal
        for the caller to actually respawn and call
        finish_death_animation()."""
        if self._death_frame_index >= len(self._death_frames):
            self._death_blank_elapsed += dt_ms
            return self._death_blank_elapsed >= constants.PADDLE_DEATH_BLANK_HOLD_MS

        self._death_frame_elapsed += dt_ms
        while self._death_frame_elapsed >= constants.PADDLE_DEATH_FRAME_DURATION_MS:
            self._death_frame_elapsed -= constants.PADDLE_DEATH_FRAME_DURATION_MS
            self._death_frame_index += 1
            if self._death_frame_index >= len(self._death_frames):
                break
        return False

    def finish_death_animation(self):
        """Clears death-animation state so draw() resumes showing the
        normal paddle sprite. Call once respawn actually happens."""
        self.dying = False
        self._death_frames = []
        self._death_frame_index = 0
        self._death_frame_elapsed = 0.0
        self._death_blank_elapsed = 0.0
