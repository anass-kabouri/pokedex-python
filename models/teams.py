from typing import List, Optional
from models.pokemon import Pokemon
import json
import os

class Team:
    """Représente une équipe de Pokémon"""
    
    MAX_SIZE = 5
    SAVE_DIR = "data/teams"
    
    def __init__(self, name: str = "Mon Équipe"):
        self.name = name
        self.pokemons: List[Pokemon] = []
        self._ensure_save_dir()
    
    def _ensure_save_dir(self):
        """Crée le dossier de sauvegarde"""
        os.makedirs(self.SAVE_DIR, exist_ok=True)
    
    def add_pokemon(self, pokemon: Pokemon) -> bool:
        """Ajoute un Pokémon à l'équipe"""
        if len(self.pokemons) >= self.MAX_SIZE:
            return False
        
        # Vérifier qu'il n'est pas déjà dans l'équipe
        if any(p.id == pokemon.id for p in self.pokemons):
            return False
        
        self.pokemons.append(pokemon)
        return True
    
    def remove_pokemon(self, index: int) -> bool:
        """Retire un Pokémon de l'équipe"""
        if 0 <= index < len(self.pokemons):
            self.pokemons.pop(index)
            return True
        return False
    
    def is_full(self) -> bool:
        """Vérifie si l'équipe est complète"""
        return len(self.pokemons) >= self.MAX_SIZE
    
    def is_empty(self) -> bool:
        """Vérifie si l'équipe est vide"""
        return len(self.pokemons) == 0
    
    def get_alive_pokemons(self) -> List[Pokemon]:
        """Retourne les Pokémon encore en vie"""
        return [p for p in self.pokemons if p.is_alive()]
    
    def has_alive_pokemons(self) -> bool:
        """Vérifie s'il reste des Pokémon en vie"""
        return len(self.get_alive_pokemons()) > 0
    
    def reset_all_hp(self):
        """Réinitialise les HP de tous les Pokémon"""
        for pokemon in self.pokemons:
            pokemon.reset_hp()
    
    def save(self, filename: Optional[str] = None):
        """Sauvegarde l'équipe dans un fichier"""
        if filename is None:
            filename = f"{self.name.replace(' ', '_')}.json"
        
        filepath = os.path.join(self.SAVE_DIR, filename)
        
        data = {
            'name': self.name,
            'pokemons': [p.to_dict() for p in self.pokemons]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filename: str, api_client) -> 'Team':
        """Charge une équipe depuis un fichier"""
        filepath = os.path.join(cls.SAVE_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        team = cls(data['name'])
        
        # Recharger les Pokémon depuis l'API
        for pokemon_data in data['pokemons']:
            pokemon_api_data = api_client.get_pokemon(pokemon_data['id'])
            if pokemon_api_data:
                pokemon = Pokemon(pokemon_api_data)
                pokemon.current_hp = pokemon_data.get('current_hp', pokemon.stats.hp)
                team.pokemons.append(pokemon)
        
        return team
    
    @classmethod
    def list_saved_teams(cls) -> List[str]:
        """Liste toutes les équipes sauvegardées"""
        if not os.path.exists(cls.SAVE_DIR):
            return []
        
        return [f for f in os.listdir(cls.SAVE_DIR) if f.endswith('.json')]