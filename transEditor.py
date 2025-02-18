#!/usr/bin/env python
# encoding: utf-8

import sys
import yaml
from PyQt4 import QtGui, QtCore, uic

from TransEdit import TransEdit
from Viewer import Viewer

class TransEditor(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		self.ui = uic.loadUi('edit.ui')
		self.ui.show()

		# SubDialeg per crear/editar estacions
		self.stDialog = QtGui.QDialog(self)
		self.stDialog.ui = uic.loadUi('editStation.ui')

		self.connect(self.ui.menuNew, QtCore.SIGNAL("activated()"), self.newFile)
		self.connect(self.ui.menuOpen, QtCore.SIGNAL("activated()"), self.openFile)
		self.connect(self.ui.menuSave, QtCore.SIGNAL("activated()"), self.saveFile)
		self.connect(self.ui.menuSaveAs, QtCore.SIGNAL("activated()"), self.saveFileAs)
		self.connect(self.ui.menuGenMap, QtCore.SIGNAL("activated()"), self.genMap)

		self.connect(self.ui.tbAddLine, QtCore.SIGNAL("clicked()"), self.addLine)
		self.connect(self.ui.tbEditLine, QtCore.SIGNAL("clicked()"), self.editLine)
		self.connect(self.ui.listLines, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.editLine)
		self.connect(self.ui.tbDelLine, QtCore.SIGNAL("clicked()"), self.delLine)

		self.connect(self.ui.tbAddStation, QtCore.SIGNAL("clicked()"), self.addStation)
		self.connect(self.ui.tbEditStation, QtCore.SIGNAL("clicked()"), self.editStation_clicked)
		self.connect(self.ui.tableStations, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.editStation_dclicked)
		self.connect(self.ui.tbDelStation, QtCore.SIGNAL("clicked()"), self.delStation)

		self.stDialog.connect(self.stDialog.ui, QtCore.SIGNAL("finished(int)"), self.editStationTancat)
		self.stDialog.connect(self.stDialog.ui.pbGuardar, QtCore.SIGNAL("clicked()"), self.saveStation)
		self.stDialog.connect(self.stDialog.ui.tbUpLine, QtCore.SIGNAL("clicked()"), self.upLine)
		self.stDialog.connect(self.stDialog.ui.tbDownLine, QtCore.SIGNAL("clicked()"), self.downLine)

		self.stDialog.connect(self.stDialog.ui.tbAddLink, QtCore.SIGNAL("clicked()"), self.addLink)
		self.stDialog.connect(self.stDialog.ui.tbEditLink, QtCore.SIGNAL("clicked()"), self.editLink)
		self.stDialog.connect(self.stDialog.ui.tableLinks, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.editLink)
		self.stDialog.connect(self.stDialog.ui.tbDelLink, QtCore.SIGNAL("clicked()"), self.delLink)

		self.trans = None # Per mantenir l'estructura del fitxer de transport en memoria
		self.lastFileName = "" # Per guardar sense buscar a on

	def unLockForm(self):
		self.ui.mainFrame.setEnabled(True)
		self.ui.tbAddLine.setEnabled(True)
		self.ui.tbEditLine.setEnabled(True)
		self.ui.tbDelLine.setEnabled(True)
		self.ui.tbAddStation.setEnabled(True)
		self.ui.tbEditStation.setEnabled(True)
		self.ui.tbDelStation.setEnabled(True)

	def genMap(self):
		if self.trans:
			Viewer(self,self.trans)

	def comprovaCreat(self):
		ok = True
		if self.trans:
			ret = QtGui.QMessageBox.warning(self, u"Atenció", u"Si continues pots perdre canvis no guardats. Estàs segur?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
			if not ret == QtGui.QMessageBox.Yes:
				ok = False
		return ok

	def setLastFileName(self,text):
		self.lastFileName = text
		self.ui.setWindowTitle("TransEdit ("+text+")")

	def newFile(self):
		"""Funció per crear un nou fitxer"""
		if not self.comprovaCreat(): return
		self.trans = TransEdit("","Metro",[],[])
		self.loadLines()
		self.loadStations()
		self.unLockForm()

	def openFile(self):
		"""Funció per obrir el fitxer de transport que volem editar"""
		if not self.comprovaCreat(): return
		fitxer = QtGui.QFileDialog.getOpenFileName(self, "Selecciona un fitxer de Transport", ".", "*.yaml")
		if not fitxer or fitxer == "": return
		self.setLastFileName(str(fitxer))
		self.trans = TransEdit.loadFile(str(fitxer))
		self.loadLines()
		self.loadStations()
		self.ui.inputNom.setText(self.trans.name)
		self.unLockForm()

	def saveFile(self):
		if not self.trans: return # No hi ha res a guardar
		if self.lastFileName == "":
			self.saveFileAs() # es un nou fitxer, s'ha de guardar buscant el nom
			return

		self.trans.name = str(self.ui.inputNom.text())
		TransEdit.saveFile(self.trans,self.lastFileName)

	def saveFileAs(self):
		if not self.trans: return # No hi ha res a guardar
		fitxer = QtGui.QFileDialog.getSaveFileName(self, "Desa el fitxer", ".", "*.yaml")
		if not fitxer or fitxer == "": return
		self.setLastFileName(str(fitxer))
		self.saveFile()

	def loadLines(self):
		"""Omple el QListWidget listLines amb les linies de transport"""
		l = self.ui.listLines
		l.clear()
		for line in self.trans.lines:
			l.addItem(line)

	def addLine(self):
		text, ok = QtGui.QInputDialog.getText(self, u'Nova Línia', 'Entra el codi:')
		if ok and not text == "":
			#addLine retorna False si no pot insertar la nova linea
			if self.trans.addLine(str(text)):
				#si la insertat a l0bjecte transport, també l'ha d'insertar a listLines
				self.ui.listLines.addItem(str(text))
			else:
				QtGui.QMessageBox.warning(self, "Error", "La línia ja existeix", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)


	def editLine(self,item=None):
		l = self.ui.listLines
		if item: current = item
		else: current = l.currentItem()
		if (current):
			old = current.text()
			new, ok = QtGui.QInputDialog.getText(self, u'Edita Línia', 'Entra el nou codi per '+old+':')
			if ok and not new == "":
				self.trans.changeLineName(str(old),str(new))
				current.setText(str(new))
				self.loadStations() # Recarreguem


	def delLine(self):
		l = self.ui.listLines
		current = l.currentItem()
		if (current):
			ret = QtGui.QMessageBox.warning(self, "Avis", "Segur que vols esborrar la linea?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
			if ret == QtGui.QMessageBox.Yes:
				self.trans.deleteLine(current.text())
				l.takeItem(l.row(current))
				self.loadStations() # Recarreguem

	def loadStations(self):
		table = self.ui.tableStations
		table.clearContents()
		table.setRowCount(0)
		for station in self.trans.stations:
			row = table.rowCount()
			table.insertRow(row)
			table.setItem(row,0,QtGui.QTableWidgetItem(str(station.id)))
			table.setItem(row,1,QtGui.QTableWidgetItem(station.name))
			table.setItem(row,2,QtGui.QTableWidgetItem(str(station.lines)))
			table.setItem(row,3,QtGui.QTableWidgetItem(str(station.x)))
			table.setItem(row,4,QtGui.QTableWidgetItem(str(station.y)))

	def addStation(self):
		ident = self.trans.getNewStationID()
		st = TransEdit.StationEdit(ident, "", 0, [], 0, 0, [])
		self.trans.stations.append(st)
		self.editStation(ident)

	def delStation(self):
		table = self.ui.tableStations
		row = table.currentRow()
		if row == -1:
			return

		ret = QtGui.QMessageBox.warning(self, "Avis", u"Segur que vols esborrar l'Estació'?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
		if ret == QtGui.QMessageBox.Yes:
			self.trans.deleteStation(self.trans.getStationByID(int(table.item(row,0).text()))) # l'eliminem del arxiu en memoria
			table.removeRow(row) # l'eliminem del control grafic

	def editStation_clicked(self):
		# Al apretar boto
		table = self.ui.tableStations
		row = table.currentRow()
		if row == -1:
			return
		self.editStation_dclicked(row,0)

	def editStation_dclicked(self,row,col):
		# Al fer doble click
		table = self.ui.tableStations
		ident = int(table.item(row,0).text())
		self.editStation(ident)

	def editStation(self,ident):
		st = self.trans.getStationByID(ident)
		if (st):
			self.ui.setEnabled(False) # desactivem formulari principal
			d = self.stDialog.ui
			d.inputID.setValue(st.id)
			d.inputStationName.setText(st.name)
			d.inputX.setValue(st.x)
			d.inputY.setValue(st.y)
			d.inputCostT.setValue(st.cost)
			self.loadStationLines(st)
			self.loadStationLinks(st)
			d.show()

	def loadStationLines(self,st):
		lAct = self.stDialog.ui.listLinesAct
		lOthers = self.stDialog.ui.listLinesOthers
		lAct.clear()
		lOthers.clear()
		for line in st.lines:
			lAct.addItem(line)
		for line in self.trans.lines:
			if not line in st.lines:
				lOthers.addItem(line)

	def loadStationLinks(self,st):
		table = self.stDialog.ui.tableLinks
		table.clearContents()
		table.setRowCount(0)
		for link in st.links:
			row = table.rowCount()
			table.insertRow(row)
			table.setItem(row,0,QtGui.QTableWidgetItem(str(link.id)))
			table.setItem(row,1,QtGui.QTableWidgetItem(str(link.cost)))
			table.setItem(row,2,QtGui.QTableWidgetItem(str(link.line)))

	def podemTreureLinia(self,ident,line):
		# Basicament, no ens deixara moure lines mentre hi hagi connexions fetes.
		# Per tant, si treure una linia, primer eliminem les connexions d'aquella linea.
		ok = True
		table = self.stDialog.ui.tableLinks
		for i in range(table.rowCount()):
			if table.item(i,2).text() == line:
				QtGui.QMessageBox.warning(self, "Error", u"No pots treure una línea mentre tingui connexions assignades", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				ok = False
				break
		
		return ok

	def upLine(self):
		""" Assignar una nova linea """
		lOthers = self.stDialog.ui.listLinesOthers
		if lOthers.currentRow() == -1: return # No hi ha cap seleccionada

		lAct = self.stDialog.ui.listLinesAct
		item = lOthers.takeItem(lOthers.currentRow())
		if item:
			lAct.addItem(item)

	def downLine(self):
		""" Treure una linea. Nomes podem si no te cap link assignat """
		lAct = self.stDialog.ui.listLinesAct
		if lAct.currentRow() == -1: return # No hi ha cap seleccionada
		if not self.podemTreureLinia(int(self.stDialog.ui.inputID.value()),lAct.currentItem().text()): return
		
		lOthers = self.stDialog.ui.listLinesOthers
		item = lAct.takeItem(lAct.currentRow())
		if item:
			lOthers.addItem(item)

	def addLink(self):
		d = self.stDialog.ui
		ident = int(d.inputID.value())
		linkID, ok = QtGui.QInputDialog.getInt(self, u'Nova Connexió', u"Entra l'ID de l'Estació:",0,0,99)
		if ok:
			# Comprovem si el id que ens han posat existeix
			linkSt = self.trans.getStationByID(linkID)
			if not linkSt:
				QtGui.QMessageBox.warning(self, "Error", u"La estació indicada no existeix", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

			# Comprovem si el id és el mateix que el nostre
			if linkSt.id == ident:
				QtGui.QMessageBox.warning(self, "Error", u"No es pot fer una connexió a la mateixa estació", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

			# Ha d'existir alguna relacio entre les linies
			# No fem servir el getCommonLines degut a que encara no tenim les lines al objecte, sino al control listLinesAct
			lineRelation = False 
			for i in range(d.listLinesAct.count()):
				line = str(d.listLinesAct.item(i).text())
				if line in linkSt.lines:
					lineRelation = line

			if not lineRelation:
				QtGui.QMessageBox.warning(self, "Error", u"La estació indicada no té cap de les línies d'aquesta", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

			# Comprovem que no estem ficant mes de dos links a la mateixa linea (en actual)
			cont = 0
			for i in range(d.tableLinks.rowCount()):
				if lineRelation == d.tableLinks.item(i,2).text(): cont += 1
			if cont >= 2:
				QtGui.QMessageBox.warning(self, "Error", u"Ja tens dos connexions a la línea "+lineRelation, QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

			# Ara, el mateix amb l'altre banda
			cont = 0
			for link in linkSt.links: # mirem cadascun dels seus links
				# Si la linea d'aquells links es la mateixa que tenim, sumem
				if lineRelation == link.line: cont += 1
			if cont >= 2:
				QtGui.QMessageBox.warning(self, "Error", u"L'estació amb la que vols fer la connexió ja té dos connexions a la línea "+lineRelation, QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

			# Tot comprovat
			cost, ok2 = QtGui.QInputDialog.getInt(self, u'Nova Connexió', u"Entra el cost:",0,0,99)
			if ok2:
				row = d.tableLinks.rowCount()
				d.tableLinks.insertRow(row)
				d.tableLinks.setItem(row,0,QtGui.QTableWidgetItem(str(linkID)))
				d.tableLinks.setItem(row,1,QtGui.QTableWidgetItem(str(cost)))
				d.tableLinks.setItem(row,2,QtGui.QTableWidgetItem(str(lineRelation)))

	def editLink(self,row=None,col=None):
		d = self.stDialog.ui
		if not row:
			row = d.tableLinks.currentRow()

		if row == -1:
			return

		oldCost = int(d.tableLinks.item(row,1).text())
		cost, ok = QtGui.QInputDialog.getInt(self, u'Nova Connexió', u"Entra el cost:",oldCost,0,99)
		if ok:
			d.tableLinks.item(row,1).setText(str(cost))

	def delLink(self):
		d = self.stDialog.ui
		row = d.tableLinks.currentRow()
		if row == -1:
			return

		ret = QtGui.QMessageBox.warning(self, "Avis", u"Segur que vols esborrar la Connexió?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.Cancel)
		if ret == QtGui.QMessageBox.Yes:
			d.tableLinks.removeRow(row)

	def saveStation(self):
		d = self.stDialog.ui
		ident = int(d.inputID.value())
		x = int(d.inputX.value())
		y = int(d.inputY.value())

		# Comprovem que les coordenades no coincideixin amb una altre
		for otherSt in self.trans.stations:
			if otherSt.id == ident: continue
			if otherSt.x == x and otherSt.y == y:
				QtGui.QMessageBox.warning(self, "Error", u"Ja existeix una altre estació en aquestes coordenades.", QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
				return

		# Posem les noves dades al objecte Estació
		st = self.trans.getStationByID(ident)
		st.name = str(d.inputStationName.text())
		st.x = x
		st.y = y
		st.cost = int(d.inputCostT.value())

		# Linies: Les posem de nou
		lines = []
		for i in range(d.listLinesAct.count()):
			lines.append(str(d.listLinesAct.item(i).text()))
		st.lines = lines

		# Links: Els posem de nou, però hem de mantenir la relacio a l'altre banda
		links = []
		for i in range(d.tableLinks.rowCount()):
			# tupla amb id,cost, line
			links.append((int(d.tableLinks.item(i,0).text()),int(d.tableLinks.item(i,1).text()),str(d.tableLinks.item(i,2).text())))
		st.reloadLinks(self.trans,links)

		d.done(1)

	def editStationTancat(self,estat=None):
		# Estat 0 = Tancat, 1 = Guardat
		print "ADEU! Estat: "+str(estat)
		self.ui.setEnabled(True) # activem formulari principal
		self.unLockForm()
		self.loadLines()
		self.loadStations()

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = TransEditor()
	sys.exit(app.exec_())