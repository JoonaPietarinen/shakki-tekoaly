from board import Board
from moves import generate_legal_moves

def test_start_position():
    b = Board()
    moves = generate_legal_moves(b)
    assert len(moves) == 20, f"Expected 20 moves, got {len(moves)}"

def test_promotion():
    # Position where white pawn can promote
    b = Board("8/P7/8/8/8/8/8/K6k w - - 0 1")
    moves = generate_legal_moves(b)
    assert 'a7a8q' in moves
    assert 'a7a8r' in moves

def test_castling():
    # Position where white can castle both sides
    b = Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    moves = generate_legal_moves(b)
    assert 'e1g1' in moves  # Kingside
    assert 'e1c1' in moves  # Queenside

def test_en_passant():
    b = Board("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 1")
    moves = generate_legal_moves(b)
    assert 'e5d6' in moves  # En passant capture

if __name__ == "__main__":
    test_start_position()
    test_promotion()
    test_castling()
    test_en_passant()
    print("All tests passed!")
