import copy
import random

FILES = "abcdefgh"
RANKS = "12345678"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

random.seed(42)
ZOBRIST_TABLE = {}

# Generate Zobrist keys for all pieces and squares
for piece in 'pnbrqkPNBRQK':
    ZOBRIST_TABLE[piece] = [random.getrandbits(64) for _ in range(64)]

ZOBRIST_WHITE = random.getrandbits(64)
ZOBRIST_BLACK = random.getrandbits(64)

ZOBRIST_CASTLING = {
    'K': random.getrandbits(64),
    'Q': random.getrandbits(64),
    'k': random.getrandbits(64),
    'q': random.getrandbits(64)
}

ZOBRIST_EP = [random.getrandbits(64) for _ in range(8)]


def compute_zobrist_hash(board):
    """
    Compute Zobrist hash for the current board position.
    Used for transposition table lookups.
    """
    h = 0
    
    for r in range(8):
        for c in range(8):
            piece = board.grid[r][c]
            if piece != '.':
                square_index = r * 8 + c
                h ^= ZOBRIST_TABLE[piece][square_index]
    
    if board.turn == 'w':
        h ^= ZOBRIST_WHITE
    else:
        h ^= ZOBRIST_BLACK

    for right in board.castling:
        if right in ZOBRIST_CASTLING:
            h ^= ZOBRIST_CASTLING[right]

    if board.en_passant:
        ep_file = ord(board.en_passant[0]) - ord('a')
        h ^= ZOBRIST_EP[ep_file]
    
    return h


def coord_to_sq(coord: str):
    """Convert algebraic notation like 'e4' to (row, col) indices."""
    col = FILES.index(coord[0])
    row = 8 - int(coord[1])
    return row, col

def sq_to_coord(row: int, col: int):
    """Convert (row, col) indices back to algebraic notation like 'e4'."""
    return f"{FILES[col]}{8 - row}"

class Board:
    def __init__(self, fen: str = None):
        """Initialize board from FEN string or default start position."""
        if fen and fen != "startpos_fen":
            self.set_fen(fen)
        else:  
            self.set_fen(START_FEN)

    def set_fen(self, fen: str):
        """Parse FEN string into internal board state."""
        if fen == "startpos_fen":
            fen = START_FEN
        parts = fen.split()
        rows = parts[0].split('/')
        self.grid = []
        for r in rows:
            row = []
            for ch in r:
                if ch.isdigit():
                    row += ['.'] * int(ch)
                else:
                    row.append(ch)
            self.grid.append(row)   
        self.turn = parts[1]
        self.castling = parts[2]
        self.en_passant = parts[3] if parts[3] != '-' else None
        self.halfmove = int(parts[4])
        self.fullmove = int(parts[5])

    def to_fen(self) -> str:
        """Convert internal board state back to FEN string."""
        rows = []
        for r in self.grid:
            comp = []
            empty = 0
            for ch in r:
                if ch == '.':
                    empty += 1
                else:
                    if empty: 
                        comp.append(str(empty))
                        empty = 0
                    comp.append(ch)
            if empty:
                comp.append(str(empty))
            rows.append(''.join(comp))
        ep = self.en_passant if self.en_passant else '-'
        castling = self.castling if self.castling else '-'
        return f"{'/'.join(rows)} {self.turn} {castling} {ep} {self.halfmove} {self.fullmove}"

    def make_move(self, move_uci: str):
        """
        Apply a move in UCI format to the board.
        Handles castling, en passant, promotion, and updates board state.
        """
        from_sq = move_uci[:2]
        to_sq = move_uci[2:4]
        promo = move_uci[4:].lower() if len(move_uci) == 5 else None
        fr, fc = coord_to_sq(from_sq)
        tr, tc = coord_to_sq(to_sq)
        piece = self.grid[fr][fc]
        if piece == '.':
            raise ValueError("No piece on from-square")

        direction = -1 if piece.isupper() else 1
        capture = self.grid[tr][tc] != '.'

        # En passant capture
        if piece.lower() == 'p' and fc != tc and self.grid[tr][tc] == '.' and self.en_passant == to_sq:
            self.grid[tr - direction][tc] = '.'
            capture = True

        self.grid[fr][fc] = '.'
        if promo:
            self.grid[tr][tc] = promo.upper() if piece.isupper() else promo.lower()
        else:
            self.grid[tr][tc] = piece

        # Castling: move the rook
        if piece.lower() == 'k' and abs(tc - fc) == 2:
            if tc > fc:
                rook_from = (fr, 7)
                rook_to = (fr, 5)
            else:
                rook_from = (fr, 0)
                rook_to = (fr, 3)
            rook_piece = self.grid[rook_from[0]][rook_from[1]]
            self.grid[rook_from[0]][rook_from[1]] = '.'
            self.grid[rook_to[0]][rook_to[1]] = rook_piece

        # Update castling rights
        def remove_castling(right: str):
            if right in self.castling:
                self.castling = self.castling.replace(right, '')

        if piece == 'K':
            remove_castling('K')
            remove_castling('Q')
        if piece == 'k':
            remove_castling('k')
            remove_castling('q')
        if fr == 7 and fc == 0:
            remove_castling('Q')
        if fr == 7 and fc == 7:
            remove_castling('K')
        if fr == 0 and fc == 0:
            remove_castling('q')
        if fr == 0 and fc == 7:
            remove_castling('k')
        if tr == 7 and tc == 0:
            remove_castling('Q')
        if tr == 7 and tc == 7:
            remove_castling('K')
        if tr == 0 and tc == 0:
            remove_castling('q')
        if tr == 0 and tc == 7:
            remove_castling('k')

        if not self.castling:
            self.castling = '-'

        # Set en passant target after double pawn push
        if piece.lower() == 'p' and abs(tr - fr) == 2:
            mid_row = (tr + fr) // 2
            self.en_passant = sq_to_coord(mid_row, fc)
        else:
            self.en_passant = None

        # Update halfmove clock (50-move rule)
        if piece.lower() == 'p' or capture:
            self.halfmove = 0
        else:
            self.halfmove += 1

        if self.turn == 'b':
            self.fullmove += 1

        self.turn = 'b' if self.turn == 'w' else 'w'

    def copy(self):
        """Create a deep copy of the board for search calculations."""
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        new_board.turn = self.turn
        new_board.castling = self.castling
        new_board.en_passant = self.en_passant
        new_board.halfmove = self.halfmove
        new_board.fullmove = self.fullmove
        return new_board

