from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .positions.allowed_moves import allowed_moves
from .positions.mills_positions import mills_positions
from .positions.all_positions import all_positions


@csrf_exempt
@api_view(['Post'])
def your_view_function(request):
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
            }
        }

        print(board)
        
        new_stone = minimax(board, 3, 'computer')
        print(new_stone)
        stone = {
            'square': 1,
            'index': 4,
            'color': 'black'
        }
        computerStones.append(stone)
        available_positions = find_available_position(board, player)
        # print(available_positions)


        isMills = check_for_mill(board)

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
            'humanStones': humanStones,
            'computerStones': computerStones,
            'availablePositions': available_positions,
            'totalPlacedStones2': totalPlacedStones2,
            'allowed_moves': allowed_moves,
            'isComputerMills': isMills,
            'found_mill': found_mill,
            'bestMove': new_stone
        }

        print(computerStones)
        print(response_data)

        return Response(response_data)
    
#TODO
# def minimax(board, depth, player):
#     if depth == 0 or game_over(board):
#         return numberOfMoveablePiecesHeuristic(board, None, player)

#     if player == 'human':
#         maxEval = float('-inf')
#         for move in get_all_possible_moves(board, player):
#             evaluation = minimax(make_move(board, move, player), depth - 1, 'computer')
#             maxEval = max(maxEval, evaluation)
#         return maxEval
#     else:
#         minEval = float('inf')
#         for move in get_all_possible_moves(board, player):
#             evaluation = minimax(make_move(board, move, player), depth - 1, 'human')
#             minEval = min(minEval, evaluation)
#         return minEval

# def get_best_move(board, player):
#     maxEval = float('-inf')
#     bestMove = None
#     for move in get_all_possible_moves(board, player):
#         evaluation = minimax(make_move(board, move, player), 3, player)
#         if evaluation > maxEval:
#             maxEval = evaluation
#             bestMove = move
#     return bestMove
    

#minimax algorithm
def minimax(board, depth, player):
    
    bestMove = float("-inf")

    if depth == 0:
        return bestMove

    # global states_reached
    # states_reached += 1
    possible_configs = find_available_position(board, player)
    print(possible_configs)
    for move in possible_configs:
        score = getHeuristic(board, move, player)
        if bestMove < score:
            bestMove = score 


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

#TODO jos heuristika
def getHeuristic(board, move, player):
    if potentional_mills(board, move, player): 
        return 350
    if check_if_mill_blocked(board, move, player): 
        return 300
    else: 
        return 100
        # return numberOfMoveablePiecesHeuristic(board, move, player)

def numOfValue(board, player):
    if player == 'human':
        return len(board['currentState']['humanStones'])
    else:
        return len(board['currentState']['computerStones'])


def numberOfMoveablePiecesHeuristic(board, move, player):
    isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) <= 18

    numPlayerOneTokens = numOfValue(board, 'human')
    numPlayerTwoTokens = numOfValue(board, 'computer')

    movablePiecesBlack = 0

    if not isStage1:
        movablePiecesBlack = len(find_available_position(board, 'computer'))

    if not isStage1:
        if numPlayerTwoTokens <= 2 or movablePiecesBlack == 0:
            evaluation = float('inf')
        elif numPlayerOneTokens <= 2:
            evaluation = float('-inf')
        else:
            evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)
            evaluation -= 50 * movablePiecesBlack
    else:
        evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

    return evaluation

def numberOfPiecesHeuristic(board, player):
    isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) < 18
    numPlayerOneTokens = numOfValue(board, player)
    numPlayerTwoTokens = numOfValue(board, player)

    movablePiecesBlack = 0

    if not isStage1:
        movablePiecesBlack = len(find_available_position(board, player))

    if not isStage1:
        if numPlayerTwoTokens <= 2 or movablePiecesBlack == 0:
            evaluation = float('inf')
        elif numPlayerOneTokens <= 2:
            evaluation = float('-inf')
        else:
            evaluation = 200 * (numPlayerOneTokens - numPlayerTwoTokens)
    else:
        evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

    return evaluation

#TODO jedna koja ima sve  
# def advancedHeuristic(board, player):
#     isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) < 18
#     numPlayerOneTokens = numOfValue(board, player)
#     numPlayerTwoTokens = numOfValue(board, player)

#     numPlayerOneMills = numOfMills(board, player)
#     numPlayerTwoMills = numOfMills(board, player)

#     numPlayerOneBlocked = numOfBlocked(board, player)
#     numPlayerTwoBlocked = numOfBlocked(board, player)

#     numPlayerOnePotentialMills = numOfPotentialMills(board, player)
#     numPlayerTwoPotentialMills = numOfPotentialMills(board, player)

#     if not isStage1:
#         evaluation = 200 * (numPlayerOneTokens - numPlayerTwoTokens) + 50 * (numPlayerOneMills - numPlayerTwoMills) - 50 * (numPlayerOneBlocked - numPlayerTwoBlocked) + 100 * (numPlayerOnePotentialMills - numPlayerTwoPotentialMills)
#     else:
#         evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

#     return evaluation

def numOfMills(board, player):
    mills = 0

    playerStones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

    for mill in mills_positions:
        if all(position in playerStones for position in mill):
            mills += 1

    return mills

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
def check_for_mill(board):
    # check for each player is mills
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for 
                   stone in board['currentState']['computerStones']) for position in mill) == 3:
            return True
    return 

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


def evaluate(white_left, black_left):
    return white_left - black_left


#metoda za izbacivanje stones
def remove_stone(stones, stone, allWhiteMills):
    # Pravimo kopiju niza `stones` kako bismo zadržali originalni niz nepromenjen
    new_stones = stones.copy()

    # Pronađemo indeks kamena koji želimo da izbacimo
    index = next((i for i, s in enumerate(new_stones) if s == stone), None)

    if index is not None and stone not in allWhiteMills:
        # Uklanjanje kamena sa odgovarajućim indeksom
        del new_stones[index]

    return new_stones 

## TESTOVI

# def test_check_if_mill_blocked():
#     # Testni slučaj 1: Potez blokira mlin
#     board1 = {
#         'currentState': {
#             'humanStones': [{'square': 0, 'index': 2}, {'square': 0, 'index': 3}],
#             'computerStones': []
#         },
#         'pending': {
#             'totalHuman': 0,
#             'totalComputer': 0,
#         },
#         'out': {
#             'totalHuman': 0,
#             'totalComputer': 0,
#         }
#     }
#     move1 = {'square': 0, 'index': 2, 'color': 'balck'}
#     result1 = check_for_mill2(board1, move1, "computer")
#     print(f"Test 1: {'Blokiran' if result1 else 'Moguc'}")

#     # Testni slučaj 2: Potez ne blokira mlin
#     board2 = {
#         'currentState': {
#             'humanStones': [{'square': 0, 'index': 0}],
#             'computerStones': []
#         },
#         'pending': {
#             'totalHuman': 0,
#             'totalComputer': 0,
#         },
#         'out': {
#             'totalHuman': 0,
#             'totalComputer': 0,
#         }
#     }
#     move2 = {'square': 0, 'index': 2, 'color': 'black'}
#     result2 = check_for_mill2(board2, move2, "computer")
#     print(f"Test 2: {'Blokiran' if result2 else 'Nije blokiran'}")

# # Pozivamo funkciju za testiranje
# test_check_if_mill_blocked()

# print(determine_winner(5, 5))  

# computerStones = [{'square': 2, 'index': 6}, {'square': 2, 'index': 5}, {'square': 2, 'index': 4}, {'square': 2, 'index': 7}]
# allWhiteMills = [{'square': 0, 'index': 0}, {'square': 0, 'index': 1}]
# stone1 = {'square': 2, 'index': 6}
# stone2 = {'square': 2, 'index': 7} 
# print("REZULTAT 1")
# print(find_avaliable_if_tree(computerStones, allWhiteMills))

# if check_for_mill(computerStones):
#     print("A mill has been formed")
# else:
#     print("No mill has been formed")

# humanStones = humanStones = [{'square': 0, 'index': 0}, {'square': 0, 'index': 1}]
# selectedStone = {'square': 0, 'index': 1}

# result = find_available_moves(humanStones, computerStones, selectedStone)
# print("REZULTAT")
# print(result)











