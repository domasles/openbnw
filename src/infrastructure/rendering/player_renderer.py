"""Player entity renderer."""

from ursina import *
from domain.components.first_person_controller import FirstPersonController
from domain.entities import Player
from config.game_config import GameConfig


class PlayerRenderer(FirstPersonController):
    """
    Ursina player controller with visible model.
    Bridges domain Player with Ursina first-person controls.
    Infrastructure layer - Ursina specific.
    """

    def __init__(self, player_domain: Player):
        """
        Initialize player renderer.

        Args:
            player_domain: Domain Player instance
        """
        super().__init__(
            origin_y=-0.5,
            speed=GameConfig.PLAYER_SPEED,
            position=(0, 0, 0),
            jump_height=GameConfig.PLAYER_JUMP_HEIGHT,
            collider="sphere",
            mouse_sensitivity=GameConfig.PLAYER_MOUSE_SENSITIVITY,
        )

        self.player_domain = player_domain

        # Gun attached to player
        self.gun = Entity(
            model="cube",
            parent=camera,
            position=(0.5, -0.25, 0.25),
            scale=(0.3, 0.2, 1),
            origin_z=-0.5,
            color=GameConfig.GUN_COLOR,
        )
        self.gun.muzzle_flash = Entity(
            parent=self.gun, z=1, world_scale=0.5, model="quad", color=GameConfig.MUZZLE_FLASH_COLOR, enabled=False
        )

    def take_damage(self, amount: int):
        """
        Apply damage to domain player.

        Args:
            amount: Damage to apply
        """
        self.player_domain.take_damage(amount)
        # Visual feedback
        self.blink(color.red)

    def reset_position(self):
        """Reset player to spawn position."""
        self.position = (0, 0, 0)

    def destroy(self):
        """Properly clean up all child entities before destroying."""
        # Explicitly destroy gun and its children
        if hasattr(self, "gun") and self.gun:
            if hasattr(self.gun, "muzzle_flash") and self.gun.muzzle_flash:
                destroy(self.gun.muzzle_flash)
                self.gun.muzzle_flash = None
            destroy(self.gun)
            self.gun = None

        # Then destroy self using Ursina's destroy
        destroy(self, delay=0)
