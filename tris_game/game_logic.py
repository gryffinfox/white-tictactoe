import random

# Controlla tutte le possibili linee vincenti sulla scacchiera.
def check_winner(board):
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Orizzontali
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Verticali
        [0, 4, 8], [2, 4, 6]             # Diagonali
    ]
    for line in lines:
        if board[line[0]] == board[line[1]] == board[line[2]] and board[line[0]] != '_':
            return board[line[0]]
    return None

# Calcola la mossa per il BOT di difficoltà facile.
def calculate_easy_bot_move(board, bot_symbol, player_symbol):
    available_moves = [i for i, cell in enumerate(board) if cell == '_']
    if not available_moves: return -1

    # 1. Cerca una mossa vincente per il BOT.
    for move in available_moves:
        test_board = list(board); test_board[move] = bot_symbol
        if check_winner("".join(test_board)) == bot_symbol: return move

    # 2. Cerca di bloccare una mossa vincente dell'avversario.
    for move in available_moves:
        test_board = list(board); test_board[move] = player_symbol
        if check_winner("".join(test_board)) == player_symbol: return move

    # 3. Sceglie posizioni strategiche (centro, angoli).
    if 4 in available_moves: return 4
    corners = [i for i in [0, 2, 6, 8] if i in available_moves]
    if corners: return random.choice(corners)
    
    return random.choice(available_moves)

# Algoritmo Minimax per un BOT imbattibile.
def calculate_minimax_move(new_board, player_symbol):
    bot_symbol = 'O'
    human_player_symbol = 'X'
    available_moves = [i for i, v in enumerate(new_board) if v == '_']

    if check_winner(new_board) == human_player_symbol: return {'score': -10}
    if check_winner(new_board) == bot_symbol: return {'score': 10}
    if len(available_moves) == 0: return {'score': 0}

    moves = []
    for move_index in available_moves:
        move = {'index': move_index}
        test_board = list(new_board)
        test_board[move_index] = player_symbol
        
        next_player = human_player_symbol if player_symbol == bot_symbol else bot_symbol
        result = calculate_minimax_move("".join(test_board), next_player)
        
        move['score'] = result['score']
        moves.append(move)

    if player_symbol == bot_symbol:
        best_move = max(moves, key=lambda x: x['score'])
    else:
        best_move = min(moves, key=lambda x: x['score'])
    
    return best_move