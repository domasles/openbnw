"""Arena renderer for environment."""

from ursina import *
from config.game_config import GameConfig


class ArenaRenderer:
    """
    Manages arena environment (ground, sky, lighting, walls).
    Infrastructure layer - Ursina specific.
    """

    def __init__(self, arena_size: int):
        """
        Create arena environment.

        Args:
            arena_size: Size of the ground plane
        """
        # Ground
        self.ground = Entity(
            model="plane",
            collider="box",
            scale=arena_size,
            texture=GameConfig.GROUND_TEXTURE,
            texture_scale=(sqrt(GameConfig.ARENA_SIZE), sqrt(GameConfig.ARENA_SIZE)),
        )

        # Walls - create perimeter
        wall_height = GameConfig.ARENA_WALL_HEIGHT
        wall_thickness = 1
        half_size = arena_size / 2

        # North wall
        self.north_wall = Entity(
            model="cube",
            scale=(arena_size, wall_height, wall_thickness),
            position=(0, wall_height / 2, half_size),
            collider="box",
            texture=GameConfig.WALL_TEXTURE,
            texture_scale=(GameConfig.ARENA_SIZE / 2, 1),
            color=color.gray,
        )

        # South wall
        self.south_wall = Entity(
            model="cube",
            scale=(arena_size, wall_height, wall_thickness),
            position=(0, wall_height / 2, -half_size),
            collider="box",
            texture=GameConfig.WALL_TEXTURE,
            texture_scale=(GameConfig.ARENA_SIZE / 2, 1),
            color=color.gray,
        )

        # East wall
        self.east_wall = Entity(
            model="cube",
            scale=(wall_thickness, wall_height, arena_size),
            position=(half_size, wall_height / 2, 0),
            collider="box",
            texture=GameConfig.WALL_TEXTURE,
            texture_scale=(GameConfig.ARENA_SIZE / 2, 1),
            color=color.gray,
        )

        # West wall
        self.west_wall = Entity(
            model="cube",
            scale=(wall_thickness, wall_height, arena_size),
            position=(-half_size, wall_height / 2, 0),
            collider="box",
            texture=GameConfig.WALL_TEXTURE,
            texture_scale=(GameConfig.ARENA_SIZE / 2, 1),
            color=color.gray,
        )

        # Lighting
        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1, -1, -1))

        # Sky
        self.sky = Sky()
