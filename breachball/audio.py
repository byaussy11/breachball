"""Minimal SFX/music wrapper (`play_sound`, `play_music`) — shared plumbing
alongside controls.py and display.py, built early per the roadmap so every
milestone after this just adds a sound file and a call into it.

No real SFX exist yet, so each named sound is currently a synthesized
placeholder tone (a short decaying sine blip) rather than a designed sound
effect — same idea as the placeholder rects standing in for sprites. Swapping
in real audio later means pointing _TONE_SPECS (or a future asset map) at
actual files; call sites don't change.
"""

import array
import math

import pygame

# name -> (frequency_hz, duration_seconds). Distinct pitch/length per event
# so they're at least tellable apart by ear during playtesting.
_TONE_SPECS = {
    "paddle_bounce": (440, 0.04),
    "wall_bounce": (330, 0.03),
    "brick_hit": (500, 0.03),
    "brick_break": (660, 0.06),
    "life_lost": (220, 0.25),
    "game_over": (150, 0.6),
    "win": (880, 0.5),
}

_SAMPLE_RATE = 44100


class AudioManager:
    def __init__(self):
        # WSL (the usual dev environment, per controls.py's keyboard
        # fallback) often has no audio device wired up at all — degrade to
        # silent no-ops rather than crashing the whole game over sound.
        try:
            pygame.mixer.init(frequency=_SAMPLE_RATE, size=-16, channels=2)
            self._enabled = True
        except pygame.error:
            print("AudioManager: no audio device available, sound disabled.")
            self._enabled = False

        self._sounds = (
            {
                name: self._make_tone(frequency, duration)
                for name, (frequency, duration) in _TONE_SPECS.items()
            }
            if self._enabled
            else {}
        )

    def _make_tone(
        self, frequency: float, duration_seconds: float, volume: float = 0.25
    ) -> pygame.mixer.Sound:
        sample_count = int(_SAMPLE_RATE * duration_seconds)
        amplitude = int(volume * 32767)
        samples = array.array("h")
        for i in range(sample_count):
            # Linear decay envelope so each tone reads as a short "blip"
            # instead of clicking sharply on/off at the start and end.
            envelope = 1.0 - (i / sample_count)
            value = int(amplitude * envelope * math.sin(2 * math.pi * frequency * i / _SAMPLE_RATE))
            samples.append(value)  # left
            samples.append(value)  # right
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play_sound(self, name: str):
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self, name: str):
        """Stub for now — background music lands with 0.9.0's first full
        Section, per the roadmap."""
        pass
