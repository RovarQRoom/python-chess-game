"""Chess Game - AI Module"""
import random
import time
import copy
from .player import Player
from .constants import (
    WHITE, BLACK, PIECE_VALUES,
    PAWN_TABLE, KNIGHT_TABLE, BISHOP_TABLE, ROOK_TABLE, QUEEN_TABLE, 
    KING_EARLY_TABLE, KING_LATE_TABLE,
    PAWN_TABLE_BLACK, KNIGHT_TABLE_BLACK, BISHOP_TABLE_BLACK, ROOK_TABLE_BLACK,
    QUEEN_TABLE_BLACK, KING_EARLY_TABLE_BLACK, KING_LATE_TABLE_BLACK
)
from .pieces import Pawn, Knight, Bishop, Rook, Queen, King

class ChessAI(Player):
    """AI chess player implementing minimax algorithm with alpha-beta pruning"""
    
    def __init__(self, color, difficulty=3):
        """Initialize AI player with specified color and difficulty level"""
        super().__init__(color)
        self.difficulty = difficulty  # Difficulty from 1-4, controls search depth
        self.max_depth = difficulty + 1  # Search depth (2-5)
        self.nodes_evaluated = 0
        self.transposition_table = {}  # For caching board evaluations
    
    def get_move(self, board):
        """Get the best move according to the AI's evaluation"""
        self.nodes_evaluated = 0
        start_time = time.time()
        
        # Check if there are any valid moves at all
        valid_moves = self._get_all_valid_moves(board, self.color)
        if not valid_moves:
            return None
        
        # Find the best move using minimax with alpha-beta pruning
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for piece_pos, moves in valid_moves.items():
            for move in moves:
                # Make a temporary move
                temp_board = self._make_temp_move(board, piece_pos, move)
                
                # Evaluate the move
                score = self._minimax(temp_board, self.max_depth - 1, alpha, beta, False)
                
                # Update best move if this one is better
                if score > best_score:
                    best_score = score
                    best_move = (piece_pos, move)
                
                # Update alpha
                alpha = max(alpha, best_score)
        
        end_time = time.time()
        print(f"AI move evaluation: {self.nodes_evaluated} nodes in {end_time - start_time:.2f}s")
        
        return best_move
    
    def _get_all_valid_moves(self, board, color):
        """Get all valid moves for a given color"""
        all_moves = {}
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    valid_moves = board.get_valid_moves(row, col)
                    if valid_moves:
                        all_moves[(row, col)] = valid_moves
        return all_moves
    
    def _make_temp_move(self, board, start_pos, end_pos):
        """Make a temporary move on a copy of the board"""
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Create a deep copy of the board
        temp_board = copy.deepcopy(board)
        
        # Make the move
        temp_board.move_piece(start_row, start_col, end_row, end_col)
        
        return temp_board
    
    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax algorithm with alpha-beta pruning for chess AI"""
        self.nodes_evaluated += 1
        
        # Generate a unique hash for the current board position
        board_hash = self._get_board_hash(board)
        
        # Check if this position has already been evaluated
        if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
            return self.transposition_table[board_hash]['score']
        
        # Terminal states: max depth reached or game over
        if depth == 0 or board.is_checkmate(self.color) or board.is_checkmate(BLACK if self.color == WHITE else WHITE) or board.is_stalemate(WHITE) or board.is_stalemate(BLACK):
            score = self._evaluate_board(board)
            self.transposition_table[board_hash] = {'score': score, 'depth': depth}
            return score
        
        if is_maximizing:
            # Maximizing player (AI)
            max_score = float('-inf')
            valid_moves = self._get_all_valid_moves(board, self.color)
            
            for piece_pos, moves in valid_moves.items():
                for move in moves:
                    # Make a temporary move
                    temp_board = self._make_temp_move(board, piece_pos, move)
                    
                    # Recursively evaluate
                    score = self._minimax(temp_board, depth - 1, alpha, beta, False)
                    max_score = max(max_score, score)
                    
                    # Alpha-beta pruning
                    alpha = max(alpha, max_score)
                    if beta <= alpha:
                        break
                
                if beta <= alpha:
                    break
            
            self.transposition_table[board_hash] = {'score': max_score, 'depth': depth}
            return max_score
        else:
            # Minimizing player (opponent)
            min_score = float('inf')
            opponent_color = BLACK if self.color == WHITE else WHITE
            valid_moves = self._get_all_valid_moves(board, opponent_color)
            
            for piece_pos, moves in valid_moves.items():
                for move in moves:
                    # Make a temporary move
                    temp_board = self._make_temp_move(board, piece_pos, move)
                    
                    # Recursively evaluate
                    score = self._minimax(temp_board, depth - 1, alpha, beta, True)
                    min_score = min(min_score, score)
                    
                    # Alpha-beta pruning
                    beta = min(beta, min_score)
                    if beta <= alpha:
                        break
                
                if beta <= alpha:
                    break
            
            self.transposition_table[board_hash] = {'score': min_score, 'depth': depth}
            return min_score
    
    def _get_board_hash(self, board):
        """Generate a unique hash for the current board position"""
        # Simple representation - in a full implementation, this would use Zobrist hashing
        hash_str = ""
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    piece_char = piece.symbol
                    color_char = 'w' if piece.color == WHITE else 'b'
                    hash_str += color_char + piece_char
                else:
                    hash_str += 'xx'
        return hash_str
    
    def _evaluate_board(self, board):
        """Evaluate the board position"""
        if board.is_checkmate(BLACK if self.color == WHITE else WHITE):
            # If opponent is checkmated, return highest possible score
            return 100000
        
        if board.is_checkmate(self.color):
            # If AI is checkmated, return lowest possible score
            return -100000
        
        if board.is_stalemate(WHITE) or board.is_stalemate(BLACK):
            # Stalemate is evaluated as 0
            return 0
        
        # Count material and positional advantage
        score = 0
        
        # Determine game phase (early, mid, late)
        game_phase = self._determine_game_phase(board)
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece:
                    # Material value
                    piece_value = PIECE_VALUES[piece.symbol]
                    
                    # Positional value based on piece type and color
                    positional_value = self._get_positional_value(piece, row, col, game_phase)
                    
                    # Add to score (positive for AI pieces, negative for opponent pieces)
                    piece_score = piece_value + positional_value
                    if piece.color == self.color:
                        score += piece_score
                    else:
                        score -= piece_score
        
        # Additional strategic evaluations
        score += self._evaluate_king_safety(board, self.color) - self._evaluate_king_safety(board, BLACK if self.color == WHITE else WHITE)
        score += self._evaluate_pawn_structure(board, self.color) - self._evaluate_pawn_structure(board, BLACK if self.color == WHITE else WHITE)
        score += self._evaluate_mobility(board, self.color) - self._evaluate_mobility(board, BLACK if self.color == WHITE else WHITE)
        
        return score
    
    def _determine_game_phase(self, board):
        """Determine the game phase (early, mid, late)"""
        # Count the total material value on the board
        total_value = 0
        queens_present = False
        
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.symbol != 'K':  # Exclude kings
                    total_value += PIECE_VALUES[piece.symbol]
                    if piece.symbol == 'Q':
                        queens_present = True
        
        # Early game: most pieces still present
        if total_value > 5000 and queens_present:
            return 'early'
        # Late game: few pieces remain
        elif total_value < 3000:
            return 'late'
        # Mid game: between early and late
        else:
            return 'mid'
    
    def _get_positional_value(self, piece, row, col, game_phase):
        """Get the positional value for a piece based on its position"""
        # Flip the table for black pieces
        if piece.color == BLACK:
            row = 7 - row  # Flip the row index
        
        if isinstance(piece, Pawn):
            return PAWN_TABLE[row][col] if piece.color == WHITE else PAWN_TABLE_BLACK[row][col]
        elif isinstance(piece, Knight):
            return KNIGHT_TABLE[row][col] if piece.color == WHITE else KNIGHT_TABLE_BLACK[row][col]
        elif isinstance(piece, Bishop):
            return BISHOP_TABLE[row][col] if piece.color == WHITE else BISHOP_TABLE_BLACK[row][col]
        elif isinstance(piece, Rook):
            return ROOK_TABLE[row][col] if piece.color == WHITE else ROOK_TABLE_BLACK[row][col]
        elif isinstance(piece, Queen):
            return QUEEN_TABLE[row][col] if piece.color == WHITE else QUEEN_TABLE_BLACK[row][col]
        elif isinstance(piece, King):
            # Use different tables based on game phase
            if game_phase == 'early' or game_phase == 'mid':
                return KING_EARLY_TABLE[row][col] if piece.color == WHITE else KING_EARLY_TABLE_BLACK[row][col]
            else:
                return KING_LATE_TABLE[row][col] if piece.color == WHITE else KING_LATE_TABLE_BLACK[row][col]
        
        return 0
    
    def _evaluate_king_safety(self, board, color):
        """Evaluate the safety of the king"""
        score = 0
        king_row, king_col = board.king_positions[color]
        
        # Check if the king is in check
        if board.is_in_check(color):
            score -= 150  # Heavy penalty for being in check
        
        # Count squares around the king that are attacked
        attacked_squares = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the king's position
                
                new_row, new_col = king_row + dr, king_col + dc
                if board.is_valid_position(new_row, new_col):
                    if board.is_square_under_attack(new_row, new_col, color):
                        attacked_squares += 1
        
        # Penalize for each attacked square around the king
        score -= attacked_squares * 20
        
        # Castling bonus
        if color == WHITE:
            # If king is castled, give a bonus
            if king_col == 6 and king_row == 7:  # Kingside
                score += 100
            elif king_col == 2 and king_row == 7:  # Queenside
                score += 100
        else:
            if king_col == 6 and king_row == 0:  # Kingside
                score += 100
            elif king_col == 2 and king_row == 0:  # Queenside
                score += 100
        
        # Pawn shield bonus (pawns in front of the king)
        direction = -1 if color == WHITE else 1
        for dc in [-1, 0, 1]:
            shield_row, shield_col = king_row + direction, king_col + dc
            if board.is_valid_position(shield_row, shield_col):
                piece = board.get_piece(shield_row, shield_col)
                if piece and isinstance(piece, Pawn) and piece.color == color:
                    score += 30  # Bonus for each pawn shielding the king
        
        return score
    
    def _evaluate_pawn_structure(self, board, color):
        """Evaluate the pawn structure"""
        score = 0
        pawns = []
        
        # Find all pawns of the given color
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and isinstance(piece, Pawn) and piece.color == color:
                    pawns.append((row, col))
        
        # Evaluate doubled pawns (same column)
        pawn_columns = [col for _, col in pawns]
        for col in range(8):
            count = pawn_columns.count(col)
            if count > 1:
                score -= 20 * (count - 1)  # Penalty for doubled pawns
        
        # Evaluate isolated pawns (no friendly pawns in adjacent columns)
        for row, col in pawns:
            is_isolated = True
            for adj_col in [col - 1, col + 1]:
                if adj_col in pawn_columns:
                    is_isolated = False
                    break
            
            if is_isolated:
                score -= 15  # Penalty for isolated pawns
        
        # Evaluate passed pawns (no enemy pawns ahead in same or adjacent columns)
        opponent_color = BLACK if color == WHITE else WHITE
        for row, col in pawns:
            is_passed = True
            
            # Direction depends on color
            direction = -1 if color == WHITE else 1
            
            # Check for enemy pawns ahead in the same or adjacent columns
            for r in range(row + direction, 0 if color == WHITE else 7, direction):
                for c in [col - 1, col, col + 1]:
                    if 0 <= c < 8:
                        piece = board.get_piece(r, c)
                        if piece and isinstance(piece, Pawn) and piece.color == opponent_color:
                            is_passed = False
                            break
                
                if not is_passed:
                    break
            
            if is_passed:
                # Bonus for passed pawns, higher for more advanced pawns
                advancement = abs(row - (7 if color == WHITE else 0))
                score += 20 + advancement * 10
        
        # Evaluate pawn chains (pawns protecting each other)
        for row, col in pawns:
            # Check if this pawn is protected by another pawn
            protector_row = row + (1 if color == WHITE else -1)
            for protector_col in [col - 1, col + 1]:
                if board.is_valid_position(protector_row, protector_col):
                    piece = board.get_piece(protector_row, protector_col)
                    if piece and isinstance(piece, Pawn) and piece.color == color:
                        score += 10  # Bonus for pawn chains
        
        return score
    
    def _evaluate_mobility(self, board, color):
        """Evaluate piece mobility (number of available moves)"""
        score = 0
        
        # Count the total number of legal moves
        for row in range(8):
            for col in range(8):
                piece = board.get_piece(row, col)
                if piece and piece.color == color:
                    moves = board.get_valid_moves(row, col)
                    score += len(moves) * 5  # Bonus for each available move
                    
                    # Additional bonuses for specific pieces
                    if isinstance(piece, Knight) or isinstance(piece, Bishop):
                        score += len(moves) * 2  # Knights and bishops benefit more from mobility
        
        return score 