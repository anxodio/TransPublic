#!/usr/bin/env python
# encoding: utf-8

import yaml

class Transport(yaml.YAMLObject):
	"""docstring for Contenidor"""
	yaml_tag = u'!TransportFile'
	def __init__(self,name,type,lines,stations):
		super(Transport, self).__init__()
		self.name = name
		self.type = type
		self.lines = lines
		self.stations = stations


class Station(yaml.YAMLObject):
	"""docstring for Station"""
	yaml_tag = u'!Station'
	def __init__(self, id, name, line, x, y, links):
		super(Station, self).__init__()
		self.id = int(id)
		self.name = name
		self.line = line
		self.x = int(x)
		self.y = int(y)
		self.links = links

class Link(yaml.YAMLObject):
	"""docstring for Link"""
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