import regina, snappy
import geometricmoves as gm
import time
from sage.all import QQbar

#####################################################################################
########################### Searching Functions #####################################
#####################################################################################

def geometricSearch(sig, max_tets, verify=False, verbose=True, census=False):
	"""
	Search the geometric subgraph component containing the input isomorphism signature;
	that is, perform 2-3 and 3-2 moves on the starting triangulation until either there
	are no more geometric triangulations connected to `sig` or all such triangulations 
	are beyond the `max_tets` ceiling.
	- sig: isometry signature (not decorated), assumed to be of a geometric triangulation
	- max_tets: an integer, triangulations of this size or greater not to be searched
	- verify: if true, will use SnapPy's `verify_hyperbolicity()` to check the output's
		correctness. Usually takes a long time.
	- census: if true, will output geometric triangulations to {sig}.txt. It is better
		to use a graphing function instead.

	Outputs list containing isosigs of geometric triangulations found.
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
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.twoThreeMove(S, shapes2, i)

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

#####################################################################################
########################### Graphing Functions ######################################
#####################################################################################

def graphGeometricSearch(sig, max_tets, verbose=True, geometric_only=False, directory='.'):
	"""
	Search the geometric subgraph component containing the input isomorphism signature;
	that is, perform 2-3 and 3-2 moves on the starting triangulation until either there
	are no more geometric triangulations connected to `sig` or all such triangulations 
	are beyond the `max_tets` ceiling. Records the node and edge data in CSVs, which can
	be read by e.g. Gephi. Will record both geometric and non-geometric nodes, where
	1 = geometric, 0 = pseudogeometric, -1 = essential, -2 = inessential.
	(For clarity, since this continues to search down nodes which are geometric, 
	non-geometric triangulations are 'leaves' on the output graph.)
	- sig: isometry signature (not decorated), assumed to be of a geometric triangulation
	- max_tets: an integer, triangulations of this size or greater not to be searched
	- geometric_only: if true, only records geometric triangulations in the output files.
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

	f = open(f'{directory}/{sig}-geometric-nodes.csv', "w")
	f.write(f'id,oriented,tetrahedra\n{sig},1,{T.countTetrahedra()}\n')
	f.close()
	f = open(f'{directory}/{sig}-geometric-edges.csv', "w")
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
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.twoThreeMove(S, shapes2, i)

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
			f = open(f'{directory}/{sig}-geometric-nodes.csv', "a")
			f.write(f'{newSig},{oriented},{newT.countTetrahedra()}\n')
			f.close()
			f = open(f'{directory}/{sig}-geometric-edges.csv', "a")
			# labeling edge with #tet - index to look for repeated patterns!
			f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
			f.close()
						
	if verbose:
		print(f'Number of geometric triangulations: {len(geometric)}')
		print(f'Number of non-geometric triangulations: {len(nongeometric)}')
		print(f'Total: {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')

	return

def graphPseudogeometricSearch(sig, max_tets, verbose=True, record_nons=True, directory='.'):
	"""
	Similar to `graphGeometricSearch`, except searches through the pseudogeometric subgraph.
	(That is, allows tetrahedra to have shape parameter with imaginary part equal to 0, i.e. flat.)
	"""

	if verbose:
		print(f"Searching {sig}...")
	t0 = time.time()

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	name = ''
	l = M.identify()
	if l:
		name = l[0]

	### field may not be found -- to fix later
	L = M.tetrahedra_field_gens()
	try:
		shapes = L.find_field(10000,100, True, True)[2] # shapes = L.find_field(100,10)[2]
	except:
		print("Could not find field: falling back to floating point")
		shapes = M.tetrahedra_shapes(part='rect')
	
	flat = [sig]
	notflat = []
	edges = []

	f = open(f'{directory}/{name}-({sig})-pseudogeometric-nodes.csv', "w")
	f.write(f'id,oriented,tetrahedra,flat count,negative count\n{sig},1,{T.countTetrahedra()},0,0\n')
	f.close()
	f = open(f'{directory}/{name}-({sig})-pseudogeometric-edges.csv', "w")
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
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.threeTwoMove(S, shapes2, i)

		elif d == 2: # 2-3 move
			success, newT, newShapes, (oriented, (flat_count, negative_count)) = gm.twoThreeMove(S, shapes2, i)

		if success:
			newSig = newT.isoSig()
			if oriented > -1: # if flat or geometric
				if not newSig in flat: #if we haven't seen it before
					# record new triangulation sig
					flat.append(newSig)
					edges.append((Tsig, newSig))
					f = open(f'{directory}/{name}-({sig})-pseudogeometric-nodes.csv', "a")
					f.write(f'{newSig},{oriented},{newT.countTetrahedra()},{flat_count},{negative_count}\n')
					f.close()

					# add neighbors to queue
					TODO.extend([(newT, newShapes, j, 1) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2) for j in range(newT.countTriangles())])
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)
				f = open(f'{directory}/{name}-({sig})-pseudogeometric-edges.csv', "a")
				# labeling edge with #tet - index to look for repeated patterns!
				f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
				f.close()
					
			else: # if negatively oriented or inessential
				if record_nons:
					if not newSig in notflat: #if we haven't seen it before
						notflat.append(newSig)
						edges.append((Tsig, newSig))
						f = open(f'{directory}/{name}-({sig})-pseudogeometric-nodes.csv', "a")
						f.write(f'{newSig},{oriented},{newT.countTetrahedra()},{flat_count},{negative_count}\n')
						f.close()
					else:
						if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
							continue #here is why we don't loop (we are backtracking a little)
					f = open(f'{directory}/{name}-({sig})-pseudogeometric-edges.csv', "a")
					# labeling edge with #tet - index to look for repeated patterns!
					f.write(f'{newSig},{T.isoSig()},{'Edge: ' if d==1 else 'Face: '}{T.countTriangles() - i}\n')
					f.close()
						
	if verbose:
		print(f'Number of pseudogeometric triangulations: {len(flat)}')
		print(f'Number of non-pseudogeometric triangulations: {len(notflat)}')
		print(f'Total: {len(flat) + len(notflat)} triangulations in {round(time.time() - t0, 2)} seconds.')

	return


def graphEssentialSearch(sig, max_tets, max_1_flat=False, verbose=True, directory='.'):
	"""
	Similar to `graphGeometricSearch`, except searches through the essential graph.
	Note: the essential graph is known to be connected.

	Almost geometric means that it is geometric except for possibly one flat tetrahedron.

	max_1_flat: if true, only graphs essential triangulations with no negatively oriented tetrahedra
	   and at most 1 flat tetrahedron. For testing conjecture that the subset of triangulations
	   with at most one flat tetrahedron is connected
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
	f.write(f'id,oriented,tetrahedra,flat count,negative count\n{sig},1,{T.countTetrahedra()},0,0\n')
	f.close()
	f = open(f'{directory}/{sig}-essential-edges.csv', "w")
	# labeling edge with #tet - index to look for repeated patterns!
	f.write('target,source,label\n')
	f.close()

	# TODO : [ (Triangulation, [Shapes], index, dimension, almostgeom) ]
	TODO = [(T, shapes, i, 2, True) for i in range(T.countTriangles())] + [(T, shapes, i, 1, True) for i in range(T.countEdges())]

	while len(TODO) > 0:
		T, shapes, i, d, almostgeom = TODO.pop(0)
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
			newAlmostgeom = oriented > -1 and flat_count < 2
			if oriented > -2: # if essential
				if not newSig in essential: #if we haven't seen it before
					# record new triangulation sig
					essential.append(newSig)
					edges.append((Tsig, newSig))

					if not max_1_flat or newAlmostgeom:
						f = open(f'{directory}/{sig}-essential-nodes.csv', "a")
						f.write(f'{newSig},{oriented},{newT.countTetrahedra()},{flat_count},{negative_count}\n')
						f.close()


					# add neighbors to queue
					TODO.extend([(newT, newShapes, j, 1, newAlmostgeom) for j in range(newT.countEdges())])
					if newT.countTetrahedra() < max_tets: # don't go up if you're at max tetrahedra
						TODO.extend([(newT, newShapes, j, 2, newAlmostgeom) for j in range(newT.countTriangles())])
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)
					
			else: # if inessential edge exists
				if not newSig in inessential: #if we haven't seen it before
					inessential.append(newSig)
					edges.append((Tsig, newSig))
					if not max_1_flat:
						f = open(f'{directory}/{sig}-essential-nodes.csv', "a")
						f.write(f'{newSig},{oriented},{newT.countTetrahedra()},{flat_count},{negative_count}\n')
						f.close()
				else:
					if (Tsig, newSig) in edges or (newSig, Tsig) in edges: # check so we can record edges later
						continue #here is why we don't loop (we are backtracking a little)

			if not max_1_flat or (newAlmostgeom and almostgeom):
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


def pseudogeometricCensus(max_tets, start, end):
	t0 = time.time()
	for i in range(start, end):
		print(f'Searching manifold {i}. Time since start: {round((time.time() - t0) / 60, 2)} minutes.')
		M = snappy.OrientableCuspedCensus[i]
		graphPseudogeometricSearch(M.triangulation_isosig(decorated=False), max_tets, False, False, f'pseudogeometric-census-{max_tets}-tets')
