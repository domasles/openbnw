"""Enemy entity renderer."""
from ursina import *
import time as time_module
from domain.entities import Enemy
from config.game_config import GameConfig


class EnemyRenderer(Entity):
    """
    Ursina enemy entity with visual feedback and AI.
    Bridges domain Enemy with Ursina rendering.
    Infrastructure layer - Ursina specific.
    """
    
    def __init__(self, enemy_domain: Enemy, player_entity: Entity, game_service, shootables_parent: Entity, **kwargs):
        x, y, z = enemy_domain.position
        
        super().__init__(
            parent=shootables_parent,
            model='cube',
            scale_y=2,
            origin_y=-.5,
            color=color.light_gray,
            collider='box',
            position=(x, y, z),
            **kwargs
        )
        
        self.enemy_domain = enemy_domain
        self.player_entity = player_entity
        self.game_service = game_service
        
        # Health bar
        self.health_bar = Entity(
            parent=self,
            y=1.2,
            model='cube',
            color=color.red,
            world_scale=(1.5, .1, .1)
        )
        
        self.last_attack_time = 0
    
    @property
    def hp(self):
        """Property for shooting compatibility."""
        return self.enemy_domain.health
    
    @hp.setter
    def hp(self, value):
        """Setter for shooting compatibility."""
        damage = self.enemy_domain.health - value
        if damage > 0:
            self.enemy_domain.take_damage(int(damage))
            self.take_damage()
            if not self.enemy_domain.is_alive:
                # Enemy died - add kill and trigger death callback directly
                self.game_service.player.add_kill()
                if self.game_service.on_enemy_death:
                    self.game_service.on_enemy_death(self.enemy_domain)
    
    def update(self):
        """AI behavior: chase player, attack on contact."""
        if not self.enemy_domain.is_alive:
            return
        
        # Distance check
        dist = distance_xz(self.player_entity.position, self.position)
        
        # Fade health bar
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        
        # Look at player
        self.look_at_2d(self.player_entity.position, 'y')
        
        # Check line of sight
        hit_info = raycast(
            self.world_position + Vec3(0, 1, 0),
            self.forward,
            distance=GameConfig.ENEMY_DETECTION_RANGE,
            ignore=(self,)
        )
        
        # If player in sight, chase
        if hit_info.entity == self.player_entity:
            if dist > GameConfig.ENEMY_STOP_DISTANCE:
                # Move toward player
                self.position += self.forward * time.dt * self.enemy_domain.speed
            else:
                # Attack
                current_time = time_module.time()
                if self.enemy_domain.can_attack(current_time, GameConfig.ENEMY_ATTACK_COOLDOWN):
                    self.enemy_domain.perform_attack(current_time)
                    self.game_service.handle_player_hit(GameConfig.ENEMY_DAMAGE)
                    self.player_entity.blink(color.red)
    
    def take_damage(self):
        """Visual feedback when hit."""
        # Update health bar
        health_percent = self.enemy_domain.health / self.enemy_domain.max_health
        self.health_bar.world_scale_x = health_percent * 1.5
        self.health_bar.alpha = 1
        
        # Blink red
        self.blink(color.red)
