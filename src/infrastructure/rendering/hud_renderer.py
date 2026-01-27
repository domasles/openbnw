"""HUD renderer for UI display."""
from ursina import *


class HUDRenderer:
    """
    Manages HUD text elements.
    Infrastructure layer - Ursina specific.
    """
    
    def __init__(self):
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
    
    def update_wave(self, wave_number: int):
        """Update wave display."""
        self.wave_text.text = f'Wave: {wave_number}'
    
    def update_enemies(self, enemy_count: int):
        """Update enemy count display."""
        self.enemy_text.text = f'Enemies: {enemy_count}'
    
    def update_health(self, health: int):
        """Update health display."""
        self.health_text.text = f'Health: {health}'
    
    def update_kills(self, kills: int):
        """Update kills display."""
        self.kills_text.text = f'Kills: {kills}'
    
    def show_game_over(self, wave: int, kills: int):
        """Show game over screen."""
        self.game_over_text.text = f'GAME OVER\nWave: {wave}\nKills: {kills}\n\nPress R to restart or ESC to quit'
        self.game_over_text.enabled = True
    
    def hide_game_over(self):
        """Hide game over screen."""
        self.game_over_text.enabled = False
