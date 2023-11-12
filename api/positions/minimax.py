#TODO

# def minimax(board, depth, player):
#     if depth == 0:
#         return getHeuristic(board, None, player)  # Assuming None as the move for the root node

#     if player == 'computer':
#         bestMove = float('-inf')
#         for move in find_available_position(board, player):
#             score = minimax(board, depth - 1, 'human')  # Switch player for the next level of the tree
#             if score > bestMove:
#                 bestMove = score
#         return bestMove

#     else:  # Human player's turn
#         bestMove = float('inf')
#         for move in find_available_position(board, player):
#             score = minimax(board, depth - 1, 'computer')  # Switch player for the next level of the tree
#             if score < bestMove:
#                 bestMove = score
#         return bestMove


# def minimax(board, depth, player):
#     if depth == 0 or game_over(board):
#         return numberOfMoveablePiecesHeuristic(board, None, player)
#            return evaluate(board, player)

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

# def minimax(board, depth, player):
#     if depth == 0 or game_over(board):
#         return evaluate(board, player)

#     if player == 'human':
#         maxEval = float('-inf')
#         for move in get_all_moves(board, player):
#             new_board = make_move(board, move)
#             eval = minimax(new_board, depth - 1, 'computer')
#             maxEval = max(maxEval, eval)
#         return maxEval
#     else:  # player == 'computer'
#         minEval = float('inf')
#         for move in get_all_moves(board, player):
#             new_board = make_move(board, move)
#             eval = minimax(new_board, depth - 1, 'human')
#             minEval = min(minEval, eval)
#         return minEval

# def evaluate(board, player):
#     numPlayerOneTokens = numOfValue(board, 'human')
#     numPlayerTwoTokens = numOfValue(board, 'computer')

#     numPlayerOneMills = numOfMills(board, 'human')
#     numPlayerTwoMills = numOfMills(board, 'computer')

#     numPlayerOneBlocked = numOfBlocked(board, 'human')
#     numPlayerTwoBlocked = numOfBlocked(board, 'computer')

#     numPlayerOnePotentialMills = numOfPotentialMills(board, 'human')
#     numPlayerTwoPotentialMills = numOfPotentialMills(board, 'computer')

#     if player == 'human':
#         evaluation = 200 * (numPlayerOneTokens - numPlayerTwoTokens) + 50 * (numPlayerOneMills - numPlayerTwoMills) - 50 * (numPlayerOneBlocked - numPlayerTwoBlocked) + 100 * (numPlayerOnePotentialMills - numPlayerTwoPotentialMills)
#     else:  # player == 'computer'
#         evaluation = 200 * (numPlayerTwoTokens - numPlayerOneTokens) + 50 * (numPlayerTwoMills - numPlayerOneMills) - 50 * (numPlayerTwoBlocked - numPlayerOneBlocked) + 100 * (numPlayerTwoPotentialMills - numPlayerOnePotentialMills)

#     return evaluation