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

lastMill = {
    'human': [],
    'computer': []
}
@csrf_exempt
@api_view(['Post'])
def your_view_function(request):
    global lastMill
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
            'lastMill': {
                'human': [],
                'computer': []
            }
        }

        # print(board)
        
        
        board = make_best_move(board, 'computer')
        new_stones = board['currentState']['computerStones']
        humanStones2 = board['currentState']['humanStones']
        # print("NOVI STONE", new_stone)
        # new_stone['color'] = 'black'
        # print(new_stone)
        stone = {
            'square': 1,
            'index': 2,
            'color': 'black'
        }
        # computerStones.append(new_stone)
        available_positions = find_available_position(board, player)
        # print(available_positions)

        isMills = check_for_mill(board, "computer")

        #decrement setTotalPlacedStones2 but if its > 0 and not None
        if totalPlacedStones2 is not None and totalPlacedStones2 > 0:
            totalPlacedStones2 = totalPlacedStones2 - 1
        #else return old value
        else:
            totalPlacedStones2 = totalPlacedStones2

        if isMills is True:
            found_mill = find_mill(board)
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
            'whitePlayerStonesOut': board['out']['totalHuman']
        }

        # print(computerStones)
        # print(response_data)

        return Response(response_data)
    

#minimax algorithm
def minimax(board, depth, player):
    
    bestMove = float("-inf")
    best = None

    if depth == 0:
        return bestMove

    # global states_reached
    # states_reached += 1
    possible_configs = find_available_position(board, player)
    print(possible_configs)
    for move in possible_configs:
        print("MOVES")
        print(move)
        score = heuristic(board, player)
        if bestMove < score:
            bestMove = score 
            best = move
            print("BESTTTTT")
            print(bestMove)
            return best


#     if depth != 0:
#         possible_configs = find_available_position(board, player)

# # za svaki od treba da nadjemo heuristiku, i da vratimo potez sa najvecom heuristikom
#         for move in possible_configs:
#             score = getHeuristic(board, move)
#             if bestMove < score:
#               bestMove = score 
#             # currentMove = minimax(move, depth - 1, False, getHeuristic(board)) 
    else:
        return bestMove




def game_over(board):
    # Check if a player cannot make a valid move
    if len(find_available_position(board, 'human')) == 0 or len(find_available_position(board, 'computer')) == 0:
        return True

    # Check if a player has less than three pieces on the board
    if board['out']['totalHuman'] == 7 or board['out']['totalComputer'] == 7:
        return True

    return False

def can_form_mill(board, player):
    player_color = 'black' if player == 'computer' else 'white'
    player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones) for position in mill) == 2:
            empty_positions = [position for position in mill if not any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones)]
            if empty_positions:
                return True

    return False

#TODO jos heuristika
def getHeuristic(board, move, player):
    # if opponent_can_form_mill(board, player): 
    #     return 350
    # if potentional_mills(board, move, player): 
    #     return 300
    # else: 
    #     return 100
    #     # return numberOfMoveablePiecesHeuristic(board, move, player)
    new_board = make_move(board, move, player)
    if check_for_mill2(new_board, player): 
        return 350
    return 100

def heuristic(board, player):
    # Weights for each factor
    weights = {
        'num_of_value': 10,
        'num_of_mills': 40,
        'blocked_mills': 30,
        'potential_mills': 50,
        'possible_moves': 10,
        'blocked_pieces': 10
    }

    # Calculate the score for each factor
    num_of_value_score = numOfValue(board, player) * weights['num_of_value']
    num_of_mills_score = numOfMills(board, player) * weights['num_of_mills']
    blocked_mills_score = count_blocked_mills(board, player) * weights['blocked_mills']
    potential_mills_score = count_potential_mills(board, player) * weights['potential_mills']
    possible_moves_score = count_possible_moves(board, player) * weights['possible_moves']
    blocked_pieces_score = count_blocked_pieces(board, player) * weights['blocked_pieces']

    # Sum up the scores to get the total score
    total_score = num_of_value_score + num_of_mills_score + blocked_mills_score + potential_mills_score + possible_moves_score + blocked_pieces_score

    return total_score

def opponent_can_form_mill(board, player):
    opponent_color = 'black' if player == 'human' else 'white'
    opponent_stones = board['currentState']['computerStones'] if player == 'human' else board['currentState']['humanStones']

    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones) for position in mill) == 2:
            empty_positions = [position for position in mill if not any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones)]
            if empty_positions:
                return True

    return False

#broj igraca
def numOfValue(board, player):
    if player == 'human':
        return len(board['currentState']['humanStones'])
    else:
        return len(board['currentState']['computerStones'])

#broj mlinova
def numOfMills(board, player):
    mills = 0

    playerStones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

    for mill in mills_positions:
        if all(position in playerStones for position in mill):
            mills += 1

    return mills

#broj blokiranih mlinova
def count_blocked_mills(board, player):
    blocked_mills = 0

    # Get the opponent's stones
    opponent_stones = board['currentState']['computerStones'] if player == 'human' else board['currentState']['humanStones']

    # Iterate over all possible mill positions
    for mill in mills_positions:
        # Check if the player has two pieces in this mill position
        player_pieces_in_mill = [position for position in mill if position in board['currentState'][player + 'Stones']]
        if len(player_pieces_in_mill) == 2:
            # Check if the remaining position is occupied by the opponent
            remaining_position = [position for position in mill if position not in player_pieces_in_mill][0]
            if remaining_position in opponent_stones:
                blocked_mills += 1

    return blocked_mills

#broj potencijalnih mlinova
def count_potential_mills(board, player):
    potential_mills = 0

    # Get the player's stones
    player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

    # Iterate over all possible mill positions
    for mill in mills_positions:
        # Check if the player has two pieces in this mill position and the third position is empty
        player_pieces_in_mill = [position for position in mill if position in player_stones]
        if len(player_pieces_in_mill) == 2:
            # Check if the remaining position is empty
            remaining_position = [position for position in mill if position not in player_pieces_in_mill][0]
            if remaining_position not in board['currentState']['humanStones'] and remaining_position not in board['currentState']['computerStones']:
                potential_mills += 1

    return potential_mills

#broj mogucih pomeranja
def count_possible_moves(board, player):
    # Get the available positions for the player
    available_positions = find_available_position(board, player)

    # The number of possible moves is the number of available positions
    return len(available_positions)

def count_blocked_pieces(board, player):
    blocked_pieces = 0

    # Get the player's stones
    player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

    # Iterate over all player's stones
    for stone in player_stones:
        # Get the available moves for this stone
        available_moves = find_available_moves(board['currentState']['humanStones'], board['currentState']['computerStones'], stone)
        # If there are no available moves, the stone is blocked
        if len(available_moves) == 0:
            blocked_pieces += 1

    return blocked_pieces

def check_if_mill_blocked(board, move, player):

    color = 'white' if player == 'human' else 'black'

    # Izvlačimo kamenčiće protivnika
    opponent_stones = board['currentState']['computerStones'] if color == 'white' else board['currentState']['humanStones']

    # Proveravamo da li bi potez blokirao mlin
    for mill in mills_positions:
        # Proveravamo da li protivnik ima dva kamena u mlinu i da li je treća pozicija prazna
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones) for position in mill) == 2 and any(position['square'] == move['square'] and position['index'] == move['index'] for position in mill):
            return True

    # Ako nije blokiran nijedan mlin, potez ne blokira mlin
    return False

def potentional_mills(board, move, player):
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

    # Uklanjamo potez iz liste kamenčića igrača jer je ovo samo privremena provera
    player_stones.remove(move)

    # Ako potez ne stvara mlin, vraćamo False
    return False

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

#isMills
#check for the mill from mills_positions if im sending [{'square': 2, 'index': 6, 'color': 'black'}]
def check_for_mill(board, player):
    # check for each player is mills
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for 
                   stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
          
                return True  
    return False



def check_for_mill2(board, player):
    # check for each player is mills
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for 
                   stone in board['currentState'][player + 'Stones']) for position in mill) == 3:
            return True
    return False

def find_mill(board):
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] 
                   for stone in board['currentState']['computerStones']) for position in mill) == 3:
            return mill 
    return None  


def determine_winner(board):
    if board['out']['totalHuman'] == 2:
        return "AI is the winner"
    elif board['out']['totalComputer'] == 2:
        return "Human is the winner"
    else:
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

#metoda za izbacivanje stones
def remove_random_stone(board, player):
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


def remove_random_stone2(board):
    # Pravimo kopiju niza `stones` kako bismo zadržali originalni niz nepromenjen
    new_board = copy.deepcopy(board)
    white_stones = new_board['currentState']['humanStones']

    # Uklanjanje nasumičnog kamena
    if white_stones:
        stone_to_remove = random.choice(white_stones)
        print(f"Removing stone: {stone_to_remove}")
        white_stones.remove(stone_to_remove)
        new_board['out']['totalHuman'] += 1

    return new_board


def make_move(board, move, player):
    new_board = copy.deepcopy(board)
    if player == 'human':
        new_board['currentState']['humanStones'].append(move)
    else: # player == 'computer'
        new_board['currentState']['computerStones'].append(move)
        print("Board pre", new_board['lastMill'][player])
        if check_for_mill(new_board, player):
            mill = find_mill(new_board)
            if mill not in new_board['lastMill']['computer']:
                new_board['lastMill']['computer'].append(mill)
                new_board = remove_random_stone(new_board, player)
                print("Board posle", new_board['lastMill'][player])
    return new_board

def minimax2(board, depth, player):
    if game_over(board) or depth == 0:
        return getHeuristic(board, None, player), None

    if player == 'computer':
        bestScore = float('-inf')
        bestMove = None
        for move in find_available_position(board, player):
            new_board = make_move(board, move, player)
            score = getHeuristic(new_board, move, player)
            if score > bestScore:
                bestScore = score
                bestMove = move
        return bestScore, bestMove
    else:  # Human player's turn
        bestScore = float('inf')
        bestMove = None
        for move in find_available_position(board, player):
            new_board = make_move(board, move, player)
            score = getHeuristic(new_board, move, player)
            if score < bestScore:
                bestScore = score
                bestMove = move
        return bestScore, bestMove
    
def make_best_move(board, player):
    best_score, best_move = minimax2(board, 5, player)
    print(best_score)

    # Ako postoji najbolji potez, pokušajte ga izvršiti
    if best_move:
        if best_score == 100:
            print("No mill opportunity. Placing a stone randomly.")
            # Inače, postavite kamen na nasumičnu poziciju
            available_positions = find_available_position(board, player)
            if available_positions:
                move = random.choice(available_positions)
                return make_move(board, move, player)
        else:
            # Inače, izvršite potez s najboljom heuristikom
            print("Executing the best move.", best_move)
            return make_move(board, best_move, player)

    # Ako nema najboljeg poteza, postavite kamen na nasumičnu poziciju
    available_positions = find_available_position(board, player)
    if available_positions:
        move = random.choice(available_positions)
        return make_move(board, move, player)

    return None
