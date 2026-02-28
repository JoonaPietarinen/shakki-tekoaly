"""
Position evaluation for chess AI.
Positive scores favor white, negative scores favor black.
For now, we use Simplified Evaluation Function by Tomasz Michniewski.
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

PIECE_SQUARE_TABLES = {
    'p': PAWN_TABLE,
    'n': KNIGHT_TABLE,
    'b': BISHOP_TABLE,
    'r': ROOK_TABLE,
    'q': QUEEN_TABLE,
    'k': KING_MIDDLE_TABLE
}


def evaluate(board):
    """
    Evaluate the current board position.
    Returns score in centipawns from white's perspective.
    Positive = white advantage, negative = black advantage.
    """
    score = 0

    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece == '.':
                continue

            piece_type = piece.lower()
            piece_value = PIECE_VALUES.get(piece_type, 0)

            # Get piece-square table bonus
            if piece_type in PIECE_SQUARE_TABLES:
                table = PIECE_SQUARE_TABLES[piece_type]
                # For black pieces, flip the table vertically
                if piece.islower():  # Black piece
                    index = (7 - r) * 8 + c
                    bonus = -table[index]
                else:  # White piece
                    index = r * 8 + c
                    bonus = table[index]
            else: # pragma : no cover
                bonus = 0 # Redundant, should not happen. But just in case.


            # Add material + positional value
            if piece.isupper():  # White
                score += piece_value + bonus
            else:  # Black
                score -= piece_value + bonus

    return score


def evaluate_from_perspective(board):
    """
    Evaluate from current side to move's perspective.
    Returns positive if side to move is winning.
    """
    score = evaluate(board)
    return score if board.turn == 'w' else -score
