"""Wave management system - pure Python domain logic."""
from typing import List, Tuple
from ..entities.enemy import Enemy


class WaveManager:
    """
    Manages wave progression and enemy spawning.
    Pure Python - no engine dependencies.
    """
    
    def __init__(
        self,
        base_enemy_count: int,
        enemy_count_increment: int,
        base_enemy_speed: float,
        enemy_speed_increment: float,
        enemy_max_health: int,
        spawn_distance_min: float,
        spawn_distance_max: float
    ):
        """
        Initialize wave manager.
        
        Args:
            base_enemy_count: Starting number of enemies
            enemy_count_increment: Additional enemies per wave
            base_enemy_speed: Starting enemy speed
            enemy_speed_increment: Speed increase per wave
            enemy_max_health: Enemy health
            spawn_distance_min: Minimum spawn distance
            spawn_distance_max: Maximum spawn distance
        """
        self.base_enemy_count = base_enemy_count
        self.enemy_count_increment = enemy_count_increment
        self.base_enemy_speed = base_enemy_speed
        self.enemy_speed_increment = enemy_speed_increment
        self.enemy_max_health = enemy_max_health
        self.spawn_distance_min = spawn_distance_min
        self.spawn_distance_max = spawn_distance_max
        
        self.current_wave = 0
        self.enemies_spawned_this_wave = 0
        
    def calculate_enemy_count_for_wave(self, wave_number: int) -> int:
        """
        Calculate how many enemies should spawn in a wave.
        
        Args:
            wave_number: The wave number (1-based)
            
        Returns:
            Number of enemies
        """
        return self.base_enemy_count + (wave_number - 1) * self.enemy_count_increment
    
    def calculate_enemy_speed_for_wave(self, wave_number: int) -> float:
        """
        Calculate enemy speed for a wave.
        
        Args:
            wave_number: The wave number (1-based)
            
        Returns:
            Enemy speed
        """
        return self.base_enemy_speed + (wave_number - 1) * self.enemy_speed_increment
    
    def spawn_wave(self, wave_number: int) -> List[Enemy]:
        """
        Generate enemies for a wave.
        
        Args:
            wave_number: The wave number (1-based)
            
        Returns:
            List of Enemy instances
        """
        enemy_count = self.calculate_enemy_count_for_wave(wave_number)
        enemy_speed = self.calculate_enemy_speed_for_wave(wave_number)
        
        enemies = []
        for _ in range(enemy_count):
            position = Enemy.generate_spawn_position(
                self.spawn_distance_min,
                self.spawn_distance_max
            )
            enemy = Enemy(position, enemy_speed, self.enemy_max_health)
            enemies.append(enemy)
        
        self.enemies_spawned_this_wave = enemy_count
        return enemies
    
    def advance_to_next_wave(self) -> int:
        """
        Move to the next wave.
        
        Returns:
            New wave number
        """
        self.current_wave += 1
        return self.current_wave
