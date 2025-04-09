
class ChessPiece:
    """
    Base class that handles common properties and methods.
    """
    def __init__(self, color, position):
        self.color = color  # 'white' or 'black'
        self.position = position  # Tuple (row, col)

    def is_valid_move(self, start_pos, end_pos, board):
        """
        Base method for movement validation
        Subclasses should override this.
        """

        raise NotImplementedError("This method should be implemented by subclasses")

    def __str__(self):
        symbols = {
            'Pawn': 'P',
            'Rook': 'R',
            'Knight': 'N',
            'Bishop': 'B',
            'Queen': 'Q',
            'King': 'K'
        }
        symbol = symbols.get(self.__class__.__name__, '?')
        return symbol.upper() if self.color == 'white' else symbol.lower()


class Pawn(ChessPiece):
    """
    Subclass for pawn
    """
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False

    def is_valid_move(self, start_pos, end_pos, board, last_pawn_double_move=None):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        direction = -1 if self.color == 'white' else 1  # White moves up, Black moves down

        # Normal one-step forward move
        if (
            start_col == end_col and
            end_row == start_row + direction and
            board[end_row][end_col] == ' '
        ):
            return True

        # Two-step forward move from starting position
        if (
            (self.color == 'white' and start_row == 6) or (self.color == 'black' and start_row == 1)
        ) and (
            start_col == end_col and
            end_row == start_row + 2 * direction and
            board[start_row + direction][end_col] == ' ' and
            board[end_row][end_col] == ' '
        ):
            return True

        # Diagonal capture
        if (
            abs(end_col - start_col) == 1 and
            end_row == start_row + direction and
            board[end_row][end_col] != ' ' and
            board[end_row][end_col].color != self.color
        ):
            return True

        # En Passant Capture
        if last_pawn_double_move:
            last_row, last_col = last_pawn_double_move

            if self.color == 'white':
                if (
                    start_row == 3 and  # White en passant row
                    end_row == 2 and
                    abs(end_col - start_col) == 1 and
                    end_col == last_col and
                    board[start_row][end_col] != ' ' and
                    isinstance(board[start_row][end_col], Pawn) and
                    board[start_row][end_col].color == 'black'
                ):
                    return True

            if self.color == 'black':
                if (
                    start_row == 4 and  # Black en passant row
                    end_row == 5 and
                    abs(end_col - start_col) == 1 and
                    end_col == last_col and
                    board[start_row][end_col] != ' ' and
                    isinstance(board[start_row][end_col], Pawn) and
                    board[start_row][end_col].color == 'white'
                ):
                    return True

        return False


class Rook(ChessPiece):
    """
    Subclass for rook
    """
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False

    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if (
            start_row != end_row and
            start_col != end_col
        ):
            return False  # Rook can only move in a straight line

        # Horizontal or vertical movement - check of obstacles
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for col in range(start_col + step, end_col, step):
                if board[start_row][col] != ' ':
                    return False

        elif start_col == end_col:
            step = 1 if end_row > start_row else -1
            for row in range(start_row + step, end_row, step):
                if board[row][start_col] != ' ':
                    return False

        # If destination square is occupied by same color piece, it's invalid
        target_piece = board[end_row][end_col]
        if target_piece != ' ' and target_piece.color == self.color:
            return False

        return True


class Bishop(ChessPiece):
    """
    Subclass for bishop
    """
    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Check if the move is diagonal
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False # Not a diagonal move

        # Determine movement direction
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        # Check for obstructions along the diagonal path
        row, col = start_row + row_step, start_col + col_step
        while row!= end_row and col != end_col:
            if board[row][col] != ' ':
                return False  # Obstruction found
            row += row_step
            col += col_step

        # Ensure Bishop isn't capturing its own piece
        target_piece = board[end_row][end_col]
        if target_piece != ' ' and target_piece.color == self.color:
            return False

        return True  # Move is valid

class Knight(ChessPiece):
    """
    Subclass for knight
    """
    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # List of all possible L-shaped moves
        possible_moves = [
            (start_row + 2, start_col + 1), (start_row + 2, start_col - 1),
            (start_row -2, start_col + 1), (start_row -2, start_col - 1),
            (start_row + 1, start_col + 2), (start_row + 1, start_col - 2),
            (start_row - 1, start_col + 2), (start_row - 1, start_col - 2)
        ]

        # Check if the destination is a valid L-shaped move
        if (end_row, end_col) not in possible_moves:
            return False

        # Ensure the Knight isn't capturing its own piece
        target_piece = board[end_row][end_col]
        if target_piece != ' ' and target_piece.color == self.color:
            return False

        return True  # Move is valid


class Queen(ChessPiece):
    """
    Subclass for Queen
    """
    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Check if move is straight like a rook
        if start_row == end_row or start_col == end_col:
            step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
            step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)
        # Check if the move is diagonal
        elif abs(start_row - end_row) == abs(start_col - end_col):
            step_row = 1 if end_row > start_row else -1
            step_col = 1 if end_col > start_col else -1
        else:
            return False  # Not a valid Queen move

        # Check for obstacles in the path
        row, col = start_row + step_row, start_col + step_col
        while (row, col) != (end_row, end_col):
            if board[row][col] != ' ':
                return False  # Blocked path
            row += step_row
            col += step_col

        # Ensure Queen isn't capturing its own piece
        target_piece = board[end_row][end_col]
        if target_piece != ' ' and target_piece.color ==self.color:
            return False

        return True  #move is valid


class King(ChessPiece):
    """
    Subclass for King
    """
    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False

    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Check if move is only one square in any direction
        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        if row_diff <= 1 and col_diff <= 1:
            # Ensure King isn't capturing its own piece
            target_piece = board[end_row][end_col]
            if target_piece == ' ' or target_piece.color != self.color:
                return True

        # Castling Logic
        if not self.has_moved and start_row == end_row and col_diff == 2:
            direction = 1 if end_col > start_col else -1
            rook_col = 7 if direction == 1 else 0
            rook = board[start_row][rook_col]

            if isinstance(rook, Rook) and not rook.has_moved and rook.color == self.color:
                # Check if path between king and rook is clear
                for col in range(min(start_col, rook_col) + 1, max(start_col, rook_col)):
                    if board[start_row][col] != ' ':
                        return False
                return True

        return False  # Move is invalid