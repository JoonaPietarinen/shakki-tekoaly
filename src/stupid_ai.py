import random
import time
from board import Board
from moves import generate_legal_moves


def set_board(board: Board, board_position: str):
    # Set the board to a given FEN position
    print(f"Set board to {board_position}!")
    board.set_fen(board_position)


def make_move(board: Board):
    # Make a random legal move
    legal_moves = generate_legal_moves(board)
    if not legal_moves:
        raise RuntimeError("No legal moves available")
    print(f"I found {len(legal_moves)} legal moves: {', '.join(legal_moves)}")
    choice = random.choice(legal_moves)
    board.make_move(choice)
    return choice


def main():
    board = Board()
    while True:
        opponent_move = input()
        time.sleep(random.randrange(1, 10) / 100)
        if opponent_move.startswith("BOARD:"):
            set_board(board, opponent_move.removeprefix("BOARD:"))
        elif opponent_move.startswith("RESET:"):
            board = Board()
            print("Board reset!")
        elif opponent_move.startswith("PLAY:"):
            choice = make_move(board)
            print(f"I chose {choice}!")
            print(f"MOVE:{choice}")
        elif opponent_move.startswith("MOVE:"):
            move = opponent_move.removeprefix("MOVE:")
            board.make_move(move)
            print(f"Received move: {move}")
        else:
            print(f"Unknown tag: {opponent_move}")
            break


if __name__ == "__main__":
    main()
