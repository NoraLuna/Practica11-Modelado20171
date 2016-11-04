#importamos las clases a usar
import sys
from uuid import uuid4
from random import randint

from PyQt4 import QtGui, QtCore, uic

from SimpleXMLRPCServer import SimpleXMLRPCServer

#creamos la clase 
class MainWindow(QtGui.QMainWindow):

    #constructor
    def __init__(self):
        super(MainWindow, self).__init__()
        #iniciamos la interfaz
        self.empieza_interfaz()
        #variables que usaremos
        self.j_iniciado = False
        self.j_pausa = False
        self.timer = None
        self.tim = None
        self.tim_cam = None
        self.serp_en_jugada = []

    def empieza_interfaz(self):
        uic.loadUi('servidor.ui', self)
        self.pushButton_3.hide()
        self.cambiar_tabla()
        self.inicia_tab()
        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection)        
        self.spinBox_2.valueChanged.connect(self.nueva_tab)
        self.spinBox_3.valueChanged.connect(self.nueva_tab)
        self.spinBox.valueChanged.connect(self.nuevo_timer)
        self.time.valueChanged.connect(self.nuevo_timeout)
        self.pushButton_2.clicked.connect(self.inicia_juego)
        self.pushButton_3.clicked.connect(self.terminar_juego)
        self.pushButton.clicked.connect(self.inicia_servidor)
        
        self.show()

    def haz(self):
        self.servidor.handle_request()
    
    def nuevo_camino(self):
        for serpiente in self.serp_en_jugada:
            serpiente.camino = []
            for casilla in serpiente.casillas:
                serpiente.camino.append((casilla[0], casilla[1]))

    def inicia_servidor(self):       
        puerto = self.spinBox_4.value()
        direccion = self.lineEdit.text()
        self.servidor = SimpleXMLRPCServer((direccion, 0))
        puerto = self.servidor.server_address[1] 
        self.spinBox_4.setValue(puerto)
        self.spinBox_4.setReadOnly(True)
        self.lineEdit.setReadOnly(True)
        self.pushButton.setEnabled(False)
        self.servidor.register_function(self.ping)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.timeout = 0
        self.tim = QtCore.QTimer(self)
        self.tim.timeout.connect(self.haz)
        self.tim.start(self.servidor.timeout)


    def lista(self):
        return [s.dame_dicc() for s in self.serp_en_jugada]


    def ping(self):
        return "Pong"

    def yo_juego(self):       
        serpiente_nueva = self.nueva_serpiente()
        return {
            "id": serpiente_nueva.id,
            "color": serpiente_nueva.color
        }


    def cambia_direccion(self, identificador, numero):
        for s in self.serp_en_jugada:
            if s.id == identificador:
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True


    def estado_del_juego(self):
        diccionario = dict()
        diccionario = {
            'espera': self.spinBox.value(), 
            'tamX': self.tableWidget.columnCount(),
            'tamY': self.tableWidget.rowCount(),
            'viboras': self.lista_viboras() 
        }
        return diccionario


    def nueva_serpiente(self):      
        serpiente = Serpiente()
        creada = False
        while not creada:
            creada = True
            uno = randint(1, self.tableWidget.rowCount()/2)
            dos = uno + 1
            tres = dos +1 
            ancho = randint(1, self.tableWidget.columnCount()-1)
            achecar_1, achecar_2, achecar_3 = [uno, ancho], [dos, ancho], [tres, ancho], 
            for s in self.serp_en_jugada:
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 in s.casillas:
                    creada = False
                    break
            serpiente.casillas = [achecar_1, achecar_2, achecar_3]
            self.serp_en_jugada.append(serpiente)
            return serpiente


    def nuevo_timeout(self):       
        self.servidor.timeout = self.time.value()
        self.tim.setInterval(self.time.value())

        
    def inicia_juego(self):
        if not self.j_iniciado:
            self.pushButton_3.show()
            self.nueva_serpiente()
            self.timer = QtCore.QTimer(self)
            self.pushButton_2.setText("Pausa")
            self.dibuja_serp()
            self.timer.timeout.connect(self.mover_serpientes)
            self.timer.start(200)
            self.tableWidget.installEventFilter(self) 
            self.j_iniciado = True
            self.tim_cam = QtCore.QTimer(self)
            self.tim_cam.timeout.connect(self.nuevo_camino)
            self.tim_cam.start(100)
            
        elif self.j_iniciado and not self.j_pausa:
            self.timer.stop()
            self.j_pausa = True 
            self.pushButton_2.setText("Continuar")

        elif self.j_pausa:
            self.timer.start()
            self.j_pausa = False
            self.pushButton_2.setText("Pausa")

    def terminar_juego(self):    
        self.timer.stop()        
        self.serp_en_jugada = []
        self.j_iniciado = False
        self.pushButton_3.hide()
        self.pushButton_2.setText("Inicia Juego")
        self.inicia_tab()

    def cambiar_tabla(self):
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def nuevo_timer(self):
        self.timer.setInterval(self.spinBox.value())

    def dibuja_serp(self):
        for serpiente in self.serp_en_jugada:
            for seccion_corporal in serpiente.casillas:
                self.tableWidget.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))

    def choco_con_ella(self, serpiente):
        for seccion_corporal in serpiente.casillas[0:len(serpiente.casillas)-2]:
            if serpiente.casillas[-1][0] == seccion_corporal[0] and serpiente.casillas[-1][1] == seccion_corporal[1]:
                self.label_7.setText("Mal") 
                self.label_7.setStyleSheet("QLabel { color : #ff0000; }")
                QtCore.QTimer.singleShot(2000, lambda: self.label_7.setText(''))
                return True
        return False

    def choco_con_otra(self, serpiente_a_checar):
        for serpiente in self.serp_en_jugada:
            if serpiente.id != serpiente_a_checar.id:
                for seccion_corporal in serpiente.casillas[:]: 
                    if serpiente_a_checar.casillas[-1][0] == seccion_corporal[0] and serpiente_a_checar.casillas[-1][1] == seccion_corporal[1]:
                        self.label_7.setText("Mal")
                        self.label_7.setStyleSheet("QLabel { color : #ff0000; }")
                        QtCore.QTimer.singleShot(2000, lambda: self.label_7.setText(''))
                        self.serp_en_jugada.remove(serpiente_a_checar)
                        
    def mover_serpientes(self):       
        for serpiente in self.serp_en_jugada:
            if self.choco_con_ella(serpiente) or self.choco_con_otra(serpiente):
                self.serp_en_jugada.remove(serpiente)
                self.inicia_tab()               
                serpiente_1 = self.nueva_serpiente()
                self.serp_en_jugada = [serpiente_1]
                
            self.tableWidget.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(255, 255, 255))
            x = 0            
            for t in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                t[0] = serpiente.casillas[x][0]
                t[1] = serpiente.casillas[x][1]
 
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.tableWidget.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.tableWidget.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.tableWidget.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.tableWidget.columnCount()-1

        self.dibuja_serp()
        
    def inicia_tab(self):       
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QTableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(255, 255, 255))

    def nueva_tab(self):       
        self.tableWidget.setRowCount(self.spinBox_3.value())
        self.tableWidget.setColumnCount(self.spinBox_2.value())
        self.inicia_tab()

    def eventFilter(self, source, event):      
        if event.type() == QtCore.QEvent.KeyPress and source is self.tableWidget:
                key = event.key()

                if key == QtCore.Qt.Key_Up and source is self.tableWidget:
                    for serpiente in self.serp_en_jugada:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif key == QtCore.Qt.Key_Down and source is self.tableWidget:
                    for serpiente in self.serp_en_jugada:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif key == QtCore.Qt.Key_Right and source is self.tableWidget:
                    for serpiente in self.serp_en_jugada:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif key == QtCore.Qt.Key_Left and source is self.tableWidget:
                    for serpiente in self.serp_en_jugada:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
                            
        return QtGui.QMainWindow.eventFilter(self, source, event)


#creamos la clase serpiente
class Serpiente:

    def __init__(self, ):
        self.id = str(uuid4())[:7]
        self.camino = []
        self.tam = 0
        self.casillas = []
        self.direccion = "Abajo"
        self.color = {'r': randint(0, 255), 'g': randint(0, 255), 'b': randint(0, 255)}
        
    #regresamos el diccionario
    def dame_dicc(self):
        return {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec_())
