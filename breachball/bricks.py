"""Brick grid: mutable runtime playfield state (HP, destruction) built from
a level's static brick_grid + the shared catalog, plus its collision and
placeholder-shape rendering."""

import pygame

from . import constants


def _resolve_color(value):
    if isinstance(value, str) and value.startswith("#"):
        hex_value = value.lstrip("#")
        return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(pygame.Color(value))[:3]  # named colors, e.g. "silver"


class BrickCell:
    __slots__ = ("brick_id", "hp", "max_hp", "color", "sets_ball_color")

    def __init__(self, brick_id: str, hp, color, sets_ball_color=None):
        self.brick_id = brick_id
        self.hp = hp  # None = indestructible, never removed
        self.max_hp = hp  # starting hp, kept to size the damage notch as hp drops
        self.color = color
        # Optional ball_state name (e.g. "p1_owned") applied to whatever ball
        # hits this cell — color_trigger bricks per the project brief's
        # ball-ownership-color mechanic.
        self.sets_ball_color = sets_ball_color


class BrickField:
    """A level's brick grid at runtime: per-cell HP and removal-on-hit.
    Built fresh from level.brick_grid + the catalog each time a level loads."""

    def __init__(self, level, catalog, vertical_bounds=None):
        """`vertical_bounds`, if given, is an (top, bottom) pixel range to
        center the grid within — passed by the caller when a paddle actually
        occupies the top lane, so the grid sits centered between the two
        paddles instead of anchored under the fixed top margin. `None` (no
        top-lane paddle in play) keeps the old fixed, top-anchored layout."""
        grid = level.brick_grid or []
        self.rows = len(grid)
        self.cols = max((len(row) for row in grid), default=0)
        self.cells = [[self._make_cell(brick_id, catalog) for brick_id in row] for row in grid]

        cell_w = constants.BRICK_WIDTH + constants.BRICK_GAP
        grid_width = self.cols * cell_w
        area = constants.BRICK_AREA_RECT
        self._origin_x = area.x + max(0, (area.width - grid_width) // 2)

        if vertical_bounds is not None:
            top, bottom = vertical_bounds
            cell_h = constants.BRICK_HEIGHT + constants.BRICK_GAP
            grid_height = self.rows * cell_h - constants.BRICK_GAP if self.rows else 0
            self._origin_y = top + max(0, (bottom - top - grid_height) // 2)
        else:
            self._origin_y = area.y

    @staticmethod
    def _make_cell(brick_id, catalog):
        if not brick_id:
            return None
        entry = catalog.entries.get(brick_id)
        if entry is None:
            return BrickCell(brick_id, hp=1, color=constants.FALLBACK_BRICK_COLOR)
        return BrickCell(
            brick_id,
            entry.get("hp"),
            _resolve_color(entry["color"]),
            sets_ball_color=entry.get("sets_ball_color"),
        )

    def rect_for(self, row: int, col: int) -> pygame.Rect:
        cell_w = constants.BRICK_WIDTH + constants.BRICK_GAP
        cell_h = constants.BRICK_HEIGHT + constants.BRICK_GAP
        x = self._origin_x + col * cell_w
        y = self._origin_y + row * cell_h
        return pygame.Rect(x, y, constants.BRICK_WIDTH, constants.BRICK_HEIGHT)

    # Safety cap on overlaps resolved in one frame — in practice a ball
    # wedged in a corner where several bricks meet clears in 2-3 iterations.
    _MAX_COLLISIONS_PER_FRAME = 8

    def _find_overlap(self, ball):
        r = constants.BALL_RADIUS
        for row_idx, row in enumerate(self.cells):
            for col_idx, cell in enumerate(row):
                if cell is None:
                    continue
                rect = self.rect_for(row_idx, col_idx)
                # Standard AABB overlap test (ball treated as its bounding
                # box, consistent with the rest of this collision code).
                overlap_x = min(ball.x + r, rect.right) - max(ball.x - r, rect.left)
                overlap_y = min(ball.y + r, rect.bottom) - max(ball.y - r, rect.top)
                if overlap_x > 0 and overlap_y > 0:
                    return row_idx, col_idx, rect
        return None

    def resolve_ball_collision(self, ball, prev_x: float, prev_y: float, audio=None) -> bool:
        """Checks the ball against every live cell and resolves every
        overlap found this frame, not just the first — bricks sit only
        BRICK_GAP apart while the ball is several pixels wide, so it's
        common to overlap two neighboring bricks (a notch, a corner)
        simultaneously; fixing just one and leaving the ball still lodged
        in the other is what caused it to visibly stick between bricks.

        `prev_x`/`prev_y` is the ball's position *before* this frame's move
        — a position already known to be clear. Resolving off of "which
        side did it approach from" is far more robust than resolving off of
        "how deep is it embedded now": penetration-depth pushes broke down
        whenever the ball's own bounding box was larger than the brick
        along an axis (ball diameter 8px vs. brick height 6px), leaving
        residual overlap that the next frame would re-trigger. Repositioning
        exactly outside the hit face (same approach paddle collision already
        uses) sidesteps that entirely — no magnitude math to get wrong.

        A given velocity axis is only reflected once per frame (reflecting
        it once per overlapping brick would cancel back out for a flat
        two-brick hit); each overlap still damages its own brick."""
        r = constants.BALL_RADIUS
        hit_any = False
        flipped_x = False
        flipped_y = False

        for _ in range(self._MAX_COLLISIONS_PER_FRAME):
            found = self._find_overlap(ball)
            if found is None:
                break
            row_idx, col_idx, rect = found
            cell = self.cells[row_idx][col_idx]

            came_from_left = prev_x + r <= rect.left
            came_from_right = prev_x - r >= rect.right
            came_from_above = prev_y + r <= rect.top
            came_from_below = prev_y - r >= rect.bottom

            if came_from_above or came_from_below:
                axis = "y"
            elif came_from_left or came_from_right:
                axis = "x"
            else:
                # Neither axis cleanly explains the approach (e.g. already
                # grazing diagonally last frame too) — fall back to
                # whichever axis the ball is less deeply into.
                overlap_x = min(ball.x + r, rect.right) - max(ball.x - r, rect.left)
                overlap_y = min(ball.y + r, rect.bottom) - max(ball.y - r, rect.top)
                axis = "x" if overlap_x < overlap_y else "y"

            if axis == "x":
                if not flipped_x:
                    ball.vx = -ball.vx
                    flipped_x = True
                ball.x = rect.left - r if (came_from_left or ball.x < rect.centerx) else rect.right + r
            else:
                if not flipped_y:
                    ball.vy = -ball.vy
                    flipped_y = True
                ball.y = rect.top - r if (came_from_above or ball.y < rect.centery) else rect.bottom + r

            if audio:
                audio.play_sound("brick_hit")

            if cell.sets_ball_color is not None:
                ball.set_color_state(cell.sets_ball_color)

            if cell.hp is not None:
                cell.hp -= 1
                if cell.hp <= 0:
                    self.cells[row_idx][col_idx] = None
                    if audio:
                        audio.play_sound("brick_break")

            hit_any = True

        return hit_any

    def is_cleared(self) -> bool:
        """True once every breakable brick is gone. Indestructible cells
        (hp is None) never leave the grid, so they're excluded — matches the
        brief's win condition, which only counts breakable bricks."""
        return not any(
            cell is not None and cell.hp is not None
            for row in self.cells
            for cell in row
        )

    def draw(self, surface: pygame.Surface):
        for row_idx, row in enumerate(self.cells):
            for col_idx, cell in enumerate(row):
                if cell is not None:
                    rect = self.rect_for(row_idx, col_idx)
                    pygame.draw.rect(surface, cell.color, rect)
                    self._draw_damage_notch(surface, cell, rect)

    def _draw_damage_notch(self, surface: pygame.Surface, cell, rect: pygame.Rect):
        """Armored bricks (max_hp > 1) show damage as a notch eaten inward
        from the left and right edges along the brick's middle row, 1px per
        hit taken, punched through to the background color."""
        if cell.max_hp is None or cell.max_hp <= 1:
            return
        hits_taken = cell.max_hp - cell.hp
        if hits_taken <= 0:
            return
        notch_width = min(hits_taken, rect.width // 2)
        mid_y = rect.top + rect.height // 2
        left_notch = pygame.Rect(rect.left, mid_y, notch_width, 1)
        right_notch = pygame.Rect(rect.right - notch_width, mid_y, notch_width, 1)
        pygame.draw.rect(surface, constants.BACKGROUND_COLOR, left_notch)
        pygame.draw.rect(surface, constants.BACKGROUND_COLOR, right_notch)
