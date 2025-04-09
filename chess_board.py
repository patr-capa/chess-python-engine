from chess_piece import Pawn, Rook, Knight, Bishop, Queen, King

class ChessBoard:
    def __init__(self):
        self.board = [[' ' for _ in range(8)] for _ in range(8)]  # 8x8 grid
        self.setup_board()

    def setup_board(self):
        # Place pawns
        for i in range(8):
            self.board[1][i] = Pawn('black', (1, i))   # Black pawns
            self.board[6][i] = Pawn('white', (6, i))   # White pawns

        # Rooks
        self.board[0][0] = Rook('black', (0, 0))
        self.board[0][7] = Rook('black', (0, 7))
        self.board[7][0] = Rook('white', (7, 0))
        self.board[7][7] = Rook('white', (7, 7))

        # Knights
        self.board[0][1] = Knight('black', (0, 1))
        self.board[0][6] = Knight('black', (0, 6))
        self.board[7][1] = Knight('white', (7, 1))
        self.board[7][6] = Knight('white', (7, 6))

        # Bishops
        self.board[0][2] = Bishop('black', (0, 2))
        self.board[0][5] = Bishop('black', (0, 5))
        self.board[7][2] = Bishop('white', (7, 2))
        self.board[7][5] = Bishop('white', (7, 5))

        # Queens
        self.board[0][3] = Queen('black', (0, 3))
        self.board[7][3] = Queen('white', (7, 3))

        # Kings
        self.board[0][4] = King('black', (0, 4))
        self.board[7][4] = King('white', (7, 4))

    def display_board(self):
        print("\n    a b c d e f g h")
        print("  -----------------")
        for row_idx, row in enumerate(self.board):
            row_str = f"{8 - row_idx} | "
            for square in row:
                if square == ' ':
                    row_str += '. '
                else:
                    row_str += str(square) + ' '
            row_str += f"| {8 - row_idx}"
            print(row_str)
        print("  -----------------")
        print("    a b c d e f g h\n")

if __name__ == "__main__":
    chess_board = ChessBoard()
    chess_board.display_board()