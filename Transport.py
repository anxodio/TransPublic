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
		"""Esborra una linea, tambe de les estacions i els seus links"""
		for st in self.stations:
			if lin in st.lines:
				# Esborrem els links d'aquella linea
				for link in st.links:
					otherSt = self.getStationByID(link.id)
					if st.getCommonLine(otherSt) == lin: # Si estan relacionades per la linea que borrem...
						otherSt.removeLinkToID(st.id) # borrem el link (a dues bandes)
						st.removeLinkToID(otherSt.id)
				st.lines.remove(lin) # eliminem la linea de l'estacio

		self.lines.remove(lin) # eliminem la linea de les linies del fitxer

	def deleteStation(self,st):
		# Busquem les estacions que tenia linkades, i els hi borrem el link cap aquesta
		for link in st.links:
			otherSt = self.getStationByID(link.id)
			otherSt.removeLinkToID(st.id)
		self.stations.remove(st) #l'eliminem de la llista


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
	def __init__(self, id, name, cost, lines, x, y, links):
		super(Station, self).__init__()
		self.id = int(id)
		self.name = name
		self.cost = cost
		self.lines = lines
		self.x = int(x)
		self.y = int(y)
		self.links = links

	def reloadLinks(self,trans,links):
		# Primer, eliminem els links actuals
		for link in self.links:
			stLinked = trans.getStationByID(link.id)
			stLinked.removeLinkToID(self.id) # l'eliminem de l'altre banda
		self.links = [] # Un cop hem acabat d'eliminarlos de l'altre banda, buidem la llista

		# Ara, posem els nous links
		for link in links:
			self.addLink(link[0],link[1]) # Ens afegim el link
			stLinked = trans.getStationByID(link[0])
			stLinked.addLink(self.id,link[1]) # L'afegim a l'altre banda

	def addLink(self,ident,cost):
		# Si tenim un link cap a aquest ID, l'eliminem
		l = Link(ident,cost)
		self.links.append(l)

	def removeLinkToID(self,ident):
		# Si tenim un link cap a aquest ID, l'eliminem
		l = None
		for link in self.links:
			if link.id == ident:
				l = link
				break
		if l: self.links.remove(l)

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
	def __init__(self, id, cost):
		super(Link, self).__init__()
		self.id = int(id)
		self.cost = int(cost)

def loadFile(fitxer):
	t = yaml.load(file(fitxer, 'r')) # Objecte Tranport
	return t

def saveFile(trans,fitxer):
	yaml.dump(trans,file(fitxer, 'w'))


if __name__ == '__main__':
	print "Not an executable class"