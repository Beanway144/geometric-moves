import regina, snappy
import geometricmoves as gm
import geometricsearch as gs
import time
from sage.all import QQbar

##### Recursion Gadget Search ####
# A *recursion gadget* is a substructure of a geometric triangulation and a sequence of moves
# which produce a new geometric triangulation in such a way that the substructure reappears.
# Recurring on the substructure admits infinitely many geometric triangulations.
# Dadd and Duan showed the Figure-8 Knot admits a two-tetrahedron recursive gadget, which
# we call a Dadd-Duan or DD Recursion Gadget.

def checkDDRec(tri, shapes):
	"""
	Given a triangulation tri and a list of shapes, check whether the 
	Dadd-Duan Recursion Gadget exists:
	- A123 = B230 and A012 = B013
	- shape of A = shape of B (implied [write proof])
	- real part of shape < 1

	If exists, return True and the indices of corresponding tetrahedra
	"""
	found_combinatorial = False
	combin_at = []
	for face in tri.triangles():
		embed0 = face.embedding(0)
		tet0 = embed0.simplex()
		tet_num0 = tet0.index()
		tet_0_face_num = embed0.face()
		v0 = embed0.vertices() # (perm) Maps vertices (0,1,2) of face to the corresponding vertex numbers of tet0

		embed1 = face.embedding(1)
		tet1 = embed1.simplex()
		tet_num1 = tet1.index()
		tet_1_face_num = embed1.face()
		v1 = embed1.vertices() # Maps vertices (0,1,2) of face to the corresponding vertex numbers of tet1

		ag0 = tet0.adjacentGluing(v0[0])
		ag1 = tet0.adjacentGluing(v0[1])
		ag2 = tet0.adjacentGluing(v0[2])

		try:
			shape0 = QQbar(shapes[tet_num0])
		except:
			shape0 = shapes[tet_num0]

	    # check the other faces
	    # TODO: draw picture of this so it can make sense to others
		if tet0.adjacentTetrahedron(v0[0]).index() == tet_num1 and (ag0[v0[3]] == v1[0] and ag0[v0[1]] == v1[3] and ag0[v0[2]] == v1[2]):
			if (1/(1-shape0)).real() < 1:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))
		if tet0.adjacentTetrahedron(v0[2]).index() == tet_num1 and (ag2[v0[3]] == v1[2] and ag2[v0[0]] == v1[3] and ag2[v0[1]] == v1[1]):
			if shape0.real() < 1:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))
		if tet0.adjacentTetrahedron(v0[1]).index() == tet_num1 and (ag1[v0[3]] == v1[1] and ag1[v0[2]] == v1[3] and ag1[v0[0]] == v1[0]):
			if ((shape0 - 1)/shapes[tet_num0]).real() < 1:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))

	if found_combinatorial:
		print("|||||> error: Found rec gadget combinatorial rec gadget but not other conditions! <|||||")
	return (False, -1, -1)

def quick_check(sig):
	M = snappy.Manifold(sig)
	T = regina.Triangulation3(M)
	T.orient()
	shapes = M.tetrahedra_shapes(part='rect')
	print(checkDDRec(T, shapes))

def pseudogeometricDDSearch(sig, max_tets, id_string, depth, verbose=True, directory='graphs', levels=False):
	"""
	Given an isosig, search pseudogeometric graph in search of a DD Recursion Gadget.
	Returns if found, otherwise goes to max_tets ceiling.
	id_string is just an identifier to put next to the sigs that return true, e.g. index in a census
	"""
	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	og_size = T.countTetrahedra()
	M = snappy.Manifold(T)

	### field may not be found, so revert to float
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	
	# Check immediately if first triangulation has DD gadget
	if checkDDRec(T, shapes)[0]:
		f = open(f'{directory}/dd-gadget-knots-maxtet{max_tets}-depth{depth}.csv', "a")
		f.write(f'{id_string},{sig},0\n')
		f.close()
		print(f'(!***!) Found in first triangulation!')
		return


	flat = [sig]


	# TODO : [ (Triangulation, [Shapes], index, dimension) ]
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)
		Tsig = T.isoSig()

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented > -1: # if flat or geometric
				if not newSig in flat: #if we haven't seen it before
					# record new triangulation sig
					flat.append(newSig)
					if oriented > 0 and checkDDRec(newT, newShapes)[0]:
						f = open(f'{directory}/dd-gadget-knots-maxtet{max_tets}-depth{depth}.csv', "a")
						f.write(f'{id_string},{newSig},{newT.countTetrahedra() - regina.Triangulation3.fromIsoSig(sig).countTetrahedra()}\n')
						f.close()
						print(f'(*) Found after {len(flat)} pseudogeometric triangulations searched!')
						return

					# add neighbors to queue
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					keep_going = (abs(newT.countTetrahedra() -  og_size)< max_tets) if levels else (newT.countTetrahedra() < max_tets)
					if keep_going: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
				
			
						
	if verbose:
		print(f'DD gadget not found...')
		print(f'Number of pseudogeometric triangulations: {len(flat)}')

	return

def censusDDSearch(depth, max_tets, directory='.'):
	f = open(f'{directory}/dd-gadget-knots-maxtet{max_tets}-depth{depth}.csv', "w")
	f.write(f'id,sig,depth\n')
	f.close()
	for i in range(depth):
		print(f'{i}----------------------------------------------------------')
		M = snappy.OrientableCuspedCensus[i]
		sig = M.triangulation_isosig(decorated=False)
		pseudogeometricDDSearch(sig, max_tets, str(i), depth, True, directory)

def knotCensusDDSearch(depth, levels, directory='.'):
	"""
	Uses 'levels' instead of max tets, i.e. max tets = census tets + levels.
	"""
	f = open(f'{directory}/dd-gadget-knots-levels{levels}-depth{depth}.csv', "w")
	f.write(f'id,sig,depth\n')
	f.close()
	for i in range(depth):
		print(f'{i}----------------------------------------------------------')
		M = snappy.CensusKnots[i]
		sig = M.triangulation_isosig(decorated=False)
		pseudogeometricDDSearch(sig, levels, str(i), depth, True, directory, True)

