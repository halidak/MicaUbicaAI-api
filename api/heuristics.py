# def numberOfMoveablePiecesHeuristic(board, move, player):
#     isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) <= 18

#     numPlayerOneTokens = numOfValue(board, 'human')
#     numPlayerTwoTokens = numOfValue(board, 'computer')

#     movablePiecesBlack = 0

#     if not isStage1:
#         movablePiecesBlack = len(find_available_position(board, 'computer'))

#     if not isStage1:
#         if numPlayerTwoTokens <= 2 or movablePiecesBlack == 0:
#             evaluation = float('inf')
#         elif numPlayerOneTokens <= 2:
#             evaluation = float('-inf')
#         else:
#             evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)
#             evaluation -= 50 * movablePiecesBlack
#     else:
#         evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

#     return evaluation

# def numberOfPiecesHeuristic(board, player):
#     isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) < 18
#     numPlayerOneTokens = numOfValue(board, player)
#     numPlayerTwoTokens = numOfValue(board, player)

#     movablePiecesBlack = 0

#     if not isStage1:
#         movablePiecesBlack = len(find_available_position(board, player))

#     if not isStage1:
#         if numPlayerTwoTokens <= 2 or movablePiecesBlack == 0:
#             evaluation = float('inf')
#         elif numPlayerOneTokens <= 2:
#             evaluation = float('-inf')
#         else:
#             evaluation = 200 * (numPlayerOneTokens - numPlayerTwoTokens)
#     else:
#         evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

#     return evaluation

# #TODO jedna koja ima sve  
# # def advancedHeuristic(board, player):
# #     isStage1 = len(board['currentState']['humanStones']) + len(board['currentState']['computerStones']) < 18
# #     numPlayerOneTokens = numOfValue(board, player)
# #     numPlayerTwoTokens = numOfValue(board, player)

# #     numPlayerOneMills = numOfMills(board, player)
# #     numPlayerTwoMills = numOfMills(board, player)

# #     numPlayerOneBlocked = numOfBlocked(board, player)
# #     numPlayerTwoBlocked = numOfBlocked(board, player)

# #     numPlayerOnePotentialMills = numOfPotentialMills(board, player)
# #     numPlayerTwoPotentialMills = numOfPotentialMills(board, player)

# #     if not isStage1:
# #         evaluation = 200 * (numPlayerOneTokens - numPlayerTwoTokens) + 50 * (numPlayerOneMills - numPlayerTwoMills) - 50 * (numPlayerOneBlocked - numPlayerTwoBlocked) + 100 * (numPlayerOnePotentialMills - numPlayerTwoPotentialMills)
# #     else:
# #         evaluation = 100 * (numPlayerOneTokens - numPlayerTwoTokens)

# #     return evaluation

# def can_form_mill(board, player):
#     player_color = 'black' if player == 'computer' else 'white'
#     player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

#     for mill in mills_positions:
#         if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones) for position in mill) == 2:
#             empty_positions = [position for position in mill if not any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones)]
#             if empty_positions:
#                 return True

#     return False

# # if opponent_can_form_mill(board, player): 
#     #     return 350
#     # if potentional_mills(board, move, player): 
#     #     return 300
#     # else: 
#     #     return 100
#     #     # return numberOfMoveablePiecesHeuristic(board, move, player)

# def heuristic(board, player):
#     # Weights for each factor
#     weights = {
#         'num_of_value': 10,
#         'num_of_mills': 40,
#         'blocked_mills': 30,
#         'potential_mills': 50,
#         'possible_moves': 10,
#         'blocked_pieces': 10
#     }

#     # Calculate the score for each factor
#     num_of_value_score = numOfValue(board, player) * weights['num_of_value']
#     num_of_mills_score = numOfMills(board, player) * weights['num_of_mills']
#     blocked_mills_score = count_blocked_mills(board, player) * weights['blocked_mills']
#     potential_mills_score = count_potential_mills(board, player) * weights['potential_mills']
#     possible_moves_score = count_possible_moves(board, player) * weights['possible_moves']
#     blocked_pieces_score = count_blocked_pieces(board, player) * weights['blocked_pieces']

#     # Sum up the scores to get the total score
#     total_score = num_of_value_score + num_of_mills_score + blocked_mills_score + potential_mills_score + possible_moves_score + blocked_pieces_score

#     return total_score

# def opponent_can_form_mill(board, player):
#     opponent_color = 'black' if player == 'human' else 'white'
#     opponent_stones = board['currentState']['computerStones'] if player == 'human' else board['currentState']['humanStones']

#     for mill in mills_positions:
#         if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones) for position in mill) == 2:
#             empty_positions = [position for position in mill if not any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones)]
#             if empty_positions:
#                 return True

#     return False

# #broj igraca
# def numOfValue(board, player):
#     if player == 'human':
#         return len(board['currentState']['humanStones'])
#     else:
#         return len(board['currentState']['computerStones'])

# #broj mlinova
# def numOfMills(board, player):
#     mills = 0

#     playerStones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

#     for mill in mills_positions:
#         if all(position in playerStones for position in mill):
#             mills += 1

#     return mills

# #broj blokiranih mlinova
# def count_blocked_mills(board, player):
#     blocked_mills = 0

#     # Get the opponent's stones
#     opponent_stones = board['currentState']['computerStones'] if player == 'human' else board['currentState']['humanStones']

#     # Iterate over all possible mill positions
#     for mill in mills_positions:
#         # Check if the player has two pieces in this mill position
#         player_pieces_in_mill = [position for position in mill if position in board['currentState'][player + 'Stones']]
#         if len(player_pieces_in_mill) == 2:
#             # Check if the remaining position is occupied by the opponent
#             remaining_position = [position for position in mill if position not in player_pieces_in_mill][0]
#             if remaining_position in opponent_stones:
#                 blocked_mills += 1

#     return blocked_mills

# #broj potencijalnih mlinova
# def count_potential_mills(board, player):
#     potential_mills = 0

#     # Get the player's stones
#     player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

#     # Iterate over all possible mill positions
#     for mill in mills_positions:
#         # Check if the player has two pieces in this mill position and the third position is empty
#         player_pieces_in_mill = [position for position in mill if position in player_stones]
#         if len(player_pieces_in_mill) == 2:
#             # Check if the remaining position is empty
#             remaining_position = [position for position in mill if position not in player_pieces_in_mill][0]
#             if remaining_position not in board['currentState']['humanStones'] and remaining_position not in board['currentState']['computerStones']:
#                 potential_mills += 1

#     return potential_mills

# #broj mogucih pomeranja
# def count_possible_moves(board, player):
#     # Get the available positions for the player
#     available_positions = find_available_position(board, player)

#     # The number of possible moves is the number of available positions
#     return len(available_positions)

# def count_blocked_pieces(board, player):
#     blocked_pieces = 0

#     # Get the player's stones
#     player_stones = board['currentState']['humanStones'] if player == 'human' else board['currentState']['computerStones']

#     # Iterate over all player's stones
#     for stone in player_stones:
#         # Get the available moves for this stone
#         available_moves = find_available_moves(board['currentState']['humanStones'], board['currentState']['computerStones'], stone)
#         # If there are no available moves, the stone is blocked
#         if len(available_moves) == 0:
#             blocked_pieces += 1

#     return blocked_pieces

# def check_if_mill_blocked(board, move, player):

#     color = 'white' if player == 'human' else 'black'

#     # Izvlačimo kamenčiće protivnika
#     opponent_stones = board['currentState']['computerStones'] if color == 'white' else board['currentState']['humanStones']

#     # Proveravamo da li bi potez blokirao mlin
#     for mill in mills_positions:
#         # Proveravamo da li protivnik ima dva kamena u mlinu i da li je treća pozicija prazna
#         if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in opponent_stones) for position in mill) == 2 and any(position['square'] == move['square'] and position['index'] == move['index'] for position in mill):
#             return True

#     # Ako nije blokiran nijedan mlin, potez ne blokira mlin
#     return False

# def potentional_mills(board, move, player):
#     color = 'white' if player == 'human' else 'black'

#     # Izvlačimo kamenčiće trenutnog igrača
#     player_stones = board['currentState']['humanStones'] if color == 'white' else board['currentState']['computerStones']

#     # Dodajemo potez u listu kamenčića igrača da bismo proverili da li stvara mlin
#     player_stones.append(move)

#     # Proveravamo da li potez stvara mlin
#     for mill in mills_positions:
#         # Proveravamo da li igrač ima tri kamena u mlinu
#         if sum(any(stone['square'] == position['square'] and stone['index'] == position['index'] for stone in player_stones) for position in mill) == 3:
#             # Uklanjamo potez iz liste kamenčića igrača jer je ovo samo privremena provera
#             player_stones.remove(move)
#             return True

#     # Uklanjamo potez iz liste kamenčića igrača jer je ovo samo privremena provera
#     player_stones.remove(move)

#     # Ako potez ne stvara mlin, vraćamo False
#     return False



# def determine_winner(board):
#     if board['out']['totalHuman'] == 2:
#         return "AI is the winner"
#     elif board['out']['totalComputer'] == 2:
#         return "Human is the winner"
#     else:
#         return None


# #metoda za pomeranje stones na neki move
# def move_stone(stones, selected_stone, new_stone):
#     # Pravimo kopiju niza `stones` kako bismo zadržali originalni niz nepromenjen
#     new_stones = stones.copy()

#     # Pronađemo indeks odabranog kamena u nizu (ako postoji)
#     index = next((i for i, stone in enumerate(new_stones) if stone == selected_stone), None)

#     if index is not None:
#         # Zamena odabranog kamena sa novim kamenom na istom indeksu
#         new_stones[index] = new_stone

#     return new_stones


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



# #TODO jos heuristika
# def getHeuristic(board, player):
#     mill = check_mills55(board, player)

#     if mill is not None:
#         print(f'{player.capitalize()} formed a mill at positions: {mill}')
#         return 1000

#     # # opponent_player = 'human' if player == 'computer' else 'computer'
#     # # opponent_mill_positions = check_for_mill(board, opponent_player)

#     # # if opponent_mill_positions is not None:
#     # #     print(f'{opponent_player.capitalize()} formed a mill at positions: {opponent_mill_positions}')
#     # #     return -1000  # A large negative value for losing the game

#     return 100  
#     # new_board = make_move(board, player)
#     # if check_for_mill2(board, player): 
#     #     return 350
#     # return 100

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


# def check_mills55(board, player):
#     player_stones = board['currentState'][f'{player}Stones']
#     opponent_stones = board['currentState']['humanStones'] if player == 'computer' else board['currentState']['computerStones']
    
#     # Provera da li ima najmanje 2 kamena pre nego što proveri mlin
#     if len(player_stones) < 2:
#         print(f"Not enough stones for {player} to form a mill.")
#         return None  # Nije moguće formirati mlin sa manje od 2 kamena

#     for mill in mills_positions:
#         mill_positions = []
#         empty_positions = []

#         for position in mill:
#             if position in player_stones:
#                 mill_positions.append(position)
#             elif position in opponent_stones:
#                 # If the position is occupied by an opponent's stone, it's not a valid mill position
#                 return None
#             elif position not in opponent_stones and position not in player_stones:
#                 empty_positions.append(position)

#         print(f"Checking mill: {mill}")
#         print(f"Player stones in mill: {mill_positions}")
#         print(f"Empty positions in mill: {empty_positions}")

#         if len(mill_positions) == 2 and len(empty_positions) == 1:
#             print(f"Mill positions: {mill_positions}, Empty positions: {empty_positions}")
#             return empty_positions[0]  # Return the position that can form a mill

#     print(f"No potential mills found for {player}.")
#     return None  # No potential mill found


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

