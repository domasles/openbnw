"""
OpenBNW - Hellbound Survival (Ursina Enhanced)
A Domain-Driven Design FPS game with clean architecture.
"""
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup imports
from config.game_config import GameConfig
from src.domain.entities import Player, Enemy, Weapon
from src.domain.wave_system import WaveManager
from src.application.services import GameService
from src.infrastructure.rendering import EnemyRenderer, HUDRenderer, ArenaRenderer
from src.infrastructure.input import ShootingHandler


class OpenBNWGame:
    """
    Main game class with clean DDD architecture.
    Thin orchestration layer coordinating infrastructure components.
    """
    
    def __init__(self, app: Ursina):
        self.app = app
        
        # Enable shadows
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
        
        # Infrastructure - State
        self.enemy_entities = {}
        self.game_over_shown = False
        
        # Infrastructure - Shootables for mouse targeting
        self.shootables_parent = Entity()
        mouse.traverse_target = self.shootables_parent
        
        # Infrastructure - Rendering
        self.arena_renderer = ArenaRenderer(GameConfig.ARENA_SIZE)
        self.hud_renderer = HUDRenderer()
        
        # Infrastructure - Player controller
        self.player = FirstPersonController(
            model='cube',
            color=color.orange,
            origin_y=-.5,
            speed=GameConfig.PLAYER_SPEED,
            collider='box',
            position=(0, 0, 0)
        )
        self.player.collider = BoxCollider(self.player, Vec3(0, 1, 0), Vec3(1, 2, 1))
        
        # Infrastructure - Gun
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
        
        # Infrastructure - Shooting handler
        self.shooting_handler = ShootingHandler(
            self.gun,
            self.shootables_parent,
            GameConfig.WEAPON_RANGE,
            GameConfig.WEAPON_DAMAGE
        )
        
        # Start game
        self.game_service.start_game()
    
    def _on_enemy_spawn(self, enemy: Enemy):
        """Callback when enemy spawns."""
        enemy_entity = EnemyRenderer(enemy, self.player, self.game_service, self.shootables_parent)
        self.enemy_entities[id(enemy)] = enemy_entity
    
    def _on_enemy_death(self, enemy: Enemy):
        """Callback when enemy dies."""
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            destroy(self.enemy_entities[enemy_id])
            del self.enemy_entities[enemy_id]
    
    def _on_wave_start(self, wave_number: int):
        """Callback when wave starts."""
        self.hud_renderer.update_wave(wave_number)
    
    def _on_player_death(self):
        """Callback when player dies."""
        if not self.game_over_shown:
            self.game_over_shown = True
            self.hud_renderer.show_game_over(
                self.wave_manager.current_wave,
                self.player_domain.kills
            )
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
        self.hud_renderer.hide_game_over()
        self.gun.enabled = True
        mouse.locked = True
        
        # Restart game service
        self.game_service.start_game()
    
    def input(self, key):
        """Handle input."""
        if key == 'r' and self.game_over_shown:
            self._restart_game()
    
    def update(self):
        """Update game state - thin orchestration."""
        # Shooting
        if held_keys['left mouse'] and not self.game_over_shown:
            if self.game_service.handle_shoot_attempt():
                self.shooting_handler.handle_shoot()
        
        # Update game service
        self.game_service.update(time.dt)
        
        # Update HUD
        alive_enemies = len(self.game_service.get_alive_enemies())
        self.hud_renderer.update_enemies(alive_enemies)
        self.hud_renderer.update_health(self.player_domain.health)
        self.hud_renderer.update_kills(self.player_domain.kills)


if __name__ == '__main__':
    app = Ursina()
    game = OpenBNWGame(app)
    
    # Register update function globally for Ursina
    def update():
        game.update()
    
    app.run()
