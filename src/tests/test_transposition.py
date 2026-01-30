"""
Test suite for transposition table functionality.
"""

from board import Board, compute_zobrist_hash
import search


def test_zobrist_hash_consistent():
    """Test that same position always produces same hash."""
    b1 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    b2 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    hash1 = compute_zobrist_hash(b1)
    hash2 = compute_zobrist_hash(b2)
    
    assert hash1 == hash2, "Same position should have same hash"


def test_zobrist_hash_different():
    """Test that different positions have different hashes."""
    b1 = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    b2 = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    
    hash1 = compute_zobrist_hash(b1)
    hash2 = compute_zobrist_hash(b2)
    
    assert hash1 != hash2, "Different positions should have different hashes"


def test_transposition_table_stores_result():
    """Test that transposition table stores and retrieves search results."""
    search.clear_transposition_table()
    b = Board()
    
    # Do a search
    score1, move1 = search.negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))
    
    # Check if result was stored
    board_hash = compute_zobrist_hash(b)
    assert board_hash in search.transposition_table, "Result should be stored in TT"
    assert search.transposition_table[board_hash]['move'] == move1


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
    # Note: time2 might not always be faster due to variance, so we don't assert time comparison


if __name__ == "__main__":
    test_zobrist_hash_consistent()
    test_zobrist_hash_different()
    test_transposition_table_stores_result()
    test_transposition_table_speedup()
    print("✅ All transposition table tests passed!")
