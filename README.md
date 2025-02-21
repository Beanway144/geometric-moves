# Geometric Moves
This is a repository of scripts that search through geometric triangulations of cusped hyperbolic 3-manifolds.

- `geometricmoves.py`  contains functions for applying local (2-3; 3-2) moves to a geometric triangulation, updating the geometric shapes and the triangulation.
- `geometricsearch.py` contains various scripts for searching through the geometric subgraph of the Pachner graph, using geometric 2-3 and 3-2 moves.
- `verifyisolated.py` quickly verifies if an input sig is geometrically isolated. Not dependent on other files here.
- `testmoves.py` will eventually be upgraded to a test suite.


# TODO
1. Change "depth" to proper tetrahedra height
2. Move to algebraic moves
3. Run census

# Census and Things to Look For
- Census of DD Recursion Gadget
- Database of geometrically isolated triangulations
- Q: Are there any pseudo-geometrically isolated triangulations? (no flat moves)
- Fix a manifold (e.g. fig8 sibling) and analyze distribution of geometric.
- Q: (Hard) Are there any manifolds with finitely many geometric triangulations?