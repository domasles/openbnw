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
        enemy_entity = EnemyRenderer(
            enemy,
            self.player,
            self.game_service,
            self.shootables_parent
        )
        self.enemy_entities[id(enemy)] = enemy_entity
    
    def despawn_enemy(self, enemy: Enemy):
        """
        Destroy visual entity for domain enemy.
        
        Args:
            enemy: Domain Enemy instance
        """
        enemy_id = id(enemy)
        if enemy_id in self.enemy_entities:
            destroy(self.enemy_entities[enemy_id])
            del self.enemy_entities[enemy_id]
    
    def despawn_all(self):
        """Destroy all enemy entities."""
        for enemy_entity in list(self.enemy_entities.values()):
            destroy(enemy_entity)
        self.enemy_entities.clear()
