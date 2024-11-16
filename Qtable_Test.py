import pygame
import random

"""
Ce programme me servira à comprendre plus simplement les Q-table et le Q-learning
Il s'agira d'un mini jeu comportant un TAXI, un passager et une destination, le TAXI devra rammasser le passager puis le déposer à destination
"""

# -------------------------------------------- définition de la grille --------------------------------------------------------------
GRID_HEIGHT = 6
GRID_WIDTH = 6

grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

passenger_pos = [4,5]
destination = [0,0]
TAXI_pos = [0,5]
is_passenger_in = False
is_done = False

TAXI, PASSENGER, DESTINATION = 1, 2, 3

grid[TAXI_pos[0]][ TAXI_pos[1]] = TAXI # représenter le taxi sur la grille
grid[passenger_pos[0]][ passenger_pos[1]] = PASSENGER # représenter le passager sur la grille
grid[destination[0]][ destination[1]] = DESTINATION # représenter la destination sur la grille

def can_pick(taxi_pos, pass_pos):

    taxi_pos = tuple(taxi_pos)
    pass_pos = tuple(pass_pos)

    for i in (-1,1):
        if taxi_pos == (pass_pos[0] + i,pass_pos[1]):
            return True
        if taxi_pos == (pass_pos[0], pass_pos[1] + 1):
            return True
    return False

def drop():
    global is_done
    if TAXI_pos == destination:
        is_done = True
        return (-1,-1)
    for i in (-1,1):
        if  0 <= TAXI_pos[0] + i < GRID_HEIGHT:
            passenger_pos = [TAXI_pos[0] + i, TAXI_pos[1]]
    return passenger_pos

def play(action):
    global TAXI_pos, passenger_pos, is_passenger_in

    if action == "up":
        TAXI_pos[0] -= 1
    elif action == "down":
        TAXI_pos[0] += 1
    elif action == "right":
        TAXI_pos[1] += 1
    elif action == "left":
        TAXI_pos[1] -= 1
    elif action == "drop":
        if is_passenger_in:
            passenger_pos = drop()
            is_passenger_in = False
    elif action == "pick_up":
        if can_pick(TAXI_pos, passenger_pos):
            passenger_pos = [-1,-1]
            is_passenger_in = True

def update_grid(grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if TAXI_pos == [i,j]:
                grid[i][j] = TAXI
            elif passenger_pos == [i,j]:
                grid[i][j] = PASSENGER
            elif destination == [i,j]:
                grid[i][j] = DESTINATION
            else:
                grid[i][j] = 0
    return grid

def reset(grid):
    global passenger_pos, destination, TAXI_pos, is_passenger_in, is_done

    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    passenger_pos = [4,5]
    destination = [0,0]
    TAXI_pos = [0,5]
    is_passenger_in = False
    is_done = False

    grid[TAXI_pos[0]][ TAXI_pos[1]] = TAXI # représenter le taxi sur la grille
    grid[passenger_pos[0]][ passenger_pos[1]] = PASSENGER # représenter le passager sur la grille
    grid[destination[0]][ destination[1]] = DESTINATION # représenter la destination sur la grille

    return grid

# ------------------------------------------- creation de l'IA ----------------------------------------------------------------------
AI_actions = ["up","right","down","left","pick_up","drop"]

# renvoie les actions possibles en fonction d'un état donné
def possibles_actions(state):
    possibles_actions = AI_actions.copy()

    # state[0] correspond à la position du TAXI
    if state[0][0] == GRID_HEIGHT - 1 :
        possibles_actions.remove("down")
    if state[0][0] == 0:
        possibles_actions.remove("up")
    if state[0][1] == GRID_WIDTH - 1:
        possibles_actions.remove("right")
    if state[0][1] == 0:
        possibles_actions.remove("left")
    
    return possibles_actions

# Q-table {etat : {action : récompense}}
# les états seront un tuple contenant : la position du taxi et la position du passager, si le passager est dans le taxi sa position sera (-1,-1)
# pas besoin de donner la position de la destination, l'IA découvrira par elle même via les récompenses.
Q_table = {}

# renvoie les actions avec leur récompense possible dans un état donné
def get_Q_table(state):
    if not Q_table.get(state, None):
        Q_table[state] = {key : 0 for key in possibles_actions(state)}
    return Q_table[state]

# renvoie la récompense de la table en fonction de l'action réalisée dans un état donné
def get_reward(state, action):
    if state not in Q_table:
        get_Q_table(state)
    return Q_table[state][action]

# renvoie l'action a effectué en fonction de l'état et de la politique d'exploration epsilon 
# plus epsilon est haut plus la probabilité l'exploration est élevé
def choose_action(state, epsilon = 0.1):
    if random.random() < epsilon:
        return random.choice(possibles_actions(state))
    else:
        actions = get_Q_table(state)
        max_reward = max(actions.values())
        best_actions = [action for action, reward in actions.items() if reward == max_reward]
        return random.choice(best_actions)

# renvoie la récompense simulée d'une action dans un état donné 
def simulate_reward(state, action): 

    taxi_pos = state[0]

    reward = 0
    done = False
    # state[1] correspond à la position du passager, si c'est (-1,-1) alors le passager est dans le taxi
    if state[1] == (-1,-1):
        if action == "up":
            if destination == [taxi_pos[0] - 1,taxi_pos[1]]:
                pass
            else :
                reward -= 1
        elif action == "down":
            if destination == [taxi_pos[0] + 1,taxi_pos[1]]:
                pass
            else :
                reward -= 1
        elif action == "right":
            if destination == [taxi_pos[0],taxi_pos[1] + 1]:
                pass
            else :
                reward -= 1
        elif action == "left":
            if destination == [taxi_pos[0],taxi_pos[1] - 1]:
                pass
            else :
                reward -= 1
        elif action == "drop":
            if tuple(destination) == taxi_pos:
                reward += 100
                done = True
            else:
                reward -= 10
        else:
            reward -= 1
    # si le passager n'est pas ramassé, pour ramasser le passager le taxi doit être positionné à une case adjacente à celui ci.
    # si le taxi ecrase le passager la récompense est de -50
    else:
        if action == "up":
            if state[1] == [taxi_pos[0] - 1,taxi_pos[1]]:
                reward -= 50
            else :
                reward -= 1
        elif action == "down":
            if state[1] == [taxi_pos[0] + 1,taxi_pos[1]]:
                reward -= 50
            else :
                reward -= 1
        elif action == "right":
            if state[1] == [taxi_pos[0],taxi_pos[1] + 1]:
                reward -= 50
            else :
                reward -= 1
        elif action == "left":
            if state[1] == [taxi_pos[0],taxi_pos[1] - 1]:
                reward -= 50
            else :
                reward -= 1
        elif action == "pick_up":
            if can_pick(taxi_pos, state[1]):
                reward += 50
            else:
                reward -= 50
        else:
            reward -= 1
    
    return reward, done

# mettre à jour la table en utilisant l'équation de bellman, 
# le learning rate représente le multiplicateur de récompense, il est préférable de l'approcher de 0 dans un système stochastique comme le nôtre
# le discount factor (facteur d'actualisation) représente l'importance des prochaines récompenses.
def update_table(state, action, simulated_reward, next_state, done, learning_rate = 0.1, discount_factor = 0.2):
    if done:
        estimated_reward = 0
    else:
        # choix de l'action avec epsilon à 0 pour choisir la meilleur action dans l'état t+1
        estimated_reward = get_reward(next_state,choose_action(next_state, 0))

    Q_table[state][action] = get_reward(state,action) + learning_rate * (
        simulated_reward + discount_factor * estimated_reward - get_reward(state,action)
        )

# méthode permettant de créer l'état
def create_state():
    
    state = ((TAXI_pos[0], TAXI_pos[1]), (passenger_pos[0], passenger_pos[1]))

    return state

# méthode permettant d'effectuer une action dans un état donné 
# l'état n'est pas implicitement donné, car on a déjà accès aux données utilisées.
def play_and_train(epsilon, learning_rate, discount_factor):
    state = create_state()
    action = choose_action(state, epsilon)
    simulated_reward, done = simulate_reward(state, action)

    play(action)

    next_state = create_state()

    update_table(state, action, simulated_reward, next_state, done, learning_rate, discount_factor)

# ------------------------------------------- initialisation de pygame ---------------------------------------------------------------
width = 800
height = 600

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Taxi training")

cell_size = height // GRID_HEIGHT

TAXI_COLOR = (255,255,0)
PASSENGER_COLOR = (0,128,0)
DESTINATION_COLOR = (255,0,0)

play_interval = 1
last_move_time = 0
max_episode = 200
nb_episode = 0
max_move_by_ep = 100
nb_move = 0
epsilon = 0.1
# -------------------------------------------- création de l'application ------------------------------------------------------------

while True:
    actual_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill((200,200,200))

    # dessin de la grille
    for i, row in enumerate(grid): # i représente la ligne
        for j, cell in enumerate(row): # j représente la colonne
            rect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
            if cell == TAXI:
                pygame.draw.rect(screen, TAXI_COLOR, rect)
            elif cell == PASSENGER:
                pygame.draw.rect(screen, PASSENGER_COLOR, rect)
            elif cell == DESTINATION:
                pygame.draw.rect(screen, DESTINATION_COLOR, rect)
            else:
                pygame.draw.rect(screen, (255,255,255), rect) # case blanche si elle est vide
    
    if actual_time - last_move_time >= play_interval:
        last_move_time = actual_time
        play_and_train(epsilon, 1, 0.1)
        grid = update_grid(grid)
        nb_move += 1
    
    if nb_move == max_move_by_ep or is_done:
        print(nb_move)
        nb_move = 0
        nb_episode += 1
        grid = reset(grid)

    if nb_episode == max_episode:
        epsilon = 0
        play_interval = 150

    pygame.display.update()
