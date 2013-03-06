#!/usr/bin/env python
# encoding: utf-8

import yaml
import Transport

#calcular distancia
import math

#AQUESTA FUNCIO NO ES FA SERVIR AQUI PERO EM SEMBLA UTIL
def getStationsLinea(linea):
	"""Retorna una llista amb les estacions de la linea indicada"""
	estacions = []
	for station in trans.stations:
		if linea in station.lines:
			estacions.append(station)

	return estacions

def calcDistance(coord1, coord2):
	"""Calcula la distancia entre dues posicions del mapa"""
	#coord1 i coord2 son una llista amb 2 camps: (x, y)
	dist = math.sqrt( pow((coord1[0]-coord2[0]),2) + pow((coord1[1]-coord2[1]),2))
	return dist

def cercaA(arrel, objectiu):
	llista = [[arrel]]

	#mentre no trobem l'objectiu anirem expandint
	while (llista[0][0] != objectiu or llista != []):
		cami = llista.pop(0)
		cami_exp = expandirCami(cami)
		cami_exp = eliminarCicles(cami_exp)
		#TO DO: insertar cami_exp a llista
		eliminarCaminsRedundants(llista)

def eliminarCicles(cami_exp):
	"""Elimina cicles del cami expandit"""
	#Quan hi ha cicle??
	#Quan cami[0] esta repetit dins el mateix cami (Nomes mirem cami[0] perque els altres elements ja els hauriem d'haver comprovat abans)
	
	eliminar = []

	for cami in cami_exp:
		if (cami[0] in cami[1:]):
			eliminar.append(cami)

	for cami in eliminar:
		cami_exp.remove(cami)

	return cami_exp

def eliminarCaminsRedundants(llista):
	"""Elimina camins de la llista que son redundants"""
	#Un camí es redundant quan va al mateix lloc que un altre camí i té més cost
	#Un camí que té mes cost que un altre es trobará més a la dreta dins la llista

	#creem una llista amb tots els destins dels camins actuals
	llista_caps = []
	for cami in llista:
		llista_caps.append(cami[0])

	for i in range(len(llista_caps)-1, -1, -1):
		#Si el cap de la posicio=i ja està en una posició més petita, l'eliminem.
		if llista_caps[i] in llista_caps[:i]:
			llista.pop(i)


def expandirCami(cami):
	"""Expandeix un cami. Retorna els camins expandits"""
	# cami = [objecte_station, objecte_station, objecte_station arrel]
	expandit = []

	# per cada enllaç que tingui la estacio expandirem un camí
	for link in cami[0].links:
		#busquem la estació "fill"
		nova_estacio = trans.getStationByID(link.id)
		#fem una copia de la llista camí
		nou_cami = cami[:]
		#insert(0,i) afegeix i com el primer element de la llista
		nou_cami.insert(0, nova_estacio)
		#insertem el nou camí a la llista d'expandits
		expandit.insert(0, nou_cami)

	return expandit

def provaEliminarCicles():
	camins = [[1,3,1], [5,2,5], [1,2,3]]
	print camins
	print eliminarCicles(camins)

def provaEliminarRedundants():
	camins = [[4,2,3,5], [4,0,0,0], [2,5,6,5], [16,2,3,5], [4,1,1,1], [2,16,3]]
	eliminarCaminsRedundants(camins)
	print camins

def provaExpCami():
	arrel = trans.getStationByID(4)
	cami = [arrel]
	exp = expandirCami(cami)
	for llista in exp:
		print llista[0].name, llista[1].name

if __name__ == '__main__':
	trans = Transport.loadFile("lyon.yaml")
	provaEliminarRedundants()