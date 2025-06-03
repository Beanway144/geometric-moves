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

def showLocalMoves(sig):
	print('Possible 2-3 Moves:')
	M = snappy.Manifold(sig)
	T = regina.Triangulation3(M)
	for i in range(T.countTriangles()):
		S = regina.Triangulation3(T)
		if S.pachner(S.triangle(i), True, False): #dumb
			S.pachner(S.triangle(i), False, True)
			N = snappy.Manifold(S)
			if N.verify_hyperbolicity()[0]:
				print(f'Face {i} [{S.isoSig()}]: Geometric')
			else:
				print(f'Face {i} [{S.isoSig()}]: Not Geometric')
		else:
			print(f'Face {i} [{S.isoSig()}]: Not Possible')
