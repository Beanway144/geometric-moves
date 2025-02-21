import regina, snappy
import geometricmoves as gm
import time

VERIFY = True

def geometricSearch(sig, depth):
	"""
	Perform geometric pachner moves until no longer possible
	Assumes sig is geometric
	"""
	print(f"Searching {sig}")
	t0 = time.time()

	

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)
	
	shapes = M.tetrahedra_shapes(part='rect')

	geometric = [sig]
	nongeometric = []

	searched = depth

	TODO = [(T, shapes, i) for i in range(T.countTriangles())]
	while len(TODO) > 0 and searched > 0:
		T, shapes, f = TODO[0]
		TODO = TODO[1:]
		searched -= 1

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		success, newT, newShapes, geom = gm.twoThreeMove(S, shapes2, f)
		if not success:
			continue

		newSig = newT.isoSig()
		if geom:
			if newSig in geometric:
				continue
			else:
				geometric.append(newSig)
				TODO.extend([(newT, newShapes, i) for i in range(newT.countTriangles())])
		else:
			if newSig in nongeometric:
				continue
			else:
				nongeometric.append(newSig)

	if len(TODO) == 0:
		print("Geometric base component is finite")
		f = open("finite_geometric_base_comp2.txt", "a")
		f.write(sig + '\n')
		f.close()
	if searched == 0:
		print(f"HIT CAP, checked ~{depth}")
		f = open("many_geometric2.txt", "a")
		f.write(sig + '\n')
		f.close()
		

	# print(f'Geometric: {geometric}')
	# print(f'Nongeometric: {nongeometric}')

	print(f'Number of geometric triangulations: {len(geometric)}')
	print(f'Number of non-geometric triangulations: {len(nongeometric)}')
	print(f'Checked {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')
	t1 = time.time()
	if VERIFY:
		print("verifying...")

		for t in geometric:
			M = snappy.Manifold(t)
			if not M.verify_hyperbolicity()[0]:
				print(f"Geometric not actually geometric: {M.triangulation_isosig()}")
		print("done verifying geometric...")
		for t in nongeometric:
			M = snappy.Manifold(t)
			if M.verify_hyperbolicity()[0]:
				print(f"Nongeometric actually geometric: {M.triangulation_isosig(decorated=False)}")
		print(f"Done! Verified {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t1, 2)} seconds.")
	return geometric

def bigSearch(n, depth):
	for i in range(n):
		# m = snappy.OrientableCuspedCensus[i]
		m = snappy.CensusKnots[i]
		geometricSearch(m.triangulation_isosig(decorated=False), depth)
		print(f'{i}----------------------------------------------')


def checkRec(tri, shapes):
	"""
	check for Dadd Duan recursive gadget
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

		same_shape = float(abs(shapes[tet_num0] - shapes[tet_num1])) < 0.00001
		small_shape = shapes[tet_num0].real() < 1

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

def searchForRec(sig, depth):
	print(f"Searching {sig}")
	t0 = time.time()

	geometric = [sig]
	nongeometric = []

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)

	shapes = M.tetrahedra_shapes(part='rect')

	searched = depth
    # 1 = edge, 2 = face
	TODO = [(T, shapes, i, 2) for i in range(T.countTriangles())]
	while len(TODO) > 0 and searched > 0:
		T, shapes, i, dim = TODO[0]
		TODO = TODO[1:]
		searched -= 1

		# always work on a copy
		S = regina.Triangulation3(T)
		shapes2 = shapes.copy()

		if dim == 1:
			# res = gm.threeTwoMove(S, shapes2, i)
			# if res:
			# 	success, newT, newShapes, geom = res
			pass
		else:
			success, newT, newShapes, geom = gm.twoThreeMove(S, shapes2, i)

		if not success:
			continue

		newSig = newT.isoSig()
		if geom:
			if newSig in geometric:
				continue
			else:
				recFound, t1, t2 = checkRec(newT, newShapes)
				if recFound:
					return (newT.isoSig(), t1, t2, depth - searched)
				geometric.append(newSig)
				# add all face to TODO
				TODO.extend([(newT, newShapes, i, 2) for i in range(newT.countTriangles())])
				# for i in range(newT.countEdges()):
				# 	if newT.edges()[i].degree() == 3:
				# 		#add degree 3 edges to TODO
				# 		TODO.append((newT, newShapes, i, 1))


		else:
			if newSig in nongeometric:
				continue
			else:
				nongeometric.append(newSig)

	if len(TODO) == 0:
		print("Hit dead end: no more geometric triangulations")
		
	if searched == 0:
		print(f"HIT CAP, checked ~{depth}")
				

	print(f'Number of geometric triangulations: {len(geometric)}')
	print(f'Number of non-geometric triangulations: {len(nongeometric)}')
	print(f'Checked {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')
	t1 = time.time()
	print(geometric)
	return (False, -1, -1, -1)

def bigSearchRec(n, depth):
	for i in range(n):
		m = snappy.OrientableCuspedCensus[i]
		sig = m.triangulation_isosig(decorated=False)
		found, t1, t2, searched = searchForRec(sig, depth)
		if found:
			print("[~] Recursion gadget found! [~]")
			print(f"[~] After {searched} triangulations. [~]")
			T = regina.Triangulation3.fromIsoSig(found)
			S = regina.Triangulation3.fromIsoSig(sig)
			height = T.countTetrahedra() - S.countTetrahedra()
			f = open("test.txt", "a")
			f.write(found + f', tet1: {t1}, tet2: {t2}, searched: {searched}, height: {height}' + '\n')
			f.close()
		else:
			print("Nothing found.")
			f = open("nontest.txt", "a")
			f.write(sig + '\n')
			f.close()
		print(f'{i}----------------------------------------------')


