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
        # Non-None while the ball is parked on a paddle awaiting launch (game
        # start, or re-serve after a life is lost) — physics are suspended
        # and the ball just tracks the paddle until launch() is called.
        self.attached_paddle = None

    def attach_to_paddle(self, paddle):
        """Parks the ball against `paddle`, following its position each
        frame until launch() releases it."""
        self.attached_paddle = paddle
        self.vx = 0.0
        self.vy = 0.0
        self.color_state = "neutral"
        self.owner = None
        self._snap_to_paddle(paddle)

    def launch(self, vx: float, vy: float):
        """Releases the ball from its paddle with the given velocity."""
        self.attached_paddle = None
        self.vx = vx
        self.vy = vy

    # color_state -> owning player, kept alongside color_state so the two
    # never drift out of sync (owner is derived, not set independently).
    _OWNER_BY_COLOR_STATE = {"p1_owned": 1, "p2_owned": 2}

    def set_color_state(self, color_state: str):
        """Applies a new color_state (e.g. from a color_trigger brick) and
        updates `owner` to match — neutral/hazard have no owner."""
        self.color_state = color_state
        self.owner = self._OWNER_BY_COLOR_STATE.get(color_state)

    def _snap_to_paddle(self, paddle):
        rect = paddle.rect
        r = constants.BALL_RADIUS
        self.x = rect.centerx
        self.y = rect.bottom + r if paddle.lane == Lane.TOP else rect.top - r

    def update(self, paddles=(), brick_field=None, audio=None) -> bool:
        """Advances the ball one frame. Returns True if the ball was lost
        this frame. Whether an edge is a loss line or just a bounce wall is
        derived from `paddles` each frame: any lane with a paddle actually
        defending it this frame is a loss line (missing that paddle means
        the ball exits the screen behind it); a lane with no paddle in it
        is just a wall, same as the untouched left/right edges. This makes
        the top edge behave correctly whether or not a paddle currently
        occupies the top lane, without needing a separate arena_type flag."""
        if self.attached_paddle is not None:
            self._snap_to_paddle(self.attached_paddle)
            return False

        prev_x, prev_y = self.x, self.y
        self.x += self.vx * self.speed_multiplier
        self.y += self.vy * self.speed_multiplier

        hit_paddle = False
        for paddle in paddles:
            if self._bounce_off_paddle(paddle):
                hit_paddle = True
                if audio:
                    audio.play_sound("paddle_bounce")
                break  # resolve at most one collision per frame
        if not hit_paddle and brick_field is not None:
            brick_field.resolve_ball_collision(self, prev_x, prev_y, audio=audio)

        lanes_with_paddles = {paddle.lane for paddle in paddles}
        r = constants.BALL_RADIUS
        if Lane.BOTTOM in lanes_with_paddles and self.y + r > constants.VIRTUAL_HEIGHT:
            return True
        if Lane.TOP in lanes_with_paddles and self.y - r < 0:
            return True

        self._bounce_off_walls(
            audio=audio,
            bounce_top=Lane.TOP not in lanes_with_paddles,
            bounce_bottom=Lane.BOTTOM not in lanes_with_paddles,
        )
        return False

    def _can_be_hit_by(self, paddle) -> bool:
        """Ball ownership-color enforcement, per the brief: neutral is
        hittable by either paddle, an owned color only by its matching
        player, and hazard by neither. A disallowed touch passes straight
        through with no collision response at all — the paddle simply isn't
        there as far as that ball is concerned."""
        if self.color_state == "neutral":
            return True
        if self.color_state == "hazard":
            return False
        if self.color_state == "p1_owned":
            return paddle.player == 1
        if self.color_state == "p2_owned":
            return paddle.player == 2
        return True

    def _bounce_off_paddle(self, paddle) -> bool:
        if not self._can_be_hit_by(paddle):
            return False

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

    def _bounce_off_walls(self, audio=None, bounce_top: bool = True, bounce_bottom: bool = False):
        """Bounces off the left/right walls unconditionally, and off the
        top/bottom edges only when told to — update() already returned a
        lost-ball result before calling this for any edge with a paddle
        actually defending it this frame, so `bounce_top`/`bounce_bottom`
        only fire for a lane with no paddle in it (a bare wall, same
        treatment as the always-on left/right walls)."""
        r = constants.BALL_RADIUS
        bounced = False
        if self.x - r < 0:
            self.x = r
            self.vx = abs(self.vx)
            bounced = True
        elif self.x + r > constants.VIRTUAL_WIDTH:
            self.x = constants.VIRTUAL_WIDTH - r
            self.vx = -abs(self.vx)
            bounced = True

        if bounce_top and self.y - r < 0:
            self.y = r
            self.vy = abs(self.vy)
            bounced = True
        elif bounce_bottom and self.y + r > constants.VIRTUAL_HEIGHT:
            self.y = constants.VIRTUAL_HEIGHT - r
            self.vy = -abs(self.vy)
            bounced = True

        if bounced and audio:
            audio.play_sound("wall_bounce")

    def draw(self, surface: pygame.Surface):
        color = constants.BALL_COLORS.get(self.color_state, constants.BALL_COLORS["neutral"])
        center = (round(self.x), round(self.y))
        pygame.draw.circle(surface, color, center, constants.BALL_RADIUS)
        if self.color_state == "p2_owned":
            # Onyx black is otherwise near-invisible against the background.
            pygame.draw.circle(surface, (255, 255, 255), center, constants.BALL_RADIUS, width=1)
