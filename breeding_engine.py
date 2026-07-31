"""
Palworld Breeding Engine
- Computes child from two parents using the breeding power formula
- Handles unique pair exceptions from breeding.json
- BFS pathfinding to find shortest breeding chain (up to 10 generations)
"""

import json
import math
import os
from collections import deque
from pal_data import PALS
import sys


# ---------------------------------------------------------------------------
# Load unique pair exceptions from breeding.json
# ---------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(__file__)

_BREEDING_JSON = os.path.join(base_dir, "breeding.json")

def _load_exceptions():
    """Return two structures:
    - unique_pairs: dict  frozenset({parentA, parentB}) -> list of childId
    - self_breed: set of internal names that produce themselves when bred together
    """
    with open(_BREEDING_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique = {}
    self_breed = set()

    for pair in data.get("uniquePairs", []):
        pa = pair["parentAId"]
        pb = pair["parentBId"]
        child = pair["childId"]
        
        if pa == "Blueplatypus": pa = "BluePlatypus"
        if pb == "Blueplatypus": pb = "BluePlatypus"

        # Same species self-breeding entries
        if pa == pb and pa == child:
            self_breed.add(pa)
            continue

        key = frozenset((pa, pb))
        if key not in unique:
            unique[key] = []
        if child not in unique[key]:
            unique[key].append(child)

    return unique, self_breed

UNIQUE_PAIRS, SELF_BREED_SET = _load_exceptions()


# ---------------------------------------------------------------------------
# Sorted list of pals by breeding power (for closest-match lookup)
# ---------------------------------------------------------------------------
# Each entry: (breeding_power, paldex, is_variant, internal_name)
_SORTED_PALS = sorted(
    [(info[1], info[2], info[3], iname) for iname, info in PALS.items() if iname not in SELF_BREED_SET],
    key=lambda x: (x[0], x[1], x[2])
)


def _find_closest_pal(target_power: int) -> str:
    """Find the Pal whose breeding power is closest to target_power.
    Tie-break: lowest paldex wins, then lowest is_variant.
    """
    best_name = None
    best_diff = float("inf")
    best_idx = float("inf")
    best_var = float("inf")

    for bp, paldex, is_variant, iname in _SORTED_PALS:
        diff = abs(bp - target_power)
        # Tie-breaker condition
        if diff < best_diff or (
            diff == best_diff and (
                paldex < best_idx or (paldex == best_idx and is_variant < best_var)
            )
        ):
            best_diff = diff
            best_idx = paldex
            best_var = is_variant
            best_name = iname
    return best_name


def compute_child(parent_a: str, parent_b: str) -> list[str]:
    """Compute the child of two parents (internal names).
    Returns a list of possible children internal names, or empty list if either parent is unknown.
    """
    if parent_a not in PALS or parent_b not in PALS:
        return []

    # 1. Check unique pair exceptions
    key_fs = frozenset((parent_a, parent_b))
    if key_fs in UNIQUE_PAIRS:
        return UNIQUE_PAIRS[key_fs]

    # 2. Same species always resolves to itself
    if parent_a == parent_b:
        return [parent_a]

    # 3. Standard formula: floor((P1 + P2 + 1) / 2)
    p1 = PALS[parent_a][1]  # breeding power
    p2 = PALS[parent_b][1]
    child_power = math.floor((p1 + p2 + 1) / 2)

    closest = _find_closest_pal(child_power)
    return [closest] if closest else []


def get_pal_name(internal_name: str) -> str:
    """Get the English display name for an internal name."""
    if internal_name in PALS:
        return PALS[internal_name][0]
    return internal_name


def get_all_pal_names() -> list[tuple[str, str]]:
    """Return list of (internal_name, english_name) sorted by english_name."""
    return sorted(
        [(iname, info[0]) for iname, info in PALS.items()],
        key=lambda x: x[1]
    )


# ---------------------------------------------------------------------------
# BFS: find shortest breeding path from source to target
# ---------------------------------------------------------------------------
def bfs_shortest_path(source: str, target: str, max_depth: int = 10):
    """
    BFS to find shortest breeding path from source pal to target pal.
    
    The idea: at each BFS level, we have a set of "available" pals.
    Initially we have ALL pals (you can catch any pal in the wild).
    We want to find the minimal chain of breedings to produce the target.
    
    Actually, a more practical approach:
    - We want to find which pairs of pals produce the target (or produce
      intermediaries that eventually lead to the target).
    - We do REVERSE BFS: start from target, find all parent pairs that 
      produce it, then check if those parents are "simple" (directly available)
      or need to be bred themselves.
    
    Simplified approach: Since any pal can be caught in the wild, we want
    the shortest CHAIN of breedings. If target can be produced directly by
    breeding two pals, that's depth 1. If one of those parents needs to be 
    bred first, that's depth 2, etc.
    
    We use forward BFS where each node is a pal we want to produce,
    and we explore all possible parent-pair combinations.
    
    Returns: list of breeding steps [(parent_a, parent_b, child), ...]
             in order from first breeding to last, or None if no path found.
    """
    if source == target:
        return []

    if source not in PALS or target not in PALS:
        return None

    UNBREEDABLE_PALS = {"KingWhale"}
    all_pals = [p for p in PALS.keys() if p not in UNBREEDABLE_PALS]

    # BFS: we search for a breeding tree that produces `target`
    # Each state in BFS: the pal we need to produce
    # For each pal, we check: can it be produced by breeding source with something?
    # Or by breeding any two "base" pals (pals we already have)?
    
    # Available pals: all wild pals + source (always available)
    # We want to produce target with minimum breeding steps
    
    # Approach: BFS over "recipes"
    # Level 0: we have all base pals available
    # Level 1: we can breed any two base pals -> get new pals
    # Check if target is reachable at level 1
    # Level 2: breed level-1 results with base pals, etc.
    
    # Optimized: reverse lookup - for target, find all (A, B) such that breed(A,B) = target
    # If A and B are both base pals -> done in 1 step
    # If one of them needs breeding -> 2 steps, etc.
    
    # For performance we precompute: for each pal, which parent pairs produce it
    # But with 299 pals, that's 299*300/2 ≈ 45000 pairs - manageable
    
    # Build reverse map: child -> list of (parentA, parentB)
    # We compute this on the fly
    
    # Actually, let's use a simpler BFS:
    # State = set of pals we can currently produce
    # Initially = all base pals
    # At each step, breed pairs and see if we get target
    # But we want minimum STEPS (sequential breedings), not parallel
    
    # Most practical: find a CHAIN where:
    # Step 1: breed A + B -> C  (A, B are base pals or source)
    # Step 2: breed C + D -> E  (D is base, C is from step 1)
    # ...until we get target
    
    # BFS on which pal to produce at each step
    # We track "produced" set: initially all pals
    # For target: find if any (X, Y) where breed(X,Y) == target
    
    # Since all pals are available (you can catch them), the question is
    # really just: which pairs produce the target?
    # And if the target can only be produced via a unique combo requiring
    # an intermediate that is ALSO a unique combo result, then we need multi-step.
    
    # Simple BFS approach:
    # - Check if target can be produced by any pair of existing pals -> 1 step
    # - If not (e.g. target is only produced by unique combos with pals that
    #   themselves need breeding), go deeper
    
    # For most cases, since ALL pals exist in the wild, almost everything
    # is reachable in 1 step. The multi-step cases are for pals that can
    # ONLY be produced through a specific chain of unique combos.
    
    # Let's find ALL pairs that produce the target
    
    # First, check direct breeding (1 generation)
    # For target: find all (A, B) such that compute_child(A, B) == target
    # Among those, prefer pairs involving source
    
    # BFS approach with proper tree building:
    # We search for a tree of breedings where leaves are available pals
    # and the root produces target.
    
    # For efficiency, let's do iterative deepening:
    # Depth 1: any two pals breed to target
    # Depth 2: one parent needs to be bred from two base pals first
    # etc.
    
    results = []
    
    # BFS using reverse search
    visited = {source}
    queue = deque([(source, [])])
    
    depth = 1
    found_at_depth = False
    
    # max depth set to an arbitrary high limit since it's fast
    max_depth = 10
    
    while queue and depth <= max_depth and not found_at_depth:
        level_size = len(queue)
        
        for _ in range(level_size):
            current_pal, path = queue.popleft()
            
            for partner in all_pals:
                children = compute_child(current_pal, partner)
                for child in children:
                    if child == target:
                        results.append(path + [(current_pal, partner, child)])
                        found_at_depth = True
                        if len(results) >= 20:  # Cap at 20 routes to maintain UI performance
                            return results
                    elif not found_at_depth and child not in visited:
                        visited.add(child)
                        queue.append((child, path + [(current_pal, partner, child)]))
                            
        depth += 1
        
    return results if results else None
