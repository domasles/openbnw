"""Centralized game configuration constants."""

from ursina import color

class GameConfig:
    """All game constants in one place."""

    # Version
    VERSION = "1.0.0-beta"
    NAME = "OpenBNW"
    DEVELOPMENT = False  # Toggle development mode features

    # Player settings
    PLAYER_MAX_HEALTH = 100
    PLAYER_SPEED = 8
    PLAYER_MOUSE_SENSITIVITY = (90, 90)

    # Weapon settings
    WEAPON_FIRE_RATE = 0.15  # seconds between shots
    WEAPON_DAMAGE = 20
    WEAPON_RANGE = 100

    # Enemy settings
    BASE_ENEMY_SPEED = 5.0
    ENEMY_SPEED_INCREMENT = 0.5  # per wave
    ENEMY_MAX_HEALTH = 60
    ENEMY_DAMAGE = 20  # damage to player on contact
    ENEMY_ATTACK_COOLDOWN = 1.0  # seconds between attacks

    # Wave system
    BASE_ENEMY_COUNT = 5
    ENEMY_COUNT_INCREMENT = 3  # additional enemies per wave
    WAVE_START_DELAY = 2.0  # seconds before first wave
    WAVE_CLEAR_DELAY = 3.0  # seconds after wave cleared before next

    # Spawning
    SPAWN_DISTANCE_MIN = 15.0
    SPAWN_DISTANCE_MAX = 25.0

    # Arena
    ARENA_SIZE = 64
    ARENA_WALL_HEIGHT = 3

    # Visual settings
    ENEMY_COLOR = color.light_gray
    GUN_COLOR = color.red
    MUZZLE_FLASH_COLOR = color.yellow

    GROUND_TEXTURE = "grass"
    WALL_TEXTURE = "brick"
