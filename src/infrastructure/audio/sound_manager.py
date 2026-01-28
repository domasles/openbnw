"""Sound effects manager for Ursina."""

from ursina import *
import random


class SoundManager:
    """
    Wraps Ursina sound effects for cleaner code.
    Infrastructure layer - Ursina specific.
    """

    @staticmethod
    def play_gun_shot():
        """Play procedural gun shot sound."""
        try:
            from ursina.prefabs.ursfx import ursfx

            ursfx(
                [(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
                volume=0.5,
                wave="noise",
                pitch=random.uniform(-13, -12),
                pitch_change=-12,
                speed=3.0,
            )
        except Exception as e:
            # Silent fail if ursfx not available
            pass

    @staticmethod
    def play_countdown_beep():
        """Play procedural countdown beep sound."""
        try:
            from ursina.prefabs.ursfx import ursfx

            ursfx(
                [(0.0, 0.5), (0.1, 0.8), (0.2, 0.0)],
                volume=0.3,
                wave="square",
                pitch=random.uniform(8, 9),
                speed=2.0,
            )
        except Exception as e:
            # Silent fail if ursfx not available
            pass
