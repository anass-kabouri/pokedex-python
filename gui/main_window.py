import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from typing import Optional
import threading

from api.pokeapi_client import PokeAPIClient
from models.pokemon import Pokemon
from models.teams import Team

# ============ PALETTE & CONSTANTES DE STYLE ============
BG_DARK = '#1E2140'          # bleu-nuit, header
BG_APP = '#F4F5F9'           # fond général clair
BG_CARD = '#FFFFFF'          # fond des cartes
ACCENT = '#E3350D'           # rouge Pokédex (accent, pas fond total)
ACCENT_HOVER = '#FF4A20'
TEXT_DARK = '#1E2140'
TEXT_MUTED = '#7C8093'
LINE = '#E4E6EF'

FONT_TITLE = ('Segoe UI', 26, 'bold')
FONT_H2 = ('Segoe UI', 20, 'bold')
FONT_NAME = ('Segoe UI', 22, 'bold')
FONT_BODY = ('Segoe UI', 11)
FONT_BODY_BOLD = ('Segoe UI', 11, 'bold')
FONT_SMALL = ('Segoe UI', 9)
FONT_BTN = ('Segoe UI', 11, 'bold')

TYPE_COLORS = {
    'normal': '#A8A878', 'fire': '#F08030', 'water': '#6890F0', 'grass': '#78C850',
    'electric': '#F8D030', 'ice': '#98D8D8', 'fighting': '#C03028', 'poison': '#A040A0',
    'ground': '#E0C068', 'flying': '#A890F0', 'psychic': '#F85888', 'bug': '#A8B820',
    'rock': '#B8A038', 'ghost': '#705898', 'dragon': '#7038F8', 'dark': '#705848',
    'steel': '#B8B8D0', 'fairy': '#EE99AC',
}

STAT_COLORS = {
    'HP': '#FF5959', 'Attaque': '#F5AC78', 'Défense': '#FAE078',
    'Att. Spé': '#9DB7F5', 'Déf. Spé': '#A7DB8D', 'Vitesse': '#FA92B2',
}


def make_flat_button(parent, text, command, bg, fg='white', font=FONT_BTN, hover=None, **kw):
    """Bouton plat avec effet de survol (léger éclaircissement de la couleur)."""
    btn = tk.Button(
        parent, text=text, command=command, bg=bg, fg=fg, font=font,
        relief='flat', bd=0, cursor='hand2', activebackground=hover or bg,
        activeforeground=fg, padx=14, pady=8, **kw
    )
    hover_color = hover or bg
    btn.bind('<Enter>', lambda e: btn.config(bg=hover_color))
    btn.bind('<Leave>', lambda e: btn.config(bg=bg))
    return btn


class PokedexApp:
    """Application principale du Pokédex"""

    def __init__(self, root):
        self.root = root
        self.root.title("Pokédex — Projet Python B3")
        self.root.geometry("1080x800")
        self.root.minsize(980, 760)
        self.root.configure(bg=BG_APP)
        try:
            self.root.state('zoomed')  # plein écran au démarrage (Windows)
        except tk.TclError:
            pass

        self.api_client = PokeAPIClient()
        self.current_pokemon: Optional[Pokemon] = None
        self.current_id = 1
        self.current_team = Team("Équipe 1")
        self.image_cache = {}
        self.pokemon_cache = {}  # évite de re-télécharger un Pokémon déjà visité
        self.is_loading = False

        self.create_widgets()
        self.load_pokemon(1)

    # ---------------------------------------------------------------
    def create_widgets(self):
        # === HEADER ===
        header = tk.Frame(self.root, bg=BG_DARK, height=76)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title_label = tk.Label(
            header, text="⬡  POKÉDEX", font=FONT_TITLE, bg=BG_DARK, fg='white'
        )
        title_label.pack(side=tk.LEFT, padx=30, pady=10)

        subtitle = tk.Label(
            header, text="Projet Python B3", font=FONT_SMALL, bg=BG_DARK, fg='#9AA0C8'
        )
        subtitle.pack(side=tk.LEFT, pady=(28, 0))

        # === CORPS ===
        body = tk.Frame(self.root, bg=BG_APP)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        left_frame = tk.Frame(body, bg=BG_APP)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))

        right_frame = tk.Frame(body, bg=BG_APP, width=320)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        right_frame.pack_propagate(False)

        self.create_pokemon_display(left_frame)
        self.create_team_display(right_frame)

    # ---------------------------------------------------------------
    def _card(self, parent, **kw):
        """Crée une 'carte' blanche avec bordure légère."""
        card = tk.Frame(parent, bg=BG_CARD, highlightbackground=LINE, highlightthickness=1, **kw)
        return card

    def create_pokemon_display(self, parent):
        card = self._card(parent)
        card.pack(fill=tk.BOTH, expand=True)

        # -- Barre de recherche --
        search_bar = tk.Frame(card, bg=BG_CARD)
        search_bar.pack(fill=tk.X, padx=24, pady=(20, 10))

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_bar, textvariable=self.search_var, font=FONT_BODY,
            relief='flat', bg='#F0F1F6', fg=TEXT_DARK, insertbackground=TEXT_DARK
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 8))
        search_entry.insert(0, "")
        search_entry.bind('<Return>', lambda e: self.search_pokemon())

        make_flat_button(
            search_bar, "🔍  Rechercher", self.search_pokemon,
            bg=ACCENT, hover=ACCENT_HOVER
        ).pack(side=tk.LEFT)

        # -- Navigation --
        nav_frame = tk.Frame(card, bg=BG_CARD)
        nav_frame.pack(fill=tk.X, padx=24, pady=(0, 6))

        self.prev_btn = make_flat_button(
            nav_frame, "◄  Précédent", self.previous_pokemon,
            bg='#EDEFF6', fg=TEXT_DARK, hover='#DDE0EE'
        )
        self.prev_btn.pack(side=tk.LEFT)

        self.id_label = tk.Label(nav_frame, text="#001", font=FONT_H2, bg=BG_CARD, fg=TEXT_MUTED)
        self.id_label.pack(side=tk.LEFT, expand=True)

        self.next_btn = make_flat_button(
            nav_frame, "Suivant  ►", self.next_pokemon,
            bg='#EDEFF6', fg=TEXT_DARK, hover='#DDE0EE'
        )
        self.next_btn.pack(side=tk.RIGHT)

        # -- Image --
        self.image_label = tk.Label(card, bg=BG_CARD)
        self.image_label.pack(pady=(6, 2))

        # -- Nom --
        self.name_label = tk.Label(card, text="", font=FONT_NAME, bg=BG_CARD, fg=TEXT_DARK)
        self.name_label.pack()

        # -- Badges de type --
        self.type_badges_frame = tk.Frame(card, bg=BG_CARD)
        self.type_badges_frame.pack(pady=4)

        # -- Infos taille/poids --
        self.info_label = tk.Label(
            card, text="", font=FONT_BODY, bg=BG_CARD, fg=TEXT_MUTED, justify=tk.CENTER
        )
        self.info_label.pack(pady=(0, 6))

        # -- Stats --
        stats_title = tk.Label(card, text="Statistiques", font=FONT_BODY_BOLD, bg=BG_CARD, fg=TEXT_DARK)
        stats_title.pack(anchor='w', padx=24)

        self.stats_frame = tk.Frame(card, bg=BG_CARD)
        self.stats_frame.pack(pady=(4, 6), padx=24, fill=tk.X)

        # -- Bouton ajouter --
        self.add_to_team_btn = make_flat_button(
            card, "➕  Ajouter à l'équipe", self.add_to_team,
            bg=ACCENT, hover=ACCENT_HOVER, font=FONT_BTN
        )
        self.add_to_team_btn.pack(pady=(4, 12), padx=24, fill=tk.X, ipady=4)

    def create_team_display(self, parent):
        card = self._card(parent)
        card.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(card, text="👥  Mon Équipe", font=FONT_H2, bg=BG_CARD, fg=TEXT_DARK)
        title.pack(pady=(20, 4), padx=20, anchor='w')

        self.team_count_label = tk.Label(
            card, text="0 / 5 Pokémon", font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED
        )
        self.team_count_label.pack(padx=20, anchor='w', pady=(0, 10))

        list_wrap = tk.Frame(card, bg='#F0F1F6')
        list_wrap.pack(fill=tk.BOTH, expand=True, padx=20)

        self.team_listbox = tk.Listbox(
            list_wrap, font=FONT_BODY, bg='#F0F1F6', fg=TEXT_DARK,
            relief='flat', selectbackground=ACCENT, selectforeground='white',
            activestyle='none', highlightthickness=0, bd=0
        )
        self.team_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X, padx=20, pady=16)

        make_flat_button(
            btn_frame, "❌  Retirer", self.remove_from_team,
            bg='#F0F1F6', fg=ACCENT, hover='#FCE3DE'
        ).pack(fill=tk.X, pady=(0, 6), ipady=4)

        make_flat_button(
            btn_frame, "💾  Sauvegarder l'équipe", self.save_team,
            bg='#2E7D32', hover='#37944A'
        ).pack(fill=tk.X, pady=(0, 6), ipady=4)

        make_flat_button(
            btn_frame, "⚔️  Lancer le combat", self.start_combat,
            bg=BG_DARK, hover='#2C305C'
        ).pack(fill=tk.X, ipady=6)

        self.update_team_display()

    # ---------------------------------------------------------------
    def _set_loading(self, is_loading):
        self.is_loading = is_loading
        state = tk.DISABLED if is_loading else tk.NORMAL
        self.prev_btn.config(state=state)
        self.next_btn.config(state=state)
        self.add_to_team_btn.config(state=state)
        if is_loading:
            self.id_label.config(text="Chargement…")

    def load_pokemon(self, identifier):
        if self.is_loading:
            return  # ignore les clics pendant qu'un chargement est déjà en cours

        cache_key = str(identifier).lower()
        if cache_key in self.pokemon_cache:
            # déjà visité : instantané, aucune requête réseau
            pokemon = self.pokemon_cache[cache_key]
            self.current_pokemon = pokemon
            self.current_id = pokemon.id
            self.display_pokemon()
            return

        self._set_loading(True)
        thread = threading.Thread(target=self._fetch_worker, args=(identifier,), daemon=True)
        thread.start()

    def _fetch_worker(self, identifier):
        """Exécuté dans un thread séparé : ne touche à AUCUN widget ici."""
        data = self.api_client.get_pokemon(identifier)
        pokemon = None
        pil_image = None
        if data:
            pokemon = Pokemon(data)
            url = pokemon.sprite_official or pokemon.sprite_front
            if url and url not in self.image_cache:
                try:
                    response = requests.get(url, timeout=8)
                    pil_image = Image.open(BytesIO(response.content)).resize(
                        (180, 180), Image.Resampling.LANCZOS
                    )
                except Exception as e:
                    print(f"Erreur chargement image: {e}")
        # on repasse sur le thread principal pour toucher aux widgets
        self.root.after(0, self._on_pokemon_loaded, identifier, pokemon, pil_image)

    def _on_pokemon_loaded(self, identifier, pokemon, pil_image):
        self._set_loading(False)

        if not pokemon:
            messagebox.showerror("Erreur", f"Impossible de charger le Pokémon {identifier}")
            self.id_label.config(text=f"#{self.current_id:03d}")
            return

        url = pokemon.sprite_official or pokemon.sprite_front
        if pil_image is not None and url:
            self.image_cache[url] = ImageTk.PhotoImage(pil_image)

        # met en cache sous plusieurs clés pour retrouver le Pokémon instantanément
        self.pokemon_cache[str(pokemon.id)] = pokemon
        self.pokemon_cache[pokemon.name.lower()] = pokemon

        self.current_pokemon = pokemon
        self.current_id = pokemon.id
        self.display_pokemon()

    def display_pokemon(self):
        if not self.current_pokemon:
            return
        p = self.current_pokemon

        self.id_label.config(text=f"#{p.id:03d}")
        self.name_label.config(text=p.name.upper())

        for widget in self.type_badges_frame.winfo_children():
            widget.destroy()
        for t in p.types:
            color = TYPE_COLORS.get(t.lower(), '#999999')
            badge = tk.Label(
                self.type_badges_frame, text=t.upper(), font=FONT_SMALL,
                bg=color, fg='white', padx=14, pady=4
            )
            badge.pack(side=tk.LEFT, padx=4)

        self.info_label.config(text=f"Taille : {p.height} m      Poids : {p.weight} kg")

        url = p.sprite_official or p.sprite_front
        photo = self.image_cache.get(url) if url else None
        if photo:
            self.image_label.config(image=photo)
            self.image_label.image = photo

        self.display_stats()

    def display_stats(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        if not self.current_pokemon:
            return

        stats = self.current_pokemon.stats
        stats_data = [
            ("HP", stats.hp), ("Attaque", stats.attack), ("Défense", stats.defense),
            ("Att. Spé", stats.special_attack), ("Déf. Spé", stats.special_defense),
            ("Vitesse", stats.speed),
        ]

        for name, value in stats_data:
            color = STAT_COLORS.get(name, ACCENT)
            row = tk.Frame(self.stats_frame, bg=BG_CARD)
            row.pack(fill=tk.X, pady=3)

            tk.Label(row, text=name, font=FONT_SMALL, width=9, anchor='w', bg=BG_CARD, fg=TEXT_MUTED).pack(side=tk.LEFT)

            track = tk.Canvas(row, height=12, bg='#EEF0F6', highlightthickness=0)
            track.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
            track.update_idletasks()

            def draw_bar(canvas=track, val=value, col=color):
                canvas.delete('all')
                w = canvas.winfo_width() or 200
                bar_w = max(4, (val / 255) * w)
                canvas.create_rectangle(0, 0, w, 12, fill='#EEF0F6', outline='')
                canvas.create_rectangle(0, 0, bar_w, 12, fill=col, outline='')

            track.bind('<Configure>', lambda e, c=track, v=value, col=color: draw_bar(c, v, col))

            tk.Label(row, text=str(value), font=FONT_SMALL, width=4, anchor='e', bg=BG_CARD, fg=TEXT_DARK).pack(side=tk.LEFT)

    def next_pokemon(self):
        if self.current_id < 251:
            self.load_pokemon(self.current_id + 1)

    def previous_pokemon(self):
        if self.current_id > 1:
            self.load_pokemon(self.current_id - 1)

    def search_pokemon(self):
        search_term = self.search_var.get().strip().lower()
        if not search_term:
            return
        if search_term.isdigit():
            pokemon_id = int(search_term)
            if 1 <= pokemon_id <= 251:
                self.load_pokemon(pokemon_id)
                return
        self.load_pokemon(search_term)

    def add_to_team(self):
        if not self.current_pokemon:
            return
        if self.current_team.is_full():
            messagebox.showwarning("Équipe complète", "Votre équipe est déjà complète (5 Pokémon max)")
            return
        if self.current_team.add_pokemon(self.current_pokemon):
            self.update_team_display()
            messagebox.showinfo("Succès", f"{self.current_pokemon.name} ajouté à l'équipe !")
        else:
            messagebox.showwarning("Doublon", "Ce Pokémon est déjà dans l'équipe")

    def remove_from_team(self):
        selection = self.team_listbox.curselection()
        if not selection:
            messagebox.showwarning("Sélection", "Sélectionnez un Pokémon à retirer")
            return
        index = selection[0]
        pokemon_name = self.current_team.pokemons[index].name
        if self.current_team.remove_pokemon(index):
            self.update_team_display()
            messagebox.showinfo("Succès", f"{pokemon_name} retiré de l'équipe")

    def update_team_display(self):
        self.team_listbox.delete(0, tk.END)
        for i, pokemon in enumerate(self.current_team.pokemons):
            self.team_listbox.insert(tk.END, f"  {i + 1}.  {pokemon}")
        count = len(self.current_team.pokemons)
        if count == 0:
            self.team_listbox.insert(tk.END, "  Équipe vide")
        self.team_count_label.config(text=f"{count} / 5 Pokémon")

    def save_team(self):
        if self.current_team.is_empty():
            messagebox.showwarning("Équipe vide", "Ajoutez des Pokémon avant de sauvegarder")
            return
        self.current_team.save()
        messagebox.showinfo("Succès", f"Équipe '{self.current_team.name}' sauvegardée !")

    def start_combat(self):
        if len(self.current_team.pokemons) == 0:
            messagebox.showwarning("Équipe vide", "Créez une équipe avant de combattre !")
            return
        messagebox.showinfo("Combat", "Système de combat en développement...")


if __name__ == "__main__":
    root = tk.Tk()
    app = PokedexApp(root)
    root.mainloop()