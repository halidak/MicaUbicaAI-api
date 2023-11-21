import copy
import random
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .positions.allowed_moves import allowed_moves
from .positions.mills_positions import mills_positions
from .positions.all_positions import all_positions

mills = {'human': [], 'computer': []}

@csrf_exempt
@api_view(['Get'])
def reset_game(request):
    global mills
    mills = {'human': [], 'computer': []}
    return Response(mills)

@csrf_exempt
@api_view(['Post'])
def your_view_function(request):
    global mills
    if request.method == 'POST':
        data = json.loads(request.body)
        humanStones = data.get('humanStones')
        computerStones = data.get('computerStones')
        totalPlacedStones2 = data.get('totalPlacedStones2')
        totalPlacedStones1 = data.get('totalPlacedStones1')
        player = data.get('nextPlayer')
        whitePlayerStonesOut = data.get('whitePlayerStonesOut')
        blackPlayerStonesOut = data.get('blackPlayerStonesOut')
        print("PLAYER", player)
        allMills = data.get('allMills')
        
        board = {
            'currentState': {
                'humanStones': humanStones,
                'computerStones': computerStones
            },
            'pending': {
                'human': totalPlacedStones1,
                'computer': totalPlacedStones2,
            },
            'out': {
                'human': whitePlayerStonesOut,
                'computer': blackPlayerStonesOut,
            },
            'lastMill': {
                'human': allMills,
                'computer': mills['computer']
            }
        }

        board = make_best_move(board, 'computer', mills)
        board = can_remove(board, 'computer', mills)
        new_stones = board['currentState']['computerStones']
        allBlack = board['lastMill']['computer']
        humanStones2 = board['currentState']['humanStones']
        
        # computerStones.append(new_stone)
        # available_positions = find_available_position(board, player)
        # print(available_positions)

        isMills = check_for_mill(board, "computer")

        print("LAST MILL", board['lastMill'])

        #decrement setTotalPlacedStones2 but if its > 0 and not None
        if totalPlacedStones2 is not None and totalPlacedStones2 > 0:
            totalPlacedStones2 = totalPlacedStones2 - 1
        #else return old value
        else:
            totalPlacedStones2 = totalPlacedStones2

        if isMills is True:
            found_mill = find_mill(board, 'computer')
        else:
            found_mill = None


        response_data = {
            'humanStones': humanStones2,
            'computerStones': new_stones,
            # 'availablePositions': available_positions,
            'totalPlacedStones2': totalPlacedStones2,
            'allowed_moves': allowed_moves,
            'isComputerMills': isMills,
            'found_mill': found_mill,
            'bestMove': new_stones,
            'nextPlayer': player,
            'whitePlayerStonesOut': board['out']['human'],
            'board': board,
            'computerMills': mills['computer']
        }

        print(board)
        print("beli", totalPlacedStones1)
        print("crni", totalPlacedStones2)
        return Response(response_data)
    

def game_over(board):
    # Check if a player cannot make a valid move
    # if len(find_available_position(board, 'human')) == 0 or len(find_available_position(board, 'computer')) == 0:
    #     return True

    # Check if a player has less than three pieces on the board
    if board['out']['human'] == 7 or board['out']['computer'] == 7:
        return True

    return False


def potential_mills(board, move, player):
    color = 'white' if player == 'human' else 'black'

    # Izvlačimo kamenčiće trenutnog igrača
    player_stones = board['currentState']['humanStones'] if color == 'white' else board['currentState']['computerStones']

    # Dodajemo potez u listu kamenčića igrača da bismo proverili da li stvara mlin
    player_stones.append(move)

    # Proveravamo da li potez stvara mlin
    for mill in mills_positions:
        # Proveravamo da li igrač ima tri kamena u mlinu
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones) for position in mill) == 3:
            # Uklanjamo potez iz liste kamenčića igrača jer je ovo samo privremena provera
            player_stones.remove(move)
            return True

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
        if len(board['currentState']['humanStones']) == 3 and selectedStone is not None:
            return  find_avaliable_if_tree(board['currentState']['computerStones'], board['currentState']['humanStones'], selectedStone)
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
        if len(board['currentState']['humanStones']) == 3 and selectedStone is not None:
            return  find_avaliable_if_tree(board['currentState']['computerStones'], board['currentState']['humanStones'], selectedStone)
        else:
            return find_available_moves(board, selectedStone)


#nalazenje slobodnih poteza za pomeranje kamencica
def find_available_moves(board, selectedStone):
    print("Selected Stone:", selectedStone)
    available_moves = []

    humanStones = board['currentState']['humanStones']
    computerStones = board['currentState']['computerStones']

    # Check if the selected stone is in one of the arrays
    isHumanStone = any(stone['square'] == selectedStone['square'] and stone['index'] == selectedStone['index'] for stone in humanStones)
    isComputerStone = any(stone['square'] == selectedStone['square'] and stone['index'] == selectedStone['index'] for stone in computerStones)

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
                print("AVa", available_moves)
            else:
                print(f"Move {move_position} is occupied")

    return available_moves


#test
# board = {
#     'currentState': {
#         'humanStones': [{'square': 2, 'index': 6, 'color': 'black'}, {'square': 0, 'index': 7, 'color': 'black'}, {'square': 2, 'index': 8, 'color': 'black'}],
#         'computerStones': [{'square': 0, 'index': 0, 'color': 'white'}, {'square': 0, 'index': 1, 'color': 'white'}, {'square': 0, 'index': 2, 'color': 'white'}]
#     },
#     'pending': {
#         'human': 0,
#         'computer': 0,
#     },
#     'out': {
#         'human': 0,
#         'computer': 0,
#     }
# }
# stone = {'square': 0, 'index': 2, 'color': 'white'}
# print("Avaliable", find_available_moves(board, stone))

#avaliable moves ako je ostalo 3 kamencica
def find_avaliable_if_tree(computerStones, humanStones):
    available_positions = []
      # Prođemo kroz sve pozicije
    for position in all_positions:
        # Proverimo da li je pozicija slobodna
        if position not in computerStones and position not in humanStones:
            # Ako je slobodna, dodamo je u listu dostupnih pozicija
            available_positions.append(position)

    return available_positions

#isMills
#check for the mill from mills_positions if im sending [{'square': 2, 'index': 6, 'color': 'black'}]
def check_for_mill(board, player):
    global all_mills
    # check for each player is mills
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
                return True
    return False 

def check_for_mill2(board, player):
    global mills
    # check for each player is mills
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                 for stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
            return True
    return False

def check_for_mill3(board, player, mills):
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

def find_mill(board, player):
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in board['currentState']['computerStones']) for position in mill) == 3:
            return mill 
    return None  


def check_stone_in_mill(board, stone, player):
    # check if the stone is in a mill
    opponent_stones = board['currentState']['computerStones'] if player == 'human' else board['currentState']['humanStones']
    for mill in mills_positions:
        # Check if all positions in the mill are occupied by the opponent's stones
        if all(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in opponent_stones) 
                   for position in mill):
            # Check if the stone being checked is in this mill
            if any(stone['square'] == position['square'] and stone['index'] == position['index'] for position in mill):
                return True
    return False
    
#metoda za izbacivanje stones
def remove_random_stone(board, player):
    new_board = copy.deepcopy(board)
    opponent_stones = new_board['currentState']['computerStones'] if player == 'human' else new_board['currentState']['humanStones']

    # Find all opponent stones that are not in a mill
    non_mill_stones = [stone for stone in opponent_stones if not check_stone_in_mill(new_board, stone, player)]
    print(f"Non-mill stones: {non_mill_stones}")

    if non_mill_stones:
        # Remove a random stone that is not in a mill
        stone_to_remove = random.choice(non_mill_stones)
        print(f"Removing stone: {stone_to_remove}")
        opponent_stones.remove(stone_to_remove)
        new_board['out']['human'] += 1
    else:
        print("All stones are in a mill. No stone was removed.")

    return new_board

#move stone
def move_stone(board, stone, new_position, player):
    # print(f"move_stone: board={board}, stone={stone}, new_position={new_position}")

    new_board = copy.deepcopy(board)
    stones = new_board['currentState'].get(f'{player}Stones')

    if stones is None:
        print(f"move_stone: {player}Stones is None")
        return new_board

    # stone_in_mill = any(stone_in_mill(stone, mill) for mill in mills[player])

    for s in stones:
        if s == stone:  # if the stone is the one we want to move
            s['square'] = new_position['square']  # update the square
            s['index'] = new_position['index']  # update the index

            # if stone_in_mill:
            #     mills[player].remove(stone_in_mill)

            # break ne znam trebal tu

    return new_board

def make_move(board, move, player, mills):
    # print("Before move:", move)
    new_board = copy.deepcopy(board)
    if board['pending'][f'{player}'] > 0:
        if player == 'human':
            new_board['currentState']['humanStones'].append(move)
        else: # player == 'computer'
            new_board['currentState']['computerStones'].append(move)
    else: 
        new_board = move_stone(new_board, move[0], move[1], player)
    return new_board



def can_remove(new_board, player, mills):
    if check_for_mill3(new_board, player, mills):
        return remove_random_stone(new_board, player)
    return new_board


def minimax2(board, depth, player, mills, stone = None):
    if game_over(board) or depth == 0:
        score = evaluate_board(board, player, stone)
        return score, None

    if player == 'computer':
        best_value = float("-inf")
        best_move = None

        print(f"Pending stones for {player}: {board['pending'][f'{player}']}")
        stones = board['currentState'][f'{player}Stones']

        if board['pending'][f'{player}'] > 0:
            possible_moves = find_available_position(board, player, None)

            for move in possible_moves:
                new_board = make_move(copy.deepcopy(board), move, player, mills)
                value, _ = minimax2(new_board, depth - 1, 'human', mills)

                if value > best_value:
                    best_value = value
                    best_move = move
        else:
            print(f"Stones: {stones}")
            for stone in stones:
                possible_moves = find_available_position(board, player, stone)
                if not possible_moves:
                    print(f"No possible moves for stone {stone}")
                    continue
                for move in possible_moves:
                    new_board = make_move(copy.deepcopy(board), (stone, move), player, mills)
                    value, _ = minimax2(new_board, depth - 1, 'human', mills, stone)

                    if value > best_value:
                        best_value = value
                        best_move = (stone, move)
                    else:
                        print(f"Move {move} does not improve best value {best_value}")

            if best_move is None:
                print("No move improved the best value")

        return best_value, best_move

    else:
        best_value = float("inf")
        best_move = None
        stones = board['currentState'][f'{player}Stones']

        if board['pending'][f'{player}'] > 0:
            possible_moves = find_available_position(board, player, None)
            

            for move in possible_moves:
                new_board = make_move(copy.deepcopy(board), move, player, mills)
                value, _ = minimax2(new_board, depth - 1, 'computer', mills)

                if value < best_value:
                    best_value = value
                    best_move = move
        else:
            for stone in stones:
                print(stone)
                possible_moves = find_available_position(board, player, stone)
                if not possible_moves:
                    print(f"No possible moves for stone {stone}")
                    continue
                for move in possible_moves:
                    new_board = make_move(copy.deepcopy(board), (stone, move), player, mills)
                    value, _ = minimax2(new_board, depth - 1, 'computer', mills, stone)

                    if value < best_value:
                        best_value = value
                        best_move = (stone, move)

        return best_value, best_move
    
def make_best_move(board, player, mills):
    best_score, best_move = minimax2(board, 2, player, mills)
    print(best_move)
    print(best_score)

    if best_move:
        print("Executing the best move.", best_move)
        return make_move(board, best_move, player, mills)

    # If no best move is found, place a stone randomly
    available_positions = find_available_position(board, player)
    if available_positions:
        move = random.choice(available_positions)
        return make_move(board, move, player, mills)

    return None

def evaluate_board(board, player, selectedStone = None):
    opponent = 'human' if player == 'computer' else 'computer'

    # Count the number of pieces for the current player and the opponent
    player_pieces = len(board['currentState'][f'{player}Stones'])
    opponent_pieces = len(board['currentState'][f'{opponent}Stones'])

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
    player_pieces_in_mills = sum(1 for move in find_available_position(board, player, selectedStone) if potential_mill(board, move, player))
    opponent_pieces_in_mills = sum(1 for move in find_available_position(board, opponent, selectedStone) if potential_mill(board, move, opponent))

    # Evaluate the board based on the above factors
    score = (player_pieces + 3 * player_mills + 2 * player_potential_mills + player_pieces_in_mills) - (opponent_pieces + 3 * opponent_mills + 2 * opponent_potential_mills + opponent_pieces_in_mills)
    return score

def potential_mill(board, move, player):
    color = 'white' if player == 'human' else 'black'

    if board['pending'][player] > 0:
    # Make a copy of the board with the potential move
        new_board = copy.deepcopy(board)
        new_board['currentState'][f'{player}Stones'].append(move)

        # Check if the move creates a mill
        for mill in mills_positions:
            # Check if the player has three stones in the potential mill
            if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                    for stone in new_board['currentState'][f'{player}Stones']) for position in mill) == 3:
                return True
    else:
        # Make a copy of the board with the potential move
        new_board = copy.deepcopy(board)
        new_board = move_stone(new_board, move[0], move[1], player)

        # Check if the move creates a mill
        for mill in mills_positions:
            # Check if the player has three stones in the potential mill
            if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                    for stone in new_board['currentState'][f'{player}Stones']) for position in mill) == 3:
                return True

    return False
