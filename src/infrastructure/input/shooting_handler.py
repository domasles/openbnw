"""Shooting handler for player input."""
from ursina import *
from typing import Optional
from domain.entities import Enemy
from infrastructure.audio import SoundManager


class ShootingHandler:
    """
    Handles shooting input, raycasting, and visual feedback.
    Infrastructure layer - Ursina specific.
    """
    
    def __init__(self, gun: Entity, shootables_parent: Entity, weapon_range: float, weapon_damage: int):
        """
        Initialize shooting handler.
        
        Args:
            gun: Gun entity with muzzle flash
            shootables_parent: Parent entity for raycast targeting
            weapon_range: Maximum shooting distance
            weapon_damage: Damage per shot
        """
        self.gun = gun
        self.shootables_parent = shootables_parent
        self.weapon_range = weapon_range
        self.weapon_damage = weapon_damage
    
    def handle_shoot(self) -> Optional[Entity]:
        """
        Perform shooting action: visual effects + raycast.
        
        Returns:
            Hit entity if something was hit, None otherwise
        """
        # Muzzle flash
        self.gun.muzzle_flash.enabled = True
        invoke(self.gun.muzzle_flash.disable, delay=.05)
        
        # Sound
        SoundManager.play_gun_shot()
        
        # Raycast
        hit_info = raycast(
            origin=camera.world_position,
            direction=camera.forward,
            distance=self.weapon_range,
            traverse_target=self.shootables_parent
        )
        
        if hit_info.hit and hasattr(hit_info.entity, 'hp'):
            # Apply damage
            hit_info.entity.hp -= self.weapon_damage
            # Only blink if entity still exists (not destroyed)
            try:
                if hit_info.entity and hasattr(hit_info.entity, 'blink'):
                    hit_info.entity.blink(color.red)
            except:
                # Entity was destroyed, that's okay
                pass
            return hit_info.entity
        
        return None
