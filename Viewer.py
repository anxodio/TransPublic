#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore, uic
from TransEdit import TransEdit
from Map import Map

class Viewer(QtGui.QDialog):

    def __init__(self,parent,trans):
        super(Viewer, self).__init__(parent)
        self.trans = trans
        self.ui = uic.loadUi('viewer.ui')

        # Preparem el Frame del mapa i el posem al form
        self.mF = Map(self,trans)
        lay = QtGui.QGridLayout()
        lay.addWidget(self.mF)
        self.ui.mapGruopBox.setLayout(lay)

        # Connexions d'events
        self.connect(self.ui.viewerListStations, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.listStationsChanged)

        self.stOrigen = None
        self.stDesti = None # No s'utilitza, pero la declarem perque el Map es compartit amb transPublic

        self.loadLines()
        self.loadStations()

        self.ui.show()

    def loadLines(self):
        """Omple el QListWidget viewerListLines amb les linies de transport"""
        l = self.ui.viewerListLines
        l.clear()
        for line in self.trans.lines:
            item = QtGui.QListWidgetItem(line,l) # text,parent
            brush = QtGui.QBrush(self.mF.getLineColor(line)) # per la font dels elements de la llista
            item.setForeground(brush)
            l.addItem(item)

    def loadStations(self):
        """Omple el QListWidget viewerListStations amb les estacions"""
        l = self.ui.viewerListStations
        l.clear()
        for st in self.trans.stations:
            text = str(st.id)+" "+st.name
            if st.cost > 0:
                text += " (Cost: "+str(st.cost)+")"
            l.addItem(text)

    def listStationsChanged(self,newItem,oldItem):
        if oldItem and newItem: # aixi evitem que s'activi només entrar
            text = str(newItem.text())
            ident = int(text.split(" ")[0]) # Separem per espais i agafem la ID
            self.stOrigen = self.trans.getStationByID(ident) # marquem l'estació com seleccionada
            self.mF.repaint() # repintem

    def selectStationByCoords(self,x,y,button):
        # El boto en aquest cas no ens interesa
        st = self.trans.getStationByCoords(x,y)
        # pot ser que no la trobi per click en coordenades on no hi ha res
        if st:
            # La seleccionem a la llista, guardem i repintem (ja que al seleccionar desde aqui no es llença el changed de la llista)
            lS = self.ui.viewerListStations
            for i in range(lS.count()):
                item = lS.item(i)
                text = str(item.text())
                ident = int(text.split(" ")[0])
                if (st.id == ident):
                    item.setSelected(True)
                    lS.scrollToItem(item)
                    self.stOrigen = st # marquem l'estació com seleccionada
                    self.mF.repaint() # repintem
                    break

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = Viewer(None,TransEdit.loadFile("./lyon.yaml"))
    sys.exit(app.exec_())