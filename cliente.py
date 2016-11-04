import sys
from PyQt4 import QtGui, QtCore, uic
import xmlrpclib

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.id_us = 0
        self.direcc = 1
        self.us_nuevo = False
        self.con = False
        self.inter = 0
        self.server = None
        self.carga_cliente()
        self.inicia_tim()
        self.show()

    def carga_cliente(self):
        uic.loadUi('cliente.ui', self)
        self.cambia_tam()
        self.pushButton.clicked.connect(self.maneja_serv)
        self.pushButton_2.clicked.connect(self.juega)
        self.pushButton_2.clicked.connect(self.otra)

        self.tableWidget.setSelectionMode(QtGui.QTableWidget.NoSelection)

    def inicia_tim(self):
        self.timer= QtCore.QTimer(self)
        self.timer.timeout.connect(self.ajustar_tab)
        self.timer.timeout.connect(self.inicia_juego)
        self.timer.timeout.connect(self.atualiza_timer)
        self.timer.start(self.inter)
        
    def ajustar_tab(self):
        if self.us_nuevo:
            game = self.server.estado_del_juego()
            self.tableWidget.setRowCount(game["tamY"])
            self.tableWidget.setColumnCount(game["tamX"])
            self.llena_tab()

    def llena_tab(self):
        for i in range(self.tableWidget.rowCount()):
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i,j, QtGui.QtableWidgetItem())
                self.tableWidget.item(i,j).setBackground(QtGui.QColor(255, 255, 255))

    def inicia_juego(self):
        if self.us_nuevo:
            if self.murio():
                self.lineEdit.setText("ya no juegas")
            self.llena_tab()

            self.tableWidget.installEventFilter(self)
            
            diccionario = self.server.estado_del_juego()
            lista_viboras = diccionario["viboras"]
            for vibora in lista_viboras:
                lista_camino = vibora["camino"]
                colores = vibora["color"]
                self.dibuja_vibora(lista_camino, colores)
    
    def atualiza_timer(self):
        if self.us_nuevo:
            diccionario = self.server.estado_del_juego()
            intervalo = diccionario["espera"]
            if self.inter != intervalo:
                self.inter = intervalo
                self.timer.setInterval(self.inter)

    def dibuja_vibora(self, lista_camino, colores):
        for tupla in lista_camino:
            self.tableWidget.item(tupla[0], tupla[1]).setBackground(QtGui.QColor(colores['r'], colores['g'], colores['b']))

    def maneja_serv(self):
        try:
            self.crea_serv()
            pong = self.server.ping()
            self.pushButton.setText("Pong")
        except:
            self.pushButton.setText("No PONG")

    def crea_serv(self):
        self.url = self.lineEdit_3.text()
        self.port = self.spinBox.value() 
        self.direcc = xmlrpclib.ServerProxy("http://" + self.url + ":" + str(self.port))
        self.server = ServerProxy(self.direcc)
 
    def juega(self):
        try:
            self.crea_serv()
            informacion = self.server.yo_juego()
            self.lineEdit.setText(informacion["id_us"])
            self.id_us = informacion["id_us"]
            self.color = informacion["color"]
            self.red = self.color["r"]
            self.green = self.color["g"]
            self.blue = self.color["b"]
            self.us_nuevo = True
        except:
            self.lineEdit.setText("Conexion mal")


    def murio(self):
        diccionario = self.server.estado_del_juego()
        lista_serpientes = diccionario["viboras"]
        for vibora in lista_serpientes:
            if vibora["id_us"] == self.id_us:
                return False
        self.con = True
        return True

    def otra(self):
        if self.con: 
            self.con = False
            self.lineEdit.setText('')
            self.lineEdit.setText('')
            self.juega()
            self.timer.start()
            self.inicia_juego()


    def cambia_tam(self):
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tableWidget): 
                key = event.key() 
                if (key == QtCore.Qt.Key_Up and
                    source is self.tableWidget):
                    if self.direcc != 2:
                        self.direcc = 0
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tableWidget):
                    if self.direcc != 0:
                        self.direcc = 2
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tableWidget):
                    if self.direcc != 3:
                        self.direcc = 1
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tableWidget):
                    if self.direcc != 1:
                        self.direcc = 3
                self.server.cambia_direcc(self.id_us, self.direcc)
        return QtGui.QMainWindow.eventFilter(self, source, event)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    
    sys.exit(app.exec_())
