import pygame

pygame.init()
Height = 700
Width = 600
Screen = pygame.display.set_mode([Width, Height])
pygame.display.set_caption("Game of Generals")
Font = pygame.font.Font('freesansbold.ttf', 20)
BigFont = pygame.font.Font('freesansbold.ttf', 20)
Timer = pygame.time.Clock()
Fps = 60

# Game variables and images
Enemy = ["General", "Bomb", "Flag", "Soldier"]
EnemyLocations = [(0, 0), (1, 0), (2, 0), (3, 0)]

Player = ["General", "Bomb", "Flag", "Soldier"]
PlayerLocations = [(0, 3), (1, 3), (2, 3), (3, 3)]

CapturedEnemy = []
CapturedPlayer = []

turn = 0
selection = 100
ValidMoves = []

# Load in-game pieces
# Enemy
EnemyGeneral = pygame.image.load('assets/EnemyGeneral.png')
EnemyGeneral = pygame.transform.scale(EnemyGeneral, (80, 80))

EnemyBomb = pygame.image.load('assets/EnemyBomb.png')
EnemyBomb = pygame.transform.scale(EnemyBomb, (80, 80))

EnemySoldier = pygame.image.load('assets/EnemySoldier.png')
EnemySoldier = pygame.transform.scale(EnemySoldier, (80, 80))

EnemyFlag = pygame.image.load('assets/EnemyFlag.png')
EnemyFlag = pygame.transform.scale(EnemyFlag, (80, 80))

# Player
PlayerGeneral = pygame.image.load('assets/PlayerGeneral.png')
PlayerGeneral = pygame.transform.scale(PlayerGeneral, (80, 80))

PlayerBomb = pygame.image.load('assets/PlayerBomb.png')
PlayerBomb = pygame.transform.scale(PlayerBomb, (80, 80))

PlayerSoldier = pygame.image.load('assets/PlayerSoldier.png')
PlayerSoldier = pygame.transform.scale(PlayerSoldier, (80, 80))

PlayerFlag = pygame.image.load('assets/PlayerFlag.png')
PlayerFlag = pygame.transform.scale(PlayerFlag, (80, 80))

# Hidden
Hidden = pygame.image.load('assets/Hidden.png')
Hidden = pygame.transform.scale(Hidden, (80, 80))

# Drawing
EnemyImages = [EnemyGeneral, EnemyBomb, EnemyFlag, EnemySoldier]
PlayerImages = [PlayerGeneral, PlayerBomb, PlayerFlag, PlayerSoldier]

piece_list = ['General', 'Bomb', 'Flag', 'Soldier']

combat_hierarchy = {
    'General': {'wins': ['Bomb', 'Soldier', 'Flag'], 'loses': []},  # General wins against Bomb
    'Bomb': {'wins': ['Soldier', 'Flag'], 'loses': ['General']},  # Bomb loses to General
    'Flag': {'wins': [], 'loses': ['General', 'Soldier', 'Bomb']},
    'Soldier': {'wins': ['Bomb', 'Flag'], 'loses': ['General']}
}


def draw_board():
    for i in range(16):
        column = i % 4
        row = i // 4
        x = column * 100
        y = row * 100
        pygame.draw.rect(Screen, 'light gray', [x, y, 100, 100])

    pygame.draw.rect(Screen, 'gray', [0, 400, 400, 100])
    pygame.draw.rect(Screen, 'gold', [0, 400, 400, 100], 5)
    pygame.draw.rect(Screen, 'gold', [400, 0, 200, Height], 5)

    status_text = ['Player: Select a Piece to Move!', 'Player: Select a Destination!',
                   'Enemy: Selecting a Piece to Move', 'Enemy: Selecting a Destination']
    Screen.blit(BigFont.render(status_text[turn % 2], True, 'black'), (60, 435))

    for i in range(5):
        pygame.draw.line(Screen, 'black', (0, 100 * i), (400, 100 * i), 2)
        pygame.draw.line(Screen, 'black', (100 * i, 0), (100 * i, 400), 2)

def draw_pieces():
    for i in range(len(Enemy)):
        if Enemy[i] in piece_list:
            index = piece_list.index(Enemy[i])
            if turn % 2 == 0:  # Player's turn
                Screen.blit(Hidden, (EnemyLocations[i][0] * 100 + 10, EnemyLocations[i][1] * 100 + 10))
            else:
                Screen.blit(EnemyImages[index], (EnemyLocations[i][0] * 100 + 10, EnemyLocations[i][1] * 100 + 10))

    for i in range(len(Player)):
        if Player[i] in piece_list:
            index = piece_list.index(Player[i])
            Screen.blit(PlayerImages[index], (PlayerLocations[i][0] * 100 + 10, PlayerLocations[i][1] * 100 + 10))

    for move in ValidMoves:
        pygame.draw.circle(Screen, 'blue', (move[0] * 100 + 50, move[1] * 100 + 50), 10)

def check_move(position, player):
    moves_list = []
    if player == 'Player':
        own_list = PlayerLocations
        enemy_list = EnemyLocations
    else:
        own_list = EnemyLocations
        enemy_list = PlayerLocations

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Down, Up, Right, Left
    for dx, dy in directions:
        new_pos = (position[0] + dx, position[1] + dy)
        if 0 <= new_pos[0] <= 3 and 0 <= new_pos[1] <= 3:
            if new_pos not in own_list:
                moves_list.append(new_pos)
    return moves_list

def resolve_combat(attacker, defender):
    # If both pieces are the same, it's a draw (both are removed)
    if attacker == defender:
        return 'both'

    # Bomb attacking (Bomb wins against General and Soldier, unless it's attacking Flag)
    if attacker == 'Bomb' and defender != 'Flag':
        return 'attacker'  # Bomb wins when attacking General or Soldier

    # Bomb defending (Bomb loses when attacked by General or Soldier)
    if defender == 'Bomb' and attacker in ['General', 'Soldier']:
        return 'attacker'  # Bomb loses when attacked by General or Soldier

    # General behavior: General defeats Bomb and Soldier, and can't be defeated by Bomb
    if attacker == 'General' and defender == 'Bomb':
        return 'defender'  # General loses to Bomb when attacking

    if defender == 'General' and attacker == 'Bomb':
        return 'attacker'  # Bomb wins when attacking General

    # Normal combat resolution for other pieces based on combat hierarchy
    if defender in combat_hierarchy[attacker]['wins']:
        return 'attacker'
    if defender in combat_hierarchy[attacker]['loses']:
        return 'defender'

    return None





def capture_logic(attacker_index, attacker_list, attacker_locations, defender_index, defender_list, defender_locations):
    result = resolve_combat(attacker_list[attacker_index], defender_list[defender_index])

    # Capture logic based on combat result
    if result == 'attacker':
        captured_piece = defender_list[defender_index]
        captured_location = defender_locations[defender_index]  # Store the defender's location
        del defender_list[defender_index]
        del defender_locations[defender_index]  # Ensure that we remove both piece and location
        attacker_locations[attacker_index] = captured_location  # Assign new location to attacker
        # Re-check for win condition
        winner = check_win()
        if winner:
            print(f"{winner} wins!")
            pygame.quit()
            exit()
        return captured_piece

    elif result == 'defender':
        captured_piece = attacker_list[attacker_index]
        del attacker_list[attacker_index]
        del attacker_locations[attacker_index]
        # Re-check for win condition
        winner = check_win()
        if winner:
            print(f"{winner} wins!")
            pygame.quit()
            exit()
        return captured_piece

    elif result == 'both':
        # Both pieces are removed
        captured_location = defender_locations[defender_index]  # Store location for attacker
        del attacker_list[attacker_index]
        del attacker_locations[attacker_index]
        del defender_list[defender_index]
        del defender_locations[defender_index]
        # Re-check for win condition
        winner = check_win()
        if winner:
            print(f"{winner} wins!")
            pygame.quit()
            exit()
        return None





def check_win():
    # If both the Player's and Enemy's flags are missing, it's a draw
    if 'Flag' not in Player and 'Flag' not in Enemy:
        print("It's a draw! Both flags are captured.")
        pygame.quit()
        exit()

    # If the Player's Flag is the only remaining piece
    if 'Flag' not in Player:
        return "Enemy"  # Player lost because their Flag is captured
    if 'Flag' not in Enemy:
        return "Player"  # Enemy lost because their Flag is captured

    # If the Player's only piece is the Flag, they lose
    if len(Player) == 1 and 'Flag' in Player:
        return "Enemy"  # Player loses if only the Flag is left

    # If the Enemy's only piece is the Flag, they lose
    if len(Enemy) == 1 and 'Flag' in Enemy:
        return "Player"  # Enemy loses if only the Flag is left

    return None  # No winner yet



def evaluate_board():
    # Check for win conditions first
    if 'Flag' not in Player:  # If Player's flag is missing, the Player lost
        return float('-inf')  # Prioritize Player losing (minimizing score)
    if 'Flag' not in Enemy:  # If Enemy's flag is missing, the Player won
        return float('inf')  # Prioritize Player winning (maximizing score)

    # If only the AI's flag is left, it's a losing state
    if len(Enemy) == 1 and 'Flag' in Enemy:
        return float('-inf')  # AI loses if only the Flag is left

    # If only the Player's flag is left, it's a losing state for the Player
    if len(Player) == 1 and 'Flag' in Player:
        return float('inf')  # Player loses if only the Flag is left

    # Piece values adjusted for AI strategy
    piece_values = {
        'General': 4,
        'Soldier': 2,
        'Bomb': 1,
        'Flag': 5  # Flag should have high priority in win conditions
    }

    # Evaluating Player and Enemy strength based on remaining pieces
    player_strength = sum(piece_values.get(piece, 0) for piece in Player if piece != 'Flag')
    enemy_strength = sum(piece_values.get(piece, 0) for piece in Enemy if piece != 'Flag')

    # Consider flag protection (the closer the enemy's flag is to being captured, the better for the AI)
    player_flag_distance = sum(1 for loc in PlayerLocations if Player[PlayerLocations.index(loc)] == 'Flag')
    enemy_flag_distance = sum(1 for loc in EnemyLocations if Enemy[EnemyLocations.index(loc)] == 'Flag')

    # Add additional penalties or rewards based on flag proximity or exposure
    if 'Flag' in Player:
        player_flag_distance = 0  # If the Player's flag is still in play, it doesn't add to the evaluation.

    if 'Flag' in Enemy:
        enemy_flag_distance = 0  # If the Enemy's flag is still in play, it doesn't add to the evaluation.

    # Adding a penalty for the player being left with only the flag
    if len(Player) == 1 and 'Flag' in Player:
        player_strength -= 100  # Strong penalty to avoid losing

    # Adding a penalty for the enemy being left with only the flag
    if len(Enemy) == 1 and 'Flag' in Enemy:
        enemy_strength -= 100  # Strong penalty to avoid losing

    return (player_strength - enemy_strength) + (player_flag_distance - enemy_flag_distance)





def minimax(depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or not Player or not Enemy:
        return evaluate_board()

    if maximizing_player:  # Enemy's turn (maximize score)
        max_eval = float('-inf')
        for i in range(len(EnemyLocations)):
            moves = check_move(EnemyLocations[i], 'Enemy')
            for move in moves:
                original_pos = EnemyLocations[i]
                EnemyLocations[i] = move

                # Check if the move directly targets the Player's Flag
                if move in PlayerLocations and Player[PlayerLocations.index(move)] == 'Flag':
                    move_value = float('inf')  # Prioritize capturing the Flag
                else:
                    move_value = minimax(depth - 1, False, alpha, beta)

                EnemyLocations[i] = original_pos

                max_eval = max(max_eval, move_value)
                alpha = max(alpha, max_eval)

                # Beta pruning
                if beta <= alpha:
                    break
        return max_eval

    else:  # Player's turn (minimize score)
        min_eval = float('inf')
        for i in range(len(PlayerLocations)):
            moves = check_move(PlayerLocations[i], 'Player')
            for move in moves:
                original_pos = PlayerLocations[i]
                PlayerLocations[i] = move
                eval = minimax(depth - 1, True, alpha, beta)
                PlayerLocations[i] = original_pos
                min_eval = min(min_eval, eval)
                beta = min(beta, min_eval)

                # Alpha pruning
                if beta <= alpha:
                    break
        return min_eval




def enemy_ai():
    global selection, ValidMoves, turn

    best_move = None
    best_value = float('-inf')

    for i in range(len(EnemyLocations)):
        moves = check_move(EnemyLocations[i], 'Enemy')
        for move in moves:
            original_pos = EnemyLocations[i]
            EnemyLocations[i] = move

            # Check if the move directly targets the Player's Flag
            if move in PlayerLocations and Player[PlayerLocations.index(move)] == 'Flag':
                move_value = float('inf')  # Prioritize capturing the Flag
            else:
                move_value = minimax(4, False, alpha=float('-inf'), beta=float('inf'))  # Adjust depth here

            EnemyLocations[i] = original_pos

            if move_value > best_value:
                best_value = move_value
                best_move = (i, move)

    if best_move:
        piece_index, move = best_move
        target_index = None

        if move in PlayerLocations:
            target_index = PlayerLocations.index(move)

        if target_index is not None:
            capture_logic(piece_index, Enemy, EnemyLocations, target_index, Player, PlayerLocations)
        else:
            EnemyLocations[piece_index] = move

    winner = check_win()
    if winner:
        print(f"{winner} wins!")
        pygame.quit()
        exit()

    turn += 1



Playeroptions = [check_move(loc, 'Player') for loc in PlayerLocations]
Enemyoptions = [check_move(loc, 'Enemy') for loc in EnemyLocations]

run = True
while run:
    Timer.tick(Fps)
    Screen.fill("dark grey")
    draw_board()
    draw_pieces()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x_coord = event.pos[0] // 100
            y_coord = event.pos[1] // 100
            click_coords = (x_coord, y_coord)

            if turn % 2 == 0:  # Player's turn
                if click_coords in PlayerLocations:
                    selection = PlayerLocations.index(click_coords) if check_move(click_coords, 'Player') else 100
                elif click_coords in ValidMoves and selection != 100:
                    target_index = None

                    if click_coords in EnemyLocations:
                        target_index = EnemyLocations.index(click_coords)

                    if target_index is not None:
                        capture_logic(selection, Player, PlayerLocations, target_index, Enemy, EnemyLocations)
                    else:
                        PlayerLocations[selection] = click_coords

                    # Check for win condition after Player's move
                    winner = check_win()
                    if winner:
                        print(f"{winner} wins!")
                        pygame.quit()
                        exit()

                    selection = 100
                    turn += 1

    if turn % 2 == 1:
        enemy_ai()
        Playeroptions = [check_move(loc, 'Player') for loc in PlayerLocations]
        Enemyoptions = [check_move(loc, 'Enemy') for loc in EnemyLocations]

    ValidMoves = check_move(PlayerLocations[selection], 'Player') if turn % 2 == 0 and 0 <= selection < len(PlayerLocations) else []
    pygame.display.flip()

pygame.quit()
