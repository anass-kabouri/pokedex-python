# ⬡ Pokédex — Projet Python B3

Application desktop développée en Python/Tkinter permettant de consulter les Pokémon de la première génération (Kanto), de constituer une équipe personnalisée, et de la sauvegarder localement.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Tkinter-GUI-2496ED?style=for-the-badge" alt="Tkinter" />
  <img src="https://img.shields.io/badge/Pillow-Image_Processing-yellow?style=for-the-badge" alt="Pillow" />
  <img src="https://img.shields.io/badge/PokeAPI-REST-red?style=for-the-badge" alt="PokeAPI" />
</p>

## 📖 À propos

Ce projet a été réalisé dans le cadre d'un module Python en B3. Il consomme l'API publique **PokeAPI** pour afficher en temps réel les informations de chaque Pokémon (statistiques, types, sprite officiel), avec une interface graphique pensée pour rester fluide même pendant les appels réseau.

## ✨ Fonctionnalités

- 🔍 **Recherche** d'un Pokémon par nom ou par numéro de Pokédex
- ◄ ► **Navigation** séquentielle entre les 251 premiers Pokémon
- 📊 **Statistiques visuelles** (HP, Attaque, Défense, Attaque Spé., Défense Spé., Vitesse) sous forme de barres colorées
- 🏷️ **Badges de type** avec les couleurs officielles (Feu, Eau, Plante, etc.)
- 👥 **Gestion d'équipe** : ajout/retrait de Pokémon (5 maximum), avec détection des doublons
- 💾 **Sauvegarde locale** de l'équipe constituée
- ⚔️ Base pour un futur **système de combat** (en cours de développement)

## 🚀 Point technique : une interface qui ne se fige jamais

Un défi classique avec Tkinter est que les appels réseau bloquent l'interface pendant l'attente de la réponse. Ce projet résout ce problème avec :
- **Threading** : chaque requête vers PokeAPI s'exécute dans un thread séparé, pendant que la fenêtre principale reste réactive
- **Cache en mémoire** : un Pokémon déjà consulté est stocké localement — le revoir est instantané, sans nouvelle requête réseau
- **Feedback visuel** : les boutons de navigation se désactivent brièvement pendant le chargement, pour éviter les clics multiples

## 🗂️ Structure du projet

```
pokedex_project/
├── api/
│   └── pokeapi_client.py      # Client HTTP vers PokeAPI
├── models/
│   ├── pokemon.py             # Modèle de données Pokémon
│   └── teams.py                # Modèle de données Équipe
├── combat/
│   ├── combat_system.py       # Logique de combat
│   └── combat_window.py       # Interface du combat
├── gui/
│   └── main_window.py         # Fenêtre principale de l'application
└── requirements.txt
```

## ⚙️ Installation

```bash
git clone https://github.com/anass-kabouri/pokedex-python.git
cd pokedex-python

python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows (PowerShell)
# source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
```

## ▶️ Lancer l'application

```bash
python -m gui.main_window
```

## 🛠️ Stack technique

| Domaine | Technologies |
|---|---|
| Langage | Python 3 |
| Interface graphique | Tkinter |
| Traitement d'images | Pillow (PIL) |
| Requêtes HTTP | Requests |
| Source de données | [PokeAPI](https://pokeapi.co/) |
| Concurrence | Threading |

## 📌 Améliorations futures

- [ ] Finaliser le système de combat (tour par tour, calcul de dégâts par type)
- [ ] Sauvegarde de plusieurs équipes nommées
- [ ] Filtres de recherche par type
- [ ] Export de l'équipe en image/PDF

---

<p align="center"><i>Projet réalisé par Anass Kabouri — <a href="https://anass-kabouri.github.io/PortFolio/">Portfolio</a></i></p>
