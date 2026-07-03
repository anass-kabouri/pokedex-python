import random
from typing import List, Tuple, Optional
from models.pokemon import Pokemon
from models.team import Team

class CombatSystem:
    """Système de combat entre Pokémon"""
    
    # Table des types (simplifié)
    TYPE_EFFECTIVENESS = {
        'fire': {'grass': 2.0, 'water': 0.5, 'fire': 0.5},
        'water': {'fire': 2.0, 'grass': 0.5, 'water': 0.5},
        'grass': {'water': 2.0, 'fire': 0.5, 'grass': 0.5},
        'electric': {'water': 2.0, 'grass': 0.5, 'electric': 0.5},
        'normal': {},
    }
    
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2
        
        # Réinitialiser les HP
        team1.reset_all_hp()
        team2.reset_all_hp()
        
        # Pokémon actifs
        self.active_pokemon1 = team1.pokemons[0] if team1.pokemons else None
        self.active_pokemon2 = team2.pokemons[0] if team2.pokemons else None
        
        # Index des Pokémon actifs
        self.index1 = 0
        self.index2 = 0
        
        # Historique du combat
        self.battle_log: List[str] = []
    
    def calculate_damage(self, attacker: Pokemon, defender: Pokemon) -> int:
        """Calcule les dégâts d'une attaque"""
        
        # Formule simplifiée inspirée de Pokémon
        base_damage = (2 * attacker.stats.attack * 60) / (5 * defender.stats.defense)
        
        # Bonus de type
        type_bonus = 1.0
        if attacker.types and defender.types:
            attacker_type = attacker.types[0]
            defender_type = defender.types[0]
            
            if attacker_type in self.TYPE_EFFECTIVENESS:
                effectiveness = self.TYPE_EFFECTIVENESS[attacker_type]
                type_bonus = effectiveness.get(defender_type, 1.0)
        
        # Facteur aléatoire
        random_factor = random.uniform(0.85, 1.0)
        
        # Calcul final
        damage = int(base_damage * type_bonus * random_factor)
        
        return max(1, damage)  # Minimum 1 dégât
    
    def attack(self, attacker: Pokemon, defender: Pokemon) -> Tuple[int, str]:
        """Effectue une attaque"""
        damage = self.calculate_damage(attacker, defender)
        defender.take_damage(damage)
        
        effectiveness = ""
        if attacker.types and defender.types:
            attacker_type = attacker.types[0]
            defender_type = defender.types[0]
            
            if attacker_type in self.TYPE_EFFECTIVENESS:
                eff_value = self.TYPE_EFFECTIVENESS[attacker_type].get(defender_type, 1.0)
                if eff_value > 1.0:
                    effectiveness = " C'est super efficace !"
                elif eff_value < 1.0:
                    effectiveness = " Ce n'est pas très efficace..."
        
        message = f"{attacker.name} attaque {defender.name} pour {damage} dégâts !{effectiveness}"
        self.battle_log.append(message)
        
        return damage, message
    
    def player_turn(self, action: str) -> str:
        """Tour du joueur"""
        if action == "attack":
            damage, message = self.attack(self.active_pokemon1, self.active_pokemon2)
            return message
        
        elif action == "switch":
            # Le switch sera géré par l'interface
            return "Changement de Pokémon"
        
        return "Action inconnue"
    
    def ai_turn(self) -> str:
        """Tour de l'IA (simple)"""
        # IA basique : attaque toujours
        # Amélioration possible : stratégie plus complexe
        
        damage, message = self.attack(self.active_pokemon2, self.active_pokemon1)
        return message
    
    def switch_pokemon(self, team_index: int, new_pokemon_index: int):
        """Change le Pokémon actif"""
        if team_index == 1:
            if 0 <= new_pokemon_index < len(self.team1.pokemons):
                new_pokemon = self.team1.pokemons[new_pokemon_index]
                if new_pokemon.is_alive():
                    self.active_pokemon1 = new_pokemon
                    self.index1 = new_pokemon_index
                    self.battle_log.append(f"Vous envoyez {new_pokemon.name} !")
        else:
            if 0 <= new_pokemon_index < len(self.team2.pokemons):
                new_pokemon = self.team2.pokemons[new_pokemon_index]
                if new_pokemon.is_alive():
                    self.active_pokemon2 = new_pokemon
                    self.index2 = new_pokemon_index
                    self.battle_log.append(f"L'adversaire envoie {new_pokemon.name} !")
    
    def check_ko(self) -> Optional[int]:
        """Vérifie si un Pokémon est KO et retourne le gagnant"""
        # Vérifier KO du Pokémon 2
        if not self.active_pokemon2.is_alive():
            self.battle_log.append(f"{self.active_pokemon2.name} est KO !")
            
            # Chercher un remplaçant
            alive_pokemons = [p for p in self.team2.pokemons if p.is_alive()]
            if alive_pokemons:
                # Choisir automatiquement le prochain
                for i, p in enumerate(self.team2.pokemons):
                    if p.is_alive():
                        self.switch_pokemon(2, i)
                        break
            else:
                return 1  # Joueur 1 gagne
        
        # Vérifier KO du Pokémon 1
        if not self.active_pokemon1.is_alive():
            self.battle_log.append(f"{self.active_pokemon1.name} est KO !")
            
            # Le joueur doit choisir un remplaçant
            alive_pokemons = [p for p in self.team1.pokemons if p.is_alive()]
            if not alive_pokemons:
                return 2  # Joueur 2 gagne
        
        return None  # Personne ne gagne encore
    
    def is_battle_over(self) -> Optional[int]:
        """Vérifie si le combat est terminé"""
        if not self.team1.has_alive_pokemons():
            return 2  # Équipe 2 gagne
        if not self.team2.has_alive_pokemons():
            return 1  # Équipe 1 gagne
        return None