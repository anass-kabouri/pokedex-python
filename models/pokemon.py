from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class PokemonStats:
    """Statistiques d'un Pokémon"""
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    
    @classmethod
    def from_api_data(cls, stats_data: List[Dict]):
        """Crée les stats depuis les données API"""
        stats_dict = {stat['stat']['name']: stat['base_stat'] for stat in stats_data}
        return cls(
            hp=stats_dict.get('hp', 0),
            attack=stats_dict.get('attack', 0),
            defense=stats_dict.get('defense', 0),
            special_attack=stats_dict.get('special-attack', 0),
            special_defense=stats_dict.get('special-defense', 0),
            speed=stats_dict.get('speed', 0)
        )

class Pokemon:
    """Représente un Pokémon"""
    
    def __init__(self, pokemon_data: Dict):
        self.id = pokemon_data['id']
        self.name = pokemon_data['name'].capitalize()
        self.height = pokemon_data['height'] / 10  # Convertir en mètres
        self.weight = pokemon_data['weight'] / 10  # Convertir en kg
        
        # Types
        self.types = [t['type']['name'] for t in pokemon_data['types']]
        
        # Stats
        self.stats = PokemonStats.from_api_data(pokemon_data['stats'])
        
        # HP actuel (pour les combats)
        self.current_hp = self.stats.hp
        
        # Capacités
        self.abilities = [a['ability']['name'] for a in pokemon_data['abilities']]
        
        # Images
        sprites = pokemon_data['sprites']
        self.sprite_front = sprites.get('front_default')
        self.sprite_back = sprites.get('back_default')
        self.sprite_official = sprites.get('other', {}).get('official-artwork', {}).get('front_default')
    
    def __str__(self):
        return f"#{self.id:03d} - {self.name}"
    
    def __repr__(self):
        return self.__str__()
    
    def get_type_display(self) -> str:
        """Retourne les types formatés"""
        return " / ".join(self.types)
    
    def reset_hp(self):
        """Réinitialise les HP au maximum"""
        self.current_hp = self.stats.hp
    
    def is_alive(self) -> bool:
        """Vérifie si le Pokémon est encore en vie"""
        return self.current_hp > 0
    
    def take_damage(self, damage: int):
        """Inflige des dégâts au Pokémon"""
        self.current_hp = max(0, self.current_hp - damage)
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour la sauvegarde"""
        return {
            'id': self.id,
            'name': self.name,
            'current_hp': self.current_hp
        }