"""Chess Game - Board Module"""
import copy
from .constants import WHITE, BLACK
from .pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    """Chess board representation and game rules"""
    
    def __init__(self):
        """Initialize a new chess board with pieces in starting positions"""
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.captured_pieces = {WHITE: [], BLACK: []}
        self.move_history = []
        self.king_positions = {WHITE: (7, 4), BLACK: (0, 4)}
        self.castling_rights = {
            WHITE: {'kingside': True, 'queenside': True},
            BLACK: {'kingside': True, 'queenside': True}
        }
        self.en_passant_target = None
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_counter = 1  # Incremented after Black's move
        
        self._setup_pieces()
    
    def _setup_pieces(self):
        """Place all pieces in their initial positions"""
        # Set up pawns
        for col in range(8):
            self.board[1][col] = Pawn(BLACK, 1, col)
            self.board[6][col] = Pawn(WHITE, 6, col)
        
        # Set up rooks
        self.board[0][0] = Rook(BLACK, 0, 0)
        self.board[0][7] = Rook(BLACK, 0, 7)
        self.board[7][0] = Rook(WHITE, 7, 0)
        self.board[7][7] = Rook(WHITE, 7, 7)
        
        # Set up knights
        self.board[0][1] = Knight(BLACK, 0, 1)
        self.board[0][6] = Knight(BLACK, 0, 6)
        self.board[7][1] = Knight(WHITE, 7, 1)
        self.board[7][6] = Knight(WHITE, 7, 6)
        
        # Set up bishops
        self.board[0][2] = Bishop(BLACK, 0, 2)
        self.board[0][5] = Bishop(BLACK, 0, 5)
        self.board[7][2] = Bishop(WHITE, 7, 2)
        self.board[7][5] = Bishop(WHITE, 7, 5)
        
        # Set up queens
        self.board[0][3] = Queen(BLACK, 0, 3)
        self.board[7][3] = Queen(WHITE, 7, 3)
        
        # Set up kings
        self.board[0][4] = King(BLACK, 0, 4)
        self.board[7][4] = King(WHITE, 7, 4)
    
    def get_piece(self, row, col):
        """Get piece at the specified position"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def is_valid_position(self, row, col):
        """Check if position is within the board"""
        return 0 <= row < 8 and 0 <= col < 8
    
    def move_piece(self, start_row, start_col, end_row, end_col):
        """Move a piece on the board and handle special moves"""
        piece = self.board[start_row][start_col]
        if not piece:
            return False
        
        # Store captured piece if any
        captured_piece = self.board[end_row][end_col]
        
        # Handle special moves
        move_type = self._get_move_type(piece, start_row, start_col, end_row, end_col)
        
        # Execute the move
        if move_type == 'en_passant':
            # Handle en passant capture
            captured_pawn_row = start_row
            captured_pawn_col = end_col
            captured_piece = self.board[captured_pawn_row][captured_pawn_col]
            self.board[captured_pawn_row][captured_pawn_col] = None
            self.captured_pieces[piece.color].append(captured_piece)
        elif move_type == 'castling_kingside':
            # Move rook for kingside castling
            rook = self.board[start_row][7]
            self.board[start_row][5] = rook
            self.board[start_row][7] = None
            if rook:
                rook.row, rook.col = start_row, 5
                rook.has_moved = True
        elif move_type == 'castling_queenside':
            # Move rook for queenside castling
            rook = self.board[start_row][0]
            self.board[start_row][3] = rook
            self.board[start_row][0] = None
            if rook:
                rook.row, rook.col = start_row, 3
                rook.has_moved = True
        
        # Regular move execution
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None
        
        # Update piece position
        piece.row, piece.col = end_row, end_col
        piece.has_moved = True
        
        # Handle pawn promotion
        if move_type == 'promotion':
            queen = Queen(piece.color, end_row, end_col)
            self.board[end_row][end_col] = queen
        
        # Update king position if king moved
        if isinstance(piece, King):
            self.king_positions[piece.color] = (end_row, end_col)
            # Update castling rights - king moved, so no castling is possible
            self.castling_rights[piece.color]['kingside'] = False
            self.castling_rights[piece.color]['queenside'] = False
        
        # Update castling rights if rook moved
        if isinstance(piece, Rook):
            if start_row == 7 and start_col == 0 and piece.color == WHITE:
                self.castling_rights[WHITE]['queenside'] = False
            elif start_row == 7 and start_col == 7 and piece.color == WHITE:
                self.castling_rights[WHITE]['kingside'] = False
            elif start_row == 0 and start_col == 0 and piece.color == BLACK:
                self.castling_rights[BLACK]['queenside'] = False
            elif start_row == 0 and start_col == 7 and piece.color == BLACK:
                self.castling_rights[BLACK]['kingside'] = False
        
        # Check if rook was captured (which affects castling rights)
        if captured_piece and isinstance(captured_piece, Rook):
            if end_row == 0 and end_col == 0:
                self.castling_rights[BLACK]['queenside'] = False
            elif end_row == 0 and end_col == 7:
                self.castling_rights[BLACK]['kingside'] = False
            elif end_row == 7 and end_col == 0:
                self.castling_rights[WHITE]['queenside'] = False
            elif end_row == 7 and end_col == 7:
                self.castling_rights[WHITE]['kingside'] = False
        
        # Store captured piece if there was one
        if captured_piece and move_type != 'en_passant':
            self.captured_pieces[piece.color].append(captured_piece)
        
        # Set en passant target square for next move
        self.en_passant_target = None
        if isinstance(piece, Pawn) and abs(start_row - end_row) == 2:
            # Pawn moved two squares, set en passant target
            self.en_passant_target = (
                (start_row + end_row) // 2,  # Row between start and end
                start_col  # Same column
            )
        
        # Update move counters
        if isinstance(piece, Pawn) or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        if piece.color == BLACK:
            self.fullmove_counter += 1
        
        # Add move to history
        self.move_history.append({
            'piece': piece,
            'start': (start_row, start_col),
            'end': (end_row, end_col),
            'captured': captured_piece,
            'en_passant': self.en_passant_target,
            'castling': self.castling_rights.copy(),
            'halfmove': self.halfmove_clock,
            'fullmove': self.fullmove_counter
        })
        
        return True
    
    def _get_move_type(self, piece, start_row, start_col, end_row, end_col):
        """Determine the type of move being made"""
        if isinstance(piece, Pawn):
            # Pawn promotion
            if (piece.color == WHITE and end_row == 0) or \
               (piece.color == BLACK and end_row == 7):
                return 'promotion'
            
            # En passant capture
            if abs(start_col - end_col) == 1 and not self.board[end_row][end_col]:
                if self.en_passant_target == (end_row, end_col):
                    return 'en_passant'
        
        elif isinstance(piece, King):
            # Kingside castling
            if end_col - start_col == 2:
                return 'castling_kingside'
            # Queenside castling
            elif start_col - end_col == 2:
                return 'castling_queenside'
        
        return 'regular'
    
    def is_square_under_attack(self, row, col, color):
        """Check if a square is under attack by any opponent piece"""
        opponent_color = BLACK if color == WHITE else WHITE
        
        # Check all opponent pieces
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == opponent_color:
                    # For efficiency, we need to check this without creating infinite recursion
                    # with the get_potential_moves method that also calls is_square_under_attack
                    
                    # For pawns, specifically check attack directions
                    if isinstance(piece, Pawn):
                        direction = -1 if piece.color == WHITE else 1
                        attack_positions = [
                            (piece.row + direction, piece.col - 1),
                            (piece.row + direction, piece.col + 1)
                        ]
                        if (row, col) in attack_positions:
                            return True
                    
                    # For knights, check L-shaped moves
                    elif isinstance(piece, Knight):
                        knight_moves = [
                            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                            (1, -2), (1, 2), (2, -1), (2, 1)
                        ]
                        for dr, dc in knight_moves:
                            if (piece.row + dr, piece.col + dc) == (row, col):
                                return True
                    
                    # For bishops, queens (diagonals), check diagonal lines
                    elif isinstance(piece, Bishop) or isinstance(piece, Queen):
                        # Check all diagonal directions
                        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                        for dr, dc in directions:
                            for i in range(1, 8):
                                r2, c2 = piece.row + dr * i, piece.col + dc * i
                                
                                if (r2, c2) == (row, col):
                                    return True
                                
                                if not self.is_valid_position(r2, c2) or self.board[r2][c2]:
                                    break
                    
                    # For rooks, queens (straight lines), check horizontal and vertical lines
                    if isinstance(piece, Rook) or isinstance(piece, Queen):
                        # Check all straight directions
                        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                        for dr, dc in directions:
                            for i in range(1, 8):
                                r2, c2 = piece.row + dr * i, piece.col + dc * i
                                
                                if (r2, c2) == (row, col):
                                    return True
                                
                                if not self.is_valid_position(r2, c2) or self.board[r2][c2]:
                                    break
                    
                    # For kings, check adjacent squares
                    elif isinstance(piece, King):
                        king_moves = [
                            (-1, -1), (-1, 0), (-1, 1), (0, -1),
                            (0, 1), (1, -1), (1, 0), (1, 1)
                        ]
                        for dr, dc in king_moves:
                            if (piece.row + dr, piece.col + dc) == (row, col):
                                return True
        
        return False
    
    def get_valid_moves(self, row, col):
        """Get all valid moves for a piece at the specified position"""
        piece = self.board[row][col]
        if not piece:
            return []
        
        potential_moves = piece.get_potential_moves(self)
        valid_moves = []
        
        # Check each potential move to see if it would leave the king in check
        for move in potential_moves:
            move_row, move_col = move
            
            # Make a temporary move
            temp_board = copy.deepcopy(self)
            temp_board.move_piece(row, col, move_row, move_col)
            
            # Check if the king is in check after the move
            if not temp_board.is_in_check(piece.color):
                valid_moves.append(move)
        
        return valid_moves
    
    def is_in_check(self, color):
        """Check if the king of the specified color is in check"""
        king_row, king_col = self.king_positions[color]
        return self.is_square_under_attack(king_row, king_col, color)
    
    def is_checkmate(self, color):
        """Check if the king of the specified color is in checkmate"""
        if not self.is_in_check(color):
            return False
        
        # Check if any move can get the king out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    if self.get_valid_moves(row, col):
                        return False
        
        return True
    
    def is_stalemate(self, color):
        """Check if the position is a stalemate for the specified color"""
        if self.is_in_check(color):
            return False
        
        # Check if any legal move exists
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    if self.get_valid_moves(row, col):
                        return False
        
        return True
    
    def is_draw_by_insufficient_material(self):
        """Check if there is insufficient material to checkmate"""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and not isinstance(piece, King):
                    pieces.append(piece)
        
        # King vs King
        if len(pieces) == 0:
            return True
        
        # King and Bishop vs King or King and Knight vs King
        if len(pieces) == 1:
            return isinstance(pieces[0], Bishop) or isinstance(pieces[0], Knight)
        
        # King and Bishop vs King and Bishop (same color bishops)
        if len(pieces) == 2 and isinstance(pieces[0], Bishop) and isinstance(pieces[1], Bishop):
            # Check if bishops are on same colored squares
            square1_color = (pieces[0].row + pieces[0].col) % 2
            square2_color = (pieces[1].row + pieces[1].col) % 2
            return square1_color == square2_color
        
        return False
    
    def is_draw_by_fifty_move_rule(self):
        """Check if the game is a draw by the fifty-move rule"""
        return self.halfmove_clock >= 100  # 50 moves = 100 half-moves
    
    def is_draw_by_threefold_repetition(self):
        """Check if the position has been repeated three times"""
        # This is a simplified implementation
        # A full implementation would need to track positions using FEN notation
        
        # For simplicity, just check if the most recent moves have been repeating
        if len(self.move_history) < 8:
            return False
        
        # Check for simple back-and-forth repetition pattern
        recent_moves = self.move_history[-8:]
        move_pattern_1 = recent_moves[0:4]
        move_pattern_2 = recent_moves[4:8]
        
        # Simple check - not a complete implementation
        for i in range(4):
            move1 = move_pattern_1[i]
            move2 = move_pattern_2[i]
            if move1['start'] != move2['start'] or move1['end'] != move2['end']:
                return False
        
        return True 