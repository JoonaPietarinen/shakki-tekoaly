"""Profile search performance."""
from board import Board
from search import negamax, find_best_move, clear_transposition_table, print_search_stats, search_stats
import time
import cProfile
import pstats
from io import StringIO

def profile_search():
    """Profile negamax with different depths."""
    clear_transposition_table()
    for depth in [2, 3, 4, 5]:
        search_stats['nodes_searched'] = 0
        search_stats['tt_hits'] = 0
        search_stats['tt_stores'] = 0
        search_stats['beta_cutoffs'] = 0
        search_stats['quiescence_nodes'] = 0
        
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
    search_stats['beta_cutoffs'] = 0
    search_stats['reached_depth'] = 0
    search_stats['quiescence_nodes'] = 0
    
    b = Board()
    start = time.time()
    move = find_best_move(b, depth=5, time_limit=None)
    elapsed = time.time() - start
    
    print(f"\nMax depth 5 (no time limit):")
    print(f"Time: {elapsed:.3f}s")
    print_search_stats()
    print(f"Best move: {move}")
    
    # Test 2: Time limit tests
    for time_limit in [0.1, 0.5, 1, 2, 5]:
        clear_transposition_table()
        search_stats['nodes_searched'] = 0
        search_stats['tt_hits'] = 0
        search_stats['tt_stores'] = 0
        search_stats['beta_cutoffs'] = 0
        search_stats['reached_depth'] = 0
        search_stats['quiescence_nodes'] = 0
        
        b = Board()
        start = time.time()
        move = find_best_move(b, depth=10, time_limit=time_limit)
        elapsed = time.time() - start
        
        print(f"\nTime limit: {time_limit}s (max_depth=10):")
        print(f"Actual time: {elapsed:.3f}s")
        print_search_stats()
        print(f"Reached depth: {search_stats['reached_depth']}")
        print(f"Best move: {move}")


def detailed_profile():
    """Run cProfile to see where time is spent."""
    print("\n" + "="*50)
    print("DETAILED PROFILING (cProfile)")
    print("="*50)
    
    clear_transposition_table()
    search_stats['nodes_searched'] = 0
    search_stats['tt_hits'] = 0
    search_stats['tt_stores'] = 0
    search_stats['beta_cutoffs'] = 0
    search_stats['quiescence_nodes'] = 0
    
    b = Board()
    
    # Profile depth 4 search
    profiler = cProfile.Profile()
    profiler.enable()
    
    score, move = negamax(b, 4, float('-inf'), float('inf'))
    
    profiler.disable()
    
    # Print stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    print(s.getvalue())
    print(f"\nBest move: {move}")
    print_search_stats()


if __name__ == "__main__":
    profile_search()
    profile_iterative_deepening()
    detailed_profile()