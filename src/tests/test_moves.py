"""
Test suite for chess engine core functionality.
"""

from board import Board
from moves import generate_legal_moves, is_checkmate, is_stalemate, is_draw_by_fifty_moves


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

def test_checkmate():
    """Test checkmate detection."""
    b = Board("rk6/8/8/8/8/8/8/Kqr5 w KQkq - 0 1")
    moves = generate_legal_moves(b)
    assert len(moves) == 0, "Should be checkmate"
    assert is_checkmate(b), "Should be True"

def test_stalemate():
    """Test stalemate detection."""
    b = Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    moves = generate_legal_moves(b)
    assert len(moves) == 0, "Should be stalemate"
    assert is_stalemate(b), "Should be True"

def test_not_stalemate():
    """Test stalemate detection."""
    b = Board("7k/8/8/8/8/8/8/K7 b - - 0 1")
    moves = generate_legal_moves(b)
    assert len(moves) > 0, "Should not be stalemate"
    assert not is_stalemate(b), "Should be False"

def test_50_move_rule_not_yet_draw():
    """Test 50-move rule, not yet draw at 99."""
    b = Board("8/8/8/8/8/8/8/K6k w - - 99 1")
    assert not is_draw_by_fifty_moves(b), "Should not be draw yet at 99"

def test_50_move_rule_is_draw_at_100():
    """Test 50-move rule, is draw at exactly 100."""
    b = Board("8/8/8/8/8/8/8/K6k w - - 100 1")
    assert is_draw_by_fifty_moves(b), "Should be draw at 100"

def test_50_move_rule_is_draw_over_100():
    """Test 50-move rule, is draw at 101+."""
    b = Board("8/8/8/8/8/8/8/K6k w - - 101 1")
    assert is_draw_by_fifty_moves(b), "Should be draw at 101"

def test_castling_black():
    """Test castling for black pieces."""
    b = Board("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    moves = generate_legal_moves(b)
    assert 'e8g8' in moves, "Missing black kingside castling"
    assert 'e8c8' in moves, "Missing black queenside castling"

def test_black_pawn_moves():
    """Test black pawn move generation."""
    b = Board("8/pp6/8/8/8/8/8/K6k b - - 0 1")
    moves = generate_legal_moves(b)
    assert 'a7a6' in moves or 'a7a5' in moves, "Missing black pawn moves"
    assert 'b7b6' in moves or 'b7b5' in moves, "Missing black pawn moves"

def test_black_knight_moves():
    """Test black knight move generation."""
    b = Board("8/8/8/8/8/8/8/K5nk b - - 0 1")
    moves = generate_legal_moves(b)
    assert len(moves) > 0, "Knight should have legal moves"

def test_pawn_attacks_white():
    """Test that pawn attacks are detected correctly for white pawns."""
    from moves import is_attacked
    b = Board("8/8/8/8/4P3/8/8/K6k w - - 0 1")

    grid = b.grid
    assert is_attacked(3, 3, 'w', grid), "d5 should be attacked by white pawn on e4"
    assert is_attacked(3, 5, 'w', grid), "f5 should be attacked by white pawn on e4"

def test_pawn_attacks_black():
    """Test that pawn attacks are detected correctly for black pawns."""
    from moves import is_attacked
    b = Board("8/8/8/4p3/8/8/8/K6k b - - 0 1")

    grid = b.grid
    assert is_attacked(4, 3, 'b', grid), "d4 should be attacked by black pawn on e5"
    assert is_attacked(4, 5, 'b', grid), "f4 should be attacked by black pawn on e5"

def test_black_king_attacks():
    """Test that king attacks are detected correctly for black king."""
    from moves import is_attacked
    b = Board("8/8/8/8/4k3/8/8/1K6 b - - 0 1")

    grid = b.grid
    assert is_attacked(3, 3, 'b', grid), "d5 should be attacked by black king"
    assert is_attacked(5, 5, 'b', grid), "f3 should be attacked by black king"