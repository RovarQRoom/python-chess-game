"""Chess Game - Menu System (Fixed Version)"""
import pygame
import threading
import time
import socket
from chess_game.constants import WIDTH, HEIGHT, FPS, LIGHT_SQUARE, DARK_SQUARE
from chess_game.game import ChessGame
from chess_game.ai import ChessAI
from chess_game.player import Player
from chess_game.constants import WHITE, BLACK
from chess_game.network_game import NetworkGame

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
            Button("Singleplayer", WIDTH//2 - 150, HEIGHT//2 - 80, 300, 60, 
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Local Multiplayer", WIDTH//2 - 150, HEIGHT//2, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Network Multiplayer", WIDTH//2 - 150, HEIGHT//2 + 80, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Quit", WIDTH//2 - 150, HEIGHT//2 + 160, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color)
        ]
        
        # Network menu buttons
        self.network_menu_buttons = [
            Button("Host Game", WIDTH//2 - 150, HEIGHT//2 - 50, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Join Game", WIDTH//2 - 150, HEIGHT//2 + 30, 300, 60,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Back", 50, HEIGHT - 80, 120, 50,
                  self.button_color, self.button_hover_color, self.button_text_color, 24)
        ]
        
        # Join game menu (IP entry)
        self.ip_input = ""
        self.ip_active = False
        self.join_menu_buttons = [
            Button("Connect", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50,
                  self.button_color, self.button_hover_color, self.button_text_color),
            Button("Back", 50, HEIGHT - 80, 120, 50,
                  self.button_color, self.button_hover_color, self.button_text_color, 24)
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
        self.network_game = None
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
            elif self.state == "network_menu":
                self._handle_network_menu()
            elif self.state == "join_game":
                self._handle_join_game()
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
                
                # IP input for join game menu
                if self.state == "join_game" and self.ip_active:
                    if event.key == pygame.K_RETURN:
                        # Try to connect
                        self._join_network_game(self.ip_input)
                    elif event.key == pygame.K_BACKSPACE:
                        self.ip_input = self.ip_input[:-1]
                    else:
                        # Add character if it's a valid IP character
                        if event.unicode in "0123456789.":
                            self.ip_input += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True
                
                # Handle click based on current state
                if self.state == "main_menu":
                    self._check_button_clicks(self.main_menu_buttons, mouse_pos)
                elif self.state == "difficulty":
                    self._check_button_clicks(self.difficulty_buttons, mouse_pos)
                elif self.state == "network_menu":
                    self._check_button_clicks(self.network_menu_buttons, mouse_pos)
                elif self.state == "join_game":
                    # Check if clicked in IP input box
                    ip_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 30, 300, 40)
                    self.ip_active = ip_rect.collidepoint(mouse_pos)
                    
                    # Check buttons
                    self._check_button_clicks(self.join_menu_buttons, mouse_pos)
                elif self.state == "game" and not self.paused:
                    if self.game and not self.game.game_over and not self.ai_thinking:
                        if self.game.turn == WHITE or not isinstance(self.game.black_player, ChessAI):
                            row, col = self.game._get_row_col_from_pos(mouse_pos)
                            self.game._handle_click(row, col)
                    elif self.network_game:
                        row, col = self.network_game.game._get_row_col_from_pos(mouse_pos)
                        self.network_game.handle_click(row, col)
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
            elif button.text == "Local Multiplayer":
                self.game_mode = "local_multiplayer"
                self._start_game()
            elif button.text == "Network Multiplayer":
                self.state = "network_menu"
            elif button.text == "Quit":
                self.running = False
        
        elif self.state == "network_menu":
            if button.text == "Host Game":
                self.game_mode = "network_host"
                self._start_network_game(is_server=True)
            elif button.text == "Join Game":
                self.state = "join_game"
                self.ip_input = ""
                self.ip_active = True
            elif button.text == "Back":
                self.state = "main_menu"
        
        elif self.state == "join_game":
            if button.text == "Connect":
                self._join_network_game(self.ip_input)
            elif button.text == "Back":
                self.state = "network_menu"
        
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
                self._cleanup_game()
                self.state = "main_menu"
                self.paused = False
            elif button.text == "Quit Game":
                self._cancel_ai_thread()
                self._cleanup_game()
                self.running = False
        
        elif self.state == "game_over":
            if button.text == "Back to Menu":
                self._cancel_ai_thread()
                self._cleanup_game()
                self.state = "main_menu"
            elif button.text == "Play Again":
                self._cancel_ai_thread()
                self._cleanup_game()
                self._start_game()
    
    def _handle_main_menu(self):
        """Handle main menu rendering and interaction"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 64, True)
        title_surface = title_font.render("Python Chess", True, self.title_color)
        title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
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
        """Handle game state rendering and interaction"""
        # Check for game over
        if self.game and self.game.game_over:
            self.state = "game_over"
            return
        
        # Regular game handling
        if self.network_game:
            # For network games
            self.network_game.update()
            self.network_game.draw()
            pygame.display.update()
        elif self.game:
            # For regular games (AI or local multiplayer)
            # Handle AI move if it's black's turn
            if self.game.turn == BLACK and not self.game.game_over and isinstance(self.game.black_player, ChessAI) and not self.ai_thinking:
                self.ai_thinking = True
                self.ai_start_time = pygame.time.get_ticks()
                # Start a new thread for AI calculation
                self.ai_thread = threading.Thread(target=self._ai_calculate_move)
                self.ai_thread.daemon = True
                self.ai_thread.start()
            
            # Check if AI has found a move
            if self.ai_thinking and self.ai_move:
                # Apply the AI move
                try:
                    if self.debug:
                        print(f"Applying AI move: {self.ai_move}")
                    self.game.make_move(self.ai_move[0], self.ai_move[1])
                except Exception as e:
                    print(f"Error applying AI move: {str(e)}")
                finally:
                    self.ai_thinking = False
                    self.ai_move = None
                    self.ai_start_time = 0
            
            # Draw the game state
            self.game._draw()
            
            # Draw AI thinking indicator if applicable
            if self.ai_thinking:
                self._draw_thinking_indicator(pygame.time.get_ticks() - self.ai_start_time)
            
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
        # Reset any network game
        self._cleanup_game()
        
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
        elif self.game_mode == "local_multiplayer":
            # Set up human player for black
            self.game.black_player = Player(BLACK)
        
        self.state = "game"
        self.paused = False
    
    def _start_network_game(self, is_server=False, server_ip=None):
        """Start a new network game"""
        # Reset any existing game
        self._cleanup_game()
        
        # Create new network game instance
        self.network_game = NetworkGame(self.screen, is_server=is_server, server_ip=server_ip)
        
        self.state = "game"
        self.paused = False
    
    def _join_network_game(self, ip_address):
        """Join a network game at the specified IP address"""
        if not ip_address:
            return
            
        # Start a network game in client mode
        self._start_network_game(is_server=False, server_ip=ip_address)
    
    def _cleanup_game(self):
        """Clean up game resources"""
        if self.network_game:
            self.network_game.cleanup()
            self.network_game = None
        
        self.game = None
    
    def _handle_network_menu(self):
        """Handle network menu rendering and interaction"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, True)
        title_surface = title_font.render("Network Multiplayer", True, self.title_color)
        title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_surface, title_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.network_menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        pygame.display.update()
    
    def _handle_join_game(self):
        """Handle join game menu rendering and interaction"""
        # Draw background
        self.screen.fill(self.bg_color)
        self.screen.blit(self.board_pattern, (0, 0))
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', 48, True)
        title_surface = title_font.render("Join Game", True, self.title_color)
        title_rect = title_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
        self.screen.blit(title_surface, title_rect)
        
        # Draw IP input field
        ip_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 30, 300, 40)
        pygame.draw.rect(self.screen, (255, 255, 255), ip_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), ip_rect, 2)
        
        font = pygame.font.SysFont('Arial', 24)
        ip_surface = font.render(self.ip_input, True, (0, 0, 0))
        self.screen.blit(ip_surface, (ip_rect.x + 10, ip_rect.y + 10))
        
        # Draw prompt
        prompt_font = pygame.font.SysFont('Arial', 24)
        prompt_surface = prompt_font.render("Enter server IP address:", True, self.title_color)
        prompt_rect = prompt_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        self.screen.blit(prompt_surface, prompt_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.join_menu_buttons:
            button.update(mouse_pos)
            button.draw(self.screen)
        
        pygame.display.update()


# For testing directly
if __name__ == "__main__":
    menu = MenuSystem()
    menu.run()
    pygame.quit() 