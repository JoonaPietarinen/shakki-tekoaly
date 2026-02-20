"""Profile search performance."""
from board import Board
from search import negamax, find_best_move, clear_transposition_table, print_search_stats
import search
import time
import cProfile
import pstats
from io import StringIO


def profile_optimization_combinations():
    """
    Profile different combinations of optimizations to measure their individual impact.
    This helps identify which optimizations actually help vs. hurt.
    """
    print("\n" + "="*70)
    print("OPTIMIZATION COMBINATION PROFILING")
    print("="*70)
    
    scenarios = [
        {
            "name": "Baseline (no optimizations)",
            "QS": False,
            "History": False,
            "Killers": False,
        },
        {
            "name": "Quiescence only",
            "QS": True,
            "History": False,
            "Killers": False,
        },
        {
            "name": "Quiescence + Killer Moves",
            "QS": True,
            "History": False,
            "Killers": True,
        },
        {
            "name": "Quiescence + History",
            "QS": True,
            "History": True,
            "Killers": False,
        },
        {
            "name": "All Optimizations (QS + History + Killers)",
            "QS": True,
            "History": True,
            "Killers": True,
        },
    ]
    
    results = []
    
    for scenario in scenarios:
        clear_transposition_table()
        search.search_stats['nodes_searched'] = 0
        search.search_stats['quiescence_nodes'] = 0
        search.search_stats['beta_cutoffs'] = 0
        search.search_stats['tt_hits'] = 0
        
        # Apply feature flags
        search.ENABLE_QUIESCENCE = scenario["QS"]
        search.ENABLE_HISTORY_HEURISTIC = scenario["History"]
        search.ENABLE_KILLER_MOVES = scenario["Killers"]
        
        print(f"\n{scenario['name']}:")
        print("-" * 70)
        
        b = Board()
        start = time.time()
        score, move = negamax(b, 4, float('-inf'), float('inf'))
        elapsed = time.time() - start
        
        results.append({
            'scenario': scenario['name'],
            'nodes': search.search_stats['nodes_searched'],
            'qnodes': search.search_stats['quiescence_nodes'],
            'tt_hits': search.search_stats['tt_hits'],
            'cutoffs': search.search_stats['beta_cutoffs'],
            'time': elapsed,
            'move': move
        })
        
        print_search_stats()
        print(f"Time: {elapsed:.3f}s")
        print(f"Best move: {move}")
    
    # Restore defaults
    search.ENABLE_QUIESCENCE = True
    search.ENABLE_HISTORY_HEURISTIC = True
    search.ENABLE_KILLER_MOVES = True
    
    # Print comparison table
    print("\n" + "="*70)
    print("COMPARISON TABLE")
    print("="*70)
    
    baseline = results[0]
    
    print(f"\n{'Scenario':<45} {'Nodes':>10} {'Time':>8} {'Speedup':>8}")
    print("-" * 70)
    
    for result in results:
        speedup = baseline['nodes'] / result['nodes'] if result['nodes'] > 0 else 0
        print(f"{result['scenario']:<45} {result['nodes']:>10} {result['time']:>7.3f}s {speedup:>7.2f}x")
    
    print("\n" + "="*70)
    print("DETAILED METRICS")
    print("="*70)
    
    for result in results:
        print(f"\n{result['scenario']}:")
        print(f"  Negamax nodes: {result['nodes']}")
        print(f"  Quiescence nodes: {result['qnodes']}")
        print(f"  TT hits: {result['tt_hits']}")
        print(f"  Beta cutoffs: {result['cutoffs']}")
        print(f"  Time: {result['time']:.3f}s")


def profile_search():
    """Profile negamax with different depths."""
    clear_transposition_table()
    for depth in [2, 3, 4, 5]:
        search.search_stats['nodes_searched'] = 0
        search.search_stats['tt_hits'] = 0
        search.search_stats['tt_stores'] = 0
        search.search_stats['beta_cutoffs'] = 0
        search.search_stats['quiescence_nodes'] = 0
        
        b = Board()
        score, move = negamax(b, depth, float('-inf'), float('inf'))
        
        print(f"\nDepth {depth}:")
        print_search_stats()
        print(f"Best move: {move}\n")


def profile_iterative_deepening():
    """Profile iterative deepening with time limits."""
    print("\n" + "="*70)
    print("ITERATIVE DEEPENING PROFILING")
    print("="*70)
    
    # Test 1: Max depth without time limit
    clear_transposition_table()
    search.search_stats['nodes_searched'] = 0
    search.search_stats['tt_hits'] = 0
    search.search_stats['tt_stores'] = 0
    search.search_stats['beta_cutoffs'] = 0
    search.search_stats['reached_depth'] = 0
    search.search_stats['quiescence_nodes'] = 0
    
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
        search.search_stats['nodes_searched'] = 0
        search.search_stats['tt_hits'] = 0
        search.search_stats['tt_stores'] = 0
        search.search_stats['beta_cutoffs'] = 0
        search.search_stats['reached_depth'] = 0
        search.search_stats['quiescence_nodes'] = 0
        
        b = Board()
        start = time.time()
        move = find_best_move(b, depth=10, time_limit=time_limit)
        elapsed = time.time() - start
        
        print(f"\nTime limit: {time_limit}s")
        print(f"Actual time: {elapsed:.3f}s")
        print_search_stats()
        print(f"Best move: {move}")


def detailed_profile():
    """Run cProfile to see where time is spent."""
    print("\n" + "="*70)
    print("DETAILED PROFILING (cProfile)")
    print("="*70)
    
    clear_transposition_table()
    search.search_stats['nodes_searched'] = 0
    search.search_stats['tt_hits'] = 0
    search.search_stats['tt_stores'] = 0
    search.search_stats['beta_cutoffs'] = 0
    search.search_stats['quiescence_nodes'] = 0
    
    b = Board()
    
    # Profile depth 6 search
    profiler = cProfile.Profile()
    profiler.enable()
    
    score, move = negamax(b, 6, float('-inf'), float('inf'))
    
    profiler.disable()
    
    # Print stats
    s = StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Top 20 functions
    
    print(s.getvalue())
    print(f"\nBest move: {move}")
    print_search_stats()


if __name__ == "__main__":
    print("Chess AI Performance Profiling")
    print("="*70)
    
    # Run all profiles
    profile_optimization_combinations()
    print("\n" + "="*70)
    profile_search()
    print("\n" + "="*70)
    profile_iterative_deepening()
    print("\n" + "="*70)
    detailed_profile()