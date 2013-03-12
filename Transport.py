#!/usr/bin/env python
# encoding: utf-8

import yaml

class Transport(yaml.YAMLObject):
	"""docstring for Contenidor"""
	#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
	yaml_tag = u'!TransportFile'
	def __init__(self,name,lines,stations):
		super(Transport, self).__init__()
		self.name = name
		self.lines = lines
		self.stations = stations

	def getStationByID(self,ident):
		station = None
		for st in self.stations:
			if st.id == ident: 
				station = st
				break

		return station

	def getStationByCoords(self,x,y):
		station = None
		for st in self.stations:
			if st.x == x and st.y == y: 
				station = st
				break

		return station


	class Station(yaml.YAMLObject):
		"""docstring for Station"""
		#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
		yaml_tag = u'!Station'
		def __init__(self, id, name, cost, lines, x, y, links):
			super(Transport.Station, self).__init__()
			self.id = int(id)
			self.name = name
			self.cost = cost
			self.lines = lines
			self.x = int(x)
			self.y = int(y)
			self.links = links

		def getCommonLine(self,st):
			line = None
			for l in self.lines:
				if l in st.lines:
					line = l
					break
			return line

		class Link(yaml.YAMLObject):
			"""docstring for Link"""
			#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
			yaml_tag = u'!Link'
			def __init__(self, id, cost, line=""):
				super(Transport.Station.Link, self).__init__()
				self.id = int(id)
				self.cost = int(cost)
				self.line = line

	@staticmethod
	def loadFile(fitxer):
		t = yaml.load(file(fitxer, 'r')) # Objecte Tranport
		return t

	@staticmethod
	def saveFile(trans,fitxer):
		yaml.dump(trans,file(fitxer, 'w'))


if __name__ == '__main__':
	print "Not an executable class"