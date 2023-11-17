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
        
        board = {
            'currentState': {
                'humanStones': humanStones,
                'computerStones': computerStones
            },
            'pending': {
                'totalHuman': totalPlacedStones1,
                'totalComputer': totalPlacedStones2,
            },
            'out': {
                'totalHuman': whitePlayerStonesOut,
                'totalComputer': blackPlayerStonesOut,
            },
            'lastMill': mills
        }

        print(board)
        
        
        board = make_best_move(board, 'computer')
        board2 = make_best_move(board, 'computer')
        new_stones = board['currentState']['computerStones']
        allBlack = board['lastMill']['computer']
        humanStones2 = board['currentState']['humanStones']
        
        # computerStones.append(new_stone)
        available_positions = find_available_position(board, player)
        # print(available_positions)

        isMills = check_for_mill3(board, "computer")

        request.session['lastMill'] = board['lastMill']
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
            'availablePositions': available_positions,
            'totalPlacedStones2': totalPlacedStones2,
            'allowed_moves': allowed_moves,
            'isComputerMills': isMills,
            'found_mill': found_mill,
            'bestMove': new_stones,
            'nextPlayer': player,
            'whitePlayerStonesOut': board['out']['totalHuman'],
            'board': board2
        }


        return Response(response_data)
    

# #minimax algorithm
# def minimax(board, depth, player):
    
#     bestMove = float("-inf")
#     best = None

#     if depth == 0:
#         return bestMove

#     # global states_reached
#     # states_reached += 1
#     possible_configs = find_available_position(board, player)
#     print(possible_configs)
#     for move in possible_configs:
#         print("MOVES")
#         print(move)
#         score = getHeuristic(board, move,  player)
#         if bestMove < score:
#             bestMove = score 
#             best = move
#             print("BESTTTTT")
#             print(bestMove)
#             return best


# #     if depth != 0:
# #         possible_configs = find_available_position(board, player)

# # # za svaki od treba da nadjemo heuristiku, i da vratimo potez sa najvecom heuristikom
# #         for move in possible_configs:
# #             score = getHeuristic(board, move)
# #             if bestMove < score:
# #               bestMove = score 
# #             # currentMove = minimax(move, depth - 1, False, getHeuristic(board)) 
#     else:
#         return bestMove


def game_over(board):
    # Check if a player cannot make a valid move
    if len(find_available_position(board, 'human')) == 0 or len(find_available_position(board, 'computer')) == 0:
        return True

    # Check if a player has less than three pieces on the board
    if board['out']['totalHuman'] == 7 or board['out']['totalComputer'] == 7:
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

#can form mill with move
    


# find avaliable position za prvo dodavanje kamencica
def find_available_position(board, player):
    if player == 'human':
        if board['pending']['totalHuman'] > 0:
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
        if len(board['currentState']['humanStones']) == 3:
            return  find_avaliable_if_tree(board['currentState']['computerStones'], board['currentState']['humanStones'])
        else:
            return find_available_moves(board['currentState']['computerStones'], board['currentState']['humanStones'])
    
    else:
        if board['pending']['totalComputer'] > 0:
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
        if len(board['currentState']['humanStones']) == 3:
            return  find_avaliable_if_tree(board['currentState']['computerStones'], board['currentState']['humanStones'])
        else:
            return find_available_moves(board['currentState']['computerStones'], board['currentState']['humanStones'])


#nalazenje slobodnih poteza za pomeranje kamencica
def find_available_moves(humanStones, computerStones, selectedStone):
    available_moves = []

    # Proverite da li je izabrani kamen u jednom od niza
    isHumanStone = selectedStone in humanStones
    isComputerStone = selectedStone in computerStones

    if not isHumanStone and not isComputerStone:
        # Kamen nije pronađen u ni jednom od nizova
        return []

    # Izaberite odgovarajući niz na osnovu tipa kamena (human ili computer)
    stone_list = humanStones if isHumanStone else computerStones

    # Prođite kroz sve dozvoljene poteze za izabrani kamen
    for move in allowed_moves[selectedStone['square']][selectedStone['index']]:
        move_square = move['square']
        move_index = move['index']
        move_position = {'square': move_square, 'index': move_index}

        # Provera da li je pozicija zauzeta
        if move_position not in humanStones and move_position not in computerStones:
            available_moves.append(move_position)

    return available_moves

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

all_mills = {
    'human': [],
    'computer': []
}

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


def check_for_mill3(board, player):
    for mill in mills_positions:
        if sum(any(stone is not None and stone.get('square') == position.get('square') and stone.get('index') == position.get('index') 
                 for stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
            print("Mill detected")
            return True
    print("No mill detected")
    return False

def find_mill(board, player):
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in board['currentState']['computerStones']) for position in mill) == 3:
            return mill 
    return None  


#metoda za pomeranje stones na neki move
def move_stone(stones, selected_stone, new_stone):
    # Pravimo kopiju niza `stones` kako bismo zadržali originalni niz nepromenjen
    new_stones = stones.copy()

    # Pronađemo indeks odabranog kamena u nizu (ako postoji)
    index = next((i for i, stone in enumerate(new_stones) if stone == selected_stone), None)

    if index is not None:
        # Zamena odabranog kamena sa novim kamenom na istom indeksu
        new_stones[index] = new_stone

    return new_stones

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
    

def make_move(board, move, player):
    # print("Before move:", board)
    new_board = copy.deepcopy(board)
    if player == 'human':
        new_board['currentState']['humanStones'].append(move)
    else: # player == 'computer'
        new_board['currentState']['computerStones'].append(move)
        # print("After move:", board)
        if check_for_mill3(new_board, player):
            new_board = remove_random_stone(new_board, player)
            # print("NEW",new_board)
            
    return new_board


#metoda za izbacivanje stones
def remove_random_stone(board, player):
    global mills
    new_board = copy.deepcopy(board)
    opponent_stones = new_board['currentState']['computerStones'] if player == 'human' else new_board['currentState']['humanStones']

    # Pronađemo sve kamenove protivnika koji se ne nalaze u mlinu
    non_mill_stones = [stone for stone in opponent_stones if not check_stone_in_mill(new_board, stone, player)]
    print(f"Non-mill stones: {non_mill_stones}")

    if non_mill_stones:
        # Uklanjanje nasumičnog kamena protivnika koji se ne nalazi u mlinu
        stone_to_remove = random.choice(non_mill_stones)
        print(f"Removing stone: {stone_to_remove}")
        opponent_stones.remove(stone_to_remove)
        new_board['out']['totalHuman'] += 1
    else:
        print("All stones are in a mill. No stone was removed.")

    return new_board

# def check_for_mill55(board, player):
#     for mill in mills_positions:
#         mill_positions = []
#         empty_positions = []

#         for position in mill:
#             square, index = position['square'], position['index']
#             stone = board['currentState'][player + 'Stones'][square][index]
#             if stone == player:
#                 mill_positions.append(position)
#             elif stone == ' ':
#                 empty_positions.append(position)

#         if len(mill_positions) == 2 and len(empty_positions) == 1:
#             return empty_positions[0]  # Return the position that can form a mill

#     return None  # No potential mill found

def check_mills55(board, player):
    player_stones = board['currentState'][f'{player}Stones']
    opponent_stones = board['currentState']['humanStones'] if player == 'computer' else board['currentState']['computerStones']
    
    # Provera da li ima najmanje 2 kamena pre nego što proveri mlin
    if len(player_stones) < 2:
        print(f"Not enough stones for {player} to form a mill.")
        return None  # Nije moguće formirati mlin sa manje od 2 kamena

    for mill in mills_positions:
        mill_positions = []
        empty_positions = []

        for position in mill:
            if position in player_stones:
                mill_positions.append(position)
            elif position in opponent_stones:
                # If the position is occupied by an opponent's stone, it's not a valid mill position
                return None
            elif position not in opponent_stones and position not in player_stones:
                empty_positions.append(position)

        print(f"Checking mill: {mill}")
        print(f"Player stones in mill: {mill_positions}")
        print(f"Empty positions in mill: {empty_positions}")

        if len(mill_positions) == 2 and len(empty_positions) == 1:
            print(f"Mill positions: {mill_positions}, Empty positions: {empty_positions}")
            return empty_positions[0]  # Return the position that can form a mill

    print(f"No potential mills found for {player}.")
    return None  # No potential mill found


#TODO jos heuristika
def getHeuristic(board, player):
    mill = check_mills55(board, player)

    if mill is not None:
        print(f'{player.capitalize()} formed a mill at positions: {mill}')
        return 1000

    # # opponent_player = 'human' if player == 'computer' else 'computer'
    # # opponent_mill_positions = check_for_mill(board, opponent_player)

    # # if opponent_mill_positions is not None:
    # #     print(f'{opponent_player.capitalize()} formed a mill at positions: {opponent_mill_positions}')
    # #     return -1000  # A large negative value for losing the game

    return 100  
    # new_board = make_move(board, player)
    # if check_for_mill2(board, player): 
    #     return 350
    # return 100


def minimax2(board, depth, player):
    if game_over(board) or depth == 0:
        score = evaluate_board(board, player)
        return score, None

    if player == 'computer':
        best_value = float("-inf")
        best_move = None
        possible_moves = find_available_position(board, player)

        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), move, player)
            value, _ = minimax2(new_board, depth - 1, 'human')

            # # Check if the move resulted in forming a mill
            # if check_for_mill(new_board, player):
            #     value += 500  # Add a bonus for forming a mill

            if value > best_value:
                best_value = value
                best_move = move

        return best_value, best_move

    else:
        best_value = float("inf")
        best_move = None
        possible_moves = find_available_position(board, player)

        for move in possible_moves:
            new_board = make_move(copy.deepcopy(board), move, player)
            value, _ = minimax2(new_board, depth - 1, 'computer')

            # # Check if the move resulted in forming a mill
            # if check_for_mill(new_board, 'computer'):
            #     value -= 500  # Subtract a penalty for allowing the opponent to form a mill

            if value < best_value:
                best_value = value
                best_move = move

        return best_value, best_move

    
def make_best_move(board, player):
    best_score, best_move = minimax2(board, 2, player)
    print(best_score)

    if best_move:
        # if best_score == 1000:  # Mill opportunity
        #     # print("Mill opportunity. Placing a stone to form a mill.")
        #     updated_board = make_move(board, best_move, player)
        #     mill_position = check_mills55(updated_board, player)
        #     if mill_position:
        #         print(f"A mill was formed at position {mill_position}.")
        #         return updated_board
        #     else:
        #         # print("Unexpected: Mill was not formed.")
        #         return make_move(updated_board, best_move, player)
        # elif best_score == 100:  # No mill opportunity
        #     # print("No mill opportunity. Placing a stone randomly.")
        #     available_positions = find_available_position(board, player)
        #     if available_positions:
        #         move = random.choice(available_positions)
        #         return make_move(board, move, player)
        # else:
            print("Executing the best move.", best_move)
            return make_move(board, best_move, player)

    # If no best move is found, place a stone randomly
    available_positions = find_available_position(board, player)
    if available_positions:
        move = random.choice(available_positions)
        return make_move(board, move, player)

    return None

def evaluate_board(board, player):
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
    player_potential_mills = sum(1 for move in find_available_position(board, player) if potential_mill(board, move, player))
    opponent_potential_mills = sum(1 for move in find_available_position(board, opponent) if potential_mill(board, move, opponent))

    # Count the number of pieces in potential mills for the current player and the opponent
    player_pieces_in_mills = sum(1 for move in find_available_position(board, player) if potential_mill(board, move, player))
    opponent_pieces_in_mills = sum(1 for move in find_available_position(board, opponent) if potential_mill(board, move, opponent))

    # Evaluate the board based on the above factors
    score = (player_pieces + 2 * player_mills + player_potential_mills + player_pieces_in_mills) - (opponent_pieces + 2 * opponent_mills + opponent_potential_mills + opponent_pieces_in_mills)

    return score

def potential_mill(board, move, player):
    color = 'white' if player == 'human' else 'black'

    # Make a copy of the board with the potential move
    new_board = copy.deepcopy(board)
    new_board['currentState'][f'{player}Stones'].append(move)

    # Check if the move creates a mill
    for mill in mills_positions:
        # Check if the player has three stones in the potential mill
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in new_board['currentState'][f'{player}Stones']) for position in mill) == 3:
            return True

    return False


# def make_best_move(board, player):
#     best_score, best_move = minimax2(board, 3, player)
#     print(best_score)

#     # Ako postoji najbolji potez, pokušajte ga izvršiti
#     if best_move:
#         if best_score == 100:
#             print("No mill opportunity. Placing a stone randomly.")
#             # Inače, postavite kamen na nasumičnu poziciju
#             available_positions = find_available_position(board, player)
#             if available_positions:
#                 move = random.choice(available_positions)
#                 return make_move(board, move, player)
#         else:
#             # Inače, izvršite potez s najboljom heuristikom
#             print("Executing the best move.", best_move)
#             return make_move(board, best_move, player)

#     # Ako nema najboljeg poteza, postavite kamen na nasumičnu poziciju
#     available_positions = find_available_position(board, player)
#     if available_positions:
#         move = random.choice(available_positions)
#         return make_move(board, move, player)

#     return None


# # Example usage:
# board = {
#     'currentState': {
#         'humanStones': [ { 'square': 0, 'index': 7}, { 'square': 0, 'index': 5 }],  # Your humanStones list
#         'computerStones': [{ 'square': 1, 'index': 0 }, { 'square': 1, 'index': 1}, { 'square': 0, 'index':6 }, { 'square': 0, 'index': 7 }]  # Your computerStones list
#     },
    
# }  # Your board dictionary

# third_stone_position = check_mills55(board, 'computer')
# if third_stone_position:
#     print(f"A mill can be formed at position {third_stone_position}")
# else:
#     print("No mills can be formed.")
