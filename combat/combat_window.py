import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

from combat.combat_system import CombatSystem
from models.team import Team

class CombatWindow:
    """Fenêtre de combat"""
    
    def __init__(self, parent, team1: Team, team2: Team):
        self.window = tk.Toplevel(parent)
        self.window.title("⚔️ Combat Pokémon")
        self.window.geometry("900x600")
        self.window.configure(bg='#2C3E50')
        
        self.combat_system = CombatSystem(team1, team2)
        self.image_cache = {}
        
        self.waiting_for_switch = False
        
        self.create_widgets()
        self.update_display()
    
    def create_widgets(self):
        """Crée l'interface de combat"""
        
        # === ZONE DE COMBAT ===
        combat_frame = tk.Frame(self.window, bg='#34495E', height=350)
        combat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        
        # Pokémon adversaire (en haut à droite)
        enemy_frame = tk.Frame(combat_frame, bg='#34495E')
        enemy_frame.place(relx=0.7, rely=0.1, anchor='center')
        
        self.enemy_name_label = tk.Label(
            enemy_frame,
            text="",
            font=('Arial', 16, 'bold'),
            bg='#34495E',
            fg='white'
        )
        self.enemy_name_label.pack()
        
        self.enemy_hp_label = tk.Label(
            enemy_frame,
            text="",
            font=('Arial', 12),
            bg='#34495E',
            fg='#E74C3C'
        )
        self.enemy_hp_label.pack()
        
        self.enemy_image_label = tk.Label(enemy_frame, bg='#34495E')
        self.enemy_image_label.pack(pady=10)
        
        # Pokémon du joueur (en bas à gauche)
        player_frame = tk.Frame(combat_frame, bg='#34495E')
        player_frame.place(relx=0.3, rely=0.7, anchor='center')
        
        self.player_image_label = tk.Label(player_frame, bg='#34495E')
        self.player_image_label.pack(pady=10)
        
        self.player_name_label = tk.Label(
            player_frame,
            text="",
            font=('Arial', 16, 'bold'),
            bg='#34495E',
            fg='white'
        )
        self.player_name_label.pack()
        
        self.player_hp_label = tk.Label(
            player_frame,
            text="",
            font=('Arial', 12),
            bg='#34495E',
            fg='#2ECC71'
        )
        self.player_hp_label.pack()
        
        # === ZONE DE TEXTE ===
        log_frame = tk.Frame(self.window, bg='white', height=100)
        log_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.log_text = tk.Text(
            log_frame,
            height=6,
            font=('Arial', 11),
            bg='#ECF0F1',
            fg='#2C3E50',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === ZONE D'ACTIONS ===
        action_frame = tk.Frame(self.window, bg='#2C3E50')
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Boutons d'action
        self.attack_btn = tk.Button(
            action_frame,
            text="⚔️ ATTAQUER",
            command=self.on_attack,
            font=('Arial', 14, 'bold'),
            bg='#E74C3C',
            fg='white',
            height=2,
            width=15,
            cursor='hand2'
        )
        self.attack_btn.pack(side=tk.LEFT, padx=5)
        
        self.switch_btn = tk.Button(
            action_frame,
            text="🔄 CHANGER",
            command=self.on_switch,
            font=('Arial', 14, 'bold'),
            bg='#3498DB',
            fg='white',
            height=2,
            width=15,
            cursor='hand2'
        )
        self.switch_btn.pack(side=tk.LEFT, padx=5)
        
        # Info équipe
        team_info = tk.Label(
            action_frame,
            text="",
            font=('Arial', 10),
            bg='#2C3E50',
            fg='white'
        )
        team_info.pack(side=tk.RIGHT, padx=10)
        self.team_info_label = team_info
    
    def update_display(self):
        """Met à jour l'affichage"""
        cs = self.combat_system
        
        # Pokémon du joueur
        if cs.active_pokemon1:
            p1 = cs.active_pokemon1
            self.player_name_label.config(text=p1.name.upper())
            self.player_hp_label.config(text=f"HP: {p1.current_hp}/{p1.stats.hp}")
            self.load_image(p1.sprite_back, self.player_image_label, size=150)
        
        # Pokémon adversaire
        if cs.active_pokemon2:
            p2 = cs.active_pokemon2
            self.enemy_name_label.config(text=p2.name.upper())
            self.enemy_hp_label.config(text=f"HP: {p2.current_hp}/{p2.stats.hp}")
            self.load_image(p2.sprite_front, self.enemy_image_label, size=150)
        
        # Info équipe
        alive1 = len(cs.team1.get_alive_pokemons())
        alive2 = len(cs.team2.get_alive_pokemons())
        self.team_info_label.config(text=f"Votre équipe: {alive1}/5 | Adversaire: {alive2}/5")
    
    def load_image(self, url, label, size=100):
        """Charge une image"""
        if not url:
            return
        
        try:
            if url in self.image_cache:
                photo = self.image_cache[url]
            else:
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_cache[url] = photo
            
            label.config(image=photo)
            label.image = photo
        except Exception as e:
            print(f"Erreur image: {e}")
    
    def add_log(self, message: str):
        """Ajoute un message au log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_attack(self):
        """Gère l'attaque"""
        if self.waiting_for_switch:
            messagebox.showwarning("Attention", "Vous devez d'abord changer de Pokémon!")
            return
        
        # Désactiver les boutons
        self.attack_btn.config(state=tk.DISABLED)
        self.switch_btn.config(state=tk.DISABLED)
        
        # Tour du joueur
        message = self.combat_system.player_turn("attack")
        self.add_log(message)
        self.update_display()
        
        # Vérifier KO
        winner = self.combat_system.check_ko()
        if winner:
            self.end_battle(winner)
            return
        
        # Vérifier si le joueur doit changer de Pokémon
        if not self.combat_system.active_pokemon1.is_alive():
            self.waiting_for_switch = True
            self.add_log("Votre Pokémon est KO ! Choisissez-en un autre.")
            self.switch_btn.config(state=tk.NORMAL)
            return
        
        # Tour de l'IA après un délai
        self.window.after(1000, self.ai_turn)
    
    def ai_turn(self):
        """Tour de l'IA"""
        message = self.combat_system.ai_turn()
        self.add_log(message)
        self.update_display()
        
        # Vérifier KO
        winner = self.combat_system.check_ko()
        if winner:
            self.end_battle(winner)
            return
        
        # Vérifier si le joueur doit changer de Pokémon
        if not self.combat_system.active_pokemon1.is_alive():
            self.waiting_for_switch = True
            self.add_log("Votre Pokémon est KO ! Choisissez-en un autre.")
            self.switch_btn.config(state=tk.NORMAL)
            return
        
        # Réactiver les boutons
        self.attack_btn.config(state=tk.NORMAL)
        self.switch_btn.config(state=tk.NORMAL)
    
    def on_switch(self):
        """Gère le changement de Pokémon"""
        # Créer une fenêtre de sélection
        switch_window = tk.Toplevel(self.window)
        switch_window.title("Choisir un Pokémon")
        switch_window.geometry("300x400")
        
        tk.Label(
            switch_window,
            text="Sélectionnez un Pokémon :",
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        listbox = tk.Listbox(switch_window, font=('Arial', 12))
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Remplir avec les Pokémon vivants
        for i, pokemon in enumerate(self.combat_system.team1.pokemons):
            if pokemon.is_alive() and pokemon != self.combat_system.active_pokemon1:
                listbox.insert(tk.END, f"{pokemon.name} (HP: {pokemon.current_hp}/{pokemon.stats.hp})")
                listbox.itemconfig(tk.END, {'fg': 'green'})
        
        def confirm_switch():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Sélection", "Choisissez un Pokémon")
                return
            
            # Trouver l'index réel
            selected_name = listbox.get(selection[0]).split()[0]
            for i, p in enumerate(self.combat_system.team1.pokemons):
                if p.name == selected_name:
                    self.combat_system.switch_pokemon(1, i)
                    self.update_display()
                    self.add_log(f"Vous envoyez {p.name} !")
                    
                    switch_window.destroy()
                    
                    # Si c'était obligatoire, on ne fait pas le tour de l'IA
                    if self.waiting_for_switch:
                        self.waiting_for_switch = False
                        self.attack_btn.config(state=tk.NORMAL)
                    else:
                        # Sinon, tour de l'IA
                        self.window.after(500, self.ai_turn)
                    
                    break
        
        tk.Button(
            switch_window,
            text="Confirmer",
            command=confirm_switch,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
    
    def end_battle(self, winner: int):
        """Termine le combat"""
        if winner == 1:
            message = "🎉 VICTOIRE ! Vous avez gagné le combat !"
            self.add_log(message)
            messagebox.showinfo("Victoire", message)
        else:
            message = "😞 DÉFAITE... Vous avez perdu le combat."
            self.add_log(message)
            messagebox.showinfo("Défaite", message)
        
        self.attack_btn.config(state=tk.DISABLED)
        self.switch_btn.config(state=tk.DISABLED)
        
        # Bouton pour fermer
        close_btn = tk.Button(
            self.window,
            text="Fermer",
            command=self.window.destroy,
            font=('Arial', 12),
            bg='#95a5a6',
            fg='white'
        )
        close_btn.pack(pady=10)
        