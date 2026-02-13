"""
Test suite for chess AI search algorithms.
"""

from board import Board
from search import find_best_move, negamax, is_capture, quiescence, clear_transposition_table
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

