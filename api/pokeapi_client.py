import requests
import time
from typing import Optional, Dict, List
import json
import os

class PokeAPIClient:
    """Client pour interagir avec l'API PokeAPI"""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    CACHE_DIR = "data/cache"
    
    def __init__(self):
        self.session = requests.Session()
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Crée le dossier cache s'il n'existe pas"""
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def get_pokemon(self, identifier: int | str) -> Optional[Dict]:
        """
        Récupère les informations d'un Pokémon
        identifier: ID (int) ou nom (str) du Pokémon
        """
        # Vérifier le cache
        cache_file = f"{self.CACHE_DIR}/pokemon_{identifier}.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Appel API
        try:
            url = f"{self.BASE_URL}/pokemon/{identifier}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Sauvegarder en cache
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                
                return data
            else:
                print(f"Erreur {response.status_code} pour {identifier}")
                return None
                
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return None
    
    def get_pokemon_species(self, identifier: int | str) -> Optional[Dict]:
        """Récupère les informations d'espèce (descriptions, etc.)"""
        try:
            url = f"{self.BASE_URL}/pokemon-species/{identifier}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Erreur species : {e}")
            return None
    
    def get_pokemon_list(self, limit: int = 251) -> List[Dict]:
        """Récupère la liste des Pokémon"""
        try:
            url = f"{self.BASE_URL}/pokemon?limit={limit}&offset=0"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()['results']
            return []
            
        except Exception as e:
            print(f"Erreur liste : {e}")
            return []
    
    def download_image(self, url: str, pokemon_id: int) -> Optional[str]:
        """Télécharge et cache une image de Pokémon"""
        if not url:
            return None
        
        image_path = f"{self.CACHE_DIR}/sprite_{pokemon_id}.png"
        
        # Si déjà en cache
        if os.path.exists(image_path):
            return image_path
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path
            return None
            
        except Exception as e:
            print(f"Erreur téléchargement image : {e}")
            return None