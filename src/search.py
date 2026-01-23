from evaluation import evaluate_from_perspective
from moves import generate_legal_moves
import time

# Transposition table flags
EXACT, LOWER, UPPER = 0, 1, 2
transposition_table = {}


def clear_transposition_table():
    """Clear the transposition table between games."""
    global transposition_table
    transposition_table = {}


def negamax(board, depth, alpha, beta, color=1):
    """
    Negamax search with alpha-beta pruning.
    
    Args:
        board: Current board state
        depth: Remaining search depth
        alpha: Alpha bound
        beta: Beta bound
        color: Not used in negamax formulation
    
    Returns:
        (score, best_move) tuple
    """
    # TODO: Implement transposition table lookup
    
    # Base case: depth 0 or game over
    if depth == 0:
        return evaluate_from_perspective(board), None
    
    moves = generate_legal_moves(board)
    if not moves:
        # Checkmate or stalemate
        return -100000, None
    
    # TODO: Order moves for better pruning
    
    best_move = None
    best_score = float('-inf')
    
    for move in moves:
        temp = board.copy()
        temp.make_move(move)
        
        # Recursive negamax call (negate score and swap alpha/beta)
        score, _ = negamax(temp, depth - 1, -beta, -alpha)
        score = -score
        
        if score > best_score:
            best_score = score
            best_move = move
        
        # Alpha-beta pruning
        alpha = max(alpha, score)
        if alpha >= beta:
            break  # Beta cutoff
    
    # TODO: Store result in transposition table
    
    return best_score, best_move


def iterative_deepening(board, max_depth=5, time_limit=None):
    """
    Iterative deepening search: search depth 1, 2, 3... up to max_depth.
    Stops early if time limit is exceeded.
    """
    # TODO:
    pass


def find_best_move(board, depth=4, use_iterative_deepening=False, time_limit=None):
    """Find the best move in the current position."""
    if use_iterative_deepening: # Not implemented yet, so always False
        best_move, _ = iterative_deepening(board, max_depth=depth, time_limit=time_limit)
    else:
        _, best_move = negamax(board, depth, float('-inf'), float('inf'))
    
    return best_move
