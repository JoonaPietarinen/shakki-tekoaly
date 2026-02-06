"""Profile search performance."""
from board import Board
from search import negamax, find_best_move, clear_transposition_table, print_search_stats, search_stats
import time

def profile_search():
    """Profile negamax with different depths."""
    clear_transposition_table()
    for depth in [2, 3, 4]:
        search_stats['nodes_searched'] = 0
        search_stats['tt_hits'] = 0
        search_stats['tt_stores'] = 0
        
        b = Board()
        score, move = negamax(b, depth, float('-inf'), float('inf'))
        
        print(f"\nDepth {depth}:")
        print_search_stats()
        print(f"Best move: {move}\n")


def profile_iterative_deepening():
    """Profile iterative deepening with time limits."""
    print("\n" + "="*50)
    print("ITERATIVE DEEPENING PROFILING")
    print("="*50)
    
    # Test 1: Max depth without time limit
    clear_transposition_table()
    search_stats['nodes_searched'] = 0
    search_stats['tt_hits'] = 0
    search_stats['tt_stores'] = 0
    
    b = Board()
    start = time.time()
    move = find_best_move(b, depth=5, time_limit=None)
    elapsed = time.time() - start
    
    print(f"\nMax depth 5 (no time limit):")
    print(f"Time: {elapsed:.3f}s")
    print_search_stats()
    print(f"Best move: {move}")
    
    # Test 2: Time limit tests
    for time_limit in [0.1, 0.5, 1, 2, 180]:
        clear_transposition_table()
        search_stats['nodes_searched'] = 0
        search_stats['tt_hits'] = 0
        search_stats['tt_stores'] = 0
        
        b = Board()
        start = time.time()
        move = find_best_move(b, depth=10, time_limit=time_limit)
        elapsed = time.time() - start
        
        print(f"\nTime limit: {time_limit}s (max_depth=10):")
        print(f"Actual time: {elapsed:.3f}s")
        print_search_stats()
        print(f"Best move: {move}")


if __name__ == "__main__":
    profile_search()
    profile_iterative_deepening()