#!/usr/bin/env python
# encoding: utf-8

import sys
import yaml
from PyQt4 import QtGui, QtCore, uic

from Transport import Transport
from Map import Map
from AStar import AStar

class TransPublic(QtGui.QMainWindow):
	""" Interficie grafica per l'algorisme """
	SELECT_DEFECTE = u"Escull una estació"

	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		self.trans = None # Per mantenir l'estructura del fitxer de transport en memoria

		self.stOrigen = None
		self.stDesti = None

		self.a = None
		self.cami = None

		self.ui = uic.loadUi('transPublic.ui')

		#Preparem el Frame del mapa i el posem al form
		self.mF = Map(self,None)
		lay = QtGui.QGridLayout()
		lay.addWidget(self.mF)
		self.ui.mapGruopBox.setLayout(lay)

		self.connect(self.ui.menuOpen, QtCore.SIGNAL("activated()"), self.openFile)
		self.connect(self.ui.cbOrigen, QtCore.SIGNAL("activated(QString)"), self.cbOrigen_changed)
		self.connect(self.ui.cbDesti, QtCore.SIGNAL("activated(QString)"), self.cbDesti_changed)
		self.connect(self.ui.pbCalcula, QtCore.SIGNAL("clicked()"), self.calcula)

		self.ui.show()

	def setOrigen(self,st):
		self.stOrigen = st

	def setDesti(self,st):
		self.stDesti = st

	def unLockForm(self):
		self.ui.centralwidget.setEnabled(True)

	def openFile(self):
		"""Funció per obrir el fitxer de transport per treballar"""
		fitxer = QtGui.QFileDialog.getOpenFileName(self, "Selecciona un fitxer de Transport", ".", "*.yaml")
		if not fitxer or fitxer == "": return
		self.trans = Transport.loadFile(str(fitxer))
		self.loadStations()
		self.mF.setTrans(self.trans)
		self.a = AStar(self.trans)
		self.unLockForm()

	def loadStations(self):
		cbOrigen = self.ui.cbOrigen
		cbOrigen.clear()
		cbOrigen.addItem(self.SELECT_DEFECTE)
		cbDesti = self.ui.cbDesti
		cbDesti.clear()
		cbDesti.addItem(self.SELECT_DEFECTE)
		for st in self.trans.stations:
			text = str(st.id)+" "+st.name
			cbOrigen.addItem(text)
			cbDesti.addItem(text)

	def seleccionaEstacio(self,t,funcio):
		# Permet seleccionar tant l'origen com la desti, per no repetir codi
		self.cami = None # reiniciem cami!
		self.ui.tResultat.setText("") # reiniciem text resultat
		if not t == self.SELECT_DEFECTE:
			text = str(t)
			ident = int(text.split(" ")[0]) # Separem per espais i agafem la ID
			funcio(self.trans.getStationByID(ident)) # marquem l'estació com seleccionada
		else:
			funcio(None) # marquem l'estació com seleccionada

		self.mF.repaint() # repintem

	def cbOrigen_changed(self,text):
		self.seleccionaEstacio(text,self.setOrigen)

	def cbDesti_changed(self,text):
		self.seleccionaEstacio(text,self.setDesti)

	def calcula(self):
		if self.stOrigen and self.stDesti:
			# Agafem valors de spinbox (si son diferents a 0, sino None)
			max_dist = None if int(self.ui.spDistancia.value()) == 0 else int(self.ui.spDistancia.value())
			max_transbords = None if int(self.ui.spTransbords.value()) == 0 else int(self.ui.spTransbords.value())
			max_parades = None if int(self.ui.spParades.value()) == 0 else int(self.ui.spParades.value())

			# Executem algorisme a estrella
			camins = self.a.doAStarSearch(self.stOrigen,self.stDesti,max_dist,max_transbords,max_parades)
			self.cami = camins[0]
			self.mF.repaint() # repintem

			textHR = self.a.transformPathToHumanReadable(self.cami) # text Human Readable
			textHR = textHR.replace("\n","<br />") # fiquem els salts de linea en format HTML
			textQT = QtCore.QString.fromUtf8(textHR) # el passem a format QT ara es veuran bé els accents al QTextEdit
			self.ui.tResultat.setHtml(textQT+"<br /><br />Cost (temps): <b>"+str(self.cami.cost)+"</b>\
			<br />Distancia: <b>"+str(self.cami.distancia)+"</b>\
			<br />Transbords: <b>"+str(self.cami.transbords)+"</b>\
			<br />Parades: <b>"+str(self.cami.parades)+"</b>")

	def selectStationByCoords(self,x,y,button):
		st = self.trans.getStationByCoords(x,y)
		# pot ser que no la trobi per click en coordenades on no hi ha res
		if st:
			# Boto esquerre: Origen. Boto dret: Desti
			if button == QtCore.Qt.LeftButton:
				cb = self.ui.cbOrigen
				funcio = self.setOrigen
			elif button == QtCore.Qt.RightButton:
				cb = self.ui.cbDesti
				funcio = self.setDesti
			else: return # No fem res

			for i in range(1,cb.count()): # A la 0 hi ha el Escull...
				text = str(cb.itemText(i))
				ident = int(text.split(" ")[0])
				if (st.id == ident):
					# La marquem com seleccionada
					cb.setCurrentIndex(i) 
					self.seleccionaEstacio(cb.itemText(i),funcio)

        	

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = TransPublic()
	sys.exit(app.exec_())