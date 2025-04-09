#!/usr/bin/env python3
"""
Chess Game - Main Entry Point
"""
import pygame
from chess_game.menu import MenuSystem

def main():
    """Main function to run the chess game"""
    # Initialize pygame
    pygame.init()
    
    # Start the menu system
    menu = MenuSystem()
    menu.run()
    
    # Clean up pygame
    pygame.quit()

if __name__ == "__main__":
    main()
