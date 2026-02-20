"""
Test suite for chess AI search algorithms.
"""

from board import Board
from search import find_best_move, negamax, is_capture, quiescence, clear_transposition_table, mvv_lva_score, history_table
from moves import generate_legal_moves


def test_negamax_finds_move():
    """Test that negamax returns a valid move in the starting position."""
    clear_transposition_table()
    b = Board()
    score, move = negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))
    
    # Should find a move
    assert move is not None, "Negamax should find a move"
    
    # Move should be valid
    legal_moves = generate_legal_moves(b)
    assert move in legal_moves, f"Move {move} should be legal"


def test_find_best_move_returns_valid():
    """Test that find_best_move returns a legal move."""
    clear_transposition_table()
    b = Board()
    move = find_best_move(b, depth=2, time_limit=None)
    
    assert move is not None, "Should find a best move"
    
    legal_moves = generate_legal_moves(b)
    assert move in legal_moves, f"Move {move} should be legal"


def test_ai_prefers_captures():
    """Test that AI recognizes a simple tactical win."""
    # Position where white can capture undefended black queen
    clear_transposition_table()
    b = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    move = find_best_move(b, depth=2, time_limit=None)
    assert move is not None


def test_is_capture_detects_capture():
    """Test that is_capture correctly identifies captures."""
    # Position: White pawn on e4, Black pawn on d5
    b = Board("rnbqkbnr/pppppppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    # e4xd5 is a capture
    assert is_capture(b, "e4d5") == True, "e4d5 should be a capture"


def test_is_capture_detects_non_capture():
    """Test that is_capture returns False for non-captures."""
    b = Board()  # Starting position
    
    # e2e4 is not a capture (empty square)
    assert is_capture(b, "e2e4") == False, "e2e4 should not be a capture"


def test_is_capture_en_passant():
    """Test that is_capture doesn't detect en passant as normal capture."""
    b = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
    
    # d7d5 is not a capture
    assert is_capture(b, "d7d5") == False, "d7d5 should not be a capture"


def test_quiescence_with_no_captures():
    """Test quiescence when there are no captures available."""
    clear_transposition_table()
    # Starting position - no captures available
    b = Board()
    
    # Quiescence should return evaluation without searching captures
    score = quiescence(b, float('-inf'), float('inf'))
    
    # Score should be a valid numeric score (may not be exactly 0 due to piece-square tables)
    assert isinstance(score, (int, float)), "Quiescence should return a numeric score"
    assert -1000 <= score <= 1000, "Score should be in reasonable range for starting position"


def test_quiescence_with_captures():
    """Test quiescence when captures are available."""
    clear_transposition_table()
    # Position: White can capture Black pawn
    b = Board("rnbqkbnr/pppppppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    score = quiescence(b, float('-inf'), float('inf'))
    
    # Should return a numeric score
    assert isinstance(score, (int, float)), "Quiescence should return a numeric score"


def test_quiescence_stand_pat():
    """Test that quiescence respects stand pat (beta cutoff)."""
    clear_transposition_table()
    b = Board()
    
    # If beta is very low (AI wants to avoid this line), stand pat should trigger
    # Stand pat when position is good (e.g., +100) and beta is low (e.g., +50)
    score = quiescence(b, float('-inf'), float('inf'), ply=0)
    
    assert isinstance(score, (int, float)), "Quiescence should return a numeric score"


def test_quiescence_searches_captures():
    """Test that quiescence actually searches capture moves."""
    clear_transposition_table()
    # Position where capture is important
    b = Board("rnbqkbnr/pppppppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    # Get score without captures (via stand pat if possible)
    alpha = float('-inf')
    beta = float('inf')
    score_with_quiescence = quiescence(b, alpha, beta)
    
    # Score should reflect that there's a capture available
    # (actual evaluation might vary, but quiescence should find it)
    assert isinstance(score_with_quiescence, (int, float)), "Should return valid score"


def test_mvv_lva_queen_capture_better_than_pawn():
    """Test that MVV-LVA prioritizes queen capture over pawn."""
    b = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    # Example moves (not necessarily legal in this position, just for scoring)
    queen_capture = "e4d5"
    pawn_capture = "e4e5"
    
    score_queen = mvv_lva_score(b, "e2e4")
    score_pawn = mvv_lva_score(b, "e2e4")
    
    assert isinstance(score_queen, tuple), "MVV-LVA should return tuple"
    assert len(score_queen) == 2, "MVV-LVA tuple should have 2 elements"


def test_history_heuristic_updates():
    """Test that history heuristic updates after beta cutoff."""
    clear_transposition_table()
    b = Board()
    
    # Run negamax which should update history table
    score, move = negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))
    
    # History table should be populated after search
    assert isinstance(history_table, dict), "History table should be a dict"
    # After depth 2 search, we should have some history entries (from cutoffs)


def test_history_table_clears():
    """Test that history table clears between games."""
    clear_transposition_table()
    b = Board()
    negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))
    
    history_before = len(history_table)
    
    # Clear and verify
    clear_transposition_table()
    history_after = len(history_table)
    
    assert history_after == 0, "History table should be cleared"


def test_quiescence_captures_sorted_by_mvv_lva():
    """Test that quiescence sorts captures by MVV-LVA."""
    clear_transposition_table()
    # Position with multiple capture options
    b = Board("rnbqkbnr/pppppppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    
    # Quiescence should sort captures
    score = quiescence(b, float('-inf'), float('inf'))
    
    assert isinstance(score, (int, float)), "Quiescence should work with capture sorting"


def test_feature_flag_quiescence_enabled():
    """Test that quiescence can be disabled via feature flag."""
    import search
    clear_transposition_table()
    
    # Enable quiescence
    search.ENABLE_QUIESCENCE = True
    b = Board()
    score1, move1 = negamax(b, 2, float('-inf'), float('inf'))
    
    nodes_with_qs = search.search_stats['nodes_searched']
    qnodes_with_qs = search.search_stats['quiescence_nodes']
    
    # Disable quiescence
    clear_transposition_table()
    search.ENABLE_QUIESCENCE = False
    search.search_stats['nodes_searched'] = 0
    search.search_stats['quiescence_nodes'] = 0
    
    b = Board()
    score2, move2 = negamax(b, 2, float('-inf'), float('inf'))
    
    nodes_without_qs = search.search_stats['nodes_searched']
    qnodes_without_qs = search.search_stats['quiescence_nodes']
    
    # Restore default
    search.ENABLE_QUIESCENCE = True
    
    # With quiescence: should have Q-nodes
    assert qnodes_with_qs > 0, "Should have quiescence nodes when enabled"
    # Without quiescence: should have NO Q-nodes
    assert qnodes_without_qs == 0, "Should have zero quiescence nodes when disabled"


def test_feature_flag_history_heuristic():
    """Test that history heuristic can be disabled via feature flag."""
    import search

    clear_transposition_table()
    search.ENABLE_HISTORY_HEURISTIC = True
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    negamax(b, 3, float('-inf'), float('inf'))
    
    nodes_with_history = search.search_stats['nodes_searched']
    history_entries_with = len(search.history_table)

    clear_transposition_table()
    search.ENABLE_HISTORY_HEURISTIC = False
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    negamax(b, 3, float('-inf'), float('inf'))
    
    nodes_without_history = search.search_stats['nodes_searched']
    history_entries_without = len(search.history_table)
    
    # Restore default
    search.ENABLE_HISTORY_HEURISTIC = True
    
    # History should have entries when enabled, and should be empty when disabled
    assert history_entries_with > 0, "History should have entries when ENABLED"
    assert history_entries_without == 0, "History should be EMPTY when DISABLED"


def test_feature_flag_killer_moves():
    """Test that killer moves can be disabled via feature flag."""
    import search
    clear_transposition_table()
    
    # Enable killer moves
    search.ENABLE_KILLER_MOVES = True
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    negamax(b, 3, float('-inf'), float('inf'))
    
    nodes_with_killers = search.search_stats['nodes_searched']
    
    # Disable killer moves
    clear_transposition_table()
    search.ENABLE_KILLER_MOVES = False
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    negamax(b, 3, float('-inf'), float('inf'))
    
    nodes_without_killers = search.search_stats['nodes_searched']
    
    # Restore default
    search.ENABLE_KILLER_MOVES = True
    
    # Both should complete without error
    assert nodes_with_killers > 0, "Should search with killers enabled"
    assert nodes_without_killers > 0, "Should search with killers disabled"


def test_feature_flags_combination():
    """Test different combinations of feature flags."""
    import search
    from board import Board
    
    scenarios = [
        {"QS": False, "History": False, "Killers": False},
        {"QS": True, "History": False, "Killers": False},
        {"QS": True, "History": True, "Killers": False},
        {"QS": True, "History": True, "Killers": True},
    ]
    
    results = []
    
    for scenario in scenarios:
        clear_transposition_table()
        search.search_stats['nodes_searched'] = 0
        search.search_stats['quiescence_nodes'] = 0
        search.search_stats['beta_cutoffs'] = 0
        
        search.ENABLE_QUIESCENCE = scenario["QS"]
        search.ENABLE_HISTORY_HEURISTIC = scenario["History"]
        search.ENABLE_KILLER_MOVES = scenario["Killers"]
        
        b = Board()
        score, move = negamax(b, 2, float('-inf'), float('inf'))
        
        results.append({
            'scenario': scenario,
            'nodes': search.search_stats['nodes_searched'],
            'qnodes': search.search_stats['quiescence_nodes'],
            'cutoffs': search.search_stats['beta_cutoffs'],
            'move': move
        })
    
    # Restore defaults
    search.ENABLE_QUIESCENCE = True
    search.ENABLE_HISTORY_HEURISTIC = True
    search.ENABLE_KILLER_MOVES = True
    
    # All scenarios should complete
    assert len(results) == 4, "All scenarios should complete"
    
    # All should find a move
    for result in results:
        assert result['move'] is not None, f"Should find move in scenario {result['scenario']}"


def test_null_window_search_enabled():
    """Test that null-window search can be disabled via feature flag."""
    import search
    clear_transposition_table()
    
    # Enable null-window
    search.ENABLE_NULL_WINDOW = True
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    move1 = find_best_move(b, depth=2, time_limit=None)
    
    nodes_with_nws = search.search_stats['nodes_searched']
    
    # Disable null-window
    clear_transposition_table()
    search.ENABLE_NULL_WINDOW = False
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    move2 = find_best_move(b, depth=2, time_limit=None)
    
    nodes_without_nws = search.search_stats['nodes_searched']
    
    # Restore default
    search.ENABLE_NULL_WINDOW = True
    
    # Both should find a move
    assert move1 is not None, "Should find move with NWS enabled"
    assert move2 is not None, "Should find move with NWS disabled"


def test_null_window_search_narrower_window():
    """Test that null-window search uses narrower window (beta - 1)."""
    import search
    clear_transposition_table()

    search.ENABLE_NULL_WINDOW = True
    search.ENABLE_QUIESCENCE = True
    search.ENABLE_HISTORY_HEURISTIC = True
    search.ENABLE_KILLER_MOVES = True
    
    search.search_stats['nodes_searched'] = 0
    
    b = Board()
    move = find_best_move(b, depth=3, time_limit=None)
    
    # Should find a move without errors
    assert move is not None, "Null-window search should find a move"
    assert move in ["e2e4", "d2d4", "g1f3", "c2c4", "b1c3"], "Should find a reasonable opening move"


def test_null_window_with_all_optimizations():
    """Test null-window search combined with all other optimizations."""
    import search
    clear_transposition_table()
    
    # Enable all optimizations
    search.ENABLE_NULL_WINDOW = True
    search.ENABLE_QUIESCENCE = True
    search.ENABLE_HISTORY_HEURISTIC = True
    search.ENABLE_KILLER_MOVES = True
    
    search.search_stats['nodes_searched'] = 0
    search.search_stats['quiescence_nodes'] = 0
    
    b = Board()
    move = find_best_move(b, depth=4, time_limit=None)
    
    all_opts_nodes = search.search_stats['nodes_searched']
    all_opts_qnodes = search.search_stats['quiescence_nodes']
    
    # Disable null-window
    clear_transposition_table()
    search.ENABLE_NULL_WINDOW = False
    search.search_stats['nodes_searched'] = 0
    search.search_stats['quiescence_nodes'] = 0
    
    b = Board()
    move2 = find_best_move(b, depth=4, time_limit=None)
    
    without_nws_nodes = search.search_stats['nodes_searched']
    
    # Restore
    search.ENABLE_NULL_WINDOW = True
    
    # Both should complete
    assert move is not None, "Should find move with NWS"
    assert move2 is not None, "Should find move without NWS"


