"""Game service - orchestrates game logic."""

import time
from typing import List, Optional, Callable
from domain.entities import Player, Enemy, Weapon
from domain.wave_system import WaveManager


class GameService:
    """
    Orchestrates game state and domain logic.
    Engine-agnostic application layer.
    """

    def __init__(
        self,
        player: Player,
        weapon: Weapon,
        wave_manager: WaveManager,
        wave_clear_delay: float = 3.0,
        wave_start_delay: float = 2.0,
    ):
        """
        Initialize game service.

        Args:
            player: Player entity
            weapon: Weapon entity
            wave_manager: Wave management system
            wave_clear_delay: Seconds to wait after wave cleared
            wave_start_delay: Seconds to wait before first wave
        """
        self.player = player
        self.weapon = weapon
        self.wave_manager = wave_manager
        self.wave_clear_delay = wave_clear_delay
        self.wave_start_delay = wave_start_delay

        self.enemies: List[Enemy] = []
        self.game_started = False
        self.wave_in_progress = False
        self.wave_clear_time: Optional[float] = None
        self.first_wave_start_time: Optional[float] = None
        self.last_countdown_beep: Optional[float] = None  # Track last beep time
        self.player_renderer = None  # Will be set by infrastructure

        # Callbacks for infrastructure layer
        self.on_enemy_spawn: Optional[Callable[[Enemy], None]] = None
        self.on_enemy_death: Optional[Callable[[Enemy], None]] = None
        self.on_enemy_damaged: Optional[Callable[[Enemy], None]] = None
        self.on_wave_start: Optional[Callable[[int], None]] = None
        self.on_player_death: Optional[Callable[[], None]] = None
        self.on_countdown_beep: Optional[Callable[[], None]] = None
        self.on_restart_requested: Optional[Callable[[], None]] = None

    def start_game(self) -> None:
        """Initialize and start the game."""
        self.game_started = True
        self.player.reset()
        self.enemies.clear()
        self.wave_manager.current_wave = 0
        self.first_wave_start_time = time.time()

    def _start_next_wave(self) -> None:
        """Start the next wave."""
        # Safety cleanup: remove any dead enemies before starting new wave
        self.enemies = [e for e in self.enemies if e.is_alive]

        wave_number = self.wave_manager.advance_to_next_wave()
        # Get player position from player_renderer (infrastructure reference)
        player_pos = (0, 0, 0)
        if self.player_renderer is not None:
            player_pos = (self.player_renderer.x, self.player_renderer.y, self.player_renderer.z)
        new_enemies = self.wave_manager.spawn_wave(wave_number, player_pos)
        self.enemies.extend(new_enemies)
        self.wave_in_progress = True
        self.wave_clear_time = None

        # Notify infrastructure to create visual enemies
        if self.on_wave_start:
            self.on_wave_start(wave_number)

        if self.on_enemy_spawn:
            for enemy in new_enemies:
                self.on_enemy_spawn(enemy)

    def update(self, delta_time: float) -> None:
        """
        Update game state.

        Args:
            delta_time: Time since last update
        """
        if not self.game_started or not self.player.is_alive:
            return

        # Check if first wave should start
        if self.first_wave_start_time is not None:
            elapsed = time.time() - self.first_wave_start_time
            time_remaining = self.wave_start_delay - elapsed

            # Play countdown beeps every second in the LAST 2 seconds
            if self.on_countdown_beep and time_remaining <= 2.0 and time_remaining > 0:
                beep_interval = 1.0
                # Calculate which beep we're on (0 or 1 for 2-second countdown)
                current_beep = int((2.0 - time_remaining) / beep_interval)
                last_beep = (
                    int((self.last_countdown_beep or -1) / beep_interval)
                    if self.last_countdown_beep is not None
                    else -1
                )

                if current_beep > last_beep:
                    self.on_countdown_beep()
                    self.last_countdown_beep = 2.0 - time_remaining

            if elapsed >= self.wave_start_delay:
                self.first_wave_start_time = None
                self.last_countdown_beep = None
                self._start_next_wave()
            return  # Don't process wave logic until first wave starts

        # Check if wave is cleared
        if self.wave_in_progress and len(self.enemies) == 0:
            # Wave cleared!
            self.wave_in_progress = False
            if self.wave_clear_time is None:
                self.wave_clear_time = time.time()
                self.last_countdown_beep = None  # Reset for next wave countdown

        # Start next wave after delay (with countdown beeps in last 2 seconds)
        if not self.wave_in_progress and self.wave_clear_time is not None:
            elapsed = time.time() - self.wave_clear_time
            time_remaining = self.wave_clear_delay - elapsed

            # Play countdown beeps every second in the LAST 2 seconds
            if self.on_countdown_beep and time_remaining <= 2.0 and time_remaining > 0:
                beep_interval = 1.0
                # Calculate which beep we're on (0 or 1 for 2-second countdown)
                current_beep = int((2.0 - time_remaining) / beep_interval)
                last_beep = (
                    int((self.last_countdown_beep or -1) / beep_interval)
                    if self.last_countdown_beep is not None
                    else -1
                )

                if current_beep > last_beep:
                    self.on_countdown_beep()
                    self.last_countdown_beep = 2.0 - time_remaining

            if elapsed >= self.wave_clear_delay:
                self.wave_clear_time = None
                self.last_countdown_beep = None
                self._start_next_wave()

    def handle_shoot_attempt(self) -> bool:
        """
        Try to fire weapon.

        Returns:
            True if weapon fired
        """
        if not self.player.is_alive:
            return False

        if self.weapon.can_fire():
            self.weapon.fire()
            return True
        return False

    def handle_enemy_hit(self, enemy: Enemy) -> bool:
        """
        Handle an enemy being hit by weapon.

        Args:
            enemy: Enemy that was hit

        Returns:
            True if enemy died
        """
        if not enemy.is_alive:
            return False

        enemy.take_damage(self.weapon.damage)

        # Notify infrastructure for visual feedback (blink, health bar update)
        if self.on_enemy_damaged:
            self.on_enemy_damaged(enemy)

        if not enemy.is_alive:
            self.player.add_kill()
            # Immediate cleanup: remove dead enemy from domain list
            if enemy in self.enemies:
                self.enemies.remove(enemy)
            # Notify infrastructure to destroy visual entity
            if self.on_enemy_death:
                self.on_enemy_death(enemy)
            return True

        return False

    def handle_player_hit(self, damage: int) -> None:
        """
        Handle player taking damage.

        Args:
            damage: Amount of damage
        """
        if not self.player.is_alive:
            return

        self.player.take_damage(damage)

        if not self.player.is_alive:
            self.game_started = False
            if self.on_player_death:
                self.on_player_death()
