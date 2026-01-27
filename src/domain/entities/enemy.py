"""Enemy entity - pure Python domain logic."""
import random
import math
from typing import Tuple


class Enemy:
    """
    Enemy entity with position, health, and movement.
    Pure Python - no engine dependencies.
    """
    
    def __init__(self, position: Tuple[float, float, float], speed: float, max_health: int = 100):
        self.position = position
        self.speed = speed
        self.max_health = max_health
        self._health = max_health
        self.last_attack_time = 0.0
        
    @property
    def health(self) -> int:
        """Current health."""
        return self._health
    
    @property
    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self._health > 0
    
    def take_damage(self, amount: int) -> None:
        """
        Reduce enemy health by damage amount.
        
        Args:
            amount: Damage to apply
        """
        if self.is_alive:
            self._health = max(0, self._health - amount)
    
    def can_attack(self, current_time: float, attack_cooldown: float) -> bool:
        """
        Check if enemy can attack based on cooldown.
        
        Args:
            current_time: Current game time
            attack_cooldown: Seconds between attacks
            
        Returns:
            True if can attack
        """
        return (current_time - self.last_attack_time) >= attack_cooldown
    
    def perform_attack(self, current_time: float) -> None:
        """Record attack time."""
        self.last_attack_time = current_time
    
    @staticmethod
    def generate_spawn_position(min_distance: float, max_distance: float) -> Tuple[float, float, float]:
        """
        Generate random spawn position around origin.
        
        Args:
            min_distance: Minimum distance from origin
            max_distance: Maximum distance from origin
            
        Returns:
            (x, y, z) position tuple
        """
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(min_distance, max_distance)
        
        x = math.cos(angle) * distance
        z = math.sin(angle) * distance
        y = 0
        
        return (x, y, z)
