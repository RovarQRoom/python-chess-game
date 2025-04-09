"""Chess Game - Menu System (Fixed Version)"""
import pygame
import threading
import time
from chess_game.constants import WIDTH, HEIGHT, FPS, LIGHT_SQUARE, DARK_SQUARE
from chess_game.game import ChessGame
from chess_game.ai import ChessAI
from chess_game.player import Player
from chess_game.constants import WHITE, BLACK

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
        self.debug = False  # Disable debug output by default
        
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
        
        # Pause menu buttons
        self.pause_menu_buttons = [
            Button("Resume", WIDTH//2 - 150, HEIGHT//2 - 80, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Back to Menu", WIDTH//2 - 150, HEIGHT//2, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Quit Game", WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color)
        ]
        
        # Chess board pattern for background
        self.board_pattern = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._draw_board_background()
        
        # Game instance
        self.game = None
        self.game_mode = None
        self.difficulty = None
        self.paused = False
        
        # AI threading variables
        self.ai_thinking = False
        self.ai_thread = None
        self.ai_move = None
        self.ai_start_time = 0
    
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
            
            # Process events based on current state
            events = pygame.event.get()
            self._process_events(events)
            
            # Handle different states
            if self.state == "main_menu":
                self._handle_main_menu()
            elif self.state == "difficulty":
                self._handle_difficulty_menu()
            elif self.state == "game":
                if self.paused:
                    self._handle_pause_menu()
                else:
                    self._handle_game()
            elif self.state == "game_over":
                self._handle_game_over()
    
    def _process_events(self, events):
        """Process events based on current state"""
        mouse_click = False
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.state == "game":
                    self.paused = not self.paused
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
                
                # Handle click based on current state
                if self.state == "main_menu":
                    self._check_button_clicks(self.main_menu_buttons, mouse_pos)
                elif self.state == "difficulty":
                    self._check_button_clicks(self.difficulty_buttons, mouse_pos)
                elif self.state == "game" and not self.paused:
                    if self.game and not self.game.game_over and not self.ai_thinking:
                        if self.game.turn == WHITE or not isinstance(self.game.black_player, ChessAI):
                            row, col = self.game._get_row_col_from_pos(mouse_pos)
                            self.game._handle_click(row, col)
                elif self.state == "game" and self.paused:
                    self._check_button_clicks(self.pause_menu_buttons, mouse_pos)
                elif self.state == "game_over":
                    self._check_button_clicks(self.game_over_buttons, mouse_pos)
    
    def _check_button_clicks(self, buttons, mouse_pos):
        """Check if any buttons were clicked"""
        for button in buttons:
            button.update(mouse_pos)
            if button.is_hovered and pygame.mouse.get_pressed()[0]:
                self._handle_button_click(button)
                return
    
    def _handle_button_click(self, button):
        """Handle button click based on button text and current state"""
        if self.debug:
            print(f"Button clicked: {button.text}")
            
        if self.state == "main_menu":
            if button.text == "Singleplayer":
                self.state = "difficulty"
            elif button.text == "Multiplayer":
                self.game_mode = "multiplayer"
                self._start_game()
            elif button.text == "Quit":
                self.running = False
        
        elif self.state == "difficulty":
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
        
        elif self.state == "game" and self.paused:
            if button.text == "Resume":
                self.paused = False
            elif button.text == "Back to Menu":
                self._cancel_ai_thread()
                self.game = None
                self.state = "main_menu"
                self.paused = False
            elif button.text == "Quit Game":
                self._cancel_ai_thread()
                self.running = False
        
        elif self.state == "game_over":
            if button.text == "Back to Menu":
                self._cancel_ai_thread()
                self.game = None
                self.state = "main_menu"
            elif button.text == "Play Again":
                self._cancel_ai_thread()
                self._start_game()
    
    def _handle_main_menu(self):
        """Handle main menu state"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        font = pygame.font.SysFont('Arial', 60, True)
        title = font.render("Python Chess", True, self.title_color)
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Update and draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.main_menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        pygame.display.update()
    
    def _handle_difficulty_menu(self):
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
        mouse_pos = pygame.mouse.get_pos()
        for button in self.difficulty_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        pygame.display.update()
    
    def _handle_pause_menu(self):
        """Handle pause menu overlay"""
        # Keep the game displayed in the background
        
        # Draw semi-transparent overlay
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))  # Black with alpha
        self.screen.blit(s, (0, 0))
        
        # Draw pause menu title
        font = pygame.font.SysFont('Arial', 50, True)
        title = font.render("Game Paused", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Update and draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.pause_menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        # Draw key hint
        hint_font = pygame.font.SysFont('Arial', 20, True)
        hint = hint_font.render("Press ESC to resume", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(WIDTH//2, HEIGHT - 50))
        self.screen.blit(hint, hint_rect)
        
        pygame.display.update()
    
    def _ai_calculate_move(self):
        """Calculate AI move in a separate thread"""
        try:
            # Get the move from AI
            move = self.game.black_player.get_move(self.game.board)
            self.ai_move = move
        except Exception as e:
            print(f"AI error: {str(e)}")
            self.ai_move = None
        finally:
            self.ai_thinking = False
    
    def _cancel_ai_thread(self):
        """Cancel any running AI thread"""
        if self.ai_thread and self.ai_thread.is_alive():
            # Can't actually cancel a thread in Python,
            # but we can set the flag to ignore the result
            self.ai_thinking = False
            self.ai_thread = None
            self.ai_move = None
    
    def _handle_game(self):
        """Handle game state"""
        if not self.game:
            self.state = "main_menu"
            return
            
        # Check if game is over
        if self.game.game_over:
            self.state = "game_over"
            return
        
        # Process AI move if available
        if self.ai_move and not self.ai_thinking:
            start_pos, end_pos = self.ai_move
            self.game.make_move(start_pos, end_pos)
            self.ai_move = None
        
        # Start AI move calculation if needed
        if (self.game.turn == BLACK and 
            isinstance(self.game.black_player, ChessAI) and 
            not self.ai_thinking and 
            not self.ai_move and 
            not self.game.game_over):
            
            self.ai_thinking = True
            self.ai_start_time = time.time()
            # Start AI calculation in a separate thread
            self.ai_thread = threading.Thread(target=self._ai_calculate_move)
            self.ai_thread.daemon = True  # Thread will exit when main program exits
            self.ai_thread.start()
        
        # Draw the game
        self.game._draw()
        
        # Draw AI thinking indicator if needed
        if self.ai_thinking:
            elapsed_time = time.time() - self.ai_start_time
            self._draw_thinking_indicator(elapsed_time)
        
        # Draw key hint for pause menu
        hint_font = pygame.font.SysFont('Arial', 16, True)
        hint = hint_font.render("Press ESC for menu", True, (50, 50, 50))
        hint_rect = hint.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
        self.screen.blit(hint, hint_rect)
        
        pygame.display.update()
    
    def _draw_thinking_indicator(self, elapsed_time):
        """Draw an indicator when AI is thinking"""
        # Create a semi-transparent overlay at the bottom
        s = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, HEIGHT - 40))
        
        # Add thinking text with animated dots
        dots = "." * (int(elapsed_time * 2) % 4)
        font = pygame.font.SysFont('Arial', 20, True)
        text = f"AI thinking{dots}"
        text_surface = font.render(text, True, pygame.Color('white'))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 20))
        self.screen.blit(text_surface, text_rect)
    
    def _handle_game_over(self):
        """Handle game over screen"""
        if not self.game:
            self.state = "main_menu"
            return
            
        # Draw the game board in the background
        self.game._draw()
        
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
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        pygame.display.update()
    
    def _start_game(self):
        """Start a new game with the selected settings"""
        # Create new game instance
        self.game = ChessGame()
        self.game.set_screen(self.screen)
        
        # Reset AI threading variables
        self.ai_thinking = False
        self.ai_thread = None
        self.ai_move = None
        
        if self.game_mode == "singleplayer":
            # Set up AI with selected difficulty
            self.game.black_player = ChessAI(BLACK, self.difficulty)
        else:  # multiplayer
            # Set up human player for black
            self.game.black_player = Player(BLACK)
        
        self.state = "game"
        self.paused = False


# For testing directly
if __name__ == "__main__":
    menu = MenuSystem()
    menu.run()
    pygame.quit() 