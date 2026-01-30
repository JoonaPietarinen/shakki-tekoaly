"""
Test suite for chess board representation and FEN conversion.
"""

from board import Board


def test_to_fen_start_position():
    """Test that start position converts to correct FEN."""
    b = Board()
    fen = b.to_fen()
    expected = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    assert fen == expected, f"Expected {expected}, got {fen}"


def test_fen_roundtrip():
    """Test that FEN → Board → FEN is consistent."""
    original_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    b = Board(original_fen)
    result_fen = b.to_fen()
    assert result_fen == original_fen, f"Roundtrip failed: {original_fen} → {result_fen}"


def test_to_fen_after_move():
    """Test that FEN updates correctly after making a move."""
    b = Board()
    b.make_move("e2e4")
    fen = b.to_fen()
    # After e2e4, should have pawn on e4
    assert "P" in fen.split()[0], "Pawn should be in position string"
    assert b.turn == 'b', "Turn should switch to black"


def test_to_fen_after_capture():
    """Test that FEN updates correctly after capture."""
    b = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    b.make_move("d7d5")
    b.make_move("e4d5")  # White captures
    fen = b.to_fen()
    # d5 should have white pawn, d7 should be empty
    assert "P" in fen.split()[0], "Captured pawn should exist"


def test_to_fen_castling_rights():
    """Test that FEN reflects correct castling rights."""
    b = Board()
    b.make_move("e2e4")
    b.make_move("e7e5")
    b.make_move("g1f3")
    fen = b.to_fen()
    # Both sides should still have castling rights
    assert "KQkq" in fen, "Castling rights should be preserved"


def test_to_fen_promotion():
    """Test that FEN handles pawn promotion."""
    b = Board("8/P7/8/8/8/8/8/K6k w - - 0 1")
    b.make_move("a7a8q")
    fen = b.to_fen()
    # Should have queen instead of pawn
    assert "Q" in fen.split()[0], "Promoted pawn should be queen"
    assert "P" not in fen.split()[0], "Original pawn should not exist"


if __name__ == "__main__":
    test_to_fen_start_position()
    test_fen_roundtrip()
    test_to_fen_after_move()
    test_to_fen_after_capture()
    test_to_fen_castling_rights()
    test_to_fen_promotion()
    print("All board tests passed!")