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
    def generate_spawn_position(
        arena_size: float,
        margin: float = 2.0,
        player_pos: Tuple[float, float, float] = (0, 0, 0),
        min_player_distance: float = 8.0,
    ) -> Tuple[float, float, float]:
        """
        Generate random spawn position inside arena bounds, away from player.

        Args:
            arena_size: Size of the arena (square)
            margin: Distance to stay away from walls
            player_pos: Player position (x, y, z)
            min_player_distance: Minimum distance from player

        Returns:
            (x, y, z) position tuple
        """
        half_size = arena_size / 2 - margin
        max_attempts = 10

        for attempt in range(max_attempts):
            # Generate random position within arena bounds
            x = random.uniform(-half_size, half_size)
            z = random.uniform(-half_size, half_size)
            y = 0

            # Check distance from player
            dx = x - player_pos[0]
            dz = z - player_pos[2]
            distance_to_player = math.sqrt(dx * dx + dz * dz)

            if distance_to_player >= min_player_distance:
                return (x, y, z)

        # If all attempts failed, return last position (better than nothing)
        return (x, y, z)
