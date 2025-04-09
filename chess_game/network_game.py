"""Chess Game - Network Game Module"""
import pygame
import logging
import threading
import time
from .constants import WIDTH, HEIGHT, WHITE, BLACK
from .game import ChessGame
from .network import ChessClient, NetworkPlayer

# Set up logging
logging.basicConfig(
    filename='chess_game.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class NetworkGame:
    """Manages a networked chess game session"""
    
    def __init__(self, screen, is_server=False, server_ip=None):
        """Initialize a network game session
        
        Args:
            screen: Pygame screen to draw on
            is_server: Whether this instance should start a server
            server_ip: IP address of the server to connect to (client mode only)
        """
        self.screen = screen
        self.is_server = is_server
        self.server_ip = server_ip
        self.game = None
        self.client = None
        self.server = None
        self.connected = False
        self.waiting_for_opponent = True
        self.game_status = "connecting"  # connecting, waiting, playing, game_over
        self.status_message = "Connecting to server..."
        self.opponent_disconnected = False
        
        # Initialize the game
        self.game = ChessGame()
        self.game.set_screen(self.screen)
        
        # Initialize network components
        self._setup_network()
    
    def _setup_network(self):
        """Set up the network components (client and server if needed)"""
        # Create client
        self.client = ChessClient()
        self.client.register_callback(self._handle_network_message)
        
        # Connect to server or start server if needed
        if self.is_server:
            # Import server class only if we need it
            from .network import ChessServer
            
            # Start server
            self.server = ChessServer()
            success = self.server.start()
            
            if success:
                logging.info("Server started successfully")
                # Connect to our own server
                time.sleep(0.5)  # Wait a bit for server to initialize
                self.server_ip = "127.0.0.1"  # Connect to localhost
            else:
                logging.error("Failed to start server")
                self.game_status = "error"
                self.status_message = "Failed to start server"
                return
                
        # Connect client to server
        if self.server_ip:
            self.status_message = f"Connecting to server at {self.server_ip}..."
            logging.info(f"Connecting to server at {self.server_ip}")
            success = self.client.connect(self.server_ip)
            
            if success:
                self.connected = True
                self.game_status = "waiting"
                self.status_message = "Waiting for opponent..."
                logging.info("Connected to server, waiting for opponent")
            else:
                self.game_status = "error"
                self.status_message = "Failed to connect to server"
                logging.error("Failed to connect to server")
    
    def _handle_network_message(self, data):
        """Handle messages received from the server"""
        msg_type = data.get("type")
        
        if msg_type == "game_assignment":
            color = data.get("color")
            logging.info(f"Assigned to game as {color}")
            
            # Sync our color with the assigned color
            if color == "white":
                self.game.white_player = NetworkPlayer(WHITE, self.client)
                self.local_color = WHITE
            else:
                self.game.black_player = NetworkPlayer(BLACK, self.client)
                self.local_color = BLACK
        
        elif msg_type == "game_start":
            self.waiting_for_opponent = False
            self.game_status = "playing"
            self.status_message = "Game started!"
            logging.info("Game started with opponent")
        
        elif msg_type == "opponent_move":
            # Process move from opponent
            start = data.get("start")
            end = data.get("end")
            
            if start and end:
                logging.info(f"Received opponent move: {start} to {end}")
                # Make the move on our board
                self.game.make_move(start, end)
        
        elif msg_type == "opponent_disconnected":
            self.opponent_disconnected = True
            self.status_message = "Opponent disconnected"
            logging.info("Opponent disconnected")
        
        elif msg_type == "disconnected":
            self.connected = False
            self.game_status = "error"
            self.status_message = "Disconnected from server"
            logging.info("Disconnected from server")
    
    def handle_click(self, row, col):
        """Handle a click on the board"""
        if self.game_status != "playing" or self.opponent_disconnected:
            return
        
        # Check if it's our turn
        if (self.local_color == WHITE and self.game.turn == WHITE) or \
           (self.local_color == BLACK and self.game.turn == BLACK):
            
            # Try making the move locally
            original_turn = self.game.turn
            result = self.game._handle_click(row, col)
            
            # If the turn changed, a move was made - send it to the server
            if result == "move_made" or (original_turn != self.game.turn):
                # The last move is stored in the game's move history
                # For simplicity, we're assuming the move was successful
                # A more robust implementation would track the exact move made
                if hasattr(self.game, "last_move") and self.game.last_move:
                    start, end = self.game.last_move
                    self.client.send_move(start, end)
    
    def update(self):
        """Update the game state"""
        # Nothing to do here for now, networking is handled in separate threads
        pass
    
    def draw(self):
        """Draw the game state"""
        if self.game_status == "playing" and not self.opponent_disconnected:
            # Draw the game normally
            self.game._draw()
        else:
            # Draw a waiting screen
            self.screen.fill((240, 240, 240))
            font = pygame.font.SysFont('Arial', 36, True)
            
            # Draw status message
            text = font.render(self.status_message, True, (0, 0, 0))
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(text, text_rect)
            
            # Draw connection details if connected
            if self.connected:
                if self.is_server:
                    server_text = f"Server running at {self.server_ip}"
                    server_surface = pygame.font.SysFont('Arial', 24).render(
                        server_text, True, (0, 100, 0))
                    self.screen.blit(server_surface, (WIDTH//2 - server_surface.get_width()//2, HEIGHT//2 + 50))
    
    def cleanup(self):
        """Clean up resources"""
        if self.client:
            self.client.disconnect()
        
        if self.server:
            self.server.stop() 