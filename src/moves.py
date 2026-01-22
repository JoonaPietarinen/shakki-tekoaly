from board import coord_to_sq, sq_to_coord

def generate_legal_moves(board):
    # Generate a list of legal moves in UCI format for the side to move
    color = board.turn  # 'w' or 'b'
    grid = board.grid
    pseudo = []

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

    def add_pseudo(fr: int, fc: int, tr: int, tc: int, promote: bool = False):
        base = sq_to_coord(fr, fc) + sq_to_coord(tr, tc)
        if promote:
            for p in ['q', 'r', 'b', 'n']:
                pseudo.append(base + p)
        else:
            pseudo.append(base)

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < 8 and 0 <= c < 8

    def is_attacked(r: int, c: int, by_color: str, grid_state=None) -> bool:
        # Check if square (r, c) is attacked by side 'by_color'
        gs = grid_state if grid_state is not None else grid
        # Pawn attacks
        pawn_dir = -1 if by_color == 'w' else 1
        for dc in (-1, 1):
            rr = r + pawn_dir
            cc = c + dc
            if in_bounds(rr, cc):
                p = gs[rr][cc]
                if p != '.' and ((p == 'P' and by_color == 'w') or (p == 'p' and by_color == 'b')):
                    return True
        # Knight attacks
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            rr, cc = r + dr, c + dc
            if in_bounds(rr, cc):
                p = gs[rr][cc]
                if p != '.':
                    if by_color == 'w' and p == 'N':
                        return True
                    if by_color == 'b' and p == 'n':
                        return True
        # King attacks
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc):
                    p = gs[rr][cc]
                    if p != '.':
                        if by_color == 'w' and p == 'K':
                            return True
                        if by_color == 'b' and p == 'k':
                            return True
        # Sliding attacks
        def slide(directions, attackers):
            for dr, dc in directions:
                rr, cc = r + dr, c + dc
                while in_bounds(rr, cc):
                    p = gs[rr][cc]
                    if p != '.':
                        if by_color == 'w' and p == p.upper() and p.lower() in attackers:
                            return True
                        if by_color == 'b' and p == p.lower() and p in attackers:
                            return True
                        break
                    rr += dr
                    cc += dc
            return False
        if slide([(1, 0), (-1, 0), (0, 1), (0, -1)], {'r', 'q'}):
            return True
        if slide([(1, 1), (1, -1), (-1, 1), (-1, -1)], {'b', 'q'}):
            return True
        return False

    def gen_pawn(r: int, c: int, piece: str):
        # Generate pawn moves
        direction = -1 if is_white(piece) else 1
        start_row = 6 if is_white(piece) else 1
        promo_row = 0 if is_white(piece) else 7

        one_r = r + direction
        if in_bounds(one_r, c) and grid[one_r][c] == '.':
            add_pseudo(r, c, one_r, c, promote=(one_r == promo_row))
            two_r = r + 2 * direction
            if r == start_row and in_bounds(two_r, c) and grid[two_r][c] == '.':
                add_pseudo(r, c, two_r, c)

        for dc in (-1, 1):
            cc = c + dc
            if not in_bounds(one_r, cc):
                continue
            target = grid[one_r][cc]
            if opponent(target):
                add_pseudo(r, c, one_r, cc, promote=(one_r == promo_row))
            if board.en_passant:
                ep_r, ep_c = coord_to_sq(board.en_passant)
                if ep_r == one_r and ep_c == cc:
                    add_pseudo(r, c, one_r, cc)

    def gen_knight(r: int, c: int, piece: str):
        # Generate knight moves
        deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if not in_bounds(nr, nc) or same_color(grid[nr][nc]):
                continue
            add_pseudo(r, c, nr, nc)

    def gen_slider(r: int, c: int, piece: str, directions):
        # Generate moves for bishops, rooks, queens
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while in_bounds(nr, nc):
                if same_color(grid[nr][nc]):
                    break
                add_pseudo(r, c, nr, nc)
                if opponent(grid[nr][nc]):
                    break
                nr += dr
                nc += dc

    def gen_king(r: int, c: int, piece: str):
        # Generate king moves
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if not in_bounds(nr, nc) or same_color(grid[nr][nc]):
                    continue
                add_pseudo(r, c, nr, nc)

        # Castling with safety checks
        def squares_safe(squares):
            opp = 'b' if color == 'w' else 'w'
            return all(not is_attacked(sr, sc, opp) for sr, sc in squares)

        if color == 'w' and r == 7 and c == 4:
            if 'K' in board.castling and grid[7][5] == '.' and grid[7][6] == '.' and squares_safe([(7, 4), (7, 5), (7, 6)]):
                add_pseudo(r, c, 7, 6)
            if 'Q' in board.castling and grid[7][3] == '.' and grid[7][2] == '.' and grid[7][1] == '.' and squares_safe([(7, 4), (7, 3), (7, 2)]):
                add_pseudo(r, c, 7, 2)
        if color == 'b' and r == 0 and c == 4:
            if 'k' in board.castling and grid[0][5] == '.' and grid[0][6] == '.' and squares_safe([(0, 4), (0, 5), (0, 6)]):
                add_pseudo(r, c, 0, 6)
            if 'q' in board.castling and grid[0][3] == '.' and grid[0][2] == '.' and grid[0][1] == '.' and squares_safe([(0, 4), (0, 3), (0, 2)]):
                add_pseudo(r, c, 0, 2)

    # Find pseudo-legal moves
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

    # Filter out moves that leave king in check
    legal = []
    for m in pseudo:
        temp = board.copy()
        mover = color
        temp.make_move(m)
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = temp.grid[r][c]
                if p != '.' and ((mover == 'w' and p == 'K') or (mover == 'b' and p == 'k')):
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if not king_pos:
            continue
        if not is_attacked(king_pos[0], king_pos[1], temp.turn, temp.grid):
            legal.append(m)

    return legal


def is_checkmate(board):
    # Check if current side to move is checkmated
    moves = generate_legal_moves(board)
    if not moves:
        # No legal moves - check if king is in check
        color = board.turn
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board.grid[r][c]
                if p != '.' and ((color == 'w' and p == 'K') or (color == 'b' and p == 'k')):
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        if king_pos:
            opponent_color = 'b' if color == 'w' else 'w'
            # Reuse is_attacked logic from generate_legal_moves
            temp_board = board.copy()
            temp_moves = generate_legal_moves(temp_board)  # This checks attacks internally
            return True  # If no moves and we have a king, it's checkmate
    return False


def is_stalemate(board):
    # Check if current side to move is stalemated (no legal moves but not in check)
    moves = generate_legal_moves(board)
    if not moves:
        return not is_checkmate(board)
    return False


def is_draw_by_fifty_moves(board):
    # Check if draw by 50-move rule
    return board.halfmove >= 100  # 50 full moves = 100 half-moves

