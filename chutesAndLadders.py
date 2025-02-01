import regina, snappy
import geometricmoves as gm
import geometricsearch as gs
import time

VERIFY = True

def pseudoGeometricSearch(sig, MAX_DEPTH):
	"""
	Perform a "chutes and ladders" BFS of the Pachner graph for geometric recursion gadgets, where
	chutes and ladders are geometric moves using faster method.
	"""
	print(f"Searching {sig}")
	t0 = time.time()

	

	T = regina.Triangulation3.fromIsoSig(sig)
	T.orient()
	M = snappy.Manifold(T)
	
	shapes = M.tetrahedra_shapes(part='rect')

	geometric = [sig]
	nongeometric = []

	searched = MAX_DEPTH

	geoTODO = [(T, shapes, i, 2) for i in range(T.countTriangles())] #only geometric
	nonTODO = [] #non geometric
	while searched > 0:
		if len(geoTODO) > 0: # if chute/ladder exists, take it
			print(f"[{MAX_DEPTH - searched}] Working on a geometric!")
			T, shapes, f, dim = geoTODO[0]
			geoTODO = geoTODO[1:]
			searched -= 1

			# always work on a copy
			S = regina.Triangulation3(T)
			shapes2 = shapes.copy()
			if dim == 2:
				success, newT, newShapes, geom = gm.twoThreeMove(S, shapes2, f)
			else:
				res = gm.threeTwoMove(S, shapes2, f)
				if res:
					success, newT, newShapes, geom = res
			if not success:
				continue

			newSig = newT.isoSig()
			if geom:
				if newSig in geometric:
					continue
				else:
					recFound, t1, t2 = gs.checkRec(newT, newShapes)
					if recFound:
						print(f"Recursive gadget found! {newSig} at tetrahedra {t1}, {t2}")
					geometric.append(newSig)
					# Add all faces to TODO
					geoTODO.extend([(newT, newShapes, i, 2) for i in range(newT.countTriangles())])
					for i in range(newT.countEdges()):
						# Add all viable edges to TODO
						if newT.edges()[i].degree() == 3:
							#add degree 3 edges to TODO
							geoTODO.append((newT, newShapes, i, 1))
			else:
				if newSig in nongeometric:
					continue
				else:
					nongeometric.append(newSig)
					nonTODO.extend([(newT, i,2) for i in range(newT.countTriangles())])
					if newT.edges()[i].degree() == 3:
						#add degree 3 edges to TODO
						nonTODO.append((newT, i, 1))

		else: # if no more geometric to check ("force forward")
			S, i, f = nonTODO[0]
			nonTODO = nonTODO[1:]
			searched -= 1

			T = regina.Triangulation3(S) #work on a copy
			if f == 2: #face
				if not T.pachner(T.triangle(i)):
					continue
			else: #edge
				if not T.pachner(T.edge(i)):
					continue
			T.orient()
			M = snappy.Manifold(T)
			newSig = T.isoSig()

			print(f"[{MAX_DEPTH - searched}] Working on a non: {newSig}")

			try:
				geom, shapes = M.verify_hyperbolicity() #this is slow, also i should do this after checking if i've seen it before
			except:
				print(f'ERROR at {newSig}')
				continue

			if geom:
				if newSig in geometric:
					continue
				else:
					recFound, t1, t2 = gs.checkRec(T, shapes)
					if recFound:
						print(f"Recursive gadget found! {newSig} at tetrahedra {t1}, {t2}")
					geometric.append(newSig)
					geoTODO.extend([(T, shapes, i, 2) for i in range(newT.countTriangles())])
					for i in range(T.countEdges()):
						# Add all viable edges to TODO
						if T.edges()[i].degree() == 3:
							#add degree 3 edges to TODO
							geoTODO.append((T, shapes, i, 1))

			else:
				if newSig in nongeometric:
					continue
				else:
					nongeometric.append(newSig)
					nonTODO.extend([(T, i, 2) for i in range(T.countTriangles())])
					for i in range(T.countEdges()):
						# Add all viable edges to TODO
						if T.edges()[i].degree() == 3:
							#add degree 3 edges to TODO
							nonTODO.append((T, i, 1))

	print(f'Number of geometric triangulations: {len(geometric)}')
	print(f'Number of non-geometric triangulations: {len(nongeometric)}')
	print(f'Checked {len(geometric) + len(nongeometric)} triangulations in {round(time.time() - t0, 2)} seconds.')
	return geometric

