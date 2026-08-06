import pygame

# Virtual/logical resolution everything is rendered to before scaling to the
# real window. 4:3 landscape per the project brief; final cabinet monitor is
# still undecided, so gameplay math stays fixed against this coordinate space.
VIRTUAL_WIDTH = 640
VIRTUAL_HEIGHT = 480
VIRTUAL_SIZE = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

DEFAULT_WINDOW_SIZE = (1280, 960)

PADDLE_WIDTH = 40
PADDLE_THICKNESS = 8

# Side length of the dead-zone square reserved at each of the arena's four
# corners (see arena.py) so two perpendicular paddles (e.g. bottom + right)
# can't slide far enough to cross or overlap each other. Matches
# PADDLE_WIDTH so a maxed-out paddle's far edge lands flush with the
# corner square's edge instead of stopping short or clipping into it.
CORNER_SIZE = 40

# Rect (within the virtual surface) that the brick grid is laid out into.
# Leaves room above/below for HUD, enemies, and paddle lanes. Grids narrower
# than this area are centered horizontally within it. Used as-is (fixed,
# top-anchored) whenever there's no paddle occupying the top lane; when
# there is, BrickField instead centers the grid vertically between the two
# paddles — see BRICK_AREA_VERTICAL_MARGIN.
BRICK_AREA_RECT = pygame.Rect(16, 40, VIRTUAL_WIDTH - 32, 220)

# Breathing room kept between a paddle's inner edge and the brick grid when
# vertically centering the grid between a top and bottom paddle.
BRICK_AREA_VERTICAL_MARGIN = 16

# Brick size is fixed (not stretched to fill the area) so it stays constant
# regardless of a given level's grid dimensions. A standalone value, not
# derived from PADDLE_WIDTH — playtested to look right at 13x6 and should
# stay put even if paddle size changes later.
BRICK_WIDTH = 13
BRICK_HEIGHT = 6
BRICK_GAP = 1

# Shown in place of a brick whose catalog ID isn't found, so a bad level/
# catalog reference is loud instead of silently invisible.
FALLBACK_BRICK_COLOR = (255, 0, 255)

BACKGROUND_COLOR = (10, 10, 20)

BALL_RADIUS = 4

# Shared pool per the brief — not per-player, since individual lives would
# create awkward questions for cooperative mechanics if one paddle ran out
# while the other kept playing.
STARTING_LIVES = 3

# Speed applied when the ball launches off the serving paddle, whether at
# the start of a life or after a re-serve. Magnitudes only — the caller
# applies sign to vy based on which lane the serving paddle is in (up from a
# bottom-lane paddle, down from a top-lane one).
BALL_LAUNCH_VX = 3.0
BALL_LAUNCH_VY = 3.2

# Mirrors the ball's color_state field from the data schema. p1_owned/
# p2_owned match the paddle colors they correspond to (silver/onyx black).
# neutral is deliberately kept out of the white/gray family (warm pale
# yellow rather than near-white) so it doesn't get lost next to P1's silver
# — both were light, low-saturation grays and read as the same color at the
# ball's small on-screen size.
BALL_COLORS = {
    "neutral": (240, 220, 120),
    "p1_owned": (192, 192, 192),
    "p2_owned": (20, 20, 20),
    "hazard": (200, 40, 40),
}
