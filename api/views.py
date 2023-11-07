from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .allowed_moves import allowed_moves
from .mills_positions import mills_postitions
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
            'square': 1,
            'index': 0,
            'color': 'black'
        }

        computerStones.append(new_stone)
        available_positions = find_available_position(humanStones, computerStones)

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
            'totalPlacedStones2': totalPlacedStones2
        }

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
