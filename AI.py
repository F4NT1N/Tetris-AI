from Tetris import TetrisModel, GRID_HEIGHT, GRID_WIDTH, get_piece_name
import random

AI_actions = ["hold","hard_drop","drop","move_left","move_right","rotate"]


"""
les états de la Q-table seront, la rotation, la position horizontale, le type de la piece courante, 
ainsi qu'un tableau contenant les 2 lignes inférieurs à la piece courante, si dépassement de la grille, remplacer par des 1

les récompenses seront calculés de la manière suivante : 
    -100 par défaite
    -10 pour chaque trou bloqué créer dans la grille
    -1 pour chaque piece posée qui augmente la hauteur maximale de la grille
    +1 pour chaque piece posée qui n'augmente pas la hauteur maximale
    et en cas de lignes complétées, la récompense correspondra à l'augmentation du score.

Q-table = {états : récompenses par actions}
"""
Q_table = {}
model_clone = TetrisModel

# renvoie les récompenses pour chaque actions dans un état donné
def get_Q_table(state):
    if not Q_table.get(state, None):
        Q_table[state] = {key : 0 for key in AI_actions}
    return Q_table[state]
    

def get_reward(state, action):
    if state not in Q_table:
        get_Q_table(state)
    return Q_table[state][action]

# renvoie l'action a effectué en fonction de l'état et de la politique d'exploration epsilon 
# plus epsilon est haut plus la probabilité l'exploration est élevé
def choose_action(state, epsilon = 0.1):
    if random.random() < epsilon:
        return random.choice(AI_actions)
    else:
        actions = get_Q_table(state)
        max_reward = max(actions.values())
        best_actions = [action for action, reward in actions.items() if reward == max_reward]
        return random.choice(best_actions)

# simuler l'action grâce au model
def simulate_action(action, model):
    model_clone = model.clone()

    # simuler l'action, seul l'action drop et hard drop peuvent modifier le reward, sinon il sera à 0:
    if action == "hard_drop":
        model_clone.hard_drop()
    elif action == "drop":
        model_clone.drop()
    else :
        if action == "hold":
            model_clone.hold()
            
        elif action == "move_left":
            model_clone.move_horizontaly("left")
            
        elif action == "move_right":
            model_clone.move_horizontaly("right")
            
        else:
            model_clone.rotate_piece()
            

    # calculer le reward.
    reward = 0

    if model_clone.score > model.score :
        reward += model_clone.score - model.score
    if model_clone.game_over:
        reward -= 100
    
    max_height_clone = 21
    for i in range(GRID_HEIGHT):
        if any(j == 1 for j in model_clone.grid[i]):
            max_height_clone = i
    
    max_height = 21
    for i in range(GRID_HEIGHT):
        if any(j == 1 for j in model.grid[i]):
            max_height = i
    
    if max_height_clone > max_height:
        reward -= (max_height_clone - max_height) * 100
    else:
        reward += 1

    # nb_hole_clone = 0
    # for j in range(GRID_WIDTH):
    #     hole = False
    #     for i in reversed(range(GRID_HEIGHT)):
    #         if model_clone.grid[i][j] == 1 and hole == True:
    #             nb_hole_clone += 1
    #         else:
    #             hole = True

    # nb_hole = 0
    # for j in range(GRID_WIDTH):
    #     hole = False
    #     for i in reversed(range(GRID_HEIGHT)):
    #         if model.grid[i][j] == 1 and hole == True:
    #             nb_hole += 1
    #         else:
    #             hole = True
    
    # reward -= (nb_hole_clone - nb_hole) * 10

    return reward, create_state(model_clone)



# mettre à jour la table en utilisant l'équation de bellman, 
# le learning rate représente le multiplicateur de récompense, il est préférable de l'approcher de 0 dans un système stochastique comme le nôtre
# le discount factor (facteur d'actualisation) représente l'importance des prochaines récompenses.
def update_table(state, action, simulated_reward, next_state, learning_rate = 0.1, discount_factor = 0.2):
    # choix de l'action avec epsilon à 0 pour choisir la meilleur action dans l'état t+1
    estimate_reward = get_reward(next_state,choose_action(next_state, 0))
    Q_table[state][action] = (1-learning_rate) * get_reward(state,action) + learning_rate * (simulated_reward + discount_factor * estimate_reward)

def create_state(model):
    
    little_grid_pos = model.current_position[0] + len(model.current_piece)
    little_grid = [[1] * GRID_WIDTH if little_grid_pos == GRID_HEIGHT else model.grid[little_grid_pos], [1] * GRID_WIDTH if little_grid_pos + 1 >= GRID_HEIGHT else model.grid[little_grid_pos + 1]]
    for i in range(2):
        little_grid[i] = [1 if cell != 0 else 0 for cell in little_grid[i]]

    state = (
    model.rotation,
    model.current_position[1],
    get_piece_name(model.current_piece),
    tuple(tuple(row) for row in little_grid)
    )

    return state

def play(model, epsilon = 0.1):
    state = create_state(model)

    action = choose_action(state, epsilon)
    simulated_reward, next_state = simulate_action(action, model)
    update_table(state, action, simulated_reward, next_state)
    print(get_reward(state,action))

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