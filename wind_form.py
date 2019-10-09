from PyQt5 import QtCore, QtWidgets, QtGui
from PyQtWithoutVideo import *

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(Form)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")


        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(535, 225, 170, 23))
        self.comboBox.setObjectName("comboBox")

        self.header_1 = QtWidgets.QLabel(Form)
        self.header_1.setGeometry(QtCore.QRect(530, 20, 240, 35))
        self.header_1.setFont(QtGui.QFont('Times', 10))
        self.header_1.setObjectName("header_1")

        self.header_2 = QtWidgets.QLabel(Form)
        self.header_2.setGeometry(QtCore.QRect(530, 90, 250, 60))
        self.header_2.setFont(QtGui.QFont('Times', 10))
        self.header_2.setObjectName("header_2")

        self.header_3 = QtWidgets.QLabel(Form)
        self.header_3.setGeometry(QtCore.QRect(530, 160, 250, 60))
        self.header_3.setFont(QtGui.QFont('Times', 10))
        self.header_3.setObjectName("header_3")

        self.header_4 = QtWidgets.QLabel(Form)
        self.header_4.setGeometry(QtCore.QRect(530, 275, 250, 60))
        self.header_4.setFont(QtGui.QFont('Times', 10))
        self.header_4.setObjectName("header_4")

        self.header_5 = QtWidgets.QLabel(Form)
        self.header_5.setGeometry(QtCore.QRect(535, 200, 240, 20))
        self.header_5.setFont(QtGui.QFont('Times', 10))
        self.header_5.setObjectName("header_5")

        self.header_6 = QtWidgets.QLabel(Form)
        self.header_6.setGeometry(QtCore.QRect(530, 325, 250, 60))
        self.header_6.setFont(QtGui.QFont('Times', 10))
        self.header_6.setObjectName("header_6")

        # 6. Адрес сервера
        self.header_7 = QtWidgets.QLabel(Form)
        self.header_7.setGeometry(QtCore.QRect(530, 380, 250, 60))
        self.header_7.setFont(QtGui.QFont('Times', 10))
        self.header_7.setObjectName("header_7")

        # 7. Передача данных на сервер
        self.header_8 = QtWidgets.QLabel(Form)
        self.header_8.setGeometry(QtCore.QRect(530, 450, 250, 60))
        self.header_8.setFont(QtGui.QFont('Times', 10))
        self.header_8.setObjectName("header_8")

        # Собственность
        self.header_9 = QtWidgets.QLabel(Form)
        self.header_9.setGeometry(QtCore.QRect(19, 553, 250, 60))
        self.header_9.setFont(QtGui.QFont('Times', 8))
        self.header_9.setObjectName("header_9")


        self.pushButton_1 = QtWidgets.QPushButton(Form)
        self.pushButton_1.setGeometry(QtCore.QRect(530, 150, 170, 23))
        self.pushButton_1.setObjectName("pushButton")

        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(535, 310, 170, 23))
        self.pushButton_3.setObjectName("pushButton_3")

        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(535, 255, 170, 23))
        self.pushButton_4.setObjectName("pushButton_4")

        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setGeometry(QtCore.QRect(535, 60, 170, 23))
        self.pushButton_5.setObjectName("pushButton_5")

        self.pushButton_6 = QtWidgets.QPushButton(Form)
        self.pushButton_6.setGeometry(QtCore.QRect(535, 500, 170, 23))
        self.pushButton_6.setObjectName("pushButton_6")

        self.pushButton_7 = QtWidgets.QPushButton(Form)
        self.pushButton_7.setGeometry(QtCore.QRect(535, 370, 170, 23))
        self.pushButton_7.setObjectName("pushButton_7")

        # Адрес сервера
        self.pushButton_8 = QtWidgets.QPushButton(Form)
        self.pushButton_8.setGeometry(QtCore.QRect(535, 430, 170, 23))
        self.pushButton_8.setObjectName("pushButton_8")

        self.pushButton_9 = QtWidgets.QPushButton(Form)
        self.pushButton_9.setGeometry(QtCore.QRect(535, 550, 170, 23))
        self.pushButton_9.setObjectName("pushButton_9")


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.table_modules = QtWidgets.QTableWidget(Form)
        #self.table_modules.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        #self.table_modules.setCornerButtonEnabled(True)
        #self.table_modules.setRowCount(6)
        self.table_modules.setColumnCount(9)




        #self.table_modules.horizontalHeader().setStretchLastSection(True)
        self.table_modules.setHorizontalHeaderLabels(['№', 'Местоположение\nкамеры', 'Номер\nкамеры', 'Состояние\nподключения', 'Состояние\nсканирования', 'Кол-во\nлюдей', 'Зона\nдетекции', 'Порог\nсрабатывания', 'Время\nфиксации'])

        self.table_modules.setObjectName("table_modules")

        self.table_modules.resizeColumnsToContents()

        #self.table_modules.horizontalHeader().setSortIndicatorShown(False)
        self.table_modules.horizontalHeader().setStretchLastSection(True)
        self.table_modules.verticalHeader().setVisible(False)
        self.table_modules.setGeometry(QtCore.QRect(20, 20, 493, 550))
        #self.verticalLayout.addWidget(self.table_modules)

        item1 = QtWidgets.QTableWidgetItem('red')
        item1.setBackground(QtGui.QColor(255, 0, 0))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)



    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "People detection system"))
        self.header_1.setText(_translate("MainWindow", "1. Добавьте новое устройство\n    (при необходимости)"))
        self.header_2.setText(_translate("MainWindow", "2. Подключитесь к камерам и\n"
                                                       "дождитесь пока индикатор состояний\nподключения не станет зеленым"))
        self.header_3.setText(_translate("MainWindow", "3. Установите область сканирования"))
        self.header_4.setText(_translate("MainWindow", "4. Начните подсчёт людей\n"))
        self.header_5.setText(_translate("MainWindow", "Выберите камеру:"))
        self.header_6.setText(_translate("MainWindow", "5. Установите параметры срабатывания:"))
        self.header_7.setText(_translate("MainWindow", "6. Адрес сервера:"))
        self.header_8.setText(_translate("MainWindow", "7. Передача данных на сервер:"))
        self.header_9.setText(_translate("MainWindow", "Место для подписи"))



        self.pushButton_1.setText(_translate("Form", "Включить камеры"))
        self.pushButton_3.setText(_translate("Form", "Подсчёт людей"))
        self.pushButton_4.setText(_translate("Form", "Установить область"))
        self.pushButton_5.setText(_translate("Form", "Добавить камеру"))
        self.pushButton_6.setText(_translate("Form", "Отправка на сервер"))
        self.pushButton_7.setText(_translate("Form", "Установить параметры"))
        self.pushButton_8.setText(_translate("Form", "Задать адрес"))
        self.pushButton_9.setText(_translate("Form", "О программе"))