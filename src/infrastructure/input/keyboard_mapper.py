"""Keyboard input mapping for Ursina."""
from ursina import *


class KeyboardMapper:
    """
    Maps keyboard input to application layer commands.
    Infrastructure layer - Ursina specific.
    """
    
    def __init__(self, input_handler, shooting_handler):
        """
        Initialize keyboard mapper.
        
        Args:
            input_handler: Application layer InputHandler
            shooting_handler: Infrastructure ShootingHandler
        """
        self.input_handler = input_handler
        self.shooting_handler = shooting_handler
    
    def handle_key(self, key):
        """
        Route keyboard input to appropriate handlers.
        
        Args:
            key: Key string from Ursina
        """
        if key == 'r':
            self.input_handler.handle_restart()
        elif key == 'escape':
            self.input_handler.handle_quit()
    
    def update(self):
        """Update held keys (shooting)."""
        if held_keys['left mouse'] and not self.input_handler.game_over:
            if self.input_handler.handle_shoot():
                self.shooting_handler.handle_shoot()
