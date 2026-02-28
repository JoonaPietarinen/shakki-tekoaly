import random

FILES = "abcdefgh"
RANKS = "12345678"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

random.seed(42)
ZOBRIST_TABLE = {}

# Generate Zobrist keys for all pieces and squares
for piece_type in 'pnbrqkPNBRQK':
    ZOBRIST_TABLE[piece_type] = [random.getrandbits(64) for _ in range(64)]

ZOBRIST_WHITE = random.getrandbits(64)
ZOBRIST_BLACK = random.getrandbits(64)

ZOBRIST_CASTLING = {
    'K': random.getrandbits(64),
    'Q': random.getrandbits(64),
    'k': random.getrandbits(64),
    'q': random.getrandbits(64)
}

ZOBRIST_EP = [random.getrandbits(64) for _ in range(8)]


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
        # Initialize all attributes with default values
        self.grid = []
        self.turn = 'w'
        self.castling = 'KQkq'
        self.en_passant = None
        self.halfmove = 0
        self.fullmove = 1
        self.hash = 0

        if fen and fen != "startpos_fen":
            self.set_fen(fen)
        else:  
            self.set_fen(START_FEN)



    def set_fen(self, fen: str):
        """Parse FEN string into internal board state and compute initial hash."""
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
        
        # Compute initial Zobrist hash
        self.hash = self._compute_hash()
    
    def _compute_hash(self):
        """Compute Zobrist hash for the current board position."""
        h = 0
        
        # Hash pieces
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece != '.':
                    square_index = r * 8 + c
                    h ^= ZOBRIST_TABLE[piece][square_index]
        
        # Hash turn
        if self.turn == 'w':
            h ^= ZOBRIST_WHITE
        else:
            h ^= ZOBRIST_BLACK

        # Hash castling rights
        if self.castling != '-':
            for right in self.castling:
                if right in ZOBRIST_CASTLING:
                    h ^= ZOBRIST_CASTLING[right]

        # Hash en passant
        if self.en_passant:
            ep_file = ord(self.en_passant[0]) - ord('a')
            h ^= ZOBRIST_EP[ep_file]
        
        return h

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
        Updates Zobrist hash incrementally for performance.
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

        # Remove old en passant from hash
        if self.en_passant:
            ep_file = ord(self.en_passant[0]) - ord('a')
            self.hash ^= ZOBRIST_EP[ep_file]
        
        # Remove old castling rights from hash
        if self.castling != '-':
            for right in self.castling:
                if right in ZOBRIST_CASTLING:
                    self.hash ^= ZOBRIST_CASTLING[right]
        
        # Remove piece from source square
        from_index = fr * 8 + fc
        self.hash ^= ZOBRIST_TABLE[piece][from_index]

        # En passant capture
        ep_capture = False
        if piece.lower() == 'p' and fc != tc and self.grid[tr][tc] == '.' and self.en_passant == to_sq:
            # Remove captured pawn from hash
            captured_pawn_row = tr - direction
            captured_pawn = self.grid[captured_pawn_row][tc]
            captured_index = captured_pawn_row * 8 + tc
            self.hash ^= ZOBRIST_TABLE[captured_pawn][captured_index]
            
            self.grid[captured_pawn_row][tc] = '.'
            capture = True
            ep_capture = True

        # Remove captured piece from hash (if not en passant)
        if capture and not ep_capture and self.grid[tr][tc] != '.':
            captured_piece = self.grid[tr][tc]
            to_index = tr * 8 + tc
            self.hash ^= ZOBRIST_TABLE[captured_piece][to_index]

        # Move piece
        self.grid[fr][fc] = '.'
        if promo:
            promoted_piece = promo.upper() if piece.isupper() else promo.lower()
            self.grid[tr][tc] = promoted_piece
            # Add promoted piece to hash
            to_index = tr * 8 + tc
            self.hash ^= ZOBRIST_TABLE[promoted_piece][to_index]
        else:
            self.grid[tr][tc] = piece
            # Add piece to destination square
            to_index = tr * 8 + tc
            self.hash ^= ZOBRIST_TABLE[piece][to_index]

        # Castling: move the rook and update hash
        if piece.lower() == 'k' and abs(tc - fc) == 2:
            if tc > fc:  # Kingside
                rook_from = (fr, 7)
                rook_to = (fr, 5)
            else:  # Queenside
                rook_from = (fr, 0)
                rook_to = (fr, 3)
            
            rook_piece = self.grid[rook_from[0]][rook_from[1]]
            
            # Remove rook from old position in hash
            rook_from_index = rook_from[0] * 8 + rook_from[1]
            self.hash ^= ZOBRIST_TABLE[rook_piece][rook_from_index]
            
            # Move rook
            self.grid[rook_from[0]][rook_from[1]] = '.'
            self.grid[rook_to[0]][rook_to[1]] = rook_piece
            
            # Add rook to new position in hash
            rook_to_index = rook_to[0] * 8 + rook_to[1]
            self.hash ^= ZOBRIST_TABLE[rook_piece][rook_to_index]

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
        
        # Add new castling rights to hash
        if self.castling != '-':
            for right in self.castling:
                if right in ZOBRIST_CASTLING:
                    self.hash ^= ZOBRIST_CASTLING[right]

        # Set en passant target after double pawn push
        if piece.lower() == 'p' and abs(tr - fr) == 2:
            mid_row = (tr + fr) // 2
            self.en_passant = sq_to_coord(mid_row, fc)
            # Add new en passant to hash
            ep_file = ord(self.en_passant[0]) - ord('a')
            self.hash ^= ZOBRIST_EP[ep_file]
        else:
            self.en_passant = None

        # Update halfmove clock (50-move rule)
        if piece.lower() == 'p' or capture:
            self.halfmove = 0
        else:
            self.halfmove += 1

        if self.turn == 'b':
            self.fullmove += 1

        # Toggle turn in hash
        self.hash ^= ZOBRIST_WHITE
        self.hash ^= ZOBRIST_BLACK
        
        self.turn = 'b' if self.turn == 'w' else 'w'

    
    def copy(self):
        """Create a shallow copy of the board for search calculations."""
        new_board = Board.__new__(Board)  # Create without calling __init__
        new_board.grid = [row[:] for row in self.grid]  # Shallow copy of lists
        new_board.turn = self.turn
        new_board.castling = self.castling
        new_board.en_passant = self.en_passant
        new_board.halfmove = self.halfmove
        new_board.fullmove = self.fullmove
        new_board.hash = self.hash
        return new_board
