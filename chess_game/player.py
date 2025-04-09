"""Chess Game - Player Module"""

class Player:
    """Base class for players (human or AI)"""
    
    def __init__(self, color):
        """Initialize a player with the specified color"""
        self.color = color
        
    def get_move(self, board):
        """Human players make moves through UI interaction, so this is not used"""
        return None 