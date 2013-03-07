#!/usr/bin/env python
# encoding: utf-8

import yaml

class TransportFile(yaml.YAMLObject):
	"""docstring for Contenidor"""
	yaml_tag = u'!TransportFile'
	def __init__(self):
		super(TransportFile, self).__init__()
		self.name = "Lyon"
		self.type = "Metro"
		self.lines = []
		self.stations = []

	def addStation(self, id, name, line, x, y, links):
		st = Station(id, name, line, x, y)
		self.stations.append(st)

		if not line in self.lines:
			self.lines.append(line)

		# Links
		lSplit = links.rsplit('\t')
		l = []
		for i,stTmp in enumerate(self.stations):
			cost = lSplit[i]
			if not cost == "0":
				st.addLink(Link(stTmp.id,int(cost)))
				# Afegim la relacio a l'altre banda
				self.stations[stTmp.id-1].addLink(Link(st.id,int(cost)))

	def searchStationByName(self,ident,name):
		for st in self.stations:
			if (st.name == name and not st.id == ident):
				return st

	def fixLinks(self,new,old):
		# Primer, esborrem la relacio que ja es innecessaria
		for link in new.links:
			if (link.id == old.id):
				break
		new.cost = link.cost # Posem el cost de transbord
		new.links.remove(link)

		# Ara, passem els links nous
		for link in old.links:
			if (not link.id == new.id):
				new.links.append(link)

		for st in self.stations:
			for link in st.links:
				if (link.id == old.id):
					link.id = new.id



class Station(yaml.YAMLObject):
	"""docstring for Station"""
	yaml_tag = u'!Station'
	def __init__(self, id, name, line, x, y):
		super(Station, self).__init__()
		self.id = int(id)
		self.name = name
		self.cost = 0 # cost de transbord
		self.lines = [line]
		self.x = int(x)
		self.y = int(y)
		self.links = [] # (id,cost)

	def addLink(self,link):
		self.links.append(link)

class Link(yaml.YAMLObject):
	"""docstring for Link"""
	yaml_tag = u'!Link'
	def __init__(self, id, cost):
		super(Link, self).__init__()
		self.id = int(id)
		self.cost = int(cost)

def netejaRedundancies(tF):
	senseRepetir = []
	repetides = []
	for st in tF.stations:
		if not st.name in senseRepetir:
			senseRepetir.append(st.name)
		else:
			# Aqui tenin una repeticio. Actualitzem antiga i esborrem aquesta
			stOrig = tF.searchStationByName(st.id,st.name)
			stOrig.lines.append(st.lines[0]) # Afegim a l'antiga estacio l'UNICA (abans de parsejar) linea de la que esborrarem
			tF.fixLinks(stOrig,st)
			repetides.append(st)

	for st in repetides:
		tF.stations.remove(st)



def main():
	tF = TransportFile()
	f = open('../enunciat/MetroLyon.txt', 'r')
	f2 = open('../enunciat/MatriuAdjacencia.txt', 'r')
	f2r = f2.read().rsplit('\n')

	for i,line in enumerate(f):
		sep = line.rsplit('\t') # separem
		tF.addStation(sep[0],sep[1],sep[2],sep[3],sep[4].rsplit(' ')[0],f2r[i])

	netejaRedundancies(tF)
	stream = file('lyon.yaml', 'w')
	yaml.dump(tF,stream)
	print yaml.dump(tF)


if __name__ == '__main__':
	main()