"""Chess Game - Main Game Logic"""
import pygame
import logging
from .board import Board
from .constants import (
    WIDTH, HEIGHT, SQUARE_SIZE, WHITE, BLACK, DARK_SQUARE, LIGHT_SQUARE,
    HIGHLIGHT_COLOR, CAPTURE_HIGHLIGHT_COLOR, CHECK_HIGHLIGHT_COLOR, FPS
)
from .player import Player
from .ai import ChessAI

# Set up logging
logging.basicConfig(
    filename='chess_game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ChessGame:
    """Main class that manages the chess game"""
    
    def __init__(self):
        """Initialize the game"""
        # Don't initialize pygame or create a new screen if this is called from menu
        # The screen will be set by the menu system
        self.screen = None
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.selected_piece = None
        self.valid_moves = []
        self.turn = WHITE
        self.white_player = Player(WHITE)
        self.black_player = ChessAI(BLACK)
        self.game_over = False
        self.winner = None
        self.check_status = {WHITE: False, BLACK: False}
        self.last_move = None  # Store the last move made (start_pos, end_pos)
        logging.info("Game initialized")

    def set_screen(self, screen):
        """Set the screen from an external source (like the menu system)"""
        self.screen = screen

    def run(self):
        """Main game loop"""
        # Initialize the screen if not already set (standalone mode)
        if not self.screen:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Python Chess")
            
        running = True
        ai_thinking = False
        ai_start_time = 0
        
        while running:
            self.clock.tick(FPS)
            
            # Update check status at the beginning of each frame
            self.check_status = {
                WHITE: self.board.is_in_check(WHITE),
                BLACK: self.board.is_in_check(BLACK)
            }
            
            # AI move if it's black's turn
            if self.turn == BLACK and not self.game_over and isinstance(self.black_player, ChessAI) and not ai_thinking:
                ai_thinking = True
                ai_start_time = pygame.time.get_ticks()
                try:
                    logging.info("AI is thinking...")
                    move = self.black_player.get_move(self.board)
                    if move:
                        start_pos, end_pos = move
                        start_row, start_col = start_pos
                        end_row, end_col = end_pos
                        piece = self.board.get_piece(start_row, start_col)
                        piece_name = f"{piece.symbol} at {start_row},{start_col}"
                        
                        logging.info(f"AI moving {piece_name} to {end_row},{end_col}")
                        print(f"AI move: {piece.symbol} at {start_row},{start_col} to position {end_row},{end_col}")
                        
                        self.make_move(move[0], move[1])
                    else:
                        logging.warning("AI couldn't find a valid move")
                        print("AI couldn't find a valid move")
                except Exception as e:
                    logging.error(f"AI move error: {str(e)}", exc_info=True)
                    print(f"Error during AI move: {str(e)}")
                finally:
                    ai_thinking = False
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not ai_thinking:
                    if self.turn == WHITE or not isinstance(self.black_player, ChessAI):
                        pos = pygame.mouse.get_pos()
                        row, col = self._get_row_col_from_pos(pos)
                        self._handle_click(row, col)
            
            self._draw()
            
            # Draw AI thinking indicator
            if ai_thinking:
                self._draw_thinking_indicator(pygame.time.get_ticks() - ai_start_time)
                
            pygame.display.update()
        
        pygame.quit()

    def run_once(self, skip_ai=False, skip_events=False):
        """Run a single iteration of the game loop, for use with the menu system
        
        Args:
            skip_ai: If True, skips AI move processing
            skip_events: If True, skips pygame event processing
        """
        # Make sure we have a screen to draw on
        if not self.screen:
            print("ERROR: No screen set for the game. Cannot run.")
            return "error"
            
        # Update check status
        self.check_status = {
            WHITE: self.board.is_in_check(WHITE),
            BLACK: self.board.is_in_check(BLACK)
        }
        
        # AI move if it's black's turn and AI is enabled
        if self.turn == BLACK and not self.game_over and isinstance(self.black_player, ChessAI) and not skip_ai:
            try:
                logging.info("AI is thinking...")
                print("AI is thinking...")
                move = self.black_player.get_move(self.board)
                if move:
                    start_pos, end_pos = move
                    start_row, start_col = start_pos
                    end_row, end_col = end_pos
                    piece = self.board.get_piece(start_row, start_col)
                    piece_name = f"{piece.symbol} at {start_row},{start_col}"
                    
                    logging.info(f"AI moving {piece_name} to {end_row},{end_col}")
                    print(f"AI move: {piece.symbol} at {start_row},{start_col} to position {end_row},{end_col}")
                    
                    self.make_move(move[0], move[1])
                else:
                    logging.warning("AI couldn't find a valid move")
                    print("AI couldn't find a valid move")
            except Exception as e:
                logging.error(f"AI move error: {str(e)}", exc_info=True)
                print(f"Error during AI move: {str(e)}")
        
        # Event handling (only if not being handled by menu system)
        if not skip_events:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if self.turn == WHITE or not isinstance(self.black_player, ChessAI):
                        pos = pygame.mouse.get_pos()
                        row, col = self._get_row_col_from_pos(pos)
                        self._handle_click(row, col)
        
        # Draw the game
        self._draw()
        pygame.display.update()
        
        # Return None for normal operation
        return None

    def _draw(self):
        """Draw the game board and pieces"""
        if not self.screen:
            print("ERROR: Cannot draw game - no screen is set")
            return
            
        self._draw_board()
        self._highlight_check()
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

    def _highlight_check(self):
        """Highlight the king that is in check"""
        for color, is_in_check in self.check_status.items():
            if is_in_check:
                king_row, king_col = self.board.king_positions[color]
                pygame.draw.rect(
                    self.screen,
                    CHECK_HIGHLIGHT_COLOR, 
                    (king_col * SQUARE_SIZE, king_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    4  # Thicker border for check
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
                # Check if the move is a capture
                target_piece = self.board.get_piece(move_row, move_col)
                if target_piece:
                    # Use red highlight for captures
                    pygame.draw.rect(
                        self.screen,
                        CAPTURE_HIGHLIGHT_COLOR,
                        (move_col * SQUARE_SIZE, move_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                        3
                    )
                else:
                    # Regular move highlight
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
        """Handle a click on the chess board at the specified position
        
        Args:
            row: Row index (0-7)
            col: Column index (0-7)
            
        Returns:
            str: Action that was taken ("select", "move", "deselect", or None)
        """
        # If a piece is already selected
        if self.selected_piece:
            # Get the position of the selected piece
            piece_row, piece_col = self.selected_piece
            
            # If clicked on the same piece, deselect it
            if piece_row == row and piece_col == col:
                self.selected_piece = None
                self.valid_moves = []
                return "deselect"
            
            # If clicked on a valid move position, make the move
            move_made = False
            for move in self.valid_moves:
                if move[0] == row and move[1] == col:
                    # Make the move
                    self.make_move((piece_row, piece_col), (row, col))
                    move_made = True
                    break
            
            if move_made:
                # Clear selection after move
                self.selected_piece = None
                self.valid_moves = []
                return "move_made"
            else:
                # Check if clicked on another piece of the same color
                piece_at_click = self.board.get_piece(row, col)
                if piece_at_click and piece_at_click.color == self.turn:
                    self.selected_piece = (row, col)
                    self.valid_moves = self.board.get_valid_moves(row, col)
                    return "select"
                    
        # If no piece is selected and a piece was clicked
        else:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.board.get_valid_moves(row, col)
                return "select"
        
        return None

    def make_move(self, start, end):
        """Make a chess move
        
        Args:
            start: Tuple of (row, col) for the start position
            end: Tuple of (row, col) for the end position
            
        Returns:
            bool: True if the move was successful, False otherwise
        """
        start_row, start_col = start
        end_row, end_col = end
        
        # Get the piece at the start position
        piece = self.board.get_piece(start_row, start_col)
        
        # Check that there is a piece and it's the correct color's turn
        if not piece or piece.color != self.turn:
            return False
        
        # Check if the move is valid
        valid_moves = self.board.get_valid_moves(start_row, start_col)
        if (end_row, end_col) not in valid_moves:
            return False
        
        # Make the move
        logging.info(f"Moving {piece.symbol} from {start_row},{start_col} to {end_row},{end_col}")
        
        # Record the move
        self.last_move = (start, end)
        
        # Check if we're capturing a piece before making the move
        captured_piece = self.board.get_piece(end_row, end_col)
        if captured_piece:
            logging.info(f"Capturing {captured_piece.symbol} at {end_row},{end_col}")
            
        # Move the piece - returns True if successful
        move_result = self.board.move_piece(start_row, start_col, end_row, end_col)
        if not move_result:
            return False
        
        # Switch turns
        self.turn = BLACK if self.turn == WHITE else WHITE
        
        # Update check status
        self.check_status = {
            WHITE: self.board.is_in_check(WHITE),
            BLACK: self.board.is_in_check(BLACK)
        }
        
        # Check for checkmate or stalemate
        opponent_color = BLACK if piece.color == WHITE else WHITE
        
        if self.board.is_checkmate(opponent_color):
            self.game_over = True
            self.winner = piece.color
            logging.info(f"Checkmate! Winner: {'White' if self.winner == WHITE else 'Black'}")
        elif self.board.is_stalemate(opponent_color):
            self.game_over = True
            self.winner = None
            logging.info("Stalemate!")
        elif self.board.is_draw_by_insufficient_material():
            self.game_over = True
            self.winner = None
            logging.info("Draw by insufficient material!")
        
        return True

    def _draw_thinking_indicator(self, elapsed_time):
        """Draw an indicator when AI is thinking"""
        # Create a semi-transparent overlay at the bottom
        s = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, HEIGHT - 40))
        
        # Add thinking text with animated dots
        dots = "." * ((elapsed_time // 500) % 4)
        font = pygame.font.SysFont('Arial', 20, True)
        text = f"AI thinking{dots}"
        text_surface = font.render(text, True, pygame.Color('white'))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20))
        self.screen.blit(text_surface, text_rect) 