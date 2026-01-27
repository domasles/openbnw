"""
Centralized game configuration constants.
"""


class GameConfig:
    """All game constants in one place."""
    
    # Version
    VERSION = "3.0.0-ursina-enhanced"
    
    # Player settings
    PLAYER_MAX_HEALTH = 100
    PLAYER_SPEED = 8
    PLAYER_MOUSE_SENSITIVITY = (40, 40)
    
    # Weapon settings
    WEAPON_FIRE_RATE = 0.15  # seconds between shots
    WEAPON_DAMAGE = 10
    WEAPON_RANGE = 100
    
    # Enemy settings
    BASE_ENEMY_SPEED = 5.0
    ENEMY_SPEED_INCREMENT = 0.5  # per wave
    ENEMY_MAX_HEALTH = 100
    ENEMY_DAMAGE = 20  # damage to player on contact
    ENEMY_ATTACK_COOLDOWN = 1.0  # seconds between attacks
    ENEMY_DETECTION_RANGE = 40  # range to detect player
    ENEMY_STOP_DISTANCE = 2  # stop chasing at this distance
    
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
    PLAYER_COLOR = "orange"
    ENEMY_COLOR = "light_gray"
    GROUND_TEXTURE = "grass"
    WALL_TEXTURE = "brick"
    GUN_COLOR = "red"
    MUZZLE_FLASH_COLOR = "yellow"
