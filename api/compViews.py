from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .views import *
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
        'level': 1
    }
    
@csrf_exempt
@api_view(['Get'])
def reset_game(request):
    global mills, board
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
        'level': 1
    }
    return Response(mills)


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


        board = make_best_move2(board, player, mills)
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


def make_best_move2(board, player, mills):
    # print("Player",player)
    depth = 2
    # print("NAPOLJE", board['out']['human'])
    # print("NAPOLJE", board['out']['computer'])
    if len(board['currentState'][f'{player}Stones']) == 3:
        depth -= 1
    elif board['pending'][player] == 0:
        depth += 1
    else:
        depth = 2
        
    # print("DUBINA", depth)
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

