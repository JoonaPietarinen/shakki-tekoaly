from board import coord_to_sq, sq_to_coord

def generate_legal_moves(board):
    # Generate a list of pseudo-legal moves in UCI format for the side to move
    moves = []
    color = board.turn  # 'w' or 'b'
    grid = board.grid

    def is_white(piece: str) -> bool:
        return piece.isupper()

    def same_color(piece: str) -> bool:
        if piece == '.':
            return False
        return (piece.isupper() and color == 'w') or (piece.islower() and color == 'b')

    def opponent(piece: str) -> bool:
        if piece == '.':
            return False
        return (piece.isupper() and color == 'b') or (piece.islower() and color == 'w')

    def add_move(fr: int, fc: int, tr: int, tc: int, promote: bool = False):
        base = sq_to_coord(fr, fc) + sq_to_coord(tr, tc)
        if promote:
            for p in ['q', 'r', 'b', 'n']:
                moves.append(base + p)
        else:
            moves.append(base)

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def gen_pawn(r: int, c: int, piece: str):
        direction = -1 if is_white(piece) else 1
        start_row = 6 if is_white(piece) else 1
        promo_row = 0 if is_white(piece) else 7

        one_r = r + direction
        if in_bounds(one_r, c) and grid[one_r][c] == '.':
            add_move(r, c, one_r, c, promote=(one_r == promo_row))
            two_r = r + 2 * direction
            if r == start_row and in_bounds(two_r, c) and grid[two_r][c] == '.':
                add_move(r, c, two_r, c)

        for dc in (-1, 1):
            cc = c + dc
            if not in_bounds(one_r, cc):
                continue
            target = grid[one_r][cc]
            if opponent(target):
                add_move(r, c, one_r, cc, promote=(one_r == promo_row))
            if board.en_passant:
                ep_r, ep_c = coord_to_sq(board.en_passant)
                if ep_r == one_r and ep_c == cc:
                    add_move(r, c, one_r, cc)

    def gen_knight(r: int, c: int, piece: str):
        deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc) or same_color(grid[nr][nc]):
                continue
            add_move(r, c, nr, nc)

    def gen_slider(r: int, c: int, piece: str, directions):
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                if same_color(grid[nr][nc]):
                    break
                add_move(r, c, nr, nc)
                if opponent(grid[nr][nc]):
                    break
                nr += dr
                nc += dc

    def gen_king(r: int, c: int, piece: str):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc) or same_color(grid[nr][nc]):
                    continue
                add_move(r, c, nr, nc)

        # Castling (does not check for check safety)
        if color == 'w' and r == 7 and c == 4:
            if 'K' in board.castling and grid[7][5] == '.' and grid[7][6] == '.':
                add_move(r, c, 7, 6)
            if 'Q' in board.castling and grid[7][3] == '.' and grid[7][2] == '.' and grid[7][1] == '.':
                add_move(r, c, 7, 2)
        if color == 'b' and r == 0 and c == 4:
            if 'k' in board.castling and grid[0][5] == '.' and grid[0][6] == '.':
                add_move(r, c, 0, 6)
            if 'q' in board.castling and grid[0][3] == '.' and grid[0][2] == '.' and grid[0][1] == '.':
                add_move(r, c, 0, 2)

    for r in range(8):
        for c in range(8):
            piece = grid[r][c]
            if piece == '.':
                continue
            if color == 'w' and not piece.isupper():
                continue
            if color == 'b' and not piece.islower():
                continue

            p = piece.lower()
            if p == 'p':
                gen_pawn(r, c, piece)
            elif p == 'n':
                gen_knight(r, c, piece)
            elif p == 'b':
                gen_slider(r, c, piece, [(1, 1), (1, -1), (-1, 1), (-1, -1)])
            elif p == 'r':
                gen_slider(r, c, piece, [(1, 0), (-1, 0), (0, 1), (0, -1)])
            elif p == 'q':
                gen_slider(r, c, piece, [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)])
            elif p == 'k':
                gen_king(r, c, piece)

    return moves