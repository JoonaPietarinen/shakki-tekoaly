"""
Position evaluation for chess AI.
Positive scores favor white, negative scores favor black.
For now, we use Simplified Evaluation Function by Tomasz Michniewski.
Endgame detection.
"""

# Piece values in centipawns
PIECE_VALUES = {
    'p': 100,
    'n': 320,
    'b': 330,
    'r': 500,
    'q': 900,
    'k': 20000
}

# Piece-square tables for positional evaluation
# White perspective (flip vertically for black)
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
   -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDDLE_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

KING_END_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

PIECE_SQUARE_TABLES = {
    'p': PAWN_TABLE,
    'n': KNIGHT_TABLE,
    'b': BISHOP_TABLE,
    'r': ROOK_TABLE,
    'q': QUEEN_TABLE,
    'k': KING_MIDDLE_TABLE
}

MAX_NON_PAWN_MATERIAL = 6400  # Both sides combined (Q+2R+2B+2N per side)


def _material_without_kings(board):
    white = 0
    black = 0
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == '.':
                continue
            p = piece.lower()
            if p == 'k':
                continue
            if piece.isupper():
                white += PIECE_VALUES[p]
            else:
                black += PIECE_VALUES[p]
    return white, black


def _non_pawn_material(board):
    total = 0
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == '.':
                continue
            p = piece.lower()
            if p in {'n', 'b', 'r', 'q'}:
                total += PIECE_VALUES[p]
    return total


def _game_phase(board) -> float:
    """Return middlegame weight in range [0, 1]."""
    npm = _non_pawn_material(board)
    return min(1.0, npm / MAX_NON_PAWN_MATERIAL)


def _king_positions(board):
    white_king = None
    black_king = None
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == 'K':
                white_king = (r, c)
            elif piece == 'k':
                black_king = (r, c)
    return white_king, black_king


def _side_piece_counts(board):
    white = {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0}
    black = {'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0}
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == '.':
                continue
            p = piece.lower()
            if piece.isupper():
                white[p] += 1
            else:
                black[p] += 1
    return white, black


def _has_basic_mating_material(counts):
    # Simple practical set for forced mate against lone king.
    return counts['q'] >= 1 or counts['r'] >= 1 or counts['b'] >= 2 or (counts['b'] >= 1 and counts['n'] >= 1)


def _mop_up_bonus(board) -> int:
    """Endgame conversion bonus when one side has only a king left."""
    white_counts, black_counts = _side_piece_counts(board)

    # Apply only to basic endgames where defender has lone king.
    white_only_king = white_counts['k'] == 1 and sum(white_counts[p] for p in ('p', 'n', 'b', 'r', 'q')) == 0
    black_only_king = black_counts['k'] == 1 and sum(black_counts[p] for p in ('p', 'n', 'b', 'r', 'q')) == 0

    if black_only_king and _has_basic_mating_material(white_counts):
        sign = 1
    elif white_only_king and _has_basic_mating_material(black_counts):
        sign = -1
    else:
        return 0

    white_king, black_king = _king_positions(board)
    if not white_king or not black_king:
        return 0

    strong_king, weak_king = (white_king, black_king) if sign == 1 else (black_king, white_king)

    wr, wc = weak_king
    edge_distance = min(wr, 7 - wr, wc, 7 - wc)  # 0 on edge, 3 near center
    push_bonus = (3 - edge_distance) * 18

    sr, sc = strong_king
    king_distance = abs(sr - wr) + abs(sc - wc)
    approach_bonus = max(0, 14 - king_distance) * 2

    return sign * (push_bonus + approach_bonus)


def evaluate(board):
    """
    Evaluate the current board position.
    Returns score in centipawns from white's perspective.
    Positive = white advantage, negative = black advantage.
    """
    score = 0
    mg_weight = _game_phase(board) # 1.0 in opening, 0.0 in endgame
    eg_weight = 1.0 - mg_weight # 0.0 in opening, 1.0 in endgame

    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == '.':
                continue

            piece_type = piece.lower()
            piece_value = PIECE_VALUES.get(piece_type, 0)

            # Get piece-square table bonus
            if piece_type == 'k':
                if piece.islower():  # Black piece
                    index = (7 - r) * 8 + c
                    mg_bonus = -KING_MIDDLE_TABLE[index]
                    eg_bonus = -KING_END_TABLE[index]
                else:  # White piece
                    index = r * 8 + c
                    mg_bonus = KING_MIDDLE_TABLE[index]
                    eg_bonus = KING_END_TABLE[index]
                bonus = int(round(mg_weight * mg_bonus + eg_weight * eg_bonus)) # Blend middle and endgame tables based on game phase for better endgame evaluation
            elif piece_type in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece_type]
                # For black pieces, flip the table vertically
                if piece.islower():  # Black piece
                    index = (7 - r) * 8 + c
                    bonus = -table[index]
                else:  # White piece
                    index = r * 8 + c
                    bonus = table[index]
            else:  # pragma : no cover
                bonus = 0

            # Add material + positional value
            if piece.isupper():  # White
                score += piece_value + bonus
            else:  # Black
                score -= piece_value + bonus

    score += _mop_up_bonus(board)
    return score


def evaluate_from_perspective(board):
    """
    Evaluate from current side to move's perspective.
    Returns positive if side to move is winning.
    """
    score = evaluate(board)
    return score if board.turn == 'w' else -score
