#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore, uic

class Map(QtGui.QFrame):  
        MIDA_COORD = 32 # constant per mida d'una coordenada
        MIDA_EST = 14 # constant per mida del punt de l'estacio (mes petit que la coordenada, perque no s'enganxin)

        def __init__(self,parent,trans=None):
            super(Map, self).__init__()
            self.parent = parent # guardem el parent per poder fer servir funcions comuns, com getLineColor
            self.trans = trans

            # Connexions
            self.mousePressEvent = self.pixelSelect

            if self.trans:
                self.initUI()

        def setTrans(self,trans):
            self.trans = trans
            if self.trans:
                self.initUI()

        def getLineColor(self,line):
            colors = [QtCore.Qt.darkGreen,QtCore.Qt.red,QtCore.Qt.yellow,QtCore.Qt.blue,QtCore.Qt.green,QtCore.Qt.magenta,QtCore.Qt.cyan]
            return colors[self.trans.lines.index(line) % len(colors)]

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
            self.vXMid = ((width/2)-(xMid*self.MIDA_COORD)) + self.MIDA_COORD/2 # Meitat virtual en amplada
            self.vYMid = ((height/2)+(yMid*self.MIDA_COORD)) - self.MIDA_COORD/2 # Meitat virtual en altura

            self.setMinimumSize(width,height)
            self.setMaximumSize(width,height)

        def pixelSelect(self,event):
            if self.trans:
                x = event.pos().x()
                y = event.pos().y()
                # TRANSFORMAR
                newX, newY = self.transformPixelToStationCoords(x,y)
                self.parent.selectStationByCoords(newX,newY,event.button())

        def paintEvent(self, e):
            qp = QtGui.QPainter()
            qp.begin(self)

            if self.trans:
                self.draw(qp)
            qp.end()

        def transformStationCoordsToPixel(self,x,y):
            # Per agafar el PUNT central d'una coordenada, aconseguim el del mitg del mapa,
            # i ens movem
            newX = self.vXMid+(x*self.MIDA_COORD)
            newY = self.vYMid-(y*self.MIDA_COORD) # No se perque ha de ser negatiu, pero si no surt al reves xD
            return newX,newY

        def transformPixelToStationCoords(self,x,y):
            # El mateix que a la funcio d'abans, pero al inreves (converteix pixels a coordenades de estació)
            # No ho se explicar massa be. TODO: Analitzar perquè funciona xD
            newX = (x-self.vXMid+(self.MIDA_COORD/2))/self.MIDA_COORD
            newY = -((y-self.vYMid+(self.MIDA_COORD/2))/self.MIDA_COORD)
            return newX,newY

        def drawStation(self,qp,st):
            ident = st.id
            x,y = self.transformStationCoordsToPixel(st.x,st.y)

            # Primer, pintem les connexions (perque quedin a sota). Nomes les pintem un cop
            # Ara, les connexions
            for link in st.links:
                if link.id > st.id:
                    otherSt = self.trans.getStationByID(link.id)
                    oX,oY = self.transformStationCoordsToPixel(otherSt.x,otherSt.y)
                    #qp.setPen(self.parent.getLineColor(st.getCommonLine(otherSt)))
                    pen = QtGui.QPen(self.getLineColor(st.getCommonLine(otherSt)))
                    pen.setWidth(2)
                    qp.setPen(pen)
                    qp.drawLine(x,y,oX,oY)
                    qp.setPen(QtCore.Qt.black)
                    qp.drawText((x+oX)/2, (y+oY)/2, str(link.cost)) # dibuixem cost

            
            # dibuixem estacio: si esta marcada com seleccionada la pintem sencera de gris
            qp.setPen(QtCore.Qt.gray)
            qp.setBrush(QtCore.Qt.black)
            if st == self.parent.stOrigen: qp.setBrush(QtCore.Qt.lightGray)
            if st == self.parent.stDesti: qp.setBrush(QtCore.Qt.darkGray)
            qp.drawEllipse(x-(self.MIDA_EST/2), y-(self.MIDA_EST/2), self.MIDA_EST, self.MIDA_EST) 

            qp.setPen(QtCore.Qt.white) # dibuixem ID dintre de les rodones
            qp.drawText(x-(self.MIDA_EST/3), y+(self.MIDA_EST/3), str(ident)) 

        def drawCami(self,qp,cami):
            ant = cami[len(cami)-1].st
            for i in range(len(cami)-2,-1,-1):
                act = cami[i].st
                x,y = self.transformStationCoordsToPixel(act.x,act.y)
                oX,oY = self.transformStationCoordsToPixel(ant.x,ant.y)
                pen = QtGui.QPen(QtCore.Qt.gray)
                pen.setWidth(3)
                qp.setPen(pen)
                qp.drawLine(x,y,oX,oY)
                ant = act
           
        def drawGrid(self,qp):
            # Funció de pintar la graella, per provar i debugar
            qp.setPen(QtCore.Qt.black)
            w = self.size().width()
            h = self.size().height()
            i = 0
            while (i <= w):
                qp.drawLine(i,0,i,h)
                i += self.MIDA_COORD

            i = 0
            while (i <= h):
                qp.drawLine(0,i,w,i)
                i += self.MIDA_COORD

        def draw(self, qp):

            #self.drawGrid(qp) # Per proves

            font = QtGui.QFont()
            font.setPixelSize(int(self.MIDA_EST/1.5))
            font.setBold(True)
            qp.setFont(font)
            for st in self.trans.stations:
                self.drawStation(qp,st)

            try:
                cami = self.parent.cami
                if cami:
                    self.drawCami(qp,cami)
            except:
                print "MEC"
                pass # Nomes hi ha cami a transPublic, per aixo esperem excepcio (per viewer)

if __name__ == '__main__':
    print "Not an executable class"
    sys.exit()