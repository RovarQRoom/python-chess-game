"""Chess Game - Network Module for Multiplayer"""
import socket
import threading
import pickle
import logging
import json
import time
from .constants import WHITE, BLACK

# Set up logging
logging.basicConfig(
    filename='chess_network.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Network constants
PORT = 5555
SERVER_IP = "0.0.0.0"  # Listen on all available interfaces
HEADER_SIZE = 10
MAX_CONNECTIONS = 2

class ChessServer:
    """Server class for hosting a chess game"""
    
    def __init__(self, port=PORT):
        """Initialize the server"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        self.server_ip = SERVER_IP
        self.connections = {}  # {connection: player_id}
        self.games = {}  # {game_id: {white: connection, black: connection}}
        self.current_game_id = 0
        self.running = False
        self.server_thread = None
        logging.info("Chess server initialized")
    
    def start(self):
        """Start the server"""
        try:
            # Allows socket to be reused
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.server_ip, self.port))
            self.server.listen(MAX_CONNECTIONS)
            self.running = True
            self.server_thread = threading.Thread(target=self._handle_connections)
            self.server_thread.daemon = True
            self.server_thread.start()
            logging.info(f"Server started on {self.server_ip}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Server start error: {str(e)}", exc_info=True)
            return False
    
    def stop(self):
        """Stop the server"""
        self.running = False
        # Close all client connections
        for conn in list(self.connections.keys()):
            try:
                conn.close()
            except:
                pass
        # Close server socket
        try:
            self.server.close()
        except:
            pass
        logging.info("Server stopped")
    
    def _handle_connections(self):
        """Handle incoming connections"""
        while self.running:
            try:
                # Accept new connection
                client, addr = self.server.accept()
                logging.info(f"Connection from {addr}")
                
                # Start a thread to handle this client
                thread = threading.Thread(target=self._handle_client, args=(client, addr))
                thread.daemon = True
                thread.start()
            except Exception as e:
                if self.running:  # Only log if we didn't stop intentionally
                    logging.error(f"Connection handling error: {str(e)}", exc_info=True)
    
    def _handle_client(self, client, addr):
        """Handle communication with a client"""
        try:
            # Send greeting to client
            self._send_msg(client, json.dumps({"type": "connect", "status": "ok"}))
            
            # Add to connections with a temporary player_id
            self.connections[client] = None
            
            # Find or create a game for this player
            game_id, player_color = self._assign_to_game(client)
            player_id = f"game_{game_id}_{player_color}"
            self.connections[client] = player_id
            
            # Inform client about their assigned game and color
            self._send_msg(client, json.dumps({
                "type": "game_assignment", 
                "game_id": game_id,
                "color": "white" if player_color == WHITE else "black"
            }))
            
            # If both players are connected, start the game
            if len(self.games[game_id]) == 2:
                # Notify both players that the game is starting
                white_conn = self.games[game_id]["white"]
                black_conn = self.games[game_id]["black"]
                
                start_msg = json.dumps({"type": "game_start"})
                self._send_msg(white_conn, start_msg)
                self._send_msg(black_conn, start_msg)
                
                logging.info(f"Game {game_id} started with both players")
            
            # Main client communication loop
            while self.running:
                try:
                    # Receive data from client
                    msg = self._recv_msg(client)
                    if not msg:
                        break
                    
                    data = json.loads(msg)
                    self._process_client_message(client, data, game_id, player_color)
                    
                except ConnectionResetError:
                    logging.info(f"Client {addr} disconnected")
                    break
                except Exception as e:
                    logging.error(f"Client handling error: {str(e)}", exc_info=True)
                    break
                    
        except Exception as e:
            logging.error(f"Client thread error: {str(e)}", exc_info=True)
        finally:
            # Clean up when client disconnects
            self._cleanup_client(client)
            logging.info(f"Client {addr} connection closed")
    
    def _cleanup_client(self, client):
        """Clean up resources when a client disconnects"""
        player_id = self.connections.get(client)
        if player_id:
            game_id = int(player_id.split('_')[1])
            if game_id in self.games:
                # Remove player from game
                if "white" in self.games[game_id] and self.games[game_id]["white"] == client:
                    del self.games[game_id]["white"]
                if "black" in self.games[game_id] and self.games[game_id]["black"] == client:
                    del self.games[game_id]["black"]
                
                # If game is empty, remove it
                if not self.games[game_id]:
                    del self.games[game_id]
                else:
                    # Notify other player about disconnection
                    other_player = None
                    if "white" in self.games[game_id]:
                        other_player = self.games[game_id]["white"]
                    elif "black" in self.games[game_id]:
                        other_player = self.games[game_id]["black"]
                    
                    if other_player:
                        try:
                            self._send_msg(other_player, json.dumps({
                                "type": "opponent_disconnected"
                            }))
                        except:
                            pass
        
        if client in self.connections:
            del self.connections[client]
        
        try:
            client.close()
        except:
            pass
    
    def _process_client_message(self, client, data, game_id, player_color):
        """Process a message from a client"""
        msg_type = data.get("type")
        
        if msg_type == "move":
            # Forward move to the other player
            other_player = None
            if player_color == WHITE and "black" in self.games[game_id]:
                other_player = self.games[game_id]["black"]
            elif player_color == BLACK and "white" in self.games[game_id]:
                other_player = self.games[game_id]["white"]
            
            if other_player:
                try:
                    self._send_msg(other_player, json.dumps({
                        "type": "opponent_move",
                        "start": data.get("start"),
                        "end": data.get("end")
                    }))
                except Exception as e:
                    logging.error(f"Error forwarding move: {str(e)}", exc_info=True)
    
    def _assign_to_game(self, client):
        """Assign a client to a game, either existing or new"""
        # Look for a game with an empty slot
        for game_id, players in self.games.items():
            if "white" not in players:
                players["white"] = client
                return game_id, WHITE
            elif "black" not in players:
                players["black"] = client
                return game_id, BLACK
        
        # No game with empty slots, create a new one
        game_id = self.current_game_id
        self.current_game_id += 1
        self.games[game_id] = {"white": client}
        return game_id, WHITE
    
    def _send_msg(self, client, msg):
        """Send a message to a client with a header indicating message size"""
        try:
            message = msg.encode("utf-8")
            header = f"{len(message):<{HEADER_SIZE}}".encode("utf-8")
            client.send(header + message)
        except Exception as e:
            logging.error(f"Send error: {str(e)}", exc_info=True)
            raise
    
    def _recv_msg(self, client):
        """Receive a message from a client, using header for message size"""
        try:
            # Get message header
            header = client.recv(HEADER_SIZE)
            if not header:
                return None
            
            # Get message length from header
            msg_len = int(header.decode("utf-8").strip())
            
            # Receive message data based on length
            chunks = []
            bytes_received = 0
            while bytes_received < msg_len:
                chunk = client.recv(min(msg_len - bytes_received, 4096))
                if not chunk:
                    return None
                chunks.append(chunk)
                bytes_received += len(chunk)
            
            # Combine chunks and decode
            data = b"".join(chunks).decode("utf-8")
            return data
        except Exception as e:
            logging.error(f"Receive error: {str(e)}", exc_info=True)
            raise


class ChessClient:
    """Client class for connecting to a chess server"""
    
    def __init__(self):
        """Initialize the client"""
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_ip = None
        self.port = PORT
        self.connected = False
        self.game_id = None
        self.player_color = None
        self.callback = None
        self.receive_thread = None
        logging.info("Chess client initialized")
    
    def connect(self, server_ip):
        """Connect to the server"""
        try:
            self.server_ip = server_ip
            self.client.connect((self.server_ip, self.port))
            self.connected = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            logging.info(f"Connected to server at {server_ip}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Connection error: {str(e)}", exc_info=True)
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.connected = False
        try:
            self.client.close()
        except:
            pass
        logging.info("Disconnected from server")
    
    def send_move(self, start, end):
        """Send a move to the server"""
        if not self.connected:
            return False
        
        try:
            msg = json.dumps({
                "type": "move",
                "start": start,
                "end": end
            })
            self._send_msg(msg)
            return True
        except Exception as e:
            logging.error(f"Send move error: {str(e)}", exc_info=True)
            return False
    
    def register_callback(self, callback):
        """Register a callback function to handle received messages"""
        self.callback = callback
    
    def _receive(self):
        """Receive messages from the server"""
        while self.connected:
            try:
                msg = self._recv_msg()
                if not msg:
                    break
                
                data = json.loads(msg)
                self._process_server_message(data)
                
            except ConnectionResetError:
                logging.info("Server connection lost")
                break
            except Exception as e:
                logging.error(f"Receive error: {str(e)}", exc_info=True)
                break
        
        self.connected = False
        if self.callback:
            try:
                self.callback({"type": "disconnected"})
            except Exception as e:
                logging.error(f"Callback error: {str(e)}", exc_info=True)
    
    def _process_server_message(self, data):
        """Process a message from the server"""
        msg_type = data.get("type")
        
        if msg_type == "game_assignment":
            # Game assignment
            self.game_id = data.get("game_id")
            self.player_color = WHITE if data.get("color") == "white" else BLACK
            logging.info(f"Assigned to game {self.game_id} as {data.get('color')}")
        
        # Call the callback function if registered
        if self.callback:
            try:
                self.callback(data)
            except Exception as e:
                logging.error(f"Callback error: {str(e)}", exc_info=True)
    
    def _send_msg(self, msg):
        """Send a message to the server with a header indicating message size"""
        try:
            message = msg.encode("utf-8")
            header = f"{len(message):<{HEADER_SIZE}}".encode("utf-8")
            self.client.send(header + message)
        except Exception as e:
            logging.error(f"Send error: {str(e)}", exc_info=True)
            raise
    
    def _recv_msg(self):
        """Receive a message from the server, using header for message size"""
        try:
            # Get message header
            header = self.client.recv(HEADER_SIZE)
            if not header:
                return None
            
            # Get message length from header
            msg_len = int(header.decode("utf-8").strip())
            
            # Receive message data based on length
            chunks = []
            bytes_received = 0
            while bytes_received < msg_len:
                chunk = self.client.recv(min(msg_len - bytes_received, 4096))
                if not chunk:
                    return None
                chunks.append(chunk)
                bytes_received += len(chunk)
            
            # Combine chunks and decode
            data = b"".join(chunks).decode("utf-8")
            return data
        except Exception as e:
            logging.error(f"Receive error: {str(e)}", exc_info=True)
            raise


class NetworkPlayer:
    """Player class that handles networked gameplay"""
    
    def __init__(self, color, client):
        """Initialize a network player with the specified color"""
        self.color = color
        self.client = client
        self.waiting_for_move = False
        self.last_move = None
    
    def get_move(self, board):
        """Get move from the network - not used directly"""
        return None
    
    def set_move(self, start, end):
        """Set the move received from the network"""
        self.last_move = (start, end)
        self.waiting_for_move = False
    
    def send_move(self, start, end):
        """Send a move to the server"""
        return self.client.send_move(start, end) 