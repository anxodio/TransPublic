#!/usr/bin/env python
# encoding: utf-8

import sys # per els arguments
import yaml
from Transport import Transport


import math #calcular distancia
import copy # per copiar objectes

class AStar(object):
	""" Classe per realitzar la cerca A* """
	def __init__(self,trans,origin=None,target=None, dist=None, transbords=None, parades=None): # Objecte transport obligatori. També es poden afegir directament origen i desti
		super(AStar, self).__init__()
		self.trans = trans
		self.list = None # per la llista que manté l'algorisme
		self.origin = origin
		self.target = target
		self.max_dist = dist
		self.max_transbords = transbords
		self.max_parades = parades

	def calcDistance(self, coord1, coord2):
		"""Calcula la distancia entre dues posicions del mapa"""
		#coord1 i coord2 son una tupla amb 2 camps: (x, y)
		dist = math.sqrt( pow((coord1[0]-coord2[0]),2) + pow((coord1[1]-coord2[1]),2))
		return int(dist)

	def calcF(self, cami):
		"""Calcula el valor de la funcio F d'un cami per arribar a l'origen"""
		#HEURISTICA PORVISIONAL: DISTANCIA ENTRE DOS ESTACIONS
		#F = HEURISTICA + COST ACUMULAT

		#DE CARA A UN FUTUR HEM DE CONSIDERAR RETORNAR UNA HEURISTICA O UNA ALTRA SEGONS
		#UN VALOR PREDEFINIT (UN VALOR CRITERI) QUE INDICARA SOBRE QUIN ESPECTE VOLEM OPTIMITZAR
		#EL RECORREGUT = TEMPS, DISTANCIA, NUM_TRANSBORDS

		estacio1 = cami.getPrimeraEstacio()
		#Primer generem les tuples amb les dues coordenades de cada estacio
		c1 = (estacio1.x, estacio1.y)
		c2 = (self.target.x, self.target.y)

		#Potser interesa multiplicar la distancia per algun valor
		return self.calcDistance(c1, c2) + cami.cost

	def expandirCami(self,cami):
		"""Expandeix un cami. Retorna els camins expandits"""
		# cami = objecte AStarList.Path, llista de elements (estacio i origen) i cost
		expandit = AStar.AStarList()

		# per cada enllaç que tingui la estacio expandirem un camí
		# nomes necesitem mirar els "fills" del primer node
		for link in cami[0].st.links:
			#busquem la estació "fill"
			nova_estacio = self.trans.getStationByID(link.id)
			#fem una copia de la llista camí
			nou_cami = copy.copy(cami)

			# Calculem cost.
			nou_cami.cost = cami.cost+link.cost # cost anterior + cost del link
			nou_cami.parades += 1 # num parades anterior + 1

			# Nova distancia
			c1 = (cami[0].st.x, cami[0].st.y)
			c2 = (nova_estacio.x, nova_estacio.y)
			nou_cami.distancia = cami.distancia + self.calcDistance(c1, c2) # distancia anterior + nova distancia

			# Si hem canviat de linea, es un transbord. Li sumem el cost del transbord (st.cost)
			# Per comprovar-ho: Si venim de la primera o caminar, res.
			# Si no es així, comprovem si la linea origen i la del link son iguals o no
			orig = nou_cami[0].origin
			if not orig == AStar.AStarList.FIRST and not orig == AStar.AStarList.WALKING and not orig == link.line:
				nou_cami.cost += nou_cami[0].st.cost
				# aumentem el número de transbords
				nou_cami.transbords += 1

			# addElement inserta un nou element (estacio i origen) al inici del cami
			nou_cami.addElement(nova_estacio,link.line)
			#insertem el nou camí a la llista d'expandits
			expandit.addPath(nou_cami)

		#CAMINS CAMINANT
		actual = cami.getPrimeraEstacio() #estacio actual desde la que caminem
		for estacio in self.trans.stations:
			#no afegim el cami d'anar caminant desde una estacio a ella mateixa
			if actual.id != estacio.id:
				#copiem la llista
				nou_cami = copy.copy(cami)

				#obtenim les coordenades per calcular la distancia
				c1 = (actual.x, actual.y)
				c2 = (estacio.x, estacio.y)
				distancia_caminant = self.calcDistance(c1, c2)

				# Actualitzem valors del cami
				nou_cami.cost = cami.cost + 12*distancia_caminant
				nou_cami.parades += 1
				nou_cami.distancia = cami.distancia + distancia_caminant
				# considerem caminar com a un transbord
				nou_cami.transbords += 1

				nou_cami.addElement(estacio,AStar.AStarList.WALKING)
				expandit.addPath(nou_cami)

		return expandit

	def eliminarCicles(self,cami_exp):
		"""Elimina cicles del cami expandit"""
		#Quan hi ha cicle??
		#Quan la primera estacio esta repetida dins el mateix cami
		
		eliminar = []

		for cami in cami_exp:
			if cami.hiHaCicle():
				eliminar.append(cami)

		for cami in eliminar:
			cami_exp.remove(cami)

		return cami_exp

	def insertarCamins(self, cami_exp):
		for cami in cami_exp:
			if self.max_transbords == None or cami.transbords <= self.max_transbords:
				if self.max_parades == None or cami.parades <= self.max_parades:
					if self.max_dist == None or cami.distancia <= self.max_distancia:
						self.list.insertOrdenat(cami, self.calcF)

	def eliminarCaminsRedundants(self):
		""" Elimina camins de la llista que son redundants """
		#Un camí es redundant quan va al mateix lloc que un altre camí i té més cost
		#Un camí que té mes cost que un altre es trobará més a la dreta dins la llista

		#creem una llista amb tots els destins dels camins actuals
		llista_caps = []

		#list es del tipus[ [[(arrel, "O")],0] ]
		for cami in self.list:
			#podem fer cami[0] en comptes de cami.paths[0] perque s'ha sobrecarregat el metode getitem per als objetces Path
			llista_caps.append(cami[0].st)

		#for i in (longitud de la llista de caps -1) fins a -1 decrementant 1
		for i in range(len(llista_caps)-1, -1, -1):
			#Si el cap de la posicio=i ja està en una posició més petita, l'eliminem.
			if llista_caps[i] in llista_caps[:i]:
				self.list.pop(i)

	def doAStarSearch(self, origin=None, target=None):
		 # es poden posar en aquest moment
		if origin: self.origin = origin
		if target: self.target = target

		self.list = AStar.AStarList(self.origin)

		#mentre no trobem l'objectiu anirem expandint
		while (len(self.list) > 0 and self.list.getCap() != self.target):
			#pop(0) agafa el primer cami (objecte AStarList.Path)
			cami = self.list.pop(0)
			cami_exp = self.expandirCami(cami)
			#cami_exp es un objecte AStarList
			cami_exp = self.eliminarCicles(cami_exp)
			#TO DO: insertar cami_exp a llista
			self.insertarCamins(cami_exp)
			self.eliminarCaminsRedundants()			

		return self.list

	def transformPathToHumanReadable(self,path):
		text = "Et trobes a l'estació "+path[-1].st.name+".\n"
		# Separem el primer per fer un text més maco
		if len(path) >= 2:
			if path[-2].origin == AStar.AStarList.WALKING:
				text += " - Ves caminant fins a l'estació "+path[-2].st.name
			else:
				text += " - Agafa la línia "+path[-2].origin+" en direcció "+self.trans.getLineHead(path[-1].st,path[-2].st,path[-2].origin).name

		for i in range(len(path)-2,0,-1):
			if path[i-1].origin == AStar.AStarList.WALKING:
				text += "\n - Baixa a l'estació "+path[i].st.name+" i ves caminant fins a l'estació "+path[i-1].st.name
			elif not path[i].origin == path[i-1].origin:
				text += "\n - A l'estació "+path[i].st.name+", agafa la línia "+path[i-1].origin+" en direcció "+self.trans.getLineHead(path[i].st,path[i-1].st,path[i-1].origin).name

		text += "\n - Baixa a "+path[0].st.name+".\nFelicitats! Has arribat!"
		return text

	class AStarList(object):
		""" Estructura de dades per la llista de l'algorisme A* """
		# Constants per l'origen del element
		WALKING = "WALKING"
		FIRST = "FIRST"

		def __init__(self,originSt=None): # Es pot iniciar amb la primera estacio (perque crei l'estructura, amb cost 0), o buit
			super(AStar.AStarList, self).__init__()
			self.paths = []
			if originSt: self.setup(originSt) #si la llista que entra no esta buida fem el setup, per afegir el node inicial a la llista

		def setup(self,originSt):
			#Creem el cami on està l'arrel. De moment té cost zero ja que només hi ha una estacio (l'arrel)
			p = AStar.AStarList.Path(0)
			p.addElement(originSt,AStar.AStarList.FIRST)
			self.paths.append(p) # afegim el primer

		def addPath(self,path):
			self.paths.insert(0,path) # afegim a la primera posició

		def insertOrdenat(self, cami, funcioHeuristica):
			""" Inserta el cami passat per parametre a la llista, calculant l'heuristica amb la funcio rebuda per parametre """
			#cami es un objecte Path
			#ha d'insertar el cami ordenat segons heuristica
			heuristica = funcioHeuristica(cami)

			#DEBUG ORDENAR
			#print cami.getPrimeraEstacio().id, heuristica

			for i in range(len(self)):
				if heuristica <= funcioHeuristica(self.paths[i]):
					#si la funcio f es menor afegim davant
					self.paths.insert(i, cami)
					break
			else:
				#si la funcio f és major, aleshores afegim al final, ja que és el camí amb més cost
				self.paths.append(cami)


		def remove(self,path):
			""" Busca el camí i l'extreu """
			self.paths.remove(path)

		def pop(self,pos):
			""" Extreu el cami a la posició 'pos' cami i el retorna """
			return self.paths.pop(pos)

		def getCap(self):
			"""Retorna l'estacio cap del primer cami de la llista"""
			#self[0] es el mateix que self.paths[0]
			return self[0].getPrimeraEstacio()

		def __len__(self):
			""" Quants camins tenim? """
			return len(self.paths)

		def __getitem__(self, pos):
			""" Podem aconseguir un cami per la seva posició, que ha de ser entera """
			if not type(pos) == type(1):
				raise TypeError

			return self.paths[pos] # Això pot llençar un indexError

		def __str__(self):
			l = ""
			for p in self.paths:
				l += str(p)+","
			l = l.rstrip(",") # elimina la coma sobrant

			return "{"+l+"}"

		def __iter__(self):
			return self.Iterator(self.paths)

		class Iterator(object):
			def __init__(self, paths):
				super(AStar.AStarList.Iterator,self).__init__()
				self.paths = paths
				self.position = 0

			def next(self):
				path = None
				try:
					path = self.paths[self.position] # Intentem agafar el cami. Si llença excepcio (IndexError), ja no hi han mes, fem StopIteration
					self.position += 1
				except:
					raise StopIteration

				return path

		
		class Path(object):
			""" Classe camí. Conte llista d'elements i cost """
			def __init__(self,cost):
				super(AStar.AStarList.Path, self).__init__()
				self.cost = cost
				self.elements = []
				self.transbords = 0
				self.parades = 0
				self.distancia = 0

			def addElement(self,st,origin):
				#parametre origin es la identificacio de la procedencia
				e = AStar.AStarList.Path.Element(st,origin)
				self.elements.insert(0,e) # es van omplint sempre desde el principi de la llista

			def hiHaCicle(self):
				# Retorna true o false si hi ha cicle o no
				cicle = False
				primera = self.elements[0].st
				for i in range(1,len(self.elements)):
					if primera == self.elements[i].st:
						cicle = True
						break
				return cicle

			def getPrimeraEstacio(self):
				"""Retorna la primera estacio (objecte Transport.Station) d'un camí"""
				#podem fer self[0] aprofitant el getitem sobrecarregat
				return self[0].st

			def __copy__(self):
				p = AStar.AStarList.Path(self.cost)
				for e in self.elements:
					p.elements.append(e)
				return p

			def __len__(self):
				""" Quants elements tenim? """
				return len(self.elements)

			def __getitem__(self, pos):
				""" Podem aconseguir un element per la seva posició, que ha de ser entera """
				if not isinstance(pos,int):
					raise TypeError

				return self.elements[pos] # Això pot llençar un indexError

			def __contains__(self, st):
				""" Es dona per soposat que el que busquem és una estacio i no ens importa el origen
				Per poder buscar, p.e., if st in path: """
				trobat = False
				for e in self.elements:
					if e.st == st:
						trobat = True
						break
				return trobat

			def __str__(self):
				l = ""
				for e in self.elements:
					l += str(e)+","
				l = l.rstrip(",") # elimina la coma sobrant

				return "["+l+","+str(self.cost)+"]"

			def __iter__(self):
				return self.Iterator(self.elements)

			class Iterator(object):
				def __init__(self, elements):
					super(AStar.AStarList.Path.Iterator,self).__init__()
					self.elements = elements
					self.position = 0

				def next(self):
					path = None
					try:
						path = self.elements[self.position] # Intentem agafar el element. Si llença excepcio (IndexError), ja no hi han mes, fem StopIteration
						self.position += 1
					except:
						raise StopIteration

					return path

			class Element(object):
				""" Classe element. Cada element d'un camí. Conté objecte estació i origen (linea, caminant o principi) """
				def __init__(self,st,origin):
					super(AStar.AStarList.Path.Element, self).__init__()
					self.st = st
					self.origin = origin

				def __str__(self):
					return "("+str(self.st.id)+","+self.origin+")"


if __name__ == '__main__':
	# Com executar: ./AStar.py fixer idOrigen idDesti mode
	# Per exemple: ./AStar.py "./lyon.yaml" 13 10 0

	if not len(sys.argv) == 5: # el propi nom de fitxer és argv[0]
		print "Parametres incorrectes."
		print
		print "Com utilitzar desde consola AStar.py:"
		print "./AStar.py fitxer idOrigen idDesti mode"
		print
		print "On mode és un enter:"
		print " 0 = Resposta sense tractar (objecte AStarList en text) "
		print " 1 = Llista simple python amb el camí òptim (ideal per jocs de proves)"
		print " 2 = Explicació llegible per humans (Human Readable) "
		print
		print "Per exemple: python AStar.py \"./lyon.yaml\" 13 10 0"
		print
		sys.exit()

	try:
		trans = Transport.loadFile(sys.argv[1])
	except:
		print "Fitxer incorrecte"
		sys.exit()

	origen = trans.getStationByID(int(sys.argv[2]))
	if not origen:
		print "ID origen incorrecte"
		sys.exit()

	desti = trans.getStationByID(int(sys.argv[3]))
	if not origen:
		print "ID destí incorrecte"
		sys.exit()

	mode = int(sys.argv[4])
	if mode < 0 or mode > 2:
		print "Mode incorrecte."
		sys.exit()

	a = AStar(trans,origen,desti)
	l = a.doAStarSearch()

	if mode == 0:
		print l
	elif mode == 1:
		llista = []
		for element in l[0]: # per cada element en el primer cami de la llista...
			llista.append(element.st.id)
		print llista
	elif mode == 2:
		cami = l[0]
		print a.transformPathToHumanReadable(cami)