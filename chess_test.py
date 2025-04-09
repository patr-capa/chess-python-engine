from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King
from chess_board import ChessBoard
import copy, random, time


# Piece values for AI targeting
target_values = {
    'Pawn': 1,
    'Knight': 3,
    'Bishop': 3,
    'Rook': 5,
    'Queen': 9,
    'King': 1000
}


def greedy_ai_move():
    global board, current_turn, last_pawn_double_move, move_history, move_count

    best_capture = None
    highest_value = -1
    legal_moves = []

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ' ' and piece.color == 'black':
                start = (row, col)
                for r in range(8):
                    for c in range(8):
                        end = (r, c)
                        target = board[r][c]
                        valid = piece.is_valid_move(start, end, board, last_pawn_double_move,) if isinstance(piece, Pawn) else piece.is_valid_move(start, end, board)

                        if not valid:
                            continue

                        legal_moves.append((piece, start, end))

                        if target != ' ' and target.color == 'white':
                            value = target_values.get(target.__class__.__name__,0)
                            if value > highest_value:
                                best_capture = (piece, start, end)
                                highest_value = value

    # Choose the best capture or fallback to random legal move
    if best_capture:
        piece, start, end = best_capture
    elif legal_moves:
        piece, start, end = random.choice(legal_moves)
    else:
        print("AI has no legal moves.")
        return

    # Execute move
    save_game_state()
    capture = board[end[0]][end[1]] != ' '

    if isinstance(piece, Pawn) and last_pawn_double_move and abs(start[1] - end[1]) == 1 and board[end[0]][end[1]] == ' ':
        board[last_pawn_double_move[0]][last_pawn_double_move[1]] = ' '
        capture = True

    if isinstance(piece, Pawn) and abs(start[0] - end[0]) == 2:
        last_pawn_double_move = end
    else:
        last_pawn_double_move = None

    if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
        row = start[0]
        rook_col, new_rook_col = (7,5) if end[1] == 6 else (0, 3)
        rook = board[row][new_rook_col]
        if isinstance(rook, Rook) and rook.color == piece.color:
            board[row][new_rook_col] = rook
            board[row][rook_col] = ' '
            rook.position = (row, new_rook_col)
            rook.has_moved = True

    board[end[0]][end[1]] = piece
    board[start[0]][start[1]] = ' '
    piece.position = end
    if isinstance(piece, (King, Rook)):
        piece.has_moved = True

    pgn_move = to_pgn(piece, start, end, capture)
    if current_turn == 'white':
        move_history.append(f"{move_count}. {pgn_move}")
    else:
        move_history[-1] += f" {pgn_move}"
        move_count += 1

    if isinstance(piece,Pawn) and end[0] == 7:
        board[end[0]][end[1]] = Queen(piece.color, end)
        print("AI promoted a pawn to Queen!")

    if check_game_state(current_turn, last_pawn_double_move):
        return

    current_turn = 'white'


def parse_position(pos):
    """Converts input like 'e2' to (row, col)"""
    if len(pos) != 2:
        return None
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    if 0 <= row < 8 and 0 <= col < 8:
        return row, col
    return None


def to_pgn(piece, start, end, capture=False):
    col_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    piece_map = {
        'Pawn': '',
        'Knight': 'N',
        'Bishop': 'B',
        'Rook': 'R',
        'Queen': 'Q',
        'King': 'K'
    }

    start_file = col_names[start[1]]
    end_file = col_names[end[1]]
    end_rank = str(8 - end[0])
    piece_name = piece.__class__.__name__
    symbol = piece_map.get(piece_name, '?')

    # Castling
    if piece_name == 'King' and abs(start[1] - end[1]) == 2:
        return "O-O" if end[1] == 6 else "O-O-O"

    # Pawn capture: exd5
    if piece_name == 'Pawn' and capture:
        return f"{start_file}x{end_file}{end_rank}"

    # Regular capture: Nxe5
    if capture:
        return f"{symbol}x{end_file}{end_rank}"

    # Normal move: Nf3 or e4
    return f"{symbol}{end_file}{end_rank}"

# Initialize board and trackers
chess_board = ChessBoard()
board = chess_board.board
last_pawn_double_move = None
current_turn = 'white'
move_history = []
move_count = 1
undo_stack = []  # List holds past game states
redo_stack = []  # List holds undone states


def save_game_state():
    undo_stack.append({
        'board':copy.deepcopy(board),
        'current_turn': current_turn,
        'last_pawn_double_move': last_pawn_double_move,
        'move_history': move_history[:],
        'move_count': move_count
    })
    redo_stack.clear()  # Clear redo history after a new move


def undo_move():
    global board, current_turn, last_pawn_double_move, move_history, move_count
    if not undo_stack:
        print("Nothing to undo.")
        return
    # Save current state to redo stack
    redo_stack.append({
        'board': copy.deepcopy(board),
        'current_turn': current_turn,
        'last_pawn_double_move': last_pawn_double_move,
        'move_history': move_history[:],
        'move_count': move_count
    })
    # Restore last state
    state = undo_stack.pop()
    board[:] = state['board']
    current_turn = state['current_turn']
    last_pawn_double_move = state['last_pawn_double_move']
    move_history[:] = state['move_history']
    move_count = state['move_count']
    print("Move undone.")


def redo_move():
    global board, current_turn, last_pawn_double_move, move_history, move_count
    if not redo_stack:
        print("Nothing to redo.")
        return
    # Save current state to undo stack
    undo_stack.append({
        'board': copy.deepcopy(board),
        'current_turn': current_turn,
        'last_pawn_double_move': last_pawn_double_move,
        'move_history': move_history[:],
        'move_count': move_count
    })
    # Restore next state
    state = redo_stack.pop()
    board[:] = state['board']
    current_turn = state['current_turn']
    last_pawn_double_move = state['last_pawn_double_move']
    move_history[:] = state['move_history']
    move_count = state['move_count']
    print("Move redone.")


def is_in_check(board, color):
    king_pos = None
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if isinstance(piece, King) and piece.color == color:
                king_pos = (row, col)
                break
        if king_pos:
            break

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ' ' and piece.color != color:
                if isinstance(piece, Pawn):
                    if piece.is_valid_move((row, col), king_pos, board, None):
                        return True
                else:
                    if piece.is_valid_move((row, col), king_pos, board):
                        return True
    return False


def has_no_legal_moves(board, color, last_pawn_double_move):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != ' ' and piece.color == color:
                for r in range(8):
                    for c in range(8):
                        if isinstance(piece, Pawn):
                            if piece.is_valid_move((row, col), (r, c), board, last_pawn_double_move):
                                saved = board[r][c]
                                board[r][c] = piece
                                board[row][col] = ' '
                                if not is_in_check(board, color):
                                    board[row][col] = piece
                                    board[r][c] = saved
                                    return False
                                board[row][col] = piece
                                board[r][c] = saved
                        else:
                            if piece.is_valid_move((row, col), (r, c), board):
                                saved = board[r][c]
                                board[r][c] = piece
                                board[row][col] = ' '
                                if not is_in_check(board, color):
                                    board[row][col] = piece
                                    board[r][c] = saved
                                    return False
                                board[row][col] = piece
                                board[r][c] = saved
    return True


def check_game_state(current_turn, last_pawn_double_move):
    opponent = 'black' if current_turn == 'white' else 'white'

    if is_in_check(board, opponent):
        if has_no_legal_moves(board, opponent, last_pawn_double_move):
            chess_board.display_board()
            print(f"Checkmate! {current_turn.capitalize()} wins!")
            return True
        else:
            print(f"{opponent.capitalize()} is in check!")
    elif has_no_legal_moves(board, opponent, last_pawn_double_move):
        chess_board.display_board()
        print("Stalemate!")
        return True

    return False


def play_game():
    global last_pawn_double_move, current_turn, move_history, move_count

    while True:
        chess_board.display_board()

        if current_turn == 'black':
            print("AI is thinking...")
            time.sleep(1.75)
            greedy_ai_move()
            continue

        print(f"{current_turn.capitalize()}'s move:")
        start_pos = input("Enter piece to move (e.g., 'e2'): ").strip()

        # Process input if user wants to undo
        if start_pos.lower() == 'undo':
            undo_move()
            continue

        # Process input if user wants to redo
        if start_pos.lower() == 'redo':
            redo_move()
            continue

        end_pos = input("Enter destination (e.g., 'e4'): ").strip()
        if end_pos.lower() == 'undo':
            undo_move()
            continue
        if start_pos.lower() == 'redo':
            redo_move()
            continue

        start = parse_position(start_pos)
        end = parse_position(end_pos)

        if not start or not end:
            print("Invalid input. Try again.")
            continue

        piece = board[start[0]][start[1]]

        if piece == ' ':
            print("No piece at that position!")
            continue

        if piece.color != current_turn:
            print(f"It's {current_turn}'s turn!")
            continue

        if isinstance(piece, Pawn):
            if piece.is_valid_move(start, end, board, last_pawn_double_move):
                save_game_state()  # Save state prior to the move
                capture = board[end[0]][end[1]] != ' '

                if last_pawn_double_move and abs(start[1] - end[1]) == 1 and board[end[0]][end[1]] == ' ':
                    board[last_pawn_double_move[0]][last_pawn_double_move[1]] = ' '
                    capture = True

                if abs(start[0] - end[0]) == 2:
                    last_pawn_double_move = end
                else:
                    last_pawn_double_move = None

                board[end[0]][end[1]] = piece
                board[start[0]][start[1]] = ' '
                piece.position = end
                piece.has_moved = True

                # PGN Logging
                pgn_move = to_pgn(piece, start, end, capture)
                if current_turn == 'white':
                    move_history.append(f"{move_count}. {pgn_move}")
                else:
                    move_history[-1] += f" {pgn_move}"
                    move_count += 1

                # Promotion
                if (piece.color == 'white' and end[0] == 0) or (piece.color == 'black' and end[0] == 7):
                    while True:
                        choice = input("Promote pawn to (Q)ueen, (R)ook, (B)ishop, or k(N)ight? ").strip().lower()
                        if choice == 'q':
                            board[end[0]][end[1]] = Queen(piece.color, end)
                            break
                        elif choice == 'r':
                            board[end[0]][end[1]] = Rook(piece.color, end)
                            break
                        elif choice == 'b':
                            board[end[0]][end[1]] = Bishop(piece.color, end)
                            break
                        elif choice == 'n':
                            board[end[0]][end[1]] = Knight(piece.color, end)
                            break
                        else:
                            print("Invalid choice. Please enter Q, R, B, or N.")
                    print("Pawn promoted!")

                if check_game_state(current_turn, last_pawn_double_move):
                    break

                current_turn = 'black' if current_turn == 'white' else 'white'
            else:
                print("Invalid move! Try again.")

        elif piece.is_valid_move(start, end, board):
            save_game_state()  # Save state prior to the move
            capture = board[end[0]][end[1]] != ' '

            if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
                row = start[0]
                if end[1] == 6:
                    rook_col = 7
                    new_rook_col = 5
                elif end[1] == 2:
                    rook_col = 0
                    new_rook_col = 3
                else:
                    rook_col = None

                if rook_col is not None:
                    rook = board[row][rook_col]
                    if isinstance(rook, Rook) and rook.color == piece.color:
                        board[row][new_rook_col] = rook
                        board[row][rook_col] = ' '
                        rook.position = (row, new_rook_col)
                        rook.has_moved = True

            board[end[0]][end[1]] = piece
            board[start[0]][start[1]] = ' '
            piece.position = end

            if isinstance(piece, (King, Rook)):
                piece.has_moved = True

            last_pawn_double_move = None

            # PGN Logging
            pgn_move = to_pgn(piece, start, end, capture)
            if current_turn == 'white':
                move_history.append(f"{move_count}. {pgn_move}")
            else:
                move_history[-1] += f" {pgn_move}"
                move_count += 1

            if check_game_state(current_turn, last_pawn_double_move):
                break

            current_turn = 'black' if current_turn == 'white' else 'white'
        else:
            print("Invalid move! Try again.")

    # End of game: display and save PGN
    print("\nGame Over. PGN Moves:")
    for move in move_history:
        print(move)
    with open("saved_game.pgn", "w") as f:
        for move in move_history:
            f.write(move + "\n")
    print("Game saved as saved_game.pgn")


# Run the game
if __name__ == "__main__":
    play_game()