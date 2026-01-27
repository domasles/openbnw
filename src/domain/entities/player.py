"""Player entity - pure Python domain logic."""

from typing import Optional


class Player:
    """
    Player entity with health and alive status.
    Pure Python - no engine dependencies.
    """

    def __init__(self, max_health: int = 100):
        self.max_health = max_health
        self._health = max_health
        self.kills = 0

    @property
    def health(self) -> int:
        """Current health."""
        return self._health

    @property
    def is_alive(self) -> bool:
        """Check if player is still alive."""
        return self._health > 0

    def take_damage(self, amount: int) -> None:
        """
        Reduce player health by damage amount.

        Args:
            amount: Damage to apply
        """
        if self.is_alive:
            self._health = max(0, self._health - amount)

    def heal(self, amount: int) -> None:
        """
        Restore player health.

        Args:
            amount: Health to restore
        """
        if self.is_alive:
            self._health = min(self.max_health, self._health + amount)

    def add_kill(self) -> None:
        """Increment kill counter."""
        self.kills += 1

    def reset(self) -> None:
        """Reset player to initial state."""
        self._health = self.max_health
        self.kills = 0
