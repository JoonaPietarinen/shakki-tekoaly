import time
from board import Board
from moves import generate_legal_moves, is_checkmate, is_stalemate, is_draw_by_fifty_moves
from search import find_best_move, clear_transposition_table


def set_board(board: Board, board_position: str):
    """Set the board to a given FEN position."""
    print(f"Set board to {board_position}!")
    board.set_fen(board_position)


def make_move(board: Board, search_depth=4):
    """
    Select and play the best move using negamax search.
    
    Args:
        board: Current board state
        search_depth: Search depth (default 4)
    
    Returns:
        Chosen move in UCI format
    """
    legal_moves = generate_legal_moves(board)
    
    if not legal_moves:
        if is_checkmate(board):
            print("Checkmate!")
        elif is_stalemate(board):
            print("Stalemate!")
        raise RuntimeError("No legal moves available")
    
    if is_draw_by_fifty_moves(board):
        print("Draw by fifty-move rule!")
    
    print(f"Searching with depth {search_depth}...")
    choice = find_best_move(board, depth=search_depth)
    
    board.make_move(choice)
    return choice


def main():
    """Main loop: receive commands and play moves."""
    board = Board()
    search_depth = 4
    
    while True:
        opponent_move = input()
        
        if opponent_move.startswith("BOARD:"):
            set_board(board, opponent_move.removeprefix("BOARD:"))
        elif opponent_move.startswith("RESET:"):
            board = Board()
            clear_transposition_table()
            print("Board reset!")
        elif opponent_move.startswith("PLAY:"):
            try:
                choice = make_move(board, search_depth=search_depth)
                print(f"I chose {choice}!")
                print(f"MOVE:{choice}")
            except RuntimeError as e:
                print(f"Game over: {e}")
                break
        elif opponent_move.startswith("MOVE:"):
            move = opponent_move.removeprefix("MOVE:")
            board.make_move(move)
            print(f"Received move: {move}")
        else:
            print(f"Unknown tag: {opponent_move}")
            break


if __name__ == "__main__":
    main()
