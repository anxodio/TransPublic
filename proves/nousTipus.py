#!/usr/bin/env python
# encoding: utf-8

# Per implementar metodes especials: http://docs.python.org/2/reference/datamodel.html#special-method-names

import yaml
from Transport import Transport

class AStarList(object):
	# Constants per l'origen del element
	WALKING = "WALKING"
	FIRST = "FIRST"

	def __init__(self,originSt=None): # Es pot iniciar amb la primera estacio (perque crei l'estructura, amb cost 0), o buit
		super(AStarList, self).__init__()
		self.paths = []
		if originSt: self.setup(originSt)

	def setup(self,originSt):
		p = AStarList.Path(0)
		p.addElement(originSt,AStarList.FIRST)
		self.paths.append(p) # afegim el primer

	def addPath(self,path):
		self.paths.insert(0,path) # afegim a la primera posició

	def remove(self,path):
		""" Busca el camí i l'extreu """
		self.paths.remove(path)

	def pop(self,pos):
		""" Extreu l'ultim cami i el retorna """
		return self.paths.pop(pos)

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
			super(AStarList.Iterator,self).__init__()
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
			super(AStarList.Path, self).__init__()
			self.cost = cost
			self.elements = []

		def addElement(self,st,origin):
			e = AStarList.Path.Element(st,origin)
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

		def __copy__(self):
			p = AStarList.Path(self.cost)
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

		class Element(object):
			""" Classe element. Cada element d'un camí. Conté objecte estació i origen (linea, caminant o principi) """
			def __init__(self,st,origin):
				super(AStarList.Path.Element, self).__init__()
				self.st = st
				self.origin = origin

			def __str__(self):
				return "("+str(self.st.id)+","+self.origin+")"

if __name__ == '__main__':
	print "KE ASE?"