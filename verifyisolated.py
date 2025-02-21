import snappy, regina

def verifyIsolated(sig):
	"""
	Given an isosig, returns True if sig is geometrically isolated (by 2-3 and 3-2 moves)
	naive (and slow?) implementation...should rework so that doesn't repeat calcs
	"""

	T = regina.Triangulation3.fromIsoSig(sig)

	for i in range(T.countTriangles()):
		S = regina.Triangulation3(T)
		if not S.pachner(S.triangle(i)):
			continue
		M = snappy.Manifold(S)
		if M.verify_hyperbolicity()[0]:
			return False

	for i in range(T.countEdges()):
		S = regina.Triangulation3(T)
		if not S.pachner(S.edge(i)):
			continue
		M = snappy.Manifold(S)
		if M.verify_hyperbolicity()[0]:
			return False

	return True
