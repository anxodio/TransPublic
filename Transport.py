#!/usr/bin/env python
# encoding: utf-8

import yaml

class Transport(yaml.YAMLObject):
	"""docstring for Contenidor"""
	#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
	yaml_tag = u'!TransportFile'
	def __init__(self,name,type,lines,stations):
		super(Transport, self).__init__()
		self.name = name
		self.type = type
		self.lines = lines
		self.stations = stations

	def addLine(self,lin):
		"""Afegeix una nova linea, si pot fer-ho retorna True, sino False"""
		ok = True
		if not lin in self.lines:
			self.lines.append(lin)
		else: ok = False
		return ok

	def changeLineName(self,old,new):
		"""Canvia el nom d'una linea. parametres: antic nom, nou nom."""
		#El canvi es fa tant a les linies del Transport com a les de cada estacio.
		self.lines.remove(old)
		self.lines.append(new)
		# Ara, el canviem a les estacions
		for st in self.stations:
			try:
				st.lines.remove(old) # Si aqui falla vol dir que no existeix, i no afegeix la nova
				st.lines.append(new)
			except:
				pass

	def deleteLine(self,lin):
		"""Esborra una linea"""
		self.lines.remove(lin)
		for st in self.stations:
			try:
				st.lines.remove(lin) # Si aqui falla vol dir que no existeix
			except:
				pass

	def getNewStationID(self):
		"""Retorna la ID que s'hauria d'assignar a una nova estacio"""
		maxId = 0
		for st in self.stations:
			if st.id > maxId: maxId = st.id

		return maxId+1

	def getStationByID(self,ident):
		station = None
		for st in self.stations:
			if st.id == ident: 
				station = st
				break

		return station


class Station(yaml.YAMLObject):
	"""docstring for Station"""
	#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
	yaml_tag = u'!Station'
	def __init__(self, id, name, lines, x, y, links):
		super(Station, self).__init__()
		self.id = int(id)
		self.name = name
		self.lines = lines
		self.x = int(x)
		self.y = int(y)
		self.links = links

class Link(yaml.YAMLObject):
	"""docstring for Link"""
	#Definim quina etiqueta del fitxer yaml correspon als objectes d'aquesta classe
	yaml_tag = u'!Link'
	def __init__(self, id, cost):
		super(Link, self).__init__()
		self.id = int(id)
		self.cost = int(cost)

def loadFile(fitxer):
	t = yaml.load(file(fitxer, 'r')) # Objecte Tranport
	return t


if __name__ == '__main__':
	print "Not an executable class"