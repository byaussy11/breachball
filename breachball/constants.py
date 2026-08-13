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

# Life-lost death animation, played once on the paddle that let the ball
# past before it respawns. Deliberately its own size rather than
# PADDLE_WIDTH/THICKNESS — an explosion/burst effect reads better bigger
# than the thin paddle bar, same reasoning that gave the turret its own
# constants — sized to match the source art (see sprites.py). Frame
# duration is played slower than the authored GIF's native 100ms/frame, by
# feel — reads better lingering than at the GIF's original quick-burst
# pace. After the frames finish, the paddle holds blank for
# PADDLE_DEATH_BLANK_HOLD_MS before respawn — a beat of "gone" before the
# paddle comes back, not just a stack of frames.
PADDLE_DEATH_FRAME_WIDTH = 50
PADDLE_DEATH_FRAME_HEIGHT = 20
PADDLE_DEATH_FRAME_DURATION_MS = 200
PADDLE_DEATH_BLANK_HOLD_MS = 1000

# How far a lane's paddle sits, measured from its ball/interior-facing edge
# in to the screen edge it's nearest. Same inset for all four lanes, so a
# paddle's "reach" toward a corner is identical regardless of which lane
# it's on — see arena.py, which reuses this to size/place corner blocks so
# they land flush against whichever paddle(s) border that corner.
PADDLE_LANE_INSET = 20

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
