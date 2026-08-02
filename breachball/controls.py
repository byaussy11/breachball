"""Input abstraction: turns raw hardware (spinners, or keyboard while
playtesting off-cabinet) into per-player logical movement along whatever
lane a paddle currently occupies.

Physical rig (per the project brief): two spinners, each wired through an
encoder-to-mouse adapter — player 1's drives mouse-Y relative motion,
player 2's drives mouse-X, per the current cabinet wiring. `MouseSpinnerDevice`
reads those two axes back apart.
`KeyboardSpinnerFallback` produces the same shape of signal from A/D and
Left/Right so gameplay can be built and tested on a regular machine.
"""

from enum import Enum

import pygame


class Lane(Enum):
    BOTTOM = "bottom"
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"


# Clockwise spinner rotation always drives the paddle the same way around the
# arena's perimeter loop, regardless of which lane it's currently in — so the
# controls don't seem to "flip" when a paddle moves lanes via a corner tube.
# Sign is applied to the raw clockwise-positive spinner delta to get movement
# along that lane's travel axis (x for bottom/top, y for left/right).
_CLOCKWISE_SIGN = {
    Lane.BOTTOM: 1,   # clockwise -> right (+x)
    Lane.RIGHT: -1,   # clockwise -> up (-y)
    Lane.TOP: -1,      # clockwise -> left (-x)
    Lane.LEFT: 1,      # clockwise -> down (+y)
}


def lane_axis(lane: Lane) -> str:
    """Which virtual-surface axis a paddle in this lane travels along."""
    return "x" if lane in (Lane.BOTTOM, Lane.TOP) else "y"


def spinner_to_lane_delta(lane: Lane, spinner_delta: float) -> float:
    """Convert a raw clockwise-positive spinner delta into a signed movement
    delta along the paddle's current lane, per the perimeter-loop mapping."""
    return spinner_delta * _CLOCKWISE_SIGN[lane]


class KeyboardSpinnerFallback:
    """Maps digital keys to a virtual spinner delta, so paddle movement can
    be tested without the physical cabinet attached."""

    KEY_BINDINGS = {
        1: {"neg": pygame.K_a, "pos": pygame.K_d},
        2: {"neg": pygame.K_LEFT, "pos": pygame.K_RIGHT},
    }
    SPEED = 6.0  # virtual "clockwise ticks" per frame while a key is held

    def __init__(self):
        self._keys = None

    def poll(self):
        self._keys = pygame.key.get_pressed()

    def get_spinner_delta(self, player: int) -> float:
        if self._keys is None:
            return 0.0
        bindings = self.KEY_BINDINGS[player]
        delta = 0.0
        if self._keys[bindings["pos"]]:
            delta += self.SPEED
        if self._keys[bindings["neg"]]:
            delta -= self.SPEED
        return delta


class MouseSpinnerDevice:
    """Reads the two spinners back apart from combined mouse motion: player 1
    off the Y axis, player 2 off the X axis, per the current cabinet wiring.

    Enable only when actually running on the cabinet — it grabs and hides the
    system cursor, which isn't wanted during normal desktop playtesting.
    """

    def __init__(self, invert_p1: bool = False, invert_p2: bool = False):
        self._invert = {1: -1 if invert_p1 else 1, 2: -1 if invert_p2 else 1}
        self._rel = (0, 0)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        pygame.mouse.get_rel()  # discard any accumulated jump before first poll

    def poll(self):
        self._rel = pygame.mouse.get_rel()

    def get_spinner_delta(self, player: int) -> float:
        raw = self._rel[1] if player == 1 else self._rel[0]
        return float(raw) * self._invert[player]


class Controls:
    """Combines the active input device(s) into per-player, per-lane paddle
    movement. Keyboard fallback is always live; mouse spinners are opt-in
    (flip on once testing on the actual cabinet)."""

    def __init__(self, use_mouse_spinners: bool = False):
        self.keyboard = KeyboardSpinnerFallback()
        self.mouse = (
            MouseSpinnerDevice(invert_p1=True, invert_p2=True)
            if use_mouse_spinners
            else None
        )

    def update(self):
        self.keyboard.poll()
        if self.mouse:
            self.mouse.poll()

    def get_spinner_delta(self, player: int) -> float:
        delta = self.keyboard.get_spinner_delta(player)
        if self.mouse:
            delta += self.mouse.get_spinner_delta(player)
        return delta

    def get_lane_movement(self, player: int, lane: Lane) -> float:
        return spinner_to_lane_delta(lane, self.get_spinner_delta(player))
