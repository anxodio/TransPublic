#!/usr/bin/env python
# encoding: utf-8

import sys
import yaml
from PyQt4 import QtGui, QtCore, uic

import Transport

class TransEditor(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		self.trans = ""
 
		self.ui = uic.loadUi('prova.ui')
		self.ui.show()

		self.connect(self.ui.menuOpen, QtCore.SIGNAL("activated()"), self.openFile)

		self.connect(self.ui.tbAddLine, QtCore.SIGNAL("clicked()"), self.addLine)
		self.connect(self.ui.tbEditLine, QtCore.SIGNAL("clicked()"), self.editLine)
		self.connect(self.ui.listLines, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem)"), self.editLine)
		self.connect(self.ui.tbDelLine, QtCore.SIGNAL("clicked()"), self.delLine)

	def openFile(self):
		fitxer = QtGui.QFileDialog.getOpenFileName(self, "Selecciona un fitxer de Transport", ".", "*.yaml")
		print fitxer
		self.trans = Transport.loadFile(str(fitxer))
		self.loadLines()
		self.loadStations()

	def loadLines(self):
		l = self.ui.listLines
		l.clear()
		for line in self.trans.lines:
			l.addItem(line)

	def addLine(self):
		self.ui.listLines.addItem("NovaLinia")

	def editLine(self,item=None):
		l = self.ui.listLines
		if item: current = item
		else: current = l.currentItem()
		if (current):
			current.setFlags(current.flags().__or__(QtCore.Qt.ItemIsEditable))
			l.editItem(current)


	def delLine(self):
		l = self.ui.listLines
		current = l.currentItem()
		if (current):
			l.takeItem(l.row(current))

	def loadStations(self):
		table = self.ui.tableStations
		table.clearContents()
		for station in self.trans.stations:
			row = table.rowCount()
			table.insertRow(row)
			table.setItem(row,0,QtGui.QTableWidgetItem(str(station.id)))
			table.setItem(row,1,QtGui.QTableWidgetItem(station.name))
			table.setItem(row,2,QtGui.QTableWidgetItem(station.line))
			table.setItem(row,3,QtGui.QTableWidgetItem(str(station.x)))
			table.setItem(row,4,QtGui.QTableWidgetItem(str(station.y)))
			



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	win = TransEditor()
	sys.exit(app.exec_())