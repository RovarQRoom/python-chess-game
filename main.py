#!/usr/bin/env python3
"""
Chess Game - Main Entry Point
"""
import pygame
import sys
import argparse
import socket
import logging

# Import the fixed menu system
from fixed_menu import MenuSystem
from chess_game.network import ChessServer

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket to determine the active network interface
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS server
        s.connect(("8.8.8.8", 80))
        # Get the IP address
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logging.error(f"Error getting local IP: {str(e)}")
        return "127.0.0.1"  # Fallback to localhost

def main():
    """Main function to run the chess game"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Python Chess Game')
    parser.add_argument('--server', action='store_true', help='Run as a dedicated server only')
    parser.add_argument('--port', type=int, default=5555, help='Port to use for server (default: 5555)')
    args = parser.parse_args()
    
    # Setup logging for server mode
    logging.basicConfig(
        filename='chess_server.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Run in server-only mode if requested
    if args.server:
        print("Starting chess server...")
        server = ChessServer(port=args.port)
        if server.start():
            local_ip = get_local_ip()
            print(f"Chess server running at {local_ip}:{args.port}")
            print("Press Ctrl+C to stop the server")
            try:
                # Keep the server running until interrupted
                while True:
                    pass
            except KeyboardInterrupt:
                print("\nStopping server...")
                server.stop()
                print("Server stopped")
        else:
            print("Failed to start server")
        return
    
    # Normal game mode with GUI
    pygame.init()
    
    # Start the menu system
    menu = MenuSystem()
    menu.run()
    
    # Clean up pygame
    pygame.quit()

if __name__ == "__main__":
    main()
