"""Chess Game - Menu System"""
import pygame
from .constants import WIDTH, HEIGHT, FPS, LIGHT_SQUARE, DARK_SQUARE
from .game import ChessGame
from .ai import ChessAI
from .player import Player
from .constants import WHITE, BLACK

class Button:
    """Button class for menu interactions"""
    
    def __init__(self, text, x, y, width, height, color, hover_color, text_color, font_size=36):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', font_size, True)
        
    def draw(self, screen):
        """Draw the button on the screen"""
        if self.is_hovered:
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        
        # Add a border
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
        
        # Draw the text on the button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_click):
        """Check if button is clicked"""
        return self.rect.collidepoint(mouse_pos) and mouse_click


class MenuSystem:
    """Menu system for the chess game"""
    
    def __init__(self):
        """Initialize the menu system"""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Python Chess")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "main_menu"
        
        # Define colors
        self.bg_color = LIGHT_SQUARE
        self.button_color = (181, 136, 99)  # Dark brown
        self.button_hover_color = (150, 111, 51)  # Darker brown
        self.button_text_color = (255, 255, 255)  # White
        self.title_color = (0, 0, 0)  # Black
        
        # Prepare buttons for main menu
        self.main_menu_buttons = [
            Button("Singleplayer", WIDTH//2 - 150, HEIGHT//2 - 50, 300, 60, 
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Multiplayer", WIDTH//2 - 150, HEIGHT//2 + 30, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Quit", WIDTH//2 - 150, HEIGHT//2 + 110, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color)
        ]
        
        # Prepare buttons for difficulty selection
        self.difficulty_buttons = [
            Button("Easy", WIDTH//2 - 150, HEIGHT//2 - 80, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Medium", WIDTH//2 - 150, HEIGHT//2, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Hard", WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Back", 50, HEIGHT - 80, 120, 50,
                  self.button_color, self.button_hover_color, self.button_text_color, 24)
        ]
        
        # Game over menu buttons
        self.game_over_buttons = [
            Button("Back to Menu", WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Play Again", WIDTH//2 - 150, HEIGHT//2 + 180, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color)
        ]
        
        # Chess board pattern for background
        self.board_pattern = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._draw_board_background()
        
        # Game instance
        self.game = None
        self.game_mode = None
        self.difficulty = None
    
    def _draw_board_background(self):
        """Draw a chess board pattern for the background"""
        square_size = 40  # Smaller squares for the background
        for row in range(HEIGHT // square_size):
            for col in range(WIDTH // square_size):
                if (row + col) % 2 == 0:
                    color = (240, 217, 181, 60)  # Light color with alpha
                else:
                    color = (181, 136, 99, 60)  # Dark color with alpha
                pygame.draw.rect(
                    self.board_pattern, 
                    color, 
                    (col * square_size, row * square_size, square_size, square_size)
                )
    
    def run(self):
        """Main menu loop"""
        while self.running:
            self.clock.tick(FPS)
            
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_click = True
            
            # Handle different states
            if self.state == "main_menu":
                self._handle_main_menu(mouse_pos, mouse_click)
            elif self.state == "difficulty":
                self._handle_difficulty_menu(mouse_pos, mouse_click)
            elif self.state == "game":
                self._handle_game()
            elif self.state == "game_over":
                self._handle_game_over(mouse_pos, mouse_click)
    
    def _handle_main_menu(self, mouse_pos, mouse_click):
        """Handle main menu interactions"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        font = pygame.font.SysFont('Arial', 60, True)
        title = font.render("Python Chess", True, self.title_color)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Update and draw buttons
        for button in self.main_menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
            
            if button.is_clicked(mouse_pos, mouse_click):
                if button.text == "Singleplayer":
                    self.state = "difficulty"
                elif button.text == "Multiplayer":
                    self.game_mode = "multiplayer"
                    self._start_game()
                elif button.text == "Quit":
                    self.running = False
        
        pygame.display.update()
    
    def _handle_difficulty_menu(self, mouse_pos, mouse_click):
        """Handle difficulty selection menu"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        font = pygame.font.SysFont('Arial', 50, True)
        title = font.render("Select Difficulty", True, self.title_color)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Update and draw buttons
        for button in self.difficulty_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
            
            if button.is_clicked(mouse_pos, mouse_click):
                if button.text == "Easy":
                    self.difficulty = 1
                    self.game_mode = "singleplayer"
                    self._start_game()
                elif button.text == "Medium":
                    self.difficulty = 2
                    self.game_mode = "singleplayer"
                    self._start_game()
                elif button.text == "Hard":
                    self.difficulty = 3
                    self.game_mode = "singleplayer"
                    self._start_game()
                elif button.text == "Back":
                    self.state = "main_menu"
        
        pygame.display.update()
    
    def _handle_game(self):
        """Handle game state"""
        if self.game:
            # Check if game is over
            if self.game.game_over:
                self.state = "game_over"
            else:
                # Get mouse events and manually handle them
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Handle mouse clicks manually
                        if not self.game.game_over:
                            if self.game.turn == WHITE or not isinstance(self.game.black_player, ChessAI):
                                pos = pygame.mouse.get_pos()
                                row, col = self.game._get_row_col_from_pos(pos)
                                self.game._handle_click(row, col)
                
                # Run one iteration of the game loop with skipped event handling
                # since we've already handled the events above
                if self.game.turn == BLACK and isinstance(self.game.black_player, ChessAI) and not self.game.game_over:
                    # Let the AI make its move
                    self.game.run_once(skip_events=True)
                else:
                    # Just draw the current game state
                    self.game._draw()
                    pygame.display.update()
    
    def _handle_game_over(self, mouse_pos, mouse_click):
        """Handle game over screen"""
        # Let the game continue drawing without processing events
        if self.game:
            self.game.run_once(skip_ai=True, skip_events=True)
        
        # Draw semi-transparent overlay
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(s, (0, 0))
        
        # Draw game over message
        font = pygame.font.SysFont('Arial', 50, True)
        if self.game.winner is not None:
            text = f"{'White' if self.game.winner == WHITE else 'Black'} wins!"
        else:
            text = "Stalemate!"
        
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(text_surface, text_rect)
        
        # Update and draw buttons
        for button in self.game_over_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
            
            if button.is_clicked(mouse_pos, mouse_click):
                if button.text == "Back to Menu":
                    self.game = None
                    self.state = "main_menu"
                elif button.text == "Play Again":
                    self._start_game()
        
        pygame.display.update()
    
    def _start_game(self):
        """Start a new game with the selected settings"""
        self.game = ChessGame()
        
        if self.game_mode == "singleplayer":
            # Set up AI with selected difficulty
            self.game.black_player = ChessAI(BLACK, self.difficulty)
        else:  # multiplayer
            # Set up human player for black
            self.game.black_player = Player(BLACK)
        
        self.state = "game" 