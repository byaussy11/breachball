"""Paddle entity: position along its lane, movement clamped to its travel
range, and rendering. Scoped to the default stacked bottom/top layout for
now — left/right (vertical) lanes arrive with corner-tube support later."""

import pygame

from . import constants
from .controls import Lane

_LANE_Y = {
    Lane.BOTTOM: constants.VIRTUAL_HEIGHT - 20,
    Lane.TOP: 20,
}

# Vertical gap used when two paddles share the same lane — per the brief,
# they stack "one above the other" rather than overlapping, same
# relationship as the default top/bottom layout, just both near one edge.
STACK_OFFSET = 16

_PLAYER_COLOR = {
    1: (192, 192, 192),  # P1 = silver
    2: (20, 20, 20),      # P2 = onyx black
}


class Paddle:
    def __init__(self, player: int, lane: Lane, x: float = None, stack_order: int = 0):
        self.player = player
        self.lane = lane
        self.width = constants.PADDLE_WIDTH
        self.thickness = constants.PADDLE_THICKNESS
        self.x = x if x is not None else (constants.VIRTUAL_WIDTH - self.width) / 2
        # 0 = normal lane position; 1+ nudges this paddle toward the center
        # of the arena, for when it shares a lane with another paddle.
        self.stack_order = stack_order

    @property
    def rect(self) -> pygame.Rect:
        base_y = _LANE_Y[self.lane]
        y = base_y - self.stack_order * STACK_OFFSET if self.lane == Lane.BOTTOM else base_y + self.stack_order * STACK_OFFSET
        return pygame.Rect(round(self.x), y, self.width, self.thickness)

    def move(self, delta: float):
        self.x += delta
        # travel_range defaults to full_width per the schema; narrower
        # per-level ranges are a later level-config concern.
        self.x = max(0, min(constants.VIRTUAL_WIDTH - self.width, self.x))

    def draw(self, surface: pygame.Surface):
        rect = self.rect
        pygame.draw.rect(surface, _PLAYER_COLOR[self.player], rect)
        if self.player == 2:
            # Onyx black is otherwise near-invisible against the background.
            pygame.draw.rect(surface, (255, 255, 255), rect, width=1)
