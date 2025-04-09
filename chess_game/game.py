"""Chess Game - Main Game Logic"""
import pygame
from .board import Board
from .constants import (
    WIDTH, HEIGHT, SQUARE_SIZE, WHITE, BLACK, DARK_SQUARE, LIGHT_SQUARE,
    HIGHLIGHT_COLOR, FPS
)
from .player import Player
from .ai import ChessAI

class ChessGame:
    """Main class that manages the chess game"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Python Chess")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []
        self.turn = WHITE
        self.white_player = Player(WHITE)
        self.black_player = ChessAI(BLACK)
        self.game_over = False
        self.winner = None

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(FPS)
            
            # AI move if it's black's turn
            if self.turn == BLACK and not self.game_over and isinstance(self.black_player, ChessAI):
                move = self.black_player.get_move(self.board)
                if move:
                    self.make_move(move[0], move[1])
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.turn == WHITE or not isinstance(self.black_player, ChessAI):
                        pos = pygame.mouse.get_pos()
                        row, col = self._get_row_col_from_pos(pos)
                        self._handle_click(row, col)
            
            self._draw()
            pygame.display.update()
        
        pygame.quit()

    def _draw(self):
        """Draw the game board and pieces"""
        self._draw_board()
        self._highlight_valid_moves()
        self._draw_pieces()
        if self.game_over:
            self._draw_game_over()

    def _draw_board(self):
        """Draw the chess board squares"""
        self.screen.fill(pygame.Color('white'))
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    color = LIGHT_SQUARE
                else:
                    color = DARK_SQUARE
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                )

    def _highlight_valid_moves(self):
        """Highlight valid moves for the selected piece"""
        if self.selected_piece:
            row, col = self.selected_piece
            # Highlight selected square
            pygame.draw.rect(
                self.screen, 
                HIGHLIGHT_COLOR, 
                (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                3
            )
            # Highlight valid moves
            for move in self.valid_moves:
                move_row, move_col = move
                pygame.draw.circle(
                    self.screen,
                    HIGHLIGHT_COLOR,
                    (move_col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                     move_row * SQUARE_SIZE + SQUARE_SIZE // 2),
                    15
                )

    def _draw_pieces(self):
        """Draw all chess pieces on the board"""
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece:
                    piece.draw(self.screen, row, col, SQUARE_SIZE)

    def _draw_game_over(self):
        """Draw game over message"""
        font = pygame.font.SysFont('Arial', 40, True)
        if self.winner:
            text = f"{'White' if self.winner == WHITE else 'Black'} wins!"
        else:
            text = "Stalemate!"
        
        text_surface = font.render(text, True, pygame.Color('red'))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Draw semi-transparent background
        s = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        s.fill((0, 0, 0, 128))
        self.screen.blit(s, (0, HEIGHT // 2 - 50))
        
        # Draw text
        self.screen.blit(text_surface, text_rect)

    def _get_row_col_from_pos(self, pos):
        """Convert screen position to board coordinates"""
        x, y = pos
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return row, col

    def _handle_click(self, row, col):
        """Handle player clicks on the board"""
        # If a piece is already selected
        if self.selected_piece:
            selected_row, selected_col = self.selected_piece
            # Check if the clicked position is a valid move
            if (row, col) in self.valid_moves:
                self.make_move((selected_row, selected_col), (row, col))
            else:
                # Either deselect or select a new piece
                piece = self.board.get_piece(row, col)
                if piece and piece.color == self.turn:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.board.get_valid_moves(row, col)
                else:
                    self.selected_piece = None
                    self.valid_moves = []
        else:
            # Select a piece if one is clicked
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.board.get_valid_moves(row, col)

    def make_move(self, start, end):
        """Make a move on the board and update game state"""
        start_row, start_col = start
        end_row, end_col = end
        
        # Execute the move
        self.board.move_piece(start_row, start_col, end_row, end_col)
        
        # Reset selection
        self.selected_piece = None
        self.valid_moves = []
        
        # Check for game ending conditions
        if self.board.is_checkmate(BLACK if self.turn == WHITE else WHITE):
            self.game_over = True
            self.winner = self.turn
        elif self.board.is_stalemate(BLACK if self.turn == WHITE else WHITE):
            self.game_over = True
            self.winner = None
        
        # Switch turns
        self.turn = BLACK if self.turn == WHITE else WHITE 