"""
Tests for evaluation helpers and endgame bonuses.
"""

from board import Board
from evaluation import _game_phase, _mop_up_bonus, evaluate


def test_game_phase_start_position_is_middlegame_weight_one():
    b = Board()
    assert _game_phase(b) == 1.0


def test_game_phase_kings_only_is_zero():
    b = Board("8/8/8/8/8/8/8/K6k w - - 0 1")
    assert _game_phase(b) == 0.0


def test_mop_up_bonus_applies_with_lone_king_defender():
    # White has mating material (rook), black has lone king.
    b = Board("8/8/8/8/8/8/8/K5Rk w - - 0 1")
    assert _mop_up_bonus(b) > 0


def test_mop_up_bonus_not_applied_if_defender_has_pawn():
    # Black is not lone king (has a pawn), so bonus must not apply.
    b = Board("8/8/8/8/8/8/7p/K5Rk w - - 0 1")
    assert _mop_up_bonus(b) == 0


def test_evaluate_is_numeric_in_simple_endgame():
    b = Board("8/8/8/8/8/8/8/K5Rk w - - 0 1")
    score = evaluate(b)
    assert isinstance(score, int)
