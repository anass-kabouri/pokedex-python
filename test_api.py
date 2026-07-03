import requests

# Test basique
response = requests.get("https://pokeapi.co/api/v2/pokemon/1")
if response.status_code == 200:
    data = response.json()
    print(f"✅ API fonctionne ! Pokémon récupéré : {data['name']}")
else:
    print("❌ Erreur API")