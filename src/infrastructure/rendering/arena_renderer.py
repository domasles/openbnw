"""Arena renderer for environment."""

from ursina import *


class ArenaRenderer:
    """
    Manages arena environment (ground, sky, lighting).
    Infrastructure layer - Ursina specific.
    """

    def __init__(self, arena_size: int):
        """
        Create arena environment.

        Args:
            arena_size: Size of the ground plane
        """
        # Ground
        self.ground = Entity(model="plane", collider="box", scale=arena_size, texture="grass", texture_scale=(4, 4))

        # Lighting
        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1, -1, -1))

        # Sky
        self.sky = Sky()
