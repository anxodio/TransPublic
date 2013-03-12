#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, random
from PyQt4 import QtGui, QtCore, uic
from TransEdit import TransEdit

class Viewer(QtGui.QDialog):

    def __init__(self,parent,trans):
        super(Viewer, self).__init__(parent)
        self.trans = trans
        self.ui = uic.loadUi('viewer.ui')

        # Preparem el Frame del mapa i el posem al form
        self.mF = Viewer.Map(self,trans)
        lay = QtGui.QGridLayout()
        lay.addWidget(self.mF)
        self.ui.mapGruopBox.setLayout(lay)

        self.loadLines()
        self.loadStations()

        self.ui.show()

    def loadLines(self):
        """Omple el QListWidget viewerListLines amb les linies de transport"""
        l = self.ui.viewerListLines
        l.clear()
        for line in self.trans.lines:
            item = QtGui.QListWidgetItem(line,l) # text,parent
            brush = QtGui.QBrush(self.getLineColor(line)) # per la font dels elements de la llista
            item.setForeground(brush)
            l.addItem(item)

    def loadStations(self):
        """Omple el QListWidget viewerListStations amb les estacions"""
        l = self.ui.viewerListStations
        l.clear()
        for st in self.trans.stations:
            l.addItem(str(st.id)+" "+st.name)

    def getLineColor(self,line):
        colors = [QtCore.Qt.darkGreen,QtCore.Qt.red,QtCore.Qt.yellow,QtCore.Qt.blue,QtCore.Qt.green,QtCore.Qt.magenta,QtCore.Qt.cyan]
        return colors[self.trans.lines.index(line) % len(colors)]
        

    class Map(QtGui.QFrame):  
        MIDA_COORD = 32 # constant per mida d'una coordenada
        MIDA_EST = 14 # constant per mida del punt de l'estacio (mes petit que la coordenada, perque no s'enganxin)

        def __init__(self,parent,trans):
            super(Viewer.Map, self).__init__()
            self.parent = parent # guardem el parent per poder fer servir funcions comuns, com getLineColor
            self.trans = trans
            self.initUI()

        def initUI(self):      
            # Busquem les posicions maximes i minimes
            maxX = 0
            maxY = 0
            minX = 0
            minY = 0
            for st in self.trans.stations:
                if st.x > maxX: maxX = st.x
                if st.x < minX: minX = st.x
                if st.y > maxY: maxY = st.y
                if st.y < minY: minY = st.y

            distX = maxX + minX*-1
            distY = maxY + minY*-1

            width = distX*self.MIDA_COORD # La distacia d'una banda a una altre
            height = distY*self.MIDA_COORD

            width += 2*self.MIDA_COORD # una mica mes gran, perque no quedi enganxat
            height += 2*self.MIDA_COORD

            # Per saber el centre des d'on hem de pintar, ho hem de fer relatiu als maxims i minims,
            # ja que pot ser que el maxim sigui 8 i el minim -3, i per tant el 0 no hauria d'estar al
            # mig del mapa, perquè la part d'adalt no ens cabria amb les mides que hem posat
            xMid = maxX - (distX/2)
            yMid = maxY - (distY/2)
            self.vXMid = (width/2)-(xMid*self.MIDA_COORD) # Meitat virtual en amplada
            self.vYMid = (height/2)+(yMid*self.MIDA_COORD) # Meitat virtual en altura

            self.setMinimumSize(width,height)
            self.setMaximumSize(width,height)
            #self.setWindowTitle('Mapa')

        def paintEvent(self, e):
            qp = QtGui.QPainter()
            qp.begin(self)

            self.draw(qp)
            qp.end()

        def transformStationCoords(self,x,y):
            # Per agafar el PUNT central d'una coordenada, aconseguim el del mitg del mapa,
            # i ens movem
            newX = self.vXMid+(x*self.MIDA_COORD)
            newY = self.vYMid-(y*self.MIDA_COORD) # No se perque ha de ser negatiu, pero si no surt al reves xD
            return newX,newY

        def drawStation(self,qp,st):
            ident = st.id
            x,y = self.transformStationCoords(st.x,st.y)

            # Primer, pintem les connexions (perque quedin a sota). Nomes les pintem un cop
            # Ara, les connexions
            for link in st.links:
                if link.id > st.id:
                    otherSt = self.trans.getStationByID(link.id)
                    oX,oY = self.transformStationCoords(otherSt.x,otherSt.y)
                    qp.setPen(self.parent.getLineColor(st.getCommonLine(otherSt)))
                    qp.drawLine(x,y,oX,oY)
                    qp.setPen(QtCore.Qt.black)
                    qp.drawText((x+oX)/2, (y+oY)/2, str(link.cost)) # dibuixem cost

            qp.setPen(QtCore.Qt.gray)
            qp.setBrush(QtCore.Qt.black)
            qp.drawEllipse(x-(self.MIDA_EST/2), y-(self.MIDA_EST/2), self.MIDA_EST, self.MIDA_EST) # dibuixem estacio
            qp.setPen(QtCore.Qt.white)
            qp.drawText(x-(self.MIDA_EST/3), y+(self.MIDA_EST/3), str(ident)) # dibuixem ID dintre de les rodones
            
        def draw(self, qp):
            font = QtGui.QFont()
            font.setPixelSize(int(self.MIDA_EST/1.5))
            font.setBold(True)
            qp.setFont(font)
            for st in self.trans.stations:
                self.drawStation(qp,st)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = Viewer(None,TransEdit.loadFile("./lyon.yaml"))
    sys.exit(app.exec_())