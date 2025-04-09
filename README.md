# Python Chess Game

A complete chess game implementation in Python with GUI and AI player.

## Features

- Complete chess rule implementation with all legal moves
- Special moves: castling, en passant, pawn promotion
- Chess AI with minimax algorithm and alpha-beta pruning
- Position evaluation based on material and strategic factors
- Game state detection (checkmate, stalemate, draw conditions)
- Simple and clean GUI using Pygame

## Requirements

- Python 3.6+
- Pygame 2.5.2+

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## How to Play

Run the game with:

```
python main.py
```

### Game Controls

- Click on a piece to select it
- Click on a highlighted square to move the selected piece
- The game automatically checks for valid moves, check, checkmate, and stalemate
- White plays first, followed by the AI (black)

## Project Structure

- `main.py` - Main entry point
- `chess_game/` - Main package containing game logic
  - `game.py` - Game loop and UI management
  - `board.py` - Chess board representation and game rules
  - `pieces.py` - Individual chess piece classes and movement rules
  - `player.py` - Player base class
  - `ai.py` - AI implementation with minimax and position evaluation
  - `constants.py` - Game constants and evaluation tables
- `assets/` - Directory for piece images

## Chess AI

The AI uses a minimax algorithm with alpha-beta pruning to search for the best move. It evaluates positions based on:

1. Material count - Basic piece values
2. Piece position - Positional tables for each piece type
3. King safety - Evaluation of king's safety including castling and pawn shield
4. Pawn structure - Evaluation of pawn formations including doubled pawns, isolated pawns, and passed pawns
5. Mobility - Count of available legal moves

## Adding Custom Chess Pieces

The game looks for chess piece images in the assets directory. If you want to add your own piece images:

1. Create PNG images for each piece with these filenames:
   - White pieces: wP.png, wR.png, wN.png, wB.png, wQ.png, wK.png
   - Black pieces: bP.png, bR.png, bN.png, bB.png, bQ.png, bK.png
2. Place them in the assets/ directory

If no images are found, the game will use text-based pieces as a fallback.

## License

This project is available under the MIT License. 