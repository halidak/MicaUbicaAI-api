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
