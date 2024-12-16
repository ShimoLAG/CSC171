import pygame, random

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

random.shuffle(EnemyLocations)
random.shuffle(PlayerLocations)

CapturedEnemy = []
CapturedPlayer = []
RevealedPlayerPieces = []  # Tracks revealed player pieces

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
    'General': {'wins': ['Bomb', 'Soldier', 'Flag'], 'loses': []},
    'Bomb': {'wins': ['Soldier', 'Flag'], 'loses': ['General']},
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
            if turn % 2 == 0:
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

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        new_pos = (position[0] + dx, position[1] + dy)
        if 0 <= new_pos[0] <= 3 and 0 <= new_pos[1] <= 3:
            if new_pos not in own_list:
                moves_list.append(new_pos)
    return moves_list

def resolve_combat(attacker, defender):
    if attacker == defender:
        return 'both'

    if attacker == 'Bomb' and defender != 'Flag':
        return 'attacker'

    if defender == 'Bomb' and attacker in ['General', 'Soldier']:
        return 'attacker'

    if attacker == 'General' and defender == 'Bomb':
        return 'defender'

    if defender == 'General' and attacker == 'Bomb':
        return 'attacker'

    if defender in combat_hierarchy[attacker]['wins']:
        return 'attacker'
    if defender in combat_hierarchy[attacker]['loses']:
        return 'defender'

    return None

def capture_logic(attacker_index, attacker_list, attacker_locations, defender_index, defender_list, defender_locations):
    global RevealedPlayerPieces

    result = resolve_combat(attacker_list[attacker_index], defender_list[defender_index])

    if result == 'attacker':
        captured_piece = defender_list[defender_index]
        RevealedPlayerPieces.append(captured_piece)  # Record the revealed piece
        captured_location = defender_locations[defender_index]
        del defender_list[defender_index]
        del defender_locations[defender_index]
        attacker_locations[attacker_index] = captured_location
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
        winner = check_win()
        if winner:
            print(f"{winner} wins!")
            pygame.quit()
            exit()
        return captured_piece

    elif result == 'both':
        captured_location = defender_locations[defender_index]
        del attacker_list[attacker_index]
        del attacker_locations[attacker_index]
        del defender_list[defender_index]
        del defender_locations[defender_index]
        winner = check_win()
        if winner:
            print(f"{winner} wins!")
            pygame.quit()
            exit()
        return None


def check_win():
    if 'Flag' not in Player and 'Flag' not in Enemy:
        print("It's a draw! Both flags are captured.")
        pygame.quit()
        exit()

    if 'Flag' not in Player:
        return "Enemy"
    if 'Flag' not in Enemy:
        return "Player"
    
    if len(Player) == 1 and 'Flag' in Player and len(Enemy) == 1 and 'Flag' in Enemy:
        print("It's a draw! Both flags are captured.")
        pygame.quit()
        exit() 

    if len(Player) == 1 and 'Flag' in Player:
        return "Enemy"

    if len(Enemy) == 1 and 'Flag' in Enemy:
        return "Player"

    return None

def evaluate_board():
    if 'Flag' not in Player:
        return float('inf')  # AI wins if player's flag is gone
    if 'Flag' not in Enemy:
        return float('-inf')  # Player wins if AI's flag is gone

    piece_values = {'General': 4, 'Soldier': 2, 'Bomb': 1, 'Flag': 10}
    player_strength = sum(piece_values.get(piece, 0) for piece in Player if piece in RevealedPlayerPieces)
    enemy_strength = sum(piece_values.get(piece, 0) for piece in Enemy if piece != 'Flag')

    # Handle hidden pieces as probabilities
    unrevealed_pieces = len(Player) - len(RevealedPlayerPieces)
    if unrevealed_pieces > 0:
        average_piece_value = sum(piece_values.values()) / len(piece_values)
        player_strength += unrevealed_pieces * average_piece_value

    # Proximity to flags
    ai_flag_pos = EnemyLocations[Enemy.index('Flag')]
    player_flag_pos = PlayerLocations[Player.index('Flag')]

    ai_proximity_to_player_flag = min(abs(loc[0] - player_flag_pos[0]) + abs(loc[1] - player_flag_pos[1])
                                      for loc in EnemyLocations)
    player_proximity_to_ai_flag = min(abs(loc[0] - ai_flag_pos[0]) + abs(loc[1] - ai_flag_pos[1])
                                      for loc in PlayerLocations)

    # Exposed flag penalties
    ai_flag_exposed = any(abs(loc[0] - ai_flag_pos[0]) + abs(loc[1] - ai_flag_pos[1]) <= 1 for loc in PlayerLocations)
    player_flag_exposed = any(abs(loc[0] - player_flag_pos[0]) + abs(loc[1] - player_flag_pos[1]) <= 1 for loc in EnemyLocations)

    # Center control bonus
    center_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    ai_center_control = sum(1 for loc in EnemyLocations if loc in center_positions)
    player_center_control = sum(1 for loc in PlayerLocations if loc in center_positions)

    score = (enemy_strength - player_strength) + \
            (5 * (ai_proximity_to_player_flag - player_proximity_to_ai_flag)) + \
            (-10 if ai_flag_exposed else 0) + (10 if player_flag_exposed else 0) + \
            (3 * (ai_center_control - player_center_control))

    return score



def minimax(depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or not Player or not Enemy:
        return evaluate_board()

    if maximizing_player:
        max_eval = float('-inf')
        for i in range(len(EnemyLocations)):
            moves = check_move(EnemyLocations[i], 'Enemy')
            for move in moves:
                original_pos = EnemyLocations[i]
                EnemyLocations[i] = move

                # Check if the move captures the player's flag
                if move in PlayerLocations and Player[PlayerLocations.index(move)] == 'Flag':
                    move_value = float('inf')  # Immediate win
                else:
                    move_value = minimax(depth - 1, False, alpha, beta)

                EnemyLocations[i] = original_pos
                max_eval = max(max_eval, move_value)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
        return max_eval
    else:
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
                if beta <= alpha:
                    break
        return min_eval

    
def enemy_turn():
    global turn
    best_score = float('-inf')
    best_move = None
    best_index = None

    for i in range(len(EnemyLocations)):
        moves = check_move(EnemyLocations[i], 'Enemy')
        for move in moves:
            original_pos = EnemyLocations[i]
            EnemyLocations[i] = move

            # Prioritize capturing the player's flag
            if move in PlayerLocations:
                target_index = PlayerLocations.index(move)
                target_piece = Player[target_index]
                if target_piece == 'Flag':
                    move_value = float('inf')  # Immediate win
                else:
                    move_value = minimax(3, False)  # Explore deeper
            else:
                # Handle proximity to flags dynamically
                move_value = minimax(3, False)

            EnemyLocations[i] = original_pos
            if move_value > best_score:
                best_score = move_value
                best_move = move
                best_index = i

    # Execute the best move
    if best_move and best_index is not None:
        if best_move in PlayerLocations:
            target_index = PlayerLocations.index(best_move)
            capture_logic(best_index, Enemy, EnemyLocations, target_index, Player, PlayerLocations)
        else:
            EnemyLocations[best_index] = best_move

    turn += 1




def player_turn_events():
    global selection, turn, ValidMoves

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            grid_pos = (x // 100, y // 100)

            if turn % 2 == 0:
                if selection == 100:
                    if grid_pos in PlayerLocations:
                        selection = PlayerLocations.index(grid_pos)
                        ValidMoves = check_move(grid_pos, 'Player')
                elif grid_pos in ValidMoves:
                    if grid_pos in EnemyLocations:
                        target_index = EnemyLocations.index(grid_pos)
                        capture_logic(selection, Player, PlayerLocations, target_index, Enemy, EnemyLocations)
                    else:
                        PlayerLocations[selection] = grid_pos

                    selection = 100
                    ValidMoves = []
                    turn += 1
                else:
                    selection = 100
                    ValidMoves = []


def main_game_loop():
    global turn
    running = True

    while running:
        Screen.fill('white')
        draw_board()
        draw_pieces()

        if turn % 2 == 0:
            player_turn_events()
        else:
            enemy_turn()

        pygame.display.flip()
        Timer.tick(Fps)


if __name__ == "__main__":
    main_game_loop()
