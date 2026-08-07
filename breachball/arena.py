"""Static arena structure that isn't owned by any single paddle: where each
lane sits (shared with paddle.py so paddle placement and corner geometry can
never drift apart), and the corner blocks that keep two perpendicular
paddles from sliding past/overlapping each other at a corner they share.

A corner gets a block only when *both* of its bordering lanes actually have
a paddle in play this run — that's the only situation a block solves
(stopping two paddles from colliding at the corner). A corner bordered by
just one paddle-lane has nothing there to collide with, so it's left open
and that paddle can travel all the way to the true screen edge. (Corner
transfer tubes will be a second, later reason for a block to exist at a
corner — see arena_type "l_shaped"/split-zone work in the roadmap — but
that's still ahead of us; a lone paddle-lane isn't reason enough on its
own.) Each block that does exist is sized and positioned to sit flush
against both paddles that border it: its near edges line up exactly with
each paddle's ball-facing edge, so a paddle sliding toward the corner meets
the block with no gap and no overlap. Blocks are solid — see
Ball._bounce_off_corner_blocks in ball.py — so the ball deflects off them
like any other wall."""

import pygame

from . import constants
from .controls import Lane, lane_axis

# Fixed coordinate (perpendicular to the paddle's travel axis) for each
# lane — how far in from that lane's screen edge the paddle sits. y for the
# horizontal bottom/top lanes, x for the vertical left/right lanes. Shared
# with paddle.py so paddle placement and corner-block geometry are always
# in lockstep.
#
# BOTTOM/RIGHT paddles have their ball-facing edge at the PADDLE_LANE_INSET
# mark and their thickness extends *toward* the wall from there; TOP/LEFT
# mirror that (thickness toward the wall too, i.e. *away* from the arena
# interior) by starting PADDLE_THICKNESS earlier, so all four lanes end up
# with the same inset-to-front-edge and the same gap-to-wall, regardless of
# which screen edge they're on.
LANE_FIXED_COORD = {
    Lane.BOTTOM: constants.VIRTUAL_HEIGHT - constants.PADDLE_LANE_INSET,
    Lane.TOP: constants.PADDLE_LANE_INSET - constants.PADDLE_THICKNESS,
    Lane.LEFT: constants.PADDLE_LANE_INSET - constants.PADDLE_THICKNESS,
    Lane.RIGHT: constants.VIRTUAL_WIDTH - constants.PADDLE_LANE_INSET,
}

# The two lanes bordering each corner, always given as (horizontal lane,
# vertical lane) — that ordering is relied on below to know which lane's
# front edge sets the block's y-extent vs. its x-extent.
_CORNER_LANES = {
    "top_left": (Lane.TOP, Lane.LEFT),
    "top_right": (Lane.TOP, Lane.RIGHT),
    "bottom_left": (Lane.BOTTOM, Lane.LEFT),
    "bottom_right": (Lane.BOTTOM, Lane.RIGHT),
}

# The other lane bordering the corner at each end of a given lane's travel
# range — e.g. a BOTTOM paddle's low end (x near 0) sits at the bottom-left
# corner, shared with LEFT. Used to look up which paddle (if any) a given
# end's travel should be clamped flush against.
_CORNER_NEIGHBOR = {
    (Lane.BOTTOM, "low"): Lane.LEFT,
    (Lane.BOTTOM, "high"): Lane.RIGHT,
    (Lane.TOP, "low"): Lane.LEFT,
    (Lane.TOP, "high"): Lane.RIGHT,
    (Lane.LEFT, "low"): Lane.TOP,
    (Lane.LEFT, "high"): Lane.BOTTOM,
    (Lane.RIGHT, "low"): Lane.TOP,
    (Lane.RIGHT, "high"): Lane.BOTTOM,
}

# Deliberately dim/desaturated so it reads as inert structure, not a brick
# or a playable surface.
CORNER_COLOR = (40, 40, 55)


def _lane_front_edge(lane: Lane) -> float:
    """The fixed-axis coordinate of this lane's ball/interior-facing edge
    (independent of travel position) — BOTTOM/RIGHT paddles face their
    smaller fixed-axis coordinate; TOP/LEFT face their larger one. Thanks
    to LANE_FIXED_COORD's symmetric insets, this comes out PADDLE_LANE_INSET
    from the nearest wall for all four lanes."""
    fixed = LANE_FIXED_COORD[lane]
    if lane in (Lane.BOTTOM, Lane.RIGHT):
        return fixed
    return fixed + constants.PADDLE_THICKNESS


def corner_blocks(active_lanes) -> list[pygame.Rect]:
    """One rect per corner where *both* bordering lanes are in
    `active_lanes` — the only case where a block is actually needed, since
    it's two paddles that could otherwise collide there. A corner with just
    one paddle-lane bordering it is left open."""
    rects = []
    for h_lane, v_lane in _CORNER_LANES.values():
        if h_lane not in active_lanes or v_lane not in active_lanes:
            continue
        y_edge = _lane_front_edge(h_lane)
        x_edge = _lane_front_edge(v_lane)
        y0, y1 = sorted((0 if h_lane == Lane.TOP else constants.VIRTUAL_HEIGHT, y_edge))
        x0, x1 = sorted((0 if v_lane == Lane.LEFT else constants.VIRTUAL_WIDTH, x_edge))
        rects.append(pygame.Rect(x0, y0, x1 - x0, y1 - y0))
    return rects


def travel_bounds(lane: Lane, length: float, active_lanes) -> tuple[float, float]:
    """Min/max for a `length`-long paddle's `pos` on `lane`. Each end
    clamps flush against a block only where one actually exists — i.e.
    where the neighboring lane at that corner is also in `active_lanes` (so
    a paddle could otherwise slide into one occupying that lane). An end
    with no neighbor paddle has no block, so the paddle can travel all the
    way to the true screen edge there."""
    low_neighbor = _CORNER_NEIGHBOR[(lane, "low")]
    high_neighbor = _CORNER_NEIGHBOR[(lane, "high")]
    axis_max = constants.VIRTUAL_WIDTH if lane_axis(lane) == "x" else constants.VIRTUAL_HEIGHT
    low = _lane_front_edge(low_neighbor) if low_neighbor in active_lanes else 0.0
    high = (
        _lane_front_edge(high_neighbor) - length
        if high_neighbor in active_lanes
        else axis_max - length
    )
    return low, high


def draw(surface: pygame.Surface, active_lanes):
    for rect in corner_blocks(active_lanes):
        pygame.draw.rect(surface, CORNER_COLOR, rect)
