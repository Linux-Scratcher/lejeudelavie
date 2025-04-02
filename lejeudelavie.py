import pygame
import random
import threading
from pypresence import Presence
import time

# Paramètres de la fenêtre
WIDTH, HEIGHT = 1200, 800  # Fenêtre plus grande
CELL_SIZE = 10
ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

# Couleurs
ALIVE_COLOR = (0, 255, 0)
DEAD_COLOR = (0, 0, 0)
GRID_COLOR = (50, 50, 50)
BACKGROUND_COLOR = (30, 30, 30)  # Couleur de fond plus sombre

# Initialisation de pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Le Jeu De La Vie")

# Grille de cellules (initialement toutes mortes)
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# Fonction pour placer entre 3 et 20 cellules vivantes collées au démarrage
def spawn_random_cells():
    num_cells = random.randint(3, 20)  # Nombre de cellules à générer
    start_x = random.randint(0, COLS - 1)  # Position aléatoire de départ en x
    start_y = random.randint(0, ROWS - 1)  # Position aléatoire de départ en y
    
    # Génère un petit bloc ou ligne de cellules vivantes
    if num_cells <= 5:  # Si peu de cellules, forme un carré ou un rectangle
        for i in range(num_cells):
            x = (start_x + i) % COLS  # Assure que les cellules restent dans la grille
            y = (start_y + i // COLS) % ROWS  # Crée un effet de ligne ou de carré
            grid[y][x] = 1
    else:  # Pour plus de cellules, on forme une sorte de ligne courbée ou un petit "blinker"
        for i in range(num_cells):
            x = (start_x + i) % COLS
            y = start_y
            grid[y][x] = 1

# Placer des cellules au démarrage
spawn_random_cells()

# Connexion à Discord Rich Presence
client_id = "1353185581475303424"  # Remplace par l'ID de ton application Discord
rpc = Presence(client_id)
rpc.connect()

# Paramètres du jeu
FPS = 10  # Initialisation de FPS
clock = pygame.time.Clock()

# Mode dieu activé ?
god_mode = False

# Met à jour le RPC toutes les 15 secondes
def update_rich_presence():
    alive_cells = sum(sum(row) for row in grid)  # Compte les cellules vivantes
    rpc.update(
        state="En train de jouer au Jeu De La Vie",  # État du joueur
        details=f"Cellules vivantes : {alive_cells}",  # Détails
        start=time.time(),  # Heure de début du jeu
        large_image="jeu_de_la_vie",  # Image du jeu (si tu en as une)
        large_text="Jeu De La Vie"  # Texte associé à l'image
    )

# Fonction pour gérer les commandes du terminal
def command_listener():
    global grid, FPS, god_mode
    while True:
        command = input("Entrez une commande : ").strip().lower()
        
        # Commande !help
        if command == "!help":
            print("""
Commandes disponibles :
1. !god mode      : Active le mode dieu, vous donnant toutes les permissions.
2. !ajouter cellule <nombre> : Ajoute le nombre spécifié de cellules vivantes aléatoires.
3. !delete cellules : Supprime toutes les cellules vivantes.
4. !pause          : Met le jeu en pause.
5. !play           : Relance le jeu.
6. !reset game     : Réinitialise toutes les cellules et rétablit les paramètres du jeu.
7. !set speed <valeur> : Définit la vitesse du jeu en FPS (ex : !set speed 30).
8. !random cells <nombre> : Ajoute un nombre spécifié de cellules vivantes aléatoires.
9. !show cells     : Affiche le nombre actuel de cellules vivantes.
10. !clear grid    : Efface toutes les cellules et réinitialise la grille.
11. !toggle grid   : Active ou désactive l'affichage des lignes de la grille.
            """)
        
        # Commandes du mode dieu
        elif command == "!god mode":
            god_mode = True
            print("Mode Dieu activé : vous avez maintenant toutes les permissions.")
        
        # Commandes pour ajouter des cellules
        elif command.startswith("!ajouter cellule"):
            if not god_mode:
                print("Permission refusée. Activez le mode dieu pour ajouter des cellules.")
                continue
            try:
                count = int(command.split()[-1])  # Récupère le nombre de cellules à ajouter
                for _ in range(count):
                    x, y = random.randint(0, COLS-1), random.randint(0, ROWS-1)
                    grid[y][x] = 1
                print(f"{count} cellules ajoutées.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Commandes pour supprimer des cellules
        elif command == "!delete cellules":
            if not god_mode:
                print("Permission refusée. Activez le mode dieu pour supprimer des cellules.")
                continue
            grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            print("Toutes les cellules ont été supprimées.")
        
        # Commandes pour mettre en pause / reprendre le jeu
        elif command == "!pause":
            FPS = 0
            print("Le jeu est en pause.")
        elif command == "!play":
            FPS = 10
            print("Le jeu a repris.")
        
        # Commande pour réinitialiser le jeu
        elif command == "!reset game":
            grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            spawn_random_cells()  # Re-spawn les cellules
            FPS = 10
            print("Jeu réinitialisé.")

        # Commande pour changer la vitesse du jeu
        elif command.startswith("!set speed"):
            if god_mode:
                try:
                    new_speed = int(command.split()[-1])
                    FPS = new_speed
                    print(f"Vitesse du jeu changée à {new_speed} FPS.")
                except ValueError:
                    print("Veuillez entrer un nombre valide pour la vitesse.")
            else:
                print("Activez le mode dieu pour changer la vitesse.")
        
        # Commande pour ajouter des cellules aléatoires
        elif command.startswith("!random cells"):
            if god_mode:
                try:
                    count = int(command.split()[-1])
                    for _ in range(count):
                        x, y = random.randint(0, COLS-1), random.randint(0, ROWS-1)
                        grid[y][x] = 1
                    print(f"{count} cellules aléatoires ajoutées.")
                except ValueError:
                    print("Veuillez entrer un nombre valide pour les cellules aléatoires.")
            else:
                print("Activez le mode dieu pour ajouter des cellules aléatoires.")
        
        # Commande pour afficher le nombre de cellules vivantes
        elif command == "!show cells":
            alive_cells = sum(sum(row) for row in grid)
            print(f"Cellules vivantes : {alive_cells}")

        # Commande pour nettoyer la grille
        elif command == "!clear grid":
            grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            print("Grille nettoyée.")
        
        # Commande pour basculer l'affichage de la grille
        elif command == "!toggle grid":
            global GRID_COLOR
            if GRID_COLOR == (50, 50, 50):
                GRID_COLOR = (255, 255, 255)  # Couleur blanche pour la grille
                print("Affichage de la grille activé.")
            else:
                GRID_COLOR = (50, 50, 50)  # Couleur grise pour la grille
                print("Affichage de la grille désactivé.")
        
        else:
            print("Commande inconnue.")

# Thread pour écouter les commandes du terminal
command_thread = threading.Thread(target=command_listener, daemon=True)
command_thread.start()

# Fonction pour dessiner la grille
def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            color = ALIVE_COLOR if grid[y][x] == 1 else DEAD_COLOR
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Dessiner les lignes de la grille
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

def get_neighbors(x, y):
    neighbors = [
        (-1, -1), (0, -1), (1, -1),
        (-1, 0),           (1, 0),
        (-1, 1), (0, 1), (1, 1)
    ]
    live_neighbors = 0
    for dx, dy in neighbors:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            live_neighbors += grid[ny][nx]
    return live_neighbors

def update_grid():
    global grid
    new_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLS):
            live_neighbors = get_neighbors(x, y)
            if grid[y][x] == 1:
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[y][x] = 0
                else:
                    new_grid[y][x] = 1
            elif grid[y][x] == 0 and live_neighbors == 3:
                new_grid[y][x] = 1
    grid = new_grid

# Boucle principale du jeu
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mettre à jour la grille
    if FPS != 0:
        update_grid()

    # Mise à jour du RPC
    update_rich_presence()

    pygame.display.flip()
    clock.tick(FPS)

rpc.close()  # Ferme la connexion RPC lors de la sortie
pygame.quit()
