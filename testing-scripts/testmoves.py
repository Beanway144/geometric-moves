import snappy, regina
import geometricmoves as gm
import geometricsearch as gs

def testThreeTwoMove(sig):
	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)
	shapes = M.tetrahedra_shapes(part='rect')
	print(f'shapes: {shapes}')
	moves = [] # [(edge #, shapes)]
	# get snappy's version
	for i in range(T.countEdges()):
		S = regina.Triangulation3(T)
		if S.pachner(S.edge(i)):
			N = snappy.Manifold(S)
			hyp, sh = N.verify_hyperbolicity()
			if hyp:
				moves.append((i, sh, S))

	if len(moves) < 1:
		print("No possible geometric 3-2 moves.")
		return
	res = []
	# get my version
	print('Comparing:')
	for (i, sh, sT) in moves:
		S = regina.Triangulation3(T)
		sh2 = shapes.copy()
		gm.threeTwoMove(S, sh2, i)
		print(f'Edge {i}:\n\t >Match?: {S.isIsomorphicTo(sT) != None}\n\t >SnapPy Shapes: {sh}\n\t >My Shapes: {sh2}')

# testThreeTwoMove('hLLAMkbcedfggglsqsqqip')

def testSearch(census_depth, max_tets):
	for i in range(census_depth):
		M = snappy.OrientableCuspedCensus[i]
		sig = M.triangulation_isosig(decorated=False)
		gs.geometricSearch(sig, max_tets, True)
		print(f'[{i}]---------------------------------------------\n')

def possibleTwoThreeMoves(sig):
	T = regina.Triangulation3.fromIsoSig(sig)
	M = snappy.Manifold(T)
	for i in range(T.countTriangles()):
		S = regina.Triangulation3(T)
		if S.pachner(S.triangle(i), True, False):
			S.pachner(S.triangle(i))
			print(f'On face {i}: {S.isoSig()}')

def possibleGeometricTwoThreeMoves(sig): #slow
	T = regina.Triangulation3.fromIsoSig(sig)
	M = snappy.Manifold(T)
	for i in range(T.countTriangles()):
		S = regina.Triangulation3(T)
		if S.pachner(S.triangle(i), True, False):
			S.pachner(S.triangle(i))
			M = snappy.Manifold(S)
			if M.verify_hyperbolicity()[0]:
				print(f'On face {i}: {S.isoSig()}')


testSearch(500, 9)