"""
Test suite for chess engine core functionality.
"""

from board import Board
from moves import generate_legal_moves


def test_start_position():
    """Test that start position has exactly 20 legal moves."""
    b = Board()
    moves = generate_legal_moves(b)
    assert len(moves) == 20, f"Expected 20 moves, got {len(moves)}"


def test_promotion():
    """Test pawn promotion generation."""
    b = Board("8/P7/8/8/8/8/8/K6k w - - 0 1")
    moves = generate_legal_moves(b)
    assert 'a7a8q' in moves, "Missing queen promotion"
    assert 'a7a8r' in moves, "Missing rook promotion"
    assert 'a7a8b' in moves, "Missing bishop promotion"
    assert 'a7a8n' in moves, "Missing knight promotion"


def test_castling():
    """Test castling move generation."""
    b = Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    moves = generate_legal_moves(b)
    assert 'e1g1' in moves, "Missing kingside castling"
    assert 'e1c1' in moves, "Missing queenside castling"


def test_en_passant():
    """Test en passant capture generation."""
    b = Board("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    moves = generate_legal_moves(b)
    assert 'e5d6' in moves, "Missing en passant capture"
