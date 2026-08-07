"""Ball entity: position, velocity, and wall/paddle collision physics, per
the ball fields in the data schema."""

import math

import pygame

from . import arena, constants
from .controls import Lane, lane_axis

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
        if lane_axis(paddle.lane) == "x":
            # Horizontal paddle (bottom/top): ball centers on the paddle's
            # x and sits just outside its inward-facing edge.
            self.x = rect.centerx
            self.y = rect.bottom + r if paddle.lane == Lane.TOP else rect.top - r
        else:
            # Vertical paddle (left/right): ball centers on the paddle's y
            # and sits just outside its inward-facing edge.
            self.y = rect.centery
            self.x = rect.right + r if paddle.lane == Lane.LEFT else rect.left - r

    def update(self, paddles=(), brick_field=None, audio=None, death_lanes=None) -> bool:
        """Advances the ball one frame. Returns True if the ball was lost
        this frame.

        Whether an edge is a loss line or just a bounce wall is governed by
        `death_lanes`, not by paddle presence alone — a paddle occupying a
        lane and that lane being able to lose the ball are separate facts.
        Shared-zone's top paddle, and eventually a mostly-solid wall with
        enemy-spawn holes, are both cases of a paddle sitting on a lane that
        isn't a death line: a miss there just bounces off the wall behind
        it instead of costing a life. `death_lanes` defaults to every lane
        with a paddle in it (today's split-zone-equivalent behavior) when
        the caller doesn't pass one explicitly."""
        if self.attached_paddle is not None:
            self._snap_to_paddle(self.attached_paddle)
            return False

        prev_x, prev_y = self.x, self.y
        self.x += self.vx * self.speed_multiplier
        self.y += self.vy * self.speed_multiplier

        lanes_with_paddles = {paddle.lane for paddle in paddles}
        # Which lanes can actually lose the ball this frame — see the
        # docstring above. Kept distinct from lanes_with_paddles, which is
        # only about paddle/corner-block collision and says nothing about
        # loss lines.
        death_lanes = lanes_with_paddles if death_lanes is None else set(death_lanes)

        hit_paddle = False
        for paddle in paddles:
            if self._bounce_off_paddle(paddle):
                hit_paddle = True
                if audio:
                    audio.play_sound("paddle_bounce")
                break  # resolve at most one collision per frame
        hit_block = False
        if not hit_paddle:
            hit_block = self._bounce_off_corner_blocks(lanes_with_paddles, prev_x, prev_y, audio=audio)
        if not hit_paddle and not hit_block and brick_field is not None:
            brick_field.resolve_ball_collision(self, prev_x, prev_y, audio=audio)

        r = constants.BALL_RADIUS
        if Lane.BOTTOM in death_lanes and self.y + r > constants.VIRTUAL_HEIGHT:
            return True
        if Lane.TOP in death_lanes and self.y - r < 0:
            return True
        if Lane.RIGHT in death_lanes and self.x + r > constants.VIRTUAL_WIDTH:
            return True
        if Lane.LEFT in death_lanes and self.x - r < 0:
            return True

        self._bounce_off_walls(
            audio=audio,
            bounce_top=Lane.TOP not in death_lanes,
            bounce_bottom=Lane.BOTTOM not in death_lanes,
            bounce_left=Lane.LEFT not in death_lanes,
            bounce_right=Lane.RIGHT not in death_lanes,
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

        if lane_axis(paddle.lane) == "x":
            # Horizontal paddle: reflects vy; bounce angle driven by hit
            # position along the paddle's x extent.
            relative_hit = (self.x - rect.centerx) / (rect.width / 2)
            relative_hit = max(-1.0, min(1.0, relative_hit))
            new_vx = relative_hit * speed * PADDLE_BOUNCE_MAX_ANGLE_FACTOR
            new_vy = math.sqrt(max(speed * speed - new_vx * new_vx, 0.0))
            # Bottom paddle sends the ball back up; top paddle sends it
            # back down.
            self.vy = -new_vy if paddle.lane == Lane.BOTTOM else new_vy
            self.vx = new_vx
            # Push the ball fully outside the paddle so it doesn't
            # immediately re-collide next frame.
            self.y = rect.top - r if paddle.lane == Lane.BOTTOM else rect.bottom + r
        else:
            # Vertical paddle: reflects vx; bounce angle driven by hit
            # position along the paddle's y extent.
            relative_hit = (self.y - rect.centery) / (rect.height / 2)
            relative_hit = max(-1.0, min(1.0, relative_hit))
            new_vy = relative_hit * speed * PADDLE_BOUNCE_MAX_ANGLE_FACTOR
            new_vx = math.sqrt(max(speed * speed - new_vy * new_vy, 0.0))
            # Left paddle sends the ball right; right paddle sends it left.
            self.vx = new_vx if paddle.lane == Lane.LEFT else -new_vx
            self.vy = new_vy
            self.x = rect.right + r if paddle.lane == Lane.LEFT else rect.left - r

        return True

    def _bounce_off_corner_blocks(self, lanes_with_paddles, prev_x: float, prev_y: float, audio=None) -> bool:
        """Corner blocks (arena.py) are solid — the ball reflects off
        whichever face it hit rather than passing through. Axis-of-approach
        logic mirrors BrickField.resolve_ball_collision (same flush,
        axis-aligned geometry, just a permanent obstacle instead of a
        destructible one), so a graze off a block's corner still resolves
        the same way a brick's does."""
        r = constants.BALL_RADIUS
        for rect in arena.corner_blocks(lanes_with_paddles):
            overlap_x = min(self.x + r, rect.right) - max(self.x - r, rect.left)
            overlap_y = min(self.y + r, rect.bottom) - max(self.y - r, rect.top)
            if overlap_x <= 0 or overlap_y <= 0:
                continue

            came_from_left = prev_x + r <= rect.left
            came_from_right = prev_x - r >= rect.right
            came_from_above = prev_y + r <= rect.top
            came_from_below = prev_y - r >= rect.bottom

            if came_from_above or came_from_below:
                axis = "y"
            elif came_from_left or came_from_right:
                axis = "x"
            else:
                axis = "x" if overlap_x < overlap_y else "y"

            if axis == "x":
                self.vx = -self.vx
                self.x = rect.left - r if (came_from_left or self.x < rect.centerx) else rect.right + r
            else:
                self.vy = -self.vy
                self.y = rect.top - r if (came_from_above or self.y < rect.centery) else rect.bottom + r

            if audio:
                audio.play_sound("wall_bounce")
            return True  # resolve at most one block per frame

        return False

    def _bounce_off_walls(
        self,
        audio=None,
        bounce_top: bool = True,
        bounce_bottom: bool = False,
        bounce_left: bool = True,
        bounce_right: bool = True,
    ):
        """Bounces off any edge told to — update() already returned a
        lost-ball result before calling this for any death-line edge, so
        each `bounce_*` flag fires for a lane that isn't a death line this
        frame, whether that's because no paddle is there at all (a bare
        wall) or because a paddle occupies it in a non-death-line role
        (e.g. shared-zone's top paddle)."""
        r = constants.BALL_RADIUS
        bounced = False
        if bounce_left and self.x - r < 0:
            self.x = r
            self.vx = abs(self.vx)
            bounced = True
        elif bounce_right and self.x + r > constants.VIRTUAL_WIDTH:
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
