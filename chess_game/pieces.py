"""Chess Game - Pieces Module"""
import os
import pygame
from .constants import WHITE, BLACK, SQUARE_SIZE

# Global images dictionary to be loaded once when the game starts
IMAGES = None

def load_images():
    """Load chess piece images"""
    global IMAGES
    if IMAGES is not None:
        return IMAGES
        
    images = {}
    pieces = ['P', 'R', 'N', 'B', 'Q', 'K']
    for piece in pieces:
        # Try to load images if they exist
        try:
            # White pieces
            white_img = pygame.image.load(os.path.join('assets', f'w{piece}.png'))
            white_img = pygame.transform.scale(white_img, (SQUARE_SIZE, SQUARE_SIZE))
            images[f'w{piece}'] = white_img
            
            # Black pieces
            black_img = pygame.image.load(os.path.join('assets', f'b{piece}.png'))
            black_img = pygame.transform.scale(black_img, (SQUARE_SIZE, SQUARE_SIZE))
            images[f'b{piece}'] = black_img
        except Exception as e:
            print(f"Error loading image for {piece}: {e}")
            # If image loading fails, create a fallback with colored text
            font = pygame.font.SysFont('Arial', 40, True)
            
            # White pieces (rendered as green text)
            white_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            white_text = font.render(piece, True, (0, 200, 0))
            white_rect = white_text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
            white_surf.blit(white_text, white_rect)
            images[f'w{piece}'] = white_surf
            
            # Black pieces (rendered as red text)
            black_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            black_text = font.render(piece, True, (200, 0, 0))
            black_rect = black_text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
            black_surf.blit(black_text, black_rect)
            images[f'b{piece}'] = black_surf
    
    IMAGES = images
    return images

class Piece:
    """Base class for all chess pieces"""
    
    def __init__(self, color, row, col):
        """Initialize a chess piece"""
        self.color = color
        self.row = row
        self.col = col
        self.has_moved = False
        
        # Ensure images are loaded once at the start
        load_images()
    
    def get_potential_moves(self, board):
        """Get all potential moves for the piece without considering check"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def draw(self, surface, row, col, square_size):
        """Draw the piece on the board"""
        color_prefix = 'w' if self.color == WHITE else 'b'
        piece_key = f'{color_prefix}{self.symbol}'
        
        if IMAGES and piece_key in IMAGES:
            surface.blit(IMAGES[piece_key], (col * square_size, row * square_size))
        else:
            # Fallback if image is not available
            font = pygame.font.SysFont('Arial', 40, True)
            text_color = (0, 200, 0) if self.color == WHITE else (200, 0, 0)
            text = font.render(self.symbol, True, text_color)
            text_rect = text.get_rect(center=(
                col * square_size + square_size // 2,
                row * square_size + square_size // 2
            ))
            surface.blit(text, text_rect)


class Pawn(Piece):
    """Pawn chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'P'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a pawn"""
        moves = []
        
        # Direction of movement depends on color
        direction = -1 if self.color == WHITE else 1
        
        # Forward move
        new_row = self.row + direction
        if board.is_valid_position(new_row, self.col) and board.get_piece(new_row, self.col) is None:
            moves.append((new_row, self.col))
            
            # Double move from starting position
            if not self.has_moved:
                new_row = self.row + 2 * direction
                if board.is_valid_position(new_row, self.col) and board.get_piece(new_row, self.col) is None:
                    moves.append((new_row, self.col))
        
        # Captures
        for col_offset in [-1, 1]:
            new_col = self.col + col_offset
            new_row = self.row + direction
            
            if board.is_valid_position(new_row, new_col):
                # Regular capture
                piece = board.get_piece(new_row, new_col)
                if piece and piece.color != self.color:
                    moves.append((new_row, new_col))
                
                # En passant capture
                if board.en_passant_target == (new_row, new_col):
                    moves.append((new_row, new_col))
        
        return moves


class Rook(Piece):
    """Rook chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'R'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a rook"""
        moves = []
        
        # Directions: up, right, down, left
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = self.row + dr * i, self.col + dc * i
                
                if not board.is_valid_position(new_row, new_col):
                    break
                
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Knight(Piece):
    """Knight chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'N'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a knight"""
        moves = []
        
        # Knight moves in L-shape: 2 squares in one direction and 1 square perpendicular
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in knight_moves:
            new_row, new_col = self.row + dr, self.col + dc
            
            if board.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves


class Bishop(Piece):
    """Bishop chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'B'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a bishop"""
        moves = []
        
        # Diagonal directions: up-left, up-right, down-right, down-left
        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = self.row + dr * i, self.col + dc * i
                
                if not board.is_valid_position(new_row, new_col):
                    break
                
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class Queen(Piece):
    """Queen chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'Q'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a queen (combines rook and bishop moves)"""
        moves = []
        
        # Combine rook and bishop directions
        # Horizontal/vertical (rook) and diagonal (bishop) directions
        directions = [
            (-1, 0), (0, 1), (1, 0), (0, -1),  # Rook directions
            (-1, -1), (-1, 1), (1, 1), (1, -1)  # Bishop directions
        ]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = self.row + dr * i, self.col + dc * i
                
                if not board.is_valid_position(new_row, new_col):
                    break
                
                piece = board.get_piece(new_row, new_col)
                if piece is None:
                    moves.append((new_row, new_col))
                elif piece.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves


class King(Piece):
    """King chess piece"""
    
    def __init__(self, color, row, col):
        super().__init__(color, row, col)
        self.symbol = 'K'
    
    def get_potential_moves(self, board):
        """Get all potential moves for a king"""
        moves = []
        
        # All 8 directions: up, up-right, right, down-right, down, down-left, left, up-left
        directions = [
            (-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)
        ]
        
        # Regular king moves
        for dr, dc in directions:
            new_row, new_col = self.row + dr, self.col + dc
            
            if board.is_valid_position(new_row, new_col):
                piece = board.get_piece(new_row, new_col)
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        
        # Castling
        if not self.has_moved and not board.is_in_check(self.color):
            # Kingside castling
            if board.castling_rights[self.color]['kingside']:
                can_castle = True
                # Check if squares between king and rook are empty
                for col in range(self.col + 1, 7):
                    if board.get_piece(self.row, col) is not None:
                        can_castle = False
                        break
                
                # Check if king passes through check
                for col in range(self.col + 1, self.col + 3):
                    # Create a temporary board to test if the square is under attack
                    temp_board = board
                    if temp_board.is_square_under_attack(self.row, col, self.color):
                        can_castle = False
                        break
                
                if can_castle:
                    moves.append((self.row, self.col + 2))
            
            # Queenside castling
            if board.castling_rights[self.color]['queenside']:
                can_castle = True
                # Check if squares between king and rook are empty
                for col in range(self.col - 1, 0, -1):
                    if board.get_piece(self.row, col) is not None:
                        can_castle = False
                        break
                
                # Check if king passes through check
                for col in range(self.col - 1, self.col - 3, -1):
                    # Create a temporary board to test if the square is under attack
                    temp_board = board
                    if temp_board.is_square_under_attack(self.row, col, self.color):
                        can_castle = False
                        break
                
                if can_castle:
                    moves.append((self.row, self.col - 2))
        
        return moves 