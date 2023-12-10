import copy
import random
import traceback
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .views import game_over, find_avaliable_if_tree, check_for_mill, check_stone_in_mill, move_stone, make_move, potential_mill, is_between_stones
from .positions.allowed_moves import allowed_moves
from .positions.mills_positions import mills_positions
from .positions.all_positions import all_positions


mills = {'human': [], 'computer': []}

board = {
        'currentState': {
            'humanStones': [],
            'computerStones': []
        },
        'pending': {
            'human': 9,
            'computer': 9,
        },
        'out': {
            'human': 0,
            'computer': 0,
        },
        'lastMill': {
            'human': mills['human'],
            'computer': mills['computer']
        },
        'level': 1,
        'last_moves_computer': [],
        'last_moves_human': [],
    }
    
@csrf_exempt
@api_view(['Get'])
def reset_gameComp(request):
    global mills, board, player
    mills = {'human': [], 'computer': []}
    board = {
        'currentState': {
            'humanStones': [],
            'computerStones': []
        },
        'pending': {
            'human': 9,
            'computer': 9,
        },
        'out': {
            'human': 0,
            'computer': 0,
        },
        'lastMill': {
            'human': mills['human'],
            'computer': mills['computer']
        },
        'level': 1,
        'last_moves_computer': [],
        'last_moves_human': [],
    }
    return Response(board)


@csrf_exempt
@api_view(['Post'])
def compVScomp(request):
    global mills, board
    if request.method == 'POST':
        data = json.loads(request.body)
        player = data.get('player')
        level = data.get('level')
        print("LEVEL", level) 
        
        board['level'] = level

        board = make_best_move(board, player, mills)
        board = can_remove2(board, player, mills)
        
        if player == 'computer' and board['pending']['computer'] > 0:
            board['pending']['computer'] -= 1
        elif player == 'human' and board['pending']['human'] > 0:
            board['pending']['human'] -= 1

        response_data = {
            'nextPlayer': player,
            'board': board,
            'level': level
        }

        # print(board)
        print("PLAYER", player)
        print("BELI", board['pending']['human'])
        print("CRNI", board['pending']['computer'])

        return Response(response_data)
    


def remove_random_stone(board, player):
    new_board = copy.deepcopy(board)
    if player == 'human':
        op = 'computer'
    else:
        op = 'human'
    opponent_stones = new_board['currentState']['computerStones'] if player == 'human' else new_board['currentState']['humanStones']

    non_mill_stones = [stone for stone in opponent_stones if not check_stone_in_mill(new_board, stone, player)]

    if non_mill_stones:
        stone_to_remove = random.choice(non_mill_stones)
        opponent_stones.remove(stone_to_remove)
        new_board['out'][op] += 1
    else:
        return board

    return new_board

def can_remove2(new_board, player, mills):
    if check_for_mill34(new_board, player, mills):
        return remove_random_stone(new_board, player)
    return new_board

def check_for_mill34(board, player, mills):
    for mill in mills_positions:
        if sum(any(stone is not None and stone.get('square') == position.get('square') and stone.get('index') == position.get('index') 
                 for stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
            if mill not in mills[player]:
                print("Mill detected")
                print("MILLS PRE ", mills)
                mills[player].append(mill)
                print("MILLS POSLE ", mills)
                return True
    print("No mill detected")
    return False

# find avaliable position za prvo dodavanje kamencica
def find_available_position(board, player, selectedStone = None):
    if player == 'human':
        if board['pending']['human'] > 0:
            occupied_positions = set()

            for stone in board['currentState']['humanStones'] + board['currentState']['computerStones']:
                occupied_positions.add((stone['square'], stone['index']))

            available_positions = []

            for position in all_positions:
                move_square = position['square']
                move_index = position['index']
                if (move_square, move_index) not in occupied_positions:
                    available_positions.append({'square': move_square, 'index': move_index})

            return available_positions
        # if len(board['currentState']['humanStones']) == 3 and selectedStone is not None:
        #     return  find_avaliable_if_tree(board, selectedStone)
        else:
            return find_available_moves(board, selectedStone)
    
    else:
        if board['pending']['computer'] > 0:
            occupied_positions = set()

            for stone in board['currentState']['humanStones'] + board['currentState']['computerStones']:
                occupied_positions.add((stone['square'], stone['index']))

            available_positions = []

            for position in all_positions:
                move_square = position['square']
                move_index = position['index']
                if (move_square, move_index) not in occupied_positions:
                    available_positions.append({'square': move_square, 'index': move_index})

            return available_positions
        # if len(board['currentState']['computerStones']) == 3 and selectedStone is not None:
        #     return  find_avaliable_if_tree(board, selectedStone)
        else:
            return find_available_moves(board, selectedStone)


#nalazenje slobodnih poteza za pomeranje kamencica
def find_available_moves(board, selectedStone):
    available_moves = []

    humanStones = board['currentState']['humanStones']
    computerStones = board['currentState']['computerStones']

    # Check if the selected stone is in one of the arrays
    isHumanStone = any(stone['square'] == selectedStone['square'] and stone['index'] == selectedStone['index'] for stone in board['currentState']['humanStones']) if selectedStone else False
    isComputerStone = any(stone['square'] == selectedStone['square'] and stone['index'] == selectedStone['index'] for stone in computerStones) if selectedStone else False

    if not isHumanStone and not isComputerStone:
        # The stone was not found in any of the arrays
        return []

    # Go through all the allowed moves for the selected stone
    if selectedStone['square'] in allowed_moves and selectedStone['index'] in allowed_moves[selectedStone['square']]:
        for move in allowed_moves[selectedStone['square']][selectedStone['index']]:
            move_square = move['square']
            move_index = move['index']
            move_position = {'square': move_square, 'index': move_index}

            # Check if the position is occupied
            if not any(stone['square'] == move_square and stone['index'] == move_index for stone in humanStones + computerStones):
                available_moves.append(move_position)

    return available_moves
    

def make_move(board, move, player, mills):
    # print("Before move:", move)
    new_board = copy.deepcopy(board)
    if board['pending'][f'{player}'] > 0:
        if player == 'human':
            new_board['currentState']['humanStones'].append(move)
        else: # player == 'computer'
            new_board['currentState']['computerStones'].append(move)
        if check_for_mill(board, player):
            remove_random_stone(board, player)
    else: 
        # print("Stone:", move[0])
        # print("New position:", move[1])
        new_board = move_stone(new_board, move[0], move[1], player)
        if check_for_mill(board, player):
            remove_random_stone(board, player)
    return new_board

def minimax2(board, depth, player, mills, alpha, beta, stone=None, destination=None):
    if game_over(board) or depth == 0:
        score = evaluate_board(board, player, stone, destination)
        return score, None

    if player == 'computer':
        best_value = float("-inf")
        best_move = None

        stones = board['currentState'][f'{player}Stones']

        if board['pending'][f'{player}'] > 0:
            possible_moves = find_available_position(board, player, None)

            for move in possible_moves:
                new_board = make_move(copy.deepcopy(board), move, player, mills)
                initial_value = evaluate_board(new_board, player, stone, move)
                value, _ = minimax2(new_board, depth - 1, 'human', mills, alpha, beta)

                value += initial_value

                if value > best_value:
                    best_value = value
                    best_move = move

                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break

        else:
            for stone in stones:
                if len(stones) == 3:
                    possible_moves = find_avaliable_if_tree(board)
                else:
                    possible_moves = find_available_position(board, player, stone)
                if not possible_moves:
                    # print(f"No possible moves for stone {stone}")
                    continue

                stone_best_move = None
                stone_best_value = float('-inf')

                for move in possible_moves:
                    new_board = make_move(copy.deepcopy(board), (stone, move), player, mills)
                    value, _ = minimax2(new_board, depth - 1, 'human', mills, alpha, beta, stone, move)

                    value += evaluate_board(new_board, player, stone, move)

                    if value > stone_best_value:
                        stone_best_value = value
                        stone_best_move = (stone, move)

                if stone_best_move is not None and stone_best_value > best_value:
                    best_value = stone_best_value
                    best_move = stone_best_move
                
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break

        return best_value, best_move

    else:
        best_value = float("inf")
        best_move = None
        stones = board['currentState'][f'{player}Stones']

        if board['pending'][f'{player}'] > 0:
            possible_moves = find_available_position(board, player, None)

            for move in possible_moves:
                new_board = make_move(copy.deepcopy(board), move, player, mills)
                initial_value = evaluate_board(new_board, player, stone, move)
                value, _ = minimax2(new_board, depth - 1, 'computer', mills, alpha, beta)

                value -= initial_value

                if value < best_value:
                    best_value = value
                    best_move = move

                beta = min(beta, best_value)
                if beta <= alpha:
                    break

        else:
            for stone in stones:
                if len(stones) == 3:
                    possible_moves = find_avaliable_if_tree(board)
                else:
                    possible_moves = find_available_position(board, player, stone)
                if not possible_moves:
                    # print(f"No possible moves for stone {stone}")
                    continue

                stone_best_move = None
                stone_best_value = float('inf')

                for move in possible_moves:
                    new_board = make_move(copy.deepcopy(board), (stone, move), player, mills)
                    value, _ = minimax2(new_board, depth - 1, 'computer', mills, alpha, beta, stone, move)

                    value -= evaluate_board(new_board, player, stone, move)

                    if value < stone_best_value:
                        stone_best_value = value
                        stone_best_move = (stone, move)
                    
                if stone_best_move is not None and stone_best_value < best_value:
                    best_value = stone_best_value
                    best_move = stone_best_move

                beta = min(beta, best_value)
                if alpha >= beta:
                    break

        return best_value, best_move
    
def make_best_move(board, player, mills):
    # print("Player",player)
    depth = 2
    if len(board['currentState'][f'{player}Stones']) == 3:
        depth -= 1
    elif board['pending'][player] == 0:
        depth += 1
    # elif board['level'] == 0:
    #     depth = 3
    else:
        depth = 2
        
    print("DUBINA", depth)
    alpha = float("-inf")
    beta = float("inf")
    # depth = 3
    # alpha = float("-inf")
    # beta = float("inf")
    best_score, best_move = minimax2(board, depth, player, mills, alpha, beta)
    print(best_move)
    print(best_score)

    if best_move:
        print("Executing the best move.", best_move)
        new_board = make_move(board, best_move, player, mills)

        # If a stone was moved, remove it from the mills
        if isinstance(best_move, tuple):  # Check if it's a tuple (stone, new_position)
            stone, new_position = best_move
            mills = remove_stone_from_mills(mills, stone, player)

        return new_board

    # If no best move is found, place a stone randomly
    available_positions = find_available_position(board, player)
    if available_positions:
        move = random.choice(available_positions)
        return make_move(board, move, player, mills)

    return None

def remove_stone_from_mills(mills, stone, player):
    new_mills = [mill for mill in mills[player] if not any(s['index'] == stone['index'] and s['square'] == stone['square'] for s in mill)]
    mills[player] = new_mills
    return mills


def evaluate_board(board, player, selectedStone = None, destination = None):
    score = 0
    opponent = 'human' if player == 'computer' else 'computer'

    # Broj figura na tabli
    player_pieces = len(board['currentState'][f'{player}Stones'])
    opponent_pieces = len(board['currentState'][f'{opponent}Stones'])

    level = board['level']
    
    if board['pending'][player] == 0:
        board['last_moves_' + player].append((selectedStone, destination))
        max_last_moves = 2
        board['last_moves_' + player] = board['last_moves_' + player][-max_last_moves:]
        if board['last_moves_' + player].count((selectedStone, destination)) > 1:
            score -= 100

    #easy level
    if level == 0:
       # Broj dostupnih poteza
        player_moves = find_available_position(board, player, selectedStone)
        opponent_moves = find_available_position(board, opponent, selectedStone)

        # Približavanje formiranju mlinova
        player_potential_mills = 0 

        score = player_pieces - opponent_pieces

        # Iterate over all possible moves for the player
        for move in player_moves:
            if potential_mill(board, move, player):
                player_potential_mills += 10
                score += 20  # Dodajte veću vrednost za formiranje mlinova
        
        # # Dodavanje težine za postavljanje figura između kamena
        # for move in player_moves:
        #     if is_between_stones(board, move, player):
        #         score += 1

        if board["pending"][player] == 0:
            if potential_mill(board, (selectedStone, destination), player):
                player_potential_mills += 50
                score += 50
        else: 
            player_potential_mills += sum(1 for move in find_available_position(board, player, selectedStone) if potential_mill(board, move, player))

        for move in opponent_moves:
            if is_between_stones(board, move, opponent):
                score -= 1

        # Dodavanje težine za približavanje formiranju mlinova
        score += player_potential_mills

        for stone1 in board['currentState']['computerStones']:
            for stone2 in board['currentState']['computerStones']:
                if stone1 != stone2:
                    distance = abs(stone1['square'] - stone2['square']) + abs(
                        stone1['index'] - stone2['index'])
                    if distance < 2:  # Adjust this value as needed
                        score -= 1
    elif level == 1:
       
        # Count the number of mills for the current player and the opponent
        player_mills = sum(1 for mill in mills_positions if all(
            any(stone['square'] == position['square'] and stone['index'] == position['index']
                for stone in board['currentState'][f'{player}Stones']) for position in mill))
        
        opponent_mills = sum(1 for mill in mills_positions if all(
            any(stone['square'] == position['square'] and stone['index'] == position['index']
                for stone in board['currentState'][f'{opponent}Stones']) for position in mill))

        # Count the number of potential mills for the current player and the opponent
        player_potential_mills = sum(1 for move in find_available_position(board, player, selectedStone) if potential_mill(board, move, player))
        opponent_potential_mills = sum(1 for move in find_available_position(board, opponent, selectedStone) if potential_mill(board, move, opponent))

        # Count the number of pieces in potential mills for the current player and the opponent
        player_pieces_in_mills = sum(1 for stone in board['currentState'][f'{player}Stones'] if any(potential_mill(board, (stone, move), player) for move in find_available_position(board, player, stone)))
        opponent_pieces_in_mills = sum(1 for stone in board['currentState'][f'{opponent}Stones'] if any(potential_mill(board, (stone, move), opponent) for move in find_available_position(board, opponent, stone)))

        if board["pending"][player] == 0:
            in_mill = any(all(stone['square'] == pos['square'] and stone['index'] == pos['index'] for stone in board['currentState'][f'{player}Stones'] for pos in position) for position in mills_positions)
            if in_mill:
                player_potential_mills += 1600
            if potential_mill(board, (selectedStone, destination), player):
                player_potential_mills += 1500
        
        if board['pending'][player] > 0:
            player_moves = len(find_available_position(board, player))
            opponent_moves = len(find_available_position(board, opponent))
        else:
            player_moves = 0
            opponent_moves = 0

        # Evaluate the board based on the above factors
        score = (3 * player_moves + 2.5 * player_mills + 2 * player_potential_mills + 1.5 * player_pieces_in_mills) - (3 * opponent_moves + 2 * opponent_mills + opponent_potential_mills + opponent_pieces_in_mills) 

    else:
           # Count the number of mills for the current player and the opponent
        player_mills = sum(1 for mill in mills_positions if all(
            any(stone['square'] == position['square'] and stone['index'] == position['index']
                for stone in board['currentState'][f'{player}Stones']) for position in mill))
        
        opponent_mills = sum(1 for mill in mills_positions if all(
            any(stone['square'] == position['square'] and stone['index'] == position['index']
                for stone in board['currentState'][f'{opponent}Stones']) for position in mill))

        # Count the number of potential mills for the current player and the opponent
        player_potential_mills = sum(1 for move in find_available_position(board, player, selectedStone) if potential_mill(board, move, player))
        opponent_potential_mills = sum(1 for move in find_available_position(board, opponent, selectedStone) if potential_mill(board, move, opponent))

        # Count the number of pieces in potential mills for the current player and the opponent -- POPRAVI OVO
        # player_pieces_in_mills = sum(1 for move in find_available_position(board, player, selectedStone) if potential_mill(board, move, player))
        # opponent_pieces_in_mills = sum(1 for move in find_available_position(board, opponent, selectedStone) if potential_mill(board, move, opponent))

        player_pieces_in_mills = sum(1 for stone in board['currentState'][f'{player}Stones'] if any(potential_mill(board, (stone, move), player) for move in find_available_position(board, player, stone)))
        opponent_pieces_in_mills = sum(1 for stone in board['currentState'][f'{opponent}Stones'] if any(potential_mill(board, (stone, move), opponent) for move in find_available_position(board, opponent, stone)))

        if board["pending"][player] == 0:
            if potential_mill(board, (selectedStone, destination), player):
                player_potential_mills += 150
            if potential_mill(board, (selectedStone, destination), opponent):
                player_potential_mills += 125 
        
        if board['pending'][player] > 0:
            player_moves = len(find_available_position(board, player))
            opponent_moves = len(find_available_position(board, opponent))
        else:
            player_moves = 0
            opponent_moves = 0
        
        player_stones_in_mills = sum(1 for stone in board['currentState'][f'{player}Stones'] if check_stone_in_mill(board, stone, player))
        opponent_stones_in_mills = sum(1 for stone in board['currentState'][f'{opponent}Stones'] if check_stone_in_mill(board, stone, opponent))

        # Evaluate the board based on the above factors
        score = (3 * player_moves + 2.5 * player_mills + 2 * player_potential_mills + player_pieces_in_mills - player_stones_in_mills) - (3 * opponent_moves + 2 * opponent_mills + opponent_potential_mills + opponent_pieces_in_mills - opponent_stones_in_mills)
    return score