"""Enemy spawning management."""

from ursina import *
from typing import Dict
from domain.entities import Enemy
from infrastructure.rendering import EnemyRenderer


class EnemySpawner:
    """
    Manages enemy entity spawning and despawning.
    Infrastructure layer - Ursina specific.
    """

    def __init__(self, shootables_parent: Entity, player: Entity, game_service):
        """
        Initialize enemy spawner.

        Args:
            shootables_parent: Parent entity for raycast targeting
            player: Player entity
            game_service: GameService instance
        """
        self.shootables_parent = shootables_parent
        self.player = player
        self.game_service = game_service
        self.enemy_entities: Dict[int, EnemyRenderer] = {}

    def spawn_enemy(self, enemy: Enemy):
        """
        Create visual entity for domain enemy.

        Args:
            enemy: Domain Enemy instance
        """
        enemy_entity = EnemyRenderer(enemy, self.player, self.game_service, self.shootables_parent)
        self.enemy_entities[id(enemy)] = enemy_entity

    def despawn_enemy(self, enemy: Enemy):
        """
        Destroy visual entity for domain enemy.

        Args:
            enemy: Domain Enemy instance
        """
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            # Call custom destroy() method to properly clean up children
            self.enemy_entities[enemy_id].destroy()
            del self.enemy_entities[enemy_id]

    def despawn_all(self):
        """Destroy all enemy entities."""
        for enemy_entity in list(self.enemy_entities.values()):
            # Call custom destroy() method to properly clean up children
            enemy_entity.destroy()
        self.enemy_entities.clear()

    def handle_enemy_damage(self, enemy: Enemy):
        """
        Handle visual feedback when enemy takes damage.

        Args:
            enemy: Domain Enemy instance
        """
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            self.enemy_entities[enemy_id].take_damage()
