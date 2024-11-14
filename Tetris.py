import pygame
import random


# initialiser Pygame et définir la fenêtre de jeu
width = 888
height = 720

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tetris")

# mettre en place les polices
font_mega = pygame.font.Font("ressources/retro_font.ttf", 44)
font = pygame.font.Font("ressources/retro_font.ttf", 20)
font_legend = pygame.font.Font("ressources/retro_font.ttf", 12)

# Charger les images
background_img = pygame.image.load("ressources/TetrisBackground.png")
sprite_sheet = pygame.image.load("ressources/Blocks.png").convert_alpha()

# Dimensions des cellules
CELL_SIZE = 24
MINI_CELL_SIZE = 20

# Listes pour les images
blocks_img = []
transparent_blocks_img = []
mini_blocks_img = []

# Découper les sprites
for i in range(7):
    x1 = i * CELL_SIZE
    x2 = i * MINI_CELL_SIZE
    
    # Image normale
    block = sprite_sheet.subsurface(pygame.Rect(x1, 0, CELL_SIZE, CELL_SIZE))
    blocks_img.append(block)
    
    # Image miniaturisée
    mini_block = pygame.transform.scale(block, (MINI_CELL_SIZE, MINI_CELL_SIZE))
    mini_blocks_img.append(mini_block)
    
    # Image transparente
    transparent_block = block.copy()  # Créer une copie pour ne pas modifier l'original
    transparent_block.set_alpha(90)  # Appliquer la transparence
    transparent_blocks_img.append(transparent_block)


# définir les pieces

T_shape = [[0,6,0],
           [6,6,6]]

L_shape = [[0,0,5],
           [5,5,5]]

J_shape = [[7,0,0],
           [7,7,7]]

O_shape = [[2, 2],
           [2, 2]]

I_shape = [[4, 4, 4, 4]]

S_shape = [[0,3,3],
           [3,3,0]]

Z_shape = [[1,1,0],
           [0,1,1]]
           

PIECES = [T_shape, L_shape, O_shape, J_shape, Z_shape, S_shape, I_shape]

# variables du modele
GRID_WIDTH = 10
GRID_HEIGHT = 22

score_per_line_cleared = [0,40,100,300,1200]
# table de rotation, pour modifier la position en fonction de la rotation effectuer par la piece.
kick_table = [[0,1],[1,-1],[-1,0],[0,0]]
kick_table_I = [[-1,2],[3,-4],[-4,5],[1,-1]]

# méthodes de génération des pieces
def generate_piece():
    return random.choice(PIECES)

def spawn_piece_pos(piece):

    if piece == I_shape:
        position = [1,3]
    elif piece == O_shape:
        position = [0, 4]
    else:
        position = [0,3]
        
    return position

# classe du model
class TetrisModel():
    def __init__(self):
        self.grid = [[0]*GRID_WIDTH for _ in range(GRID_HEIGHT)] # tableau de 10 par 22, 
        # (seuls les 20 premières lignes doivent être affichés, les 2 lignes supérieurs servent à l'apparition des formes)

        self.current_piece = generate_piece()
        self.current_position = spawn_piece_pos(self.current_piece)
        self.rotation = 0

        self.next_piece = generate_piece()
        self.holded_piece = None

        self.score = 0
        self.lines = 0
        self.level = 0
        self.game_over = False

        self.piece_echanged = False

    def fix_piece(self):
        for i, row in enumerate(self.current_piece):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_position[0] + i][self.current_position[1] + j] = cell
        self.is_game_over()
        if not self.game_over:
            self.current_piece = self.next_piece
            self.current_position = spawn_piece_pos(self.current_piece)
            self.next_piece = generate_piece()
            self.rotation = 0
            self.piece_echanged = False



    def clear_lines(self):
        line_cleared = 0
        for i, row in enumerate(self.grid):
            row_complete = True
            for cell in row:
                if not cell:
                    row_complete = False
            if row_complete:
                line_cleared += 1
                del self.grid[i]
                self.grid.insert(0,[0]*len(self.grid[0]))
        self.lines += line_cleared
        self.level = self.lines // 10
        self.score += score_per_line_cleared[line_cleared] * (self.level + 1)

    def hard_drop(self):
        while self.drop():
            pass # drop jusqu'a ce que la piece soit placé.

    # déplace la piece horizontalement 
    def move_horizontaly(self, direction):
        if direction == 'left':
            if self.is_position_valid([self.current_position[0], self.current_position[1] - 1], self.current_piece):
                self.current_position[1] -= 1
        else:
            if self.is_position_valid([self.current_position[0], self.current_position[1] + 1], self.current_piece):
                self.current_position[1] += 1

    # déplace la piece de une case vers le bas
    def drop(self):
        if self.is_position_valid([self.current_position[0] + 1, self.current_position[1]], self.current_piece):
            self.current_position[0] += 1
            return True
        else:
            self.fix_piece()
            return False
            

    def rotate_piece(self):
        if self.current_piece == O_shape:
            return # la piece carré ne tourne pas.
        
        kick_t = kick_table_I if self.current_position == I_shape else kick_table
        
        rotated_piece = [list(row) for row in zip(*self.current_piece[::-1])]
        new_position = [a + b for a, b in zip(self.current_position, kick_t[self.rotation])]

        if self.is_position_valid(new_position, rotated_piece):
            self.current_piece = rotated_piece
            self.current_position = new_position
            self.rotation = (self.rotation + 1)%4

    # vérifier que la position est valide pour savoir si l'on peut déplacer ou tourner la piece
    def is_position_valid(self, position, piece):
        for i, row in enumerate(piece):
            for j, cell in enumerate(row):
                if cell: # verifier que la case ne soit pas vide
                    x, y = position[0] + i, position[1] + j
                    if x < 0 or x >= len(self.grid) or y < 0 or y >= len(self.grid[0]) or self.grid[x][y]:
                        return False
        return True

    def hold(self):
        if self.piece_echanged == False:
            if self.holded_piece == None:
                self.holded_piece = self.current_piece
                self.current_piece = self.next_piece
                self.current_position = spawn_piece_pos(self.current_piece)
                self.next_piece = generate_piece()
                self.rotation = 0
                self.piece_echanged = True
            else:
                if self.is_position_valid(self.current_position, self.holded_piece):
                    self.current_piece, self.holded_piece = self.holded_piece, self.current_piece
                    self.rotation = 0
                    self.piece_echanged = True
    
    def is_game_over(self):
        for cell in self.grid[1]:  # Vérifie la deuxième ligne du haut
            if cell != 0:
                self.game_over = True
                return True
        return False
    
    def reset(self):
        self.grid = [[0]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current_piece = generate_piece()
        self.current_position = spawn_piece_pos(self.current_piece)
        self.rotation = 0

        self.next_piece = generate_piece()
        self.holded_piece = None

        self.score = 0
        self.lines = 0
        self.level = 0
        self.game_over = False

        self.piece_echanged = False

GRID_X = 215.5
GRID_Y = 97

def draw_grid(grid):
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if grid[i][j]:
                screen.blit(blocks_img[grid[i][j]-1], (GRID_X + j*CELL_SIZE, GRID_Y + i*CELL_SIZE))

def draw_current_piece(piece, position):
    for i, row in enumerate(piece):
        for j, cell in enumerate(row):
            if cell:
                grid_x_position = GRID_X + (position[1] + j)*CELL_SIZE
                grid_y_position = GRID_Y + (position[0] + i)*CELL_SIZE
                screen.blit(blocks_img[cell-1], ( grid_x_position, grid_y_position))

def draw_drop_pre(model):
    model_clone = TetrisModel()

    model_clone.grid = [row[:] for row in model.grid]  # Copier la grille
    model_clone.current_piece = model.current_piece
    model_clone.current_position = model.current_position[:]
    model_clone.rotation = model.rotation

    model_clone.hard_drop()

    clone_grid = model_clone.grid
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if clone_grid[i][j]:
                if clone_grid[i][j] != model.grid[i][j]:
                    screen.blit(transparent_blocks_img[clone_grid[i][j]-1], (GRID_X + j*CELL_SIZE, GRID_Y + i*CELL_SIZE))

def draw_holded_piece(piece):
    if not piece:
        return

    x = 52
    y = 139
    zone_width = 96
    zone_height = 123

    x_padding = (zone_width - len(piece[0])*MINI_CELL_SIZE) / 2
    y_padding = (zone_height - len(piece)*MINI_CELL_SIZE) / 2

    for i, row in enumerate(piece):
        for j, cell in enumerate(row):
            if cell:
                x_position = x + x_padding + j * MINI_CELL_SIZE
                y_position = y + y_padding + i * MINI_CELL_SIZE
                screen.blit(mini_blocks_img[cell-1], (x_position, y_position))

def draw_next_piece(piece):
    if not piece:
        return

    x = 524
    y = 139
    zone_width = 96
    zone_height = 123

    x_padding = (zone_width - len(piece[0])*MINI_CELL_SIZE) / 2
    y_padding = (zone_height - len(piece)*MINI_CELL_SIZE) / 2

    for i, row in enumerate(piece):
        for j, cell in enumerate(row):
            if cell:
                x_position = x + x_padding + j * MINI_CELL_SIZE
                y_position = y + y_padding + i * MINI_CELL_SIZE
                screen.blit(mini_blocks_img[cell-1], (x_position, y_position))

def draw_score(score, lines):
    x = 687
    y = 131
    zone_width = 159
    zone_height = 141
    x_center = x + zone_width/2

    score_text_surface = font.render("SCORE :",True,(255,255,255))
    score_text_surface_rect = score_text_surface.get_rect(center=(x_center,155))

    score_surface = font.render(str(score),True,(255,255,255))
    score_surface_rect = score_surface.get_rect(center=(x_center,180))

    line_text_surface = font.render("LINES :",True,(255,255,255))
    line_text_surface_rect = line_text_surface.get_rect(center=(x_center,225))

    line_surface = font.render(str(lines),True,(255,255,255))
    line_surface_rect = line_surface.get_rect(center=(x_center,250))

    screen.blit(score_text_surface, score_text_surface_rect)
    screen.blit(score_surface,score_surface_rect)
    screen.blit(line_text_surface, line_text_surface_rect)
    screen.blit(line_surface,line_surface_rect)

def draw_level(level):
    x = 209
    #y = 64
    zone_width = 255
    #zone_height = 39
    x_center = x + zone_width/2
    level_text_surface = font.render("LEVEL - "+str(level), True, (255,255,255))
    level_surface_rect = level_text_surface.get_rect(center=(x_center,83 ))

    screen.blit(level_text_surface, level_surface_rect)

def draw_AI_btn(app_state):
    x_center = pygame.Rect(73,521,54,54).centerx
    
    ai_text_surface = font.render("AI", True, (255,255,255))
    ai_surface_rect = ai_text_surface.get_rect(center=(x_center,540))

    if app_state == "human":
        enabled_text = "OFF"
    else:
        enabled_text = "ON"

    enabled_text_surface = font_legend.render(enabled_text, True, (255,255,255))
    enabled_surface_rect = enabled_text_surface.get_rect(center=(x_center,560))

    screen.blit(ai_text_surface,ai_surface_rect)
    screen.blit(enabled_text_surface,enabled_surface_rect)

def draw_game_over():
    overlay = pygame.Surface((GRID_WIDTH*CELL_SIZE,GRID_HEIGHT*CELL_SIZE), pygame.SRCALPHA)
    overlay.fill((0,0,0,200))

    rect_center = overlay.get_rect().center

    game_text_surface = font_mega.render("GAME", True, (255,255,255))
    game_surface_rect = game_text_surface.get_rect(center=(rect_center[0] + GRID_X, rect_center[1] + GRID_Y - 30))

    over_text_surface = font_mega.render("OVER", True, (255,255,255))
    over_surface_rect = over_text_surface.get_rect(center=(rect_center[0] + GRID_X, rect_center[1] + GRID_Y + 30))

    screen.blit(overlay,(GRID_X,GRID_Y))
    screen.blit(game_text_surface,game_surface_rect)
    screen.blit(over_text_surface,over_surface_rect)        



def on_reset_btn(mouse_pos):
    return 73 <= mouse_pos[0] <= 127 and 392 <= mouse_pos[1] <= 446

def on_AI_btn(mouse_pos):
    return 73 <= mouse_pos[0] <= 127 and 521 <= mouse_pos[1] <= 575


AI_actions = ["hold","hard_drop","drop","move_left","move_right","rotate"]

def random_move_AI(model):
    action = random.choice(AI_actions)
    if action == "hold":
        model.hold()
    elif action == "hard_drop":
        model.hard_drop()
    elif action == "drop":
        model.drop()
    elif action == "move_left":
        model.move_horizontaly("left")
    elif action == "move_right":
        model.move_horizontaly("right")
    else:
        model.rotate_piece()

model = TetrisModel()

app_state = "human"

# DROP INTERVAL est la constante de l'intervalle de temps entre chaque drop lorsque rien n'est touché
DROP_INTERVAL = 10

ai_drop_interval = DROP_INTERVAL
nb_AI_move_by_drop = 5
last_move_time = 0


# la variable drop interval, elle, est la variable qui change selon si l'utilisateur fais une action ou non.
drop_interval = DROP_INTERVAL
last_drop_time = 0


# Boucle principale du jeu
while True:
    actual_time = pygame.time.get_ticks()

    # detecte les touches cliquées et agit en conséquence 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and app_state == "human" and not model.game_over:
            if drop_interval < DROP_INTERVAL*2:
                drop_interval += 100 
            if event.key == pygame.K_LEFT:
                model.move_horizontaly('left')
            elif event.key == pygame.K_RIGHT:
                model.move_horizontaly('right')
            elif event.key == pygame.K_DOWN:
                model.drop()
                last_drop_time = actual_time
            elif event.key == pygame.K_SPACE:
                model.hard_drop()
                last_drop_time = actual_time
            elif event.key == pygame.K_UP:
                model.rotate_piece()
            elif event.key == pygame.K_c:
                model.hold()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if on_reset_btn(pygame.mouse.get_pos()):
                    model.reset()
                elif on_AI_btn(pygame.mouse.get_pos()):
                    if app_state == "AI" :
                        app_state = "human"
                    else:
                        app_state = "AI"
                    model.reset()

    if app_state == "AI":
        # demander à l'IA de choisir l'action
        if actual_time - last_drop_time >= DROP_INTERVAL // nb_AI_move_by_drop:
            random_move_AI(model)
            last_drop_time = actual_time

    # afficher les bloques puis l'image de fond
    screen.fill((0,0,0))
    draw_grid(model.grid)
    draw_drop_pre(model)
    draw_current_piece(model.current_piece, model.current_position)
    # si la partie est perdu, grisé la grille, et affiché game over
    if model.game_over:
        draw_game_over()

    screen.blit(background_img, (0,0))
    draw_next_piece(model.next_piece)
    draw_holded_piece(model.holded_piece)
    draw_score(model.score, model.lines)
    draw_level(model.level)
    draw_AI_btn(app_state)

    # descendre la piece toutes les intervalles de drop.
    if actual_time - last_drop_time >= drop_interval:
        model.drop()
        last_drop_time = actual_time
        drop_interval = DROP_INTERVAL
    
    # vider les lignes remplies après quelques temps pour laisser le bloque posé pendant quelques ticks (plus esthétique)
    if actual_time - last_drop_time >= DROP_INTERVAL/5:
        model.clear_lines()

    # mettre à jour l'affichage
    pygame.display.update()

