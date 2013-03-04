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


class Station(yaml.YAMLObject):
	"""docstring for Station"""
	yaml_tag = u'!Station'
	def __init__(self, id, name, line, x, y):
		super(Station, self).__init__()
		self.id = int(id)
		self.name = name
		self.line = line
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


def main():
	tF = TransportFile()
	f = open('../enunciat/MetroLyon.txt', 'r')
	f2 = open('../enunciat/MatriuAdjacencia.txt', 'r')
	f2r = f2.read().rsplit('\n')

	for i,line in enumerate(f):
		sep = line.rsplit('\t') # separem
		tF.addStation(sep[0],sep[1],sep[2],sep[3],sep[4].rsplit(' ')[0],f2r[i])

	stream = file('lyon.yaml', 'w')
	yaml.dump(tF,stream)
	print yaml.dump(tF)


if __name__ == '__main__':
	main()