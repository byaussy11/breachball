"""Ball entity: position, velocity, and wall/paddle collision physics, per
the ball fields in the data schema."""

import math

import pygame

from . import constants
from .controls import Lane

# How much of the ball's total speed can go into the horizontal component on
# a paddle-edge hit, vs. dead center (0 horizontal, straight back). Keeps
# bounce angle responsive to hit position without letting edge hits go
# nearly parallel to the paddle.
PADDLE_BOUNCE_MAX_ANGLE_FACTOR = 0.75


class Ball:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color_state: str = "neutral",
        owner=None,
        piercing: bool = False,
        speed_multiplier: float = 1.0,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color_state = color_state
        self.owner = owner
        self.piercing = piercing
        self.speed_multiplier = speed_multiplier

    def update(self, paddles=(), brick_field=None):
        prev_x, prev_y = self.x, self.y
        self.x += self.vx * self.speed_multiplier
        self.y += self.vy * self.speed_multiplier

        hit_paddle = False
        for paddle in paddles:
            if self._bounce_off_paddle(paddle):
                hit_paddle = True
                break  # resolve at most one collision per frame
        if not hit_paddle and brick_field is not None:
            brick_field.resolve_ball_collision(self, prev_x, prev_y)

        self._bounce_off_walls()

    def _bounce_off_paddle(self, paddle) -> bool:
        rect = paddle.rect
        r = constants.BALL_RADIUS

        # Closest-point-on-rect-to-circle-center test — accurate for a
        # circle against an axis-aligned rect, including corner grazes.
        closest_x = max(rect.left, min(self.x, rect.right))
        closest_y = max(rect.top, min(self.y, rect.bottom))
        dx = self.x - closest_x
        dy = self.y - closest_y
        if dx * dx + dy * dy > r * r:
            return False

        speed = math.hypot(self.vx, self.vy)
        relative_hit = (self.x - rect.centerx) / (rect.width / 2)
        relative_hit = max(-1.0, min(1.0, relative_hit))

        new_vx = relative_hit * speed * PADDLE_BOUNCE_MAX_ANGLE_FACTOR
        new_vy = math.sqrt(max(speed * speed - new_vx * new_vx, 0.0))
        # Bottom paddle sends the ball back up; top paddle sends it back down.
        self.vy = -new_vy if paddle.lane == Lane.BOTTOM else new_vy
        self.vx = new_vx

        # Push the ball fully outside the paddle so it doesn't immediately
        # re-collide next frame.
        if paddle.lane == Lane.BOTTOM:
            self.y = rect.top - r
        else:
            self.y = rect.bottom + r

        return True

    def _bounce_off_walls(self):
        r = constants.BALL_RADIUS
        if self.x - r < 0:
            self.x = r
            self.vx = abs(self.vx)
        elif self.x + r > constants.VIRTUAL_WIDTH:
            self.x = constants.VIRTUAL_WIDTH - r
            self.vx = -abs(self.vx)

        if self.y - r < 0:
            self.y = r
            self.vy = abs(self.vy)
        elif self.y + r > constants.VIRTUAL_HEIGHT:
            # Placeholder bounce — once paddle collision and the shared-lives
            # "ball lost" rule exist, missing the bottom paddle replaces this.
            self.y = constants.VIRTUAL_HEIGHT - r
            self.vy = -abs(self.vy)

    def draw(self, surface: pygame.Surface):
        color = constants.BALL_COLORS.get(self.color_state, constants.BALL_COLORS["neutral"])
        center = (round(self.x), round(self.y))
        pygame.draw.circle(surface, color, center, constants.BALL_RADIUS)
        if self.color_state == "p2_owned":
            # Onyx black is otherwise near-invisible against the background.
            pygame.draw.circle(surface, (255, 255, 255), center, constants.BALL_RADIUS, width=1)
