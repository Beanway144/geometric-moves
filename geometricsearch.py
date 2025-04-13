import regina, snappy
import geometricmoves as gm
import time
from sage.all import QQbar


def geometricSearch(sig, max_tets, verify=False, verbose=True, census=False):
	"""
	Perform geometric pachner moves until no longer possible
	Assumes sig is geometric
	Doesn't search above max_tets (depth of search)
	"""
	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	### field may not be found
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	

	geometric = [sig]
	geomshapes = [shapes] # throw shapes in here, indexed same as geometric
	nongeometric = []

	# TODO : [ (Triangulation, [Shapes], index, dimension) ]
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, oriented = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, oriented = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented == 1:
				if not newSig in geometric: #if we haven't seen it before
					geometric.append(newSig)
					if census:
						f = open(f'{sig}.txt', "a")
						f.write(f'[{newSig}], {newShapes}\n')
						f.close()
					geomshapes.append(newShapes)
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
			else:
				if not newSig in nongeometric: #if we haven't seen it before
					nongeometric.append(newSig)
						
	if verbose:
		print(f'Number of geometric triangulations: {len(geometric)}')
		print(f'Number of non-geometric triangulations: {len(nongeometric)}')
		print(f'Total: {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')
	t1 = time.time()

	if verify: #verify that geometric are geometric, non are non
		print("Verifying geometric...")

		for i in range(len(geometric)):
			t = geometric[i]
			M = snappy.Manifold(t)
			tf, shapes = M.verify_hyperbolicity()
			L = M.tetrahedra_field_gens()
			shapes = L.find_field(100,10)[2]
			# pp_copmare_shapes(shapes, geomshapes[i])
			if not tf:
				print(f"Geometric not actually geometric: {M.triangulation_isosig(decorated=False)}")
				assert False
		print("Done verifying geometric. Verifying nongeometric...")
		for t in nongeometric:
			M = snappy.Manifold(t)
			if M.verify_hyperbolicity()[0]:
				print(f"Nongeometric actually geometric: {M.triangulation_isosig(decorated=False)}")
				assert False
		print(f"Done! Verified {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t1, 2)} seconds.")
	return geometric

def graphGeometricSearch(sig, max_tets, verbose=True, geometric_only=False):
	"""
	Perform geometric pachner moves until no longer possible
	Assumes sig is geometric
	Doesn't search above max_tets (depth of search)
	makes a graph along the way, csv format for gephi
	- Recording geometric and non
	"""

	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	### field may not be found -- to fix later
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	

	geometric = [sig]
	nongeometric = []

	f = open(f'graphs/{sig}-nodes.csv', "w")
	f.write(f'id,oriented,tetrahedra\n{sig},1,{T.countTetrahedra()}\n')
	f.close()
	f = open(f'graphs/{sig}-edges.csv', "w")
	# labeling edge with #tet - index to look for repeated patterns!
	f.write('target,source,label\n')
	f.close()

	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, oriented = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, oriented = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented > 0: # if geometric
				if not newSig in geometric: #if we haven't seen it before
					geometric.append(newSig)
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
				else:
					continue #here is why we don't loop (we are backtracking a little)
			else: # if not geometric
				if not newSig in nongeometric: #if we haven't seen it before
					nongeometric.append(newSig)
				else:
					continue

			if geometric_only:
				if oriented <= 0:
					continue
			f = open(f'graphs/{sig}-nodes.csv', "a")
			f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
			f.close()
			f = open(f'graphs/{sig}-edges.csv', "a")
			# labeling edge with #tet - index to look for repeated patterns!
			f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
			f.close()
				
			
						
	if verbose:
		print(f'Number of geometric triangulations: {len(geometric)}')
		print(f'Number of non-geometric triangulations: {len(nongeometric)}')
		print(f'Total: {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')

	return

def graphEssentialSearch(sig, max_tets, verbose=True, directory='graphs'):
	"""
	Perform 'fake geometric' moves, i.e. perform moves while tracking the shape
	parameters, even if the shape parameters are flat or negatively oriented.
	Graph output.
	"""

	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	### field may not be found
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	

	essential = [sig]
	inessential = []
	edges = []

	f = open(f'{directory}/{sig}-essential-nodes.csv', "w")
	f.write(f'id,oriented,tetrahedra\n{sig},1,{T.countTetrahedra()}\n')
	f.close()
	f = open(f'{directory}/{sig}-essential-edges.csv', "w")
	# labeling edge with #tet - index to look for repeated patterns!
	f.write('target,source,label\n')
	f.close()

	# TODO : [ (Triangulation, [Shapes], index, dimension) ]
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)
		Tsig = T.isoSig()

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, oriented = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, oriented = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented > -2: # if essential
				if not newSig in essential: #if we haven't seen it before
					# record new triangulation sig
					essential.append(newSig)
					edges.append((Tsig, newSig))
					f = open(f'{directory}/{sig}-essential-nodes.csv', "a")
					f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
					f.close()

					# add neighbors to queue
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)
					
			else: # if inessential edge exists
				if not newSig in inessential: #if we haven't seen it before
					inessential.append(newSig)
					edges.append((Tsig, newSig))
					f = open(f'{directory}/{sig}-essential-nodes.csv', "a")
					f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
					f.close()
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)

			
			f = open(f'{directory}/{sig}-essential-edges.csv', "a")
			# labeling edge with #tet - index to look for repeated patterns!
			f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
			f.close()
				
			
						
	if verbose:
		print(f'Number of essential triangulations: {len(essential)}')
		print(f'Number of inessential triangulations: {len(inessential)}')
		print(f'Total: {len(essential) + len(inessential)} triangulations in {round(time.time() - t0, 2)} seconds.')

	return

def essentialCensus(max_tets):
	t0 = time.time()
	for i in range(len(snappy.OrientableCuspedCensus)):
		print(f'Searching manifold {i}. Time since start: {round((time.time() - t0) / 60, 2)} minutes.')
		M = snappy.OrientableCuspedCensus[i]
		graphEssentialSearch(M.triangulation_isosig(decorated=False), max_tets, False, 'census-'+str(max_tets)+'-tets')


def graphPseudogeometricSearch(sig, max_tets, verbose=True, directory='graphs'):
	"""
	Perform 'pseudo-geometric' moves, i.e. perform moves while tracking the shape
	parameters, even if the shape parameters are flat.
	Graph output.
	Assumes input is pseudogeometric.
	"""

	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	### field may not be found -- to fix later
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	

	flat = [sig]
	notflat = []
	edges = []

	f = open(f'{directory}/{sig}-flat-nodes.csv', "w")
	f.write(f'id,oriented,tetrahedra\n{sig},1,{T.countTetrahedra()}\n')
	f.close()
	f = open(f'{directory}/{sig}-flat-edges.csv', "w")
	# labeling edge with #tet - index to look for repeated patterns!
	f.write('target,source,label\n')
	f.close()

	# TODO : [ (Triangulation, [Shapes], index, dimension) ]
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)
		Tsig = T.isoSig()

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, oriented = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, oriented = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented > -1: # if flat or geometric
				if not newSig in flat: #if we haven't seen it before
					# record new triangulation sig
					flat.append(newSig)
					edges.append((Tsig, newSig))
					f = open(f'{directory}/{sig}-flat-nodes.csv', "a")
					f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
					f.close()

					# add neighbors to queue
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)
					
			else: # if negatively oriented or inessential
				if not newSig in notflat: #if we haven't seen it before
					notflat.append(newSig)
					edges.append((Tsig, newSig))
					f = open(f'{directory}/{sig}-flat-nodes.csv', "a")
					f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
					f.close()
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)

			
			f = open(f'{directory}/{sig}-flat-edges.csv', "a")
			# labeling edge with #tet - index to look for repeated patterns!
			f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
			f.close()
				
			
						
	if verbose:
		print(f'Number of pseudogeometric triangulations: {len(flat)}')
		print(f'Number of non-pseudogeometric triangulations: {len(notflat)}')
		print(f'Total: {len(flat) + len(notflat)} triangulations in {round(time.time() - t0, 2)} seconds.')

	return


def bigSearch(n, depth):
	for i in range(n):
		# m = snappy.OrientableCuspedCensus[i]
		m = snappy.CensusKnots[i]
		geometricSearch(m.triangulation_isosig(decorated=False), depth)
		print(f'{i}----------------------------------------------')


def checkRec(tri, shapes):
	"""
	check for Dadd Duan recursive gadget
	Warning: not well-tested. Use at own risk0
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

		same_shape = shapes[tet_num0] == shapes[tet_num1]
		small_shape = QQbar(shapes[tet_num0]).real() < 1

	    # check the other faces
		if tet0.adjacentTetrahedron(v0[0]).index() == tet_num1 and (ag0[v0[3]] == v1[0] and ag0[v0[1]] == v1[3] and ag0[v0[2]] == v1[2]):
	    	#GOOD PLACE
			if same_shape and small_shape:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))
		if tet0.adjacentTetrahedron(v0[2]).index() == tet_num1 and (ag2[v0[3]] == v1[2] and ag2[v0[0]] == v1[3] and ag2[v0[1]] == v1[1]):
	    	#GOOD PLACE
			if same_shape and small_shape:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))
		if tet0.adjacentTetrahedron(v0[1]).index() == tet_num1 and (ag1[v0[3]] == v1[1] and ag1[v0[2]] == v1[3] and ag1[v0[0]] == v1[0]):
			#GOOD PLACE
			if same_shape and small_shape:
					return (True, tet_num0, tet_num1)
			else:
				found_combinatorial = True
				combin_at.append((tet_num0, tet_num1))

	if found_combinatorial:
		print("|||||> Found rec gadget combinatorial rec gadget but not other conditions! <|||||")
		f = open("recCounterExample.txt", "a")
		f.write(tri.isoSig() + f' | Same Shape: {same_shape} | Small Shape: {small_shape} | {combin_at} | {shapes} \n')
		f.close()
	return (False, -1, -1)

def recSearch(sig, max_tets, verbose=True):
	"""
	Searches geometric Pachner tree (like geometric search above)
	and checks for Dadd-Duan Recursion Gadget
	Returns (gadget found : bool, gadget tet 1, gadget tet 2, triangulations checked)
	"""
	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()


	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)
	
	L = M.tetrahedra_field_gens()
	F = L.find_field(100,10)
	if F == None:
		print("Could not find field")
		return (False, -1, -1, -1)

	shapes = F[2]

	geometric = [sig]
	nongeometric = []

	tf, t1, t2 = checkRec(T, shapes)
	if tf:
		return sig, t1, t2, len(geometric) + len(nongeometric)

	# TODO : [ (Triangulation, [Shapes], index, dimension) ]
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] + [(T, shapes, i, 1) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d = TODO.pop(0)

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if d == 1: # 3-2 move
			success, newT, newShapes, geom = gm.threeTwoMove(S, shapes2, i)
		elif d == 2: # 2-3 move
			success, newT, newShapes, geom = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if geom:
				if not newSig in geometric: #if we haven't seen it before
					geometric.append(newSig)
					# Check for recursion gadget,
					tf, t1, t2 = checkRec(newT, newShapes)
					if tf:
						N = snappy.Manifold(newT)
						if N.verify_hyperbolicity()[0]: #VERIFY RETURN IS ACTUALLY GEOMETRIC
							return newSig, t1, t2, len(geometric) + len(nongeometric)
						else:
							print("ERROR: tried to return geometric thing that was not geometric")

					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
			else:
				if not newSig in nongeometric: #if we haven't seen it before
					nongeometric.append(newSig)
						
	if verbose:
		print(f"Failed to find DD-Gadget.")
		print(f'Number of geometric triangulations: {len(geometric)}')
		print(f'Number of non-geometric triangulations: {len(nongeometric)}')
		print(f'Total: {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')

	
	return (False, -1, -1, -1)

def bigSearchRec(n, depth, file):
	f = open(file, "a")
	f.write(f'This is a census of manifolds in the first {n} of SnapPy\'s Cusped Orientable Census which has some triangulation that contains the Dadd-Duan Recursion Gadget. Only triangulations geometrically connected in the Pachner graph to the census triangulation are checked, and only up to a max number of {depth} tetrahedra.')
	f.close()
	for i in range(n):
		M = snappy.OrientableCuspedCensus[i]
		sig = M.triangulation_isosig(decorated=False)
		found, t1, t2, searched = recSearch(sig, depth)
		if found:
			print("[~] Recursion gadget found! [~]")
			print(f"[~] After {searched} triangulations. [~]")
			T = regina.Triangulation3.fromIsoSig(found)
			S = regina.Triangulation3.fromIsoSig(sig)
			height = T.countTetrahedra() - S.countTetrahedra()
			f = open(file, "a")
			f.write(f'[Census Manifold {i}]: ' + found + f', tet1: {t1}, tet2: {t2}, searched: {searched}, height: {height}' + '\n')
			f.close()
		else:
			print("Nothing found.")
		print(f'{i}----------------------------------------------')

def pp_copmare_shapes(shapes1, shapes2):
	print('--------------------------------------------')
	if len(shapes1) != len(shapes2):
		print('Error: Shape lists not same length!')
	for i in range(len(shapes1)):
		a = shapes1[i]
		b = shapes2[i]
		print(f'{a} <||> {b}')
	print('--------------------------------------------')


