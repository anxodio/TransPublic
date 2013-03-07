#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In the example, we draw randomly 1000 red points 
on the window.

author: Jan Bodnar
website: zetcode.com 
last edited: September 2011
"""

import sys, random
from PyQt4 import QtGui, QtCore

class Map(QtGui.QDialog):
    MIDA_COORD = 32 # constant per mida d'una coordenada
    MIDA_EST = 12 # constant per mida del punt de l'estacio (mes petit que la coordenada, perque no s'enganxin)

    def __init__(self,parent,trans):
        super(Map, self).__init__(parent)
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

        width = (maxX + minX*-1)*self.MIDA_COORD # es dona per soposat que els minims son negatius
        height = (maxY + minY*-1)*self.MIDA_COORD

        width += 4*self.MIDA_COORD # una mica mes gran, per si les mosques
        height += 4*self.MIDA_COORD

        self.setGeometry(300, 300, width, height)
        self.setWindowTitle('Mapa')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def transformStationCoords(self,x,y):
        # Per agafar el PUNT central d'una coordenada, aconseguim el del mitg del mapa,
        # i ens movem
        size = self.size()
        xMid = size.width()/2
        yMid = size.height()/2
        newX = xMid+(x*self.MIDA_COORD)
        newY = yMid-(y*self.MIDA_COORD) # No se perque ha de ser negatiu, pero si no surt al reves xD
        return newX,newY

    def getLineColor(self,line):
        colors = [QtCore.Qt.blue,QtCore.Qt.red,QtCore.Qt.green,QtCore.Qt.yellow,QtCore.Qt.cyan,QtCore.Qt.magenta]
        return colors[self.trans.lines.index(line) % len(colors)]


    def drawStation(self,qp,st):
        ident = st.id
        x,y = self.transformStationCoords(st.x,st.y)

        qp.setPen(QtCore.Qt.gray)
        qp.setBrush(QtCore.Qt.black)
        qp.drawEllipse(x-(self.MIDA_EST/2), y-(self.MIDA_EST/2), self.MIDA_EST, self.MIDA_EST) # dibuixem estacio
        qp.setPen(QtCore.Qt.red)
        qp.drawText(x-self.MIDA_EST, y-self.MIDA_EST, str(ident)) # dibuixem ID

        # Ara, les connexions
        for link in st.links:
            otherSt = self.trans.getStationByID(link.id)
            oX,oY = self.transformStationCoords(otherSt.x,otherSt.y)
            qp.setPen(self.getLineColor(st.getCommonLine(otherSt)))
            qp.drawLine(x,y,oX,oY)

        
    def draw(self, qp):
        for st in self.trans.stations:
            self.drawStation(qp,st)

        
                
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Map()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()