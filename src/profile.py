"""Profile search performance."""
from board import Board
from search import negamax, clear_transposition_table, print_search_stats, search_stats

def profile_search():
    """Profile negamax with different depths."""
    clear_transposition_table()
    for depth in [2, 3, 4, 5]:
        search_stats['nodes_searched'] = 0
        search_stats['tt_hits'] = 0
        search_stats['tt_stores'] = 0
        
        b = Board()
        score, move = negamax(b, depth, float('-inf'), float('inf'))
        
        print(f"\nDepth {depth}:")
        print_search_stats()
        print(f"Best move: {move}\n")


if __name__ == "__main__":
    profile_search()