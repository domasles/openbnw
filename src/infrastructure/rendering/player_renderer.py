"""Player entity renderer."""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
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
            model='cube',
            color=color.orange,
            origin_y=-.5,
            speed=GameConfig.PLAYER_SPEED,
            collider='box',
            position=(0, 0, 0),
            visible_self=True,
            jump_height=0
        )
        
        self.player_domain = player_domain
        self.collider = BoxCollider(self, Vec3(0, 1, 0), Vec3(1, 2, 1))
        
        # Gun attached to player
        self.gun = Entity(
            model='cube',
            parent=camera,
            position=(.5, -.25, .25),
            scale=(.3, .2, 1),
            origin_z=-.5,
            color=color.red
        )
        self.gun.muzzle_flash = Entity(
            parent=self.gun,
            z=1,
            world_scale=.5,
            model='quad',
            color=color.yellow,
            enabled=False
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
