"""Renders everything to a fixed 640x480 virtual surface, then scales that
surface up to whatever the real window/monitor turns out to be. Keeps
gameplay math and layout independent of final cabinet hardware — picking
real hardware later just changes the scale factor.
"""

import pygame

from . import constants


class Display:
    def __init__(
        self,
        window_size=constants.DEFAULT_WINDOW_SIZE,
        fullscreen: bool = False,
        caption: str = "Breach Ball",
    ):
        pygame.display.set_caption(caption)
        flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
        self.window = pygame.display.set_mode(window_size, flags)
        self.surface = pygame.Surface(constants.VIRTUAL_SIZE)

    def begin_frame(self, clear_color=constants.BACKGROUND_COLOR) -> pygame.Surface:
        """Clears and returns the virtual surface for this frame's drawing."""
        self.surface.fill(clear_color)
        return self.surface

    def present(self):
        """Scales the virtual surface (preserving aspect ratio, letterboxed)
        onto the real window and flips it."""
        window_w, window_h = self.window.get_size()
        scale = min(window_w / constants.VIRTUAL_WIDTH, window_h / constants.VIRTUAL_HEIGHT)
        scaled_w = max(1, int(constants.VIRTUAL_WIDTH * scale))
        scaled_h = max(1, int(constants.VIRTUAL_HEIGHT * scale))

        # pygame.transform.scale does a fast, unfiltered resize (no
        # smoothing) — the same nearest-neighbor-style approach the brief
        # calls for so pixel art stays crisp when scaled up.
        scaled = pygame.transform.scale(self.surface, (scaled_w, scaled_h))

        self.window.fill((0, 0, 0))
        x = (window_w - scaled_w) // 2
        y = (window_h - scaled_h) // 2
        self.window.blit(scaled, (x, y))
        pygame.display.flip()

    def handle_resize(self, size):
        self.window = pygame.display.set_mode(size, self.window.get_flags())
