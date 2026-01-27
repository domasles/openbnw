"""Input handling at application layer."""
from typing import Callable, Optional


class InputHandler:
    """
    Handles game input commands.
    Application layer - engine agnostic.
    """
    
    def __init__(self, game_service):
        """
        Initialize input handler.
        
        Args:
            game_service: GameService instance to control
        """
        self.game_service = game_service
        self.game_over = False
        
        # Callbacks for infrastructure
        self.on_quit_requested: Optional[Callable[[], None]] = None
    
    def handle_shoot(self) -> bool:
        """
        Handle shoot input.
        
        Returns:
            True if shot was fired
        """
        if self.game_over:
            return False
        return self.game_service.handle_shoot_attempt()
    
    def handle_restart(self):
        """Handle restart input."""
        if self.game_over:
            self.game_service.start_game()
            self.game_over = False
    
    def handle_quit(self):
        """Handle quit input."""
        if self.on_quit_requested:
            self.on_quit_requested()
    
    def set_game_over(self, is_over: bool):
        """Set game over state."""
        self.game_over = is_over
