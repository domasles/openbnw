"""OpenBNW"""

from ursina import *
from ursina.shaders import lit_with_shadows_shader
import sys
import os

# Setup Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Domain layer
from config.game_config import GameConfig
from src.domain.entities import Player, Weapon
from src.domain.wave_system import WaveManager

# Application layer
from src.application.services import GameService
from src.application.input import InputHandler

# Infrastructure layer
from src.infrastructure.rendering import PlayerRenderer, HUDRenderer, ArenaRenderer
from src.infrastructure.spawning import EnemySpawner
from src.infrastructure.input import ShootingHandler, KeyboardMapper


class OpenBNWGame:
    """Main game orchestrator - pure component wiring."""

    def __init__(self):
        # Enable shadows
        Entity.default_shader = lit_with_shadows_shader

        # Domain layer - pure Python game logic
        player_domain = Player(GameConfig.PLAYER_MAX_HEALTH)
        weapon_domain = Weapon(GameConfig.WEAPON_FIRE_RATE, GameConfig.WEAPON_DAMAGE, GameConfig.WEAPON_RANGE)
        wave_manager = WaveManager(
            GameConfig.BASE_ENEMY_COUNT,
            GameConfig.ENEMY_COUNT_INCREMENT,
            GameConfig.BASE_ENEMY_SPEED,
            GameConfig.ENEMY_SPEED_INCREMENT,
            GameConfig.ENEMY_MAX_HEALTH,
            GameConfig.SPAWN_DISTANCE_MIN,
            GameConfig.SPAWN_DISTANCE_MAX,
        )

        # Application layer - service orchestration
        self.game_service = GameService(player_domain, weapon_domain, wave_manager, GameConfig.WAVE_CLEAR_DELAY)
        # Game state
        self.game_over_shown = False
        # Infrastructure - rendering
        self.arena = ArenaRenderer(GameConfig.ARENA_SIZE)
        self.player_renderer = PlayerRenderer(player_domain)
        self.hud = HUDRenderer(self.game_service)

        # Infrastructure - enemy spawning
        shootables_parent = Entity()
        mouse.traverse_target = shootables_parent
        self.enemy_spawner = EnemySpawner(shootables_parent, self.player_renderer, self.game_service)

        # Infrastructure - input
        self.input_handler = InputHandler(self.game_service)
        self.input_handler.on_quit_requested = application.quit

        shooting_handler = ShootingHandler(
            self.player_renderer.gun, shootables_parent, GameConfig.WEAPON_RANGE, GameConfig.WEAPON_DAMAGE
        )
        self.keyboard_mapper = KeyboardMapper(self.input_handler, shooting_handler)

        # Wire game service callbacks to infrastructure
        self.game_service.on_enemy_spawn = self.enemy_spawner.spawn_enemy
        self.game_service.on_enemy_death = self.enemy_spawner.despawn_enemy
        self.game_service.on_player_death = self._on_player_death

        # Start
        self.game_service.start_game()

    def _on_player_death(self):
        """Handle player death."""
        if not self.game_over_shown:
            self.game_over_shown = True
            self.input_handler.set_game_over(True)
            self.hud.show_game_over(self.game_service.wave_manager.current_wave, self.game_service.player.kills)
            mouse.locked = False
            self.player_renderer.disable()
            self.player_renderer.gun.enabled = False

    def _on_restart(self):
        """Handle game restart."""
        # Destroy all enemies
        self.enemy_spawner.despawn_all()

        # Reset player
        self.player_renderer.position = (0, 0, 0)
        self.player_renderer.enable()

        # Reset game state
        self.game_over_shown = False
        self.input_handler.set_game_over(False)  # Reset input handler state too
        self.hud.hide_game_over()
        self.player_renderer.gun.enabled = True
        mouse.locked = True

        # Restart game service
        self.game_service.start_game()

    def input(self, key):
        """Route input to keyboard mapper."""
        if self.game_over_shown:
            if key == "r":
                self._on_restart()
            elif key == "escape":
                application.quit()
        else:
            self.keyboard_mapper.handle_key(key)

    def update(self):
        """Update game state."""
        if not self.game_over_shown:
            self.keyboard_mapper.update()  # Handle held keys only during game
        self.game_service.update(time.dt)
        self.hud.update()  # Auto-poll game state


# Entry point
if __name__ == "__main__":
    app = Ursina()
    game = OpenBNWGame()

    # Register global functions for Ursina
    def update():
        game.update()

    def input(key):
        game.input(key)

    app.run()
