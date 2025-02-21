import snappy, regina
import geometricmoves as gm

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

	res = []
	# get my version
	print('Comparing:')
	for (i, sh, sT) in moves:
		S = regina.Triangulation3(T)
		sh2 = shapes.copy()
		gm.threeTwoMove(S, sh2, i)
		print(f'Edge {i}:\n\t >Match?: {S.isIsomorphicTo(sT) != None}\n\t >SnapPy Shapes: {sh}\n\t >My Shapes: {sh2}')

testThreeTwoMove('mLLzPLwQQcdchfihlkjkllhsngvaklbvbvb')