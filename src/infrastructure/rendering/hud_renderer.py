"""HUD renderer for UI display."""
from ursina import *


class HUDRenderer:
    """
    Manages HUD text elements with auto-update from game state.
    Infrastructure layer - Ursina specific.
    """
    
    def __init__(self, game_service):
        """
        Create HUD elements.
        
        Args:
            game_service: GameService to poll for state
        """
        self.game_service = game_service
        
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
    
    def update(self):
        """Auto-update HUD from game service state."""
        # Update stats
        self.wave_text.text = f'Wave: {self.game_service.wave_manager.current_wave}'
        alive_enemies = len(self.game_service.get_alive_enemies())
        self.enemy_text.text = f'Enemies: {alive_enemies}'
        self.health_text.text = f'Health: {self.game_service.player.health}'
        self.kills_text.text = f'Kills: {self.game_service.player.kills}'
    
    def show_game_over(self, wave: int, kills: int):
        """Show game over screen."""
        self.game_over_text.text = f'GAME OVER\nWave: {wave}\nKills: {kills}\n\nPress R to restart or ESC to quit'
        self.game_over_text.enabled = True
    
    def hide_game_over(self):
        """Hide game over screen."""
        self.game_over_text.enabled = False
