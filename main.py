"""
OpenBNW - Hellbound Survival (Ursina Enhanced)
A Domain-Driven Design FPS game inspired by test.py
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import sys
import time as time_module

# Add src to path
sys.path.insert(0, 'src')

from config.game_config import GameConfig
from src.domain.entities import Player, Enemy, Weapon
from src.domain.wave_system import WaveManager
from src.application.services import GameService


class EnemyEntity(Entity):
    """
    Ursina enemy entity with health bar and AI from test.py.
    Bridges domain Enemy with Ursina rendering.
    """
    
    def __init__(self, enemy_domain: Enemy, player_entity: Entity, game_service: GameService, shootables_parent: Entity, **kwargs):
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
        
        # Health bar inspired by test.py
        self.health_bar = Entity(
            parent=self,
            y=1.2,
            model='cube',
            color=color.red,
            world_scale=(1.5, .1, .1)
        )
        
        # Track last attack time
        self.last_attack_time = 0
    
    @property
    def hp(self):
        """Property for compatibility with test.py shooting style."""
        return self.enemy_domain.health
    
    @hp.setter
    def hp(self, value):
        """Setter for compatibility with test.py shooting style."""
        damage = self.enemy_domain.health - value
        if damage > 0:
            self.enemy_domain.take_damage(int(damage))
            self.take_damage()
            if not self.enemy_domain.is_alive:
                self.game_service.handle_enemy_hit(self.enemy_domain)
        
    def update(self):
        """AI behavior from test.py - chase player, attack on contact."""
        if not self.enemy_domain.is_alive:
            return
        
        # Distance check from test.py
        dist = distance_xz(self.player_entity.position, self.position)
        
        # Fade health bar when not recently damaged
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        
        # Look at player
        self.look_at_2d(self.player_entity.position, 'y')
        
        # Check line of sight (raycast from test.py)
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
                # Close enough to attack
                current_time = time_module.time()
                if self.enemy_domain.can_attack(current_time, GameConfig.ENEMY_ATTACK_COOLDOWN):
                    self.enemy_domain.perform_attack(current_time)
                    self.game_service.handle_player_hit(GameConfig.ENEMY_DAMAGE)
                    # Visual feedback
                    self.player_entity.blink(color.red)
    
    def take_damage(self):
        """Visual feedback when hit."""
        # Update health bar
        health_percent = self.enemy_domain.health / self.enemy_domain.max_health
        self.health_bar.world_scale_x = health_percent * 1.5
        self.health_bar.alpha = 1
        
        # Blink red
        self.blink(color.red)


class OpenBNWGame:
    """
    Main game class with DDD architecture.
    Infrastructure layer integrating domain/application with Ursina.
    """
    
    def __init__(self, app: Ursina):
        self.app = app
        
        # Enable shadows from test.py
        Entity.default_shader = lit_with_shadows_shader
        
        # Domain layer
        self.player_domain = Player(GameConfig.PLAYER_MAX_HEALTH)
        self.weapon_domain = Weapon(
            GameConfig.WEAPON_FIRE_RATE,
            GameConfig.WEAPON_DAMAGE,
            GameConfig.WEAPON_RANGE
        )
        self.wave_manager = WaveManager(
            GameConfig.BASE_ENEMY_COUNT,
            GameConfig.ENEMY_COUNT_INCREMENT,
            GameConfig.BASE_ENEMY_SPEED,
            GameConfig.ENEMY_SPEED_INCREMENT,
            GameConfig.ENEMY_MAX_HEALTH,
            GameConfig.SPAWN_DISTANCE_MIN,
            GameConfig.SPAWN_DISTANCE_MAX
        )
        
        # Application layer
        self.game_service = GameService(
            self.player_domain,
            self.weapon_domain,
            self.wave_manager,
            GameConfig.WAVE_CLEAR_DELAY
        )
        
        # Setup callbacks
        self.game_service.on_enemy_spawn = self._on_enemy_spawn
        self.game_service.on_enemy_death = self._on_enemy_death
        self.game_service.on_wave_start = self._on_wave_start
        self.game_service.on_player_death = self._on_player_death
        
        # Infrastructure - Ursina entities
        self.enemy_entities = {}  # Map domain Enemy to EnemyEntity
        self.game_over_shown = False
        
        # Shootables parent for mouse targeting (from test.py)
        self.shootables_parent = Entity()
        mouse.traverse_target = self.shootables_parent
        
        # Create arena
        self._create_arena()
        
        # Player controller from test.py
        self.player = FirstPersonController(
            model='cube',
            color=color.orange,
            origin_y=-.5,
            speed=GameConfig.PLAYER_SPEED,
            collider='box',
            position=(0, 0, 0)
        )
        self.player.collider = BoxCollider(self.player, Vec3(0, 1, 0), Vec3(1, 2, 1))
        
        # Gun from test.py
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
        
        # Lighting from test.py
        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1, -1, -1))
        Sky()
        
        # HUD
        self._create_hud()
        
        # Start game
        self.game_service.start_game()
    
    def _create_arena(self):
        """Create arena with ground from test.py."""
        # Ground
        Entity(
            model='plane',
            collider='box',
            scale=GameConfig.ARENA_SIZE,
            texture='grass',
            texture_scale=(4, 4)
        )
    
    def _create_hud(self):
        """Create HUD elements."""
        self.wave_text = Text(
            text='Wave: 0',
            position=(-0.85, 0.45),
            origin=(0, 0),
            scale=2
        )
        
        self.enemy_text = Text(
            text='Enemies: 0',
            position=(-0.85, 0.40),
            origin=(0, 0),
            scale=2
        )
        
        self.health_text = Text(
            text='Health: 100',
            position=(-0.85, 0.35),
            origin=(0, 0),
            scale=2
        )
        
        self.kills_text = Text(
            text='Kills: 0',
            position=(-0.85, 0.30),
            origin=(0, 0),
            scale=2
        )
        
        self.game_over_text = Text(
            text='',
            position=(0, 0),
            origin=(0, 0),
            scale=3,
            color=color.red,
            enabled=False
        )
    
    def _on_enemy_spawn(self, enemy: Enemy):
        """Callback when enemy spawns - create visual entity."""
        enemy_entity = EnemyEntity(enemy, self.player, self.game_service, self.shootables_parent)
        self.enemy_entities[id(enemy)] = enemy_entity
    
    def _on_enemy_death(self, enemy: Enemy):
        """Callback when enemy dies - destroy visual entity."""
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            destroy(self.enemy_entities[enemy_id])
            del self.enemy_entities[enemy_id]
    
    def _on_wave_start(self, wave_number: int):
        """Callback when wave starts."""
        self.wave_text.text = f'Wave: {wave_number}'
    
    def _on_player_death(self):
        """Callback when player dies."""
        if not self.game_over_shown:
            self.game_over_shown = True
            self.game_over_text.text = f'GAME OVER\nWave: {self.wave_manager.current_wave}\nKills: {self.player_domain.kills}\n\nPress R to restart or ESC to quit'
            self.game_over_text.enabled = True
            mouse.locked = False
            self.gun.enabled = False
    
    def _restart_game(self):
        """Restart the game."""
        # Destroy all enemies
        for enemy_entity in list(self.enemy_entities.values()):
            destroy(enemy_entity)
        self.enemy_entities.clear()
        
        # Reset player position
        self.player.position = (0, 0, 0)
        
        # Reset game state
        self.game_over_shown = False
        self.game_over_text.enabled = False
        self.gun.enabled = True
        mouse.locked = True
        
        # Restart game service
        self.game_service.start_game()
    
    def input(self, key):
        """Handle input from test.py style."""
        # Restart
        if key == 'r' and self.game_over_shown:
            self._restart_game()
    
    def update(self):
        """Update game state."""
        # Shooting with held mouse
        if held_keys['left mouse'] and not self.game_over_shown:
            if self.game_service.handle_shoot_attempt():
                # Muzzle flash
                self.gun.muzzle_flash.enabled = True
                
                # Sound effect
                try:
                    from ursina.prefabs.ursfx import ursfx
                    ursfx(
                        [(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
                        volume=0.5,
                        wave='noise',
                        pitch=random.uniform(-13, -12),
                        pitch_change=-12,
                        speed=3.0
                    )
                except:
                    pass
                
                invoke(self.gun.muzzle_flash.disable, delay=.05)
                
                # Try raycast first
                hit_info = raycast(
                    origin=camera.world_position,
                    direction=camera.forward,
                    distance=GameConfig.WEAPON_RANGE,
                    traverse_target=self.shootables_parent
                )
                
                if hit_info.hit and hasattr(hit_info.entity, 'hp'):
                    hit_info.entity.hp -= GameConfig.WEAPON_DAMAGE
                    hit_info.entity.blink(color.red)
        
        # Update game service
        self.game_service.update(time.dt)
        
        # Update HUD
        alive_enemies = len(self.game_service.get_alive_enemies())
        self.enemy_text.text = f'Enemies: {alive_enemies}'
        self.health_text.text = f'Health: {self.player_domain.health}'
        self.kills_text.text = f'Kills: {self.player_domain.kills}'


if __name__ == '__main__':
    app = Ursina()
    game = OpenBNWGame(app)
    
    # Register update function globally like test.py
    def update():
        game.update()
    
    app.run()
