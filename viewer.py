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

        # Connexions d'events
        self.connect(self.ui.viewerListStations, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.listStationsChanged)

        self.stSelected = None

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
            text = str(st.id)+" "+st.name
            if st.cost > 0:
                text += " (Cost: "+str(st.cost)+")"
            l.addItem(text)

    def listStationsChanged(self,newItem,oldItem):
        if oldItem and newItem: # aixi evitem que s'activi només entrar
            text = str(newItem.text())
            ident = int(text.split(" ")[0]) # Separem per espais i agafem la ID
            self.stSelected = self.trans.getStationByID(ident) # marquem l'estació com seleccionada
            self.mF.repaint() # repintem

    def selectStationByCoords(self,x,y):
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
                    self.stSelected = st # marquem l'estació com seleccionada
                    self.mF.repaint() # repintem
                    break

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

            # Connexions
            self.mousePressEvent = self.pixelSelect

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
            self.vXMid = ((width/2)-(xMid*self.MIDA_COORD)) + self.MIDA_COORD/2 # Meitat virtual en amplada
            self.vYMid = ((height/2)+(yMid*self.MIDA_COORD)) - self.MIDA_COORD/2 # Meitat virtual en altura

            print "mids",self.vXMid,self.vYMid

            self.setMinimumSize(width,height)
            self.setMaximumSize(width,height)
            #self.setWindowTitle('Mapa')

        def pixelSelect(self,event):
            x = event.pos().x()
            y = event.pos().y()
            print x,y
            # TRANSFORMAR
            newX, newY = self.transformPixelToStationCoords(x,y)
            print newX,newY
            self.parent.selectStationByCoords(newX,newY)

        def paintEvent(self, e):
            qp = QtGui.QPainter()
            qp.begin(self)

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
                    pen = QtGui.QPen(self.parent.getLineColor(st.getCommonLine(otherSt)))
                    pen.setWidth(2)
                    qp.setPen(pen)
                    qp.drawLine(x,y,oX,oY)
                    qp.setPen(QtCore.Qt.black)
                    qp.drawText((x+oX)/2, (y+oY)/2, str(link.cost)) # dibuixem cost

            
            # dibuixem estacio: si esta marcada com seleccionada la pintem sencera de gris
            qp.setPen(QtCore.Qt.gray)
            qp.setBrush(QtCore.Qt.black)
            if st == self.parent.stSelected: qp.setBrush(QtCore.Qt.gray)
            qp.drawEllipse(x-(self.MIDA_EST/2), y-(self.MIDA_EST/2), self.MIDA_EST, self.MIDA_EST) 

            qp.setPen(QtCore.Qt.white) # dibuixem ID dintre de les rodones
            qp.drawText(x-(self.MIDA_EST/3), y+(self.MIDA_EST/3), str(ident)) 
           
        def drawGrid(self,qp):
            # Funció de pintar la graella, per provar i debugar
            qp.setPen(QtCore.Qt.black)
            w = self.size().width()
            h = self.size().height()
            print "size",w,h
            i = 0
            while (i <= w):
                qp.drawLine(0,i,h,i)
                i += self.MIDA_COORD

            i = 0
            while (i <= h):
                qp.drawLine(i,0,i,w)
                i += self.MIDA_COORD

        def draw(self, qp):

            #self.drawGrid(qp) # Per proves

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