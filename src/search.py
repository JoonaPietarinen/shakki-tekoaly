"""
Chess AI search algorithms.
Negamax with alpha-beta pruning and transposition table.
"""

from evaluation import evaluate_from_perspective
from moves import generate_legal_moves
from board import compute_zobrist_hash
import time

search_stats = {
    'nodes_searched': 0,
    'tt_hits': 0,
    'tt_stores': 0
}

# Transposition table flags
EXACT, LOWER, UPPER = 0, 1, 2

# Transposition table: {zobrist_hash: (depth, score, flag, best_move)}
transposition_table = {}


def clear_transposition_table():
    """Clear the transposition table between games."""
    global transposition_table
    transposition_table = {}


def negamax(board, depth, alpha, beta, color=1, tt_move=None):
    """
    Negamax search with alpha-beta pruning and transposition table.
    
    Args:
        board: Current board state
        depth: Remaining search depth
        alpha: Alpha bound
        beta: Beta bound
        color: Not used in negamax formulation
    
    Returns:
        (score, best_move) tuple
    """
    global search_stats
    search_stats['nodes_searched'] += 1

    board_hash = compute_zobrist_hash(board)
    alpha_orig = alpha
    
    # Transposition table lookup
    if board_hash in transposition_table:
        entry = transposition_table[board_hash]
        entry_depth, entry_score, entry_flag = entry['depth'], entry['score'], entry['flag']
        tt_move = entry.get('move')
        if entry_depth >= depth:
            search_stats['tt_hits'] += 1
            if entry_flag == EXACT:
                return entry_score, entry.get('move')
            elif entry_flag == LOWER:
                alpha = max(alpha, entry_score)
            elif entry_flag == UPPER:
                beta = min(beta, entry_score)
            if alpha >= beta:
                return entry_score, entry.get('move')
    
    # Base case: depth 0 or game over
    if depth == 0:
        return evaluate_from_perspective(board), None

    moves = generate_legal_moves(board)
    if not moves:
        # Checkmate or stalemate
        return -100000, None
    
    if tt_move and tt_move in moves:
        moves.remove(tt_move)
        moves.insert(0, tt_move)

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
            # Beta cutoff
            break
    if alpha >= beta:
        flag = LOWER
    elif best_score > alpha_orig:
        flag = EXACT
    else:
        flag = UPPER
    
    
    # Store in transposition table
    transposition_table[board_hash] = {
        'depth': depth,
        'score': best_score,
        'flag': flag,
        'move': best_move
    }
    search_stats['tt_stores'] += 1
    return best_score, best_move

def find_best_move(board, depth, time_limit):
    """
    Find the best move using iterative deepening with negamax search and transposition table.
    Instead of soft or hard time limits, we use smart time management to decide when to stop deepening.
    """
    best_move = None
    best_score = None
    start_time = time.time()
    
    # Iterative deepening: search depth 1, 2, 3... up to max_depth
    for current_depth in range(1, depth + 1):
        elapsed = time.time() - start_time
        
        # Smart time management: don't start new iteration if unlikely to finish
        if time_limit:
            if elapsed > time_limit:
                # Soft limit: time expired, use best move from previous iteration
                break
            
            # Predict if we have enough time for next iteration
            # Next depth typically takes ~3-5x longer than previous
            # Don't start if we've used more than 40% of time budget
            if current_depth > 1 and elapsed > 0.4 * time_limit:
                break
        
        score, move = negamax(board, current_depth, float('-inf'), float('inf'))
        
        if move:
            best_move = move
            best_score = score
    
    return best_move, best_score

def print_search_stats():
    print(f"Nodes searched: {search_stats['nodes_searched']}")
    print(f"TT hits: {search_stats['tt_hits']} ({100*search_stats['tt_hits']/search_stats['nodes_searched']:.1f}%)")
    print(f"TT stores: {search_stats['tt_stores']}")