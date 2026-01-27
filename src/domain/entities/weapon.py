"""Weapon entity - pure Python domain logic."""
import time


class Weapon:
    """
    Weapon with fire rate limiting.
    Pure Python - no engine dependencies.
    """
    
    def __init__(self, fire_rate: float, damage: int, weapon_range: float):
        """
        Initialize weapon.
        
        Args:
            fire_rate: Minimum seconds between shots
            damage: Damage per shot
            weapon_range: Maximum shooting range
        """
        self.fire_rate = fire_rate
        self.damage = damage
        self.weapon_range = weapon_range
        self._last_fire_time = 0.0
        
    def can_fire(self) -> bool:
        """
        Check if weapon can fire based on fire rate.
        
        Returns:
            True if enough time has passed since last shot
        """
        current_time = time.time()
        return (current_time - self._last_fire_time) >= self.fire_rate
    
    def fire(self) -> None:
        """Record that weapon was fired."""
        self._last_fire_time = time.time()
