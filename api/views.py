from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .allowed_moves import allowed_moves
from .mills_positions import mills_positions
from .all_positions import all_positions


@csrf_exempt
@api_view(['Post'])
def your_view_function(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        humanStones = data.get('humanStones')
        computerStones = data.get('computerStones')
        totalPlacedStones2 = data.get('totalPlacedStones2')

        print(totalPlacedStones2)
        
        new_stone = {
            'square': 2,
            'index': 4,
            'color': 'black'
        }

        computerStones.append(new_stone)
        available_positions = find_available_position(humanStones, computerStones)


        isMills = check_for_mill(computerStones)

        #decrement setTotalPlacedStones2 but if its > 0 and not None
        if totalPlacedStones2 is not None and totalPlacedStones2 > 0:
            totalPlacedStones2 = totalPlacedStones2 - 1
        #else return old value
        else:
            totalPlacedStones2 = totalPlacedStones2

        response_data = {
            'humanStones': humanStones,
            'computerStones': computerStones,
            'availablePositions': available_positions,
            'totalPlacedStones2': totalPlacedStones2,
            'allowed_moves': allowed_moves,
            'isComputerMills': isMills
        }

        print(computerStones)

        return Response(response_data)
    

# find avaliable position za prvo dodavanje kamencica

def find_available_position(humanStones, computerStones):
    occupied_positions = set()

    for stone in humanStones + computerStones:
        occupied_positions.add((stone['square'], stone['index']))

    available_positions = []

    for position in all_positions:
        move_square = position['square']
        move_index = position['index']
        if (move_square, move_index) not in occupied_positions:
            available_positions.append({'square': move_square, 'index': move_index})

    return available_positions

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

#isMills
#check for the mill from mills_positions if im sending [{'square': 2, 'index': 6, 'color': 'black'}]
def check_for_mill(computerStones):
    for mill in mills_positions:
        if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in computerStones) for position in mill) == 3:
            return True
    return False

def determine_winner(human_score, ai_score):
    if human_score == 2:
        return "AI is the winner"
    elif ai_score == 2:
        return "Human is the winner"
    else:
        return "No winner yet"

print(determine_winner(2, 5))  

computerStones = [{'square': 2, 'index': 6, 'color': 'black'}, {'square': 2, 'index': 5, 'color': 'black'}, {'square': 2, 'index': 4, 'color': 'black'}]

if check_for_mill(computerStones):
    print("A mill has been formed")
else:
    print("No mill has been formed")








