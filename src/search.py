"""
Chess AI search algorithms.
Negamax with alpha-beta pruning and transposition table.
Includes quiescence search to avoid horizon effect.
Includes move ordering: history heuristic and MVV-LVA for captures.
"""

from evaluation import evaluate_from_perspective
from moves import generate_legal_moves
from board import coord_to_sq
import time

# Feature flags for optimization testing
ENABLE_QUIESCENCE = True
ENABLE_NULL_WINDOW = True
ENABLE_HISTORY_HEURISTIC = True
ENABLE_KILLER_MOVES = True

search_stats = {
    'nodes_searched': 0,
    'tt_hits': 0,
    'tt_stores': 0,
    'beta_cutoffs': 0,
    'reached_depth': 0,
    'quiescence_nodes': 0
}

# Transposition table flags
EXACT, LOWER, UPPER = 0, 1, 2

# Transposition table: {zobrist_hash: (depth, score, flag, best_move)}
transposition_table = {}

# Killer moves: store best refutation moves per depth
# killer_moves[depth] = [move1, move2]
MAX_DEPTH = 100
killer_moves = [[None, None] for _ in range(MAX_DEPTH)]

# History heuristic: tracks good moves by source-destination
history_table = {}

# Piece values for MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
PIECE_VALUES = {
    'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100,
    'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100
}

def clear_transposition_table():
    """Clear the transposition table and history heuristic between games."""
    global transposition_table, killer_moves, history_table
    transposition_table = {}
    killer_moves = [[None, None] for _ in range(MAX_DEPTH)]
    history_table = {}


def is_capture(board, move: str) -> bool:
    """Check if move is a capture."""
    to_sq = move[2:4]
    tr, tc = coord_to_sq(to_sq)
    return board.grid[tr][tc] != '.'


def mvv_lva_score(board, move: str) -> tuple:
    """
    Most Valuable Victim - Least Valuable Attacker.
    Returns (victim_value, -attacker_value) for sorting captures.
    Higher values are better (captures valuable pieces with cheap pieces).
    """
    from_sq = move[:2]
    to_sq = move[2:4]
    fr, fc = coord_to_sq(from_sq)
    tr, tc = coord_to_sq(to_sq)
    
    victim = board.grid[tr][tc]
    attacker = board.grid[fr][fc]
    
    victim_value = PIECE_VALUES.get(victim, 0)
    attacker_value = PIECE_VALUES.get(attacker, 0)
    
    # Return tuple: higher victim value first, then lower attacker value
    return (victim_value, -attacker_value)


def quiescence(board, alpha, beta, ply=0):
    """
    Quiescence search: search only captures until position is quiet.
    Solves horizon effect by continuing search at peaceful positions.
    
    Args:
        board: Current board state
        alpha: Alpha bound
        beta: Beta bound
        ply: Current ply (for depth limiting)
    
    Returns:
        Best score for current position
    """
    global search_stats
    search_stats['quiescence_nodes'] += 1
    
    # Stand pat: evaluate current position
    # If position is already good enough, we don't need to search further
    stand_pat = evaluate_from_perspective(board)
    
    if stand_pat >= beta:
        return beta
    
    alpha = max(alpha, stand_pat)
    
    # Generate all legal moves and filter to only captures
    all_moves = generate_legal_moves(board)
    interesting_moves = [m for m in all_moves if is_capture(board, m)]
    
    # Sort captures by MVV-LVA (Most Valuable Victim first)
    interesting_moves.sort(key=lambda m: mvv_lva_score(board, m), reverse=True)
    
    # If no captures, position is quiet - return eval
    if not interesting_moves:
        return stand_pat
    
    for move in interesting_moves:
        temp = board.copy()
        temp.make_move(move)
        
        # Recursive quiescence call
        score = -quiescence(temp, -beta, -alpha, ply + 1)
        
        if score >= beta:
            return beta
        
        alpha = max(alpha, score)
    
    return alpha


def negamax(board, depth, alpha, beta, color=1, tt_move=None, ply=0):
    """
    Negamax search with alpha-beta pruning and transposition table.
    Uses history heuristic and killer moves for move ordering.
    Feature flags allow selective optimization testing.
    
    Args:
        board: Current board state
        depth: Remaining search depth
        alpha: Alpha bound
        beta: Beta bound
        color: Not used in negamax formulation
        ply: Current ply from root (for killer moves)
    
    Returns:
        (score, best_move) tuple
    """
    global search_stats
    search_stats['nodes_searched'] += 1

    board_hash = board.hash  # Use incremental hash
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
    
    # Base case: depth 0
    if depth == 0:
        if ENABLE_QUIESCENCE:
            return quiescence(board, alpha, beta, ply), None
        else:
            return evaluate_from_perspective(board), None

    moves = generate_legal_moves(board)
    if not moves:
        # Checkmate or stalemate
        return -100000, None
    
    # Move ordering: TT move first, then killer moves, then history heuristic
    ordered_moves = []
    
    # 1. TT move (best move from previous search)
    if tt_move and tt_move in moves:
        ordered_moves.append(tt_move)
        moves.remove(tt_move)
    
    # 2. Killer moves (good cutoff moves from same depth)
    if ENABLE_KILLER_MOVES and ply < MAX_DEPTH:
        for killer in killer_moves[ply]:
            if killer and killer in moves:
                ordered_moves.append(killer)
                moves.remove(killer)
    
    # 3. Remaining moves sorted by history heuristic
    if ENABLE_HISTORY_HEURISTIC:
        remaining_with_history = [(m, history_table.get(m[:4], 0)) for m in moves]
        remaining_with_history.sort(key=lambda x: x[1], reverse=True)
        ordered_moves.extend([m for m, _ in remaining_with_history])
    else:
        ordered_moves.extend(moves)

    best_move = None
    best_score = float('-inf')
    
    for move in ordered_moves:
        temp = board.copy()
        _ = temp.make_move(move)
        
        # Recursive negamax call (negate score and swap alpha/beta)
        score, _ = negamax(temp, depth - 1, -beta, -alpha, ply=ply+1)
        score = -score
        
        if score > best_score:
            best_score = score
            best_move = move
        
        # Alpha-beta pruning
        alpha = max(alpha, score)
        if alpha >= beta:
            # Beta cutoff: update history heuristic and killer moves
            search_stats['beta_cutoffs'] += 1
            
            # Update history heuristic (quiet moves that cause cutoffs)
            if ENABLE_HISTORY_HEURISTIC and not is_capture(board, move):
                move_key = move[:4]
                history_table[move_key] = history_table.get(move_key, 0) + depth * depth
            
            # Update killer moves
            if ENABLE_KILLER_MOVES and ply < MAX_DEPTH:
                if killer_moves[ply][0] != move:
                    killer_moves[ply][1] = killer_moves[ply][0]
                    killer_moves[ply][0] = move
            
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
    Optionally uses null-window search for faster move evaluation.
    """
    global search_stats
    best_move = None
    best_score = None
    start_time = time.time()
    
    # Iterative deepening: search depth 1, 2, 3... up to max_depth
    for current_depth in range(1, depth + 1):
        search_stats['reached_depth'] = current_depth  # Track current depth
        elapsed = time.time() - start_time
        
        # Smart time management: don't start new iteration if unlikely to finish
        if time_limit:
            if elapsed > time_limit:
                # Soft limit: time expired, use best move from previous iteration
                break
            
            # Predict if we have enough time for next iteration
            # Next depth typically takes ~3-5x longer than previous
            # Don't start if we've used more than 40% of time budget
            if current_depth > 1 and elapsed > 0.4 * time_limit: # pragma: no cover
                break
        
        # Try null-window search first if enabled
        if ENABLE_NULL_WINDOW and best_score is not None:
            # Null-window search: search with narrow window to quickly verify if move is good
            null_score, move = negamax(board, current_depth, best_score, best_score + 1, ply=0)
            
            if null_score >= best_score + 1:
                # Re-search with full window
                score, move = negamax(board, current_depth, float('-inf'), float('inf'), ply=0)
                if move:
                    best_move = move
                    best_score = score
            else:
                # Score is within expected range, use null-window result
                score, move = null_score, move
                if move:
                    best_move = move
                    best_score = null_score
        else:
            # No best_score yet or null-window disabled, do full search
            score, move = negamax(board, current_depth, float('-inf'), float('inf'), ply=0)
            
            if move:
                best_move = move
                best_score = score
    
    return best_move

def print_search_stats(): # pragma: no cover
    print(f"Nodes searched: {search_stats['nodes_searched']}")
    print(f"Quiescence nodes: {search_stats['quiescence_nodes']}")
    print(f"TT hits: {search_stats['tt_hits']} ({100*search_stats['tt_hits']/search_stats['nodes_searched']:.1f}%)")
    print(f"TT stores: {search_stats['tt_stores']}")
    print(f"Beta cutoffs: {search_stats['beta_cutoffs']}")
    print(f"History entries: {len(history_table)}")
    if search_stats.get('reached_depth', 0) > 0:
        print(f"Reached depth: {search_stats['reached_depth']}")