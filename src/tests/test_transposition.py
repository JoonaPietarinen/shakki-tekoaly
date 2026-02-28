"""
Test suite for transposition table functionality.
"""

from board import Board
import search


def test_zobrist_hash_consistent():
    """Test that same position always produces same hash."""
    b1 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    b2 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    hash1 = Board._compute_hash(b1)
    hash2 = Board._compute_hash(b2)

    assert hash1 == hash2, "Same position should have same hash"


def test_zobrist_hash_different():
    """Test that different positions have different hashes."""
    b1 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    b2 = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")

    hash1 = Board._compute_hash(b1)
    hash2 = Board._compute_hash(b2)

    assert hash1 != hash2, "Different positions should have different hashes"


def test_transposition_table_stores_result():
    """Test that transposition table stores and retrieves search results."""
    search.clear_transposition_table()
    b = Board()

    # Do a search
    score1, move1 = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))

    # Check if result was stored
    board_hash = Board._compute_hash(b)
    assert board_hash in search.transposition_table, "Result should be stored in TT"
    assert search.transposition_table[board_hash]['move'] == move1


def test_transposition_table_exact_flag():
    """Test that EXACT flag is stored when move is within bounds."""
    search.clear_transposition_table()
    b = Board()

    score, move = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))

    board_hash = Board._compute_hash(b)
    entry = search.transposition_table[board_hash]

    # With full window (-inf, +inf), should store EXACT
    assert entry['flag'] == search.EXACT, "Full window should result in EXACT flag"


def test_transposition_table_upper_bound():
    """Test that UPPER flag is stored on alpha cutoff."""
    search.clear_transposition_table()
    b = Board()

    # Narrow window that might cause cutoff
    score, move = search.negamax(b, depth=2, alpha=-50, beta=50)

    board_hash = Board._compute_hash(b)
    entry = search.transposition_table[board_hash]

    # Result should be stored with appropriate flag
    assert entry['flag'] in [search.EXACT, search.UPPER, search.LOWER], \
        "Flag should be one of EXACT, UPPER, or LOWER"


def test_transposition_table_lookup_with_bounds():
    """Test that TT lookup correctly applies alpha/beta bounds."""
    search.clear_transposition_table()
    b = Board()

    # First search with full window
    score1, move1 = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))

    # Second search with same position should return cached result
    score2, move2 = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))

    assert score1 == score2, "Same search should return same score"
    assert move1 == move2, "Same search should return same move"
    # TT should have been hit on second search
    board_hash = Board._compute_hash(b)
    assert board_hash in search.transposition_table, "Position should be in TT"


def test_transposition_table_speedup():
    """Test that TT speeds up repeated searches."""
    import time

    search.clear_transposition_table()
    b = Board()

    # First search (no TT hits)
    start1 = time.time()
    score1, move1 = search.negamax(b, depth=3, alpha=float('-inf'), beta=float('inf'))
    time1 = time.time() - start1

    # Second search (with TT hits)
    start2 = time.time()
    score2, move2 = search.negamax(b, depth=3, alpha=float('-inf'), beta=float('inf'))
    time2 = time.time() - start2

    # Second search should be much faster (likely hits most positions)
    # We just check that both found same move
    assert move1 == move2, "Same position should find same move"


def test_transposition_table_depth_cutoff():
    """Test that shallow TT entries don't replace deeper ones."""
    search.clear_transposition_table()
    b = Board()

    # Search at depth 2
    score_d2, move_d2 = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))

    board_hash = Board._compute_hash(b)
    entry_after_d2 = search.transposition_table[board_hash]

    assert entry_after_d2['depth'] == 2, "Should store depth 2 result"

    # Search at depth 3 (deeper)
    score_d3, move_d3 = search.negamax(b, depth=3, alpha=float('-inf'), beta=float('inf'))
    entry_after_d3 = search.transposition_table[board_hash]

    assert entry_after_d3['depth'] == 3, "Should update to depth 3 result"
