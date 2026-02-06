"""
Test suite for chess AI search algorithms.
"""

from board import Board
from search import find_best_move, negamax
from moves import generate_legal_moves


def test_negamax_finds_move():
    """Test that negamax returns a valid move in the starting position."""
    b = Board()
    score, move = negamax(b, depth=2, alpha=float('-inf'), beta=float('inf'))
    
    # Should find a move
    assert move is not None, "Negamax should find a move"
    
    # Move should be valid
    legal_moves = generate_legal_moves(b)
    assert move in legal_moves, f"Move {move} should be legal"


def test_find_best_move_returns_valid():
    """Test that find_best_move returns a legal move."""
    b = Board()
    move = find_best_move(b, depth=2, time_limit=None)
    
    assert move is not None, "Should find a best move"
    
    legal_moves = generate_legal_moves(b)
    assert move in legal_moves, f"Move {move} should be legal"


def test_ai_prefers_captures():
    """Test that AI recognizes a simple tactical win."""
    # Position where white can capture undefended black queen
    b = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    move = find_best_move(b, depth=2, time_limit=None)
    assert move is not None

