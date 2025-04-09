#!/usr/bin/env python3
"""
Chess Game - Main Entry Point
"""
import pygame
from chess_game.game import ChessGame

def main():
    """Main function to run the chess game"""
    # Initialize the game
    game = ChessGame()
    # Start the game loop
    game.run()

if __name__ == "__main__":
    main()
