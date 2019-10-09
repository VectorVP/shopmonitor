import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget, QDialog, QInputDialog
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
import multiprocessing
import numpy as np
from multiprocessing import Pipe
import os
import cv2
import time
from wind_form import *
import json
import requests
import datetime

#webhook_url = 'https://httpbin.org/post'            # URL сервера (указан тестовый сервер)

webhook_url = [0]

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

IGNORE = {"background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
          "diningtable", "dog", "horse", "motorbike", "pottedplant", "sheep", "sofa", "train", "tvmonitor"}

FINAL_LINE_COLOR = (148, 0, 211)
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt", "MobileNetSSD_deploy.caffemodel")

num_Procs = 0
Camera_address = []

Camera_name = []

#Отрисовка полигона
class PolygonDrawer:
    def __init__(self):
        self.done = False
        self.recog = False
        self.current = (0, 0)
        self.points = []
        self.h = 0
        self.w = 0
        self.poly_img = 0
        self.res = 0

    def showCurrent(self, x, y):
        self.current = (x, y)

    def startDrawing(self):
        self.points = []

    def appendPoints(self, x, y):
        self.points.append([x, y])

    def getPoints(self):
        return self.points

    def getCurrent(self):
        return self.current

    def finishAct(self):
        self.recog = True

    def startRecog(self):
        return self.recog

    def completeDrawing(self):
        self.done = True

    def saveParam(self, h, w, poly_img, res):
        self.h = h
        self.w = w
        self.poly_img = poly_img
        self.res = res

    def giveH(self):
        return self.h

    def giveW(self):
        return self.w

    def givePoly(self):
        return self.poly_img

    def giveRes(self):
        return self.res

    def reDraw(self):
        self.points = []
        self.done = False
        self.recog = False


def on_mouse(event, x, y, flags, param):
    def updRegion(region):
        if region.completeDrawing():
            return

        if event == cv2.EVENT_MOUSEMOVE:
            region.showCurrent(x, y)

        elif event == cv2.EVENT_LBUTTONDOWN:
            print(f"Adding point {len(region.getPoints())} with position({x},{y})")
            region.appendPoints(x, y)

        elif event == cv2.EVENT_RBUTTONDOWN:
            print(f"Completing polygon with {len(region.getPoints())} points.")
            region.completeDrawing()

        elif event == cv2.EVENT_RBUTTONUP:
            print("Starting recognition")
            region.finishAct()

    updRegion(sign)


sign = PolygonDrawer()

class communication_thread(QtCore.QThread):
    procsNum = pyqtSignal(list)
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.NUM = len(Camera_name)
        print(self.NUM)

        self.queue_List = [multiprocessing.Manager().Queue(1) for i in range(self.NUM)]

        self.capture_video_Procs = []

        self.grab_pipe_list = []
        self.procs_pipe_list = []

        self.setArea_list_p = []
        self.setArea_list_t = []

        print(num_Procs)
        print(Camera_address)
        print(Camera_name)
        for m in range(self.NUM):
            self.area_thread_side, self.area_process_side = multiprocessing.Pipe()
            self.grabSide, self.procsSide = multiprocessing.Pipe()
            self.grab_pipe_list.append(self.grabSide)
            self.procs_pipe_list.append(self.procsSide)
            self.setArea_list_t.append(self.area_thread_side)
            self.setArea_list_p.append(self.area_process_side)
            p = multiprocessing.Process(target=video_capture, args=(Camera_address[m], self.queue_List[m], self.grab_pipe_list[m], self.setArea_list_p[m]))
            print(m)
            p.start()
            self.capture_video_Procs.append(p)

        print("Communication thread activate!")

    def run(self):
        print("Main cycle start!")
        while True:
            for j in range(self.NUM):
                if not self.queue_List[j].empty():
                    count = self.queue_List[j].get()
                    qImg = [j, count]
                    self.procsNum.emit(qImg)
            communication_thread.msleep(15)

    def initiat_processing(self, edge_mas, time1_area):
        print("Processing init!")
        for n in range(len(Camera_address)):
            procs = multiprocessing.Process(target=video_processing, args=(self.procs_pipe_list[n], edge_mas[n], time1_area[n]))
            print(n)
            procs.start()
            self.capture_video_Procs.append(procs)

    def setAreainFrame(self, areaNumber):
        print("I am here! P.S: set area in frame method")
        print(areaNumber)
        self.setArea_list_t[areaNumber].send(1)

# Считывание изображений с камер и установка области сканирования
def video_capture(ID, q, ProcsPipe, setArea_F):
    print("Done with thread!")
    print(ID)
    print(os.getpid())
    cam = cv2.VideoCapture(ID)
    time.sleep(3)
    print(cam)
    data = 0
    ProcsFL = 0
    areaNumber = 0
    withPoly = 0
    while cam.isOpened():
        ret, image = cam.read()
        if ret == True:
            original = image
            if q.empty():
                if ProcsPipe.poll():
                    ProcsFL = 1
                    data = ProcsPipe.recv()
                    if sign.startRecog():
                        res = cv2.bitwise_and(original, original, mask=mask)
                        rect = cv2.boundingRect(p_arr_n)
                        poly_img = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
                        ProcsPipe.send(poly_img)
                    else:
                        ProcsPipe.send(image)
                    q.put([ProcsFL, data])
                else:
                    q.put([ProcsFL, data])
            # Обработка запроса на установку области скнирования
            if setArea_F.poll():
                withPoly = 0
                areaNumber = setArea_F.recv()
                print(areaNumber)
                cv2.namedWindow('')
                cv2.waitKey(1)
                cv2.setMouseCallback('', on_mouse)
                sign.reDraw()

            # Если запрос получен, открывается окно видеопотока выбранной камеры
            if areaNumber == 1:
                cv2.imshow('', original)
                p_arr = np.array(sign.getPoints())
                if len(p_arr) > 0:
                    cv2.polylines(original, np.array([p_arr]), True, FINAL_LINE_COLOR, 5)
                    cv2.imshow('', original)
                    h = original.shape[0]
                    w = original.shape[1]
                    mask = np.zeros((h, w), dtype=np.uint8)
                    p_arr_n = np.array([sign.getPoints()])
                    cv2.fillPoly(mask, p_arr_n, 255)
                    res = cv2.bitwise_and(original, original, mask=mask)
                    rect = cv2.boundingRect(p_arr_n)
                    poly_img = res[rect[1]: rect[1] + rect[3], rect[0]: rect[0] + rect[2]]
                if (cv2.waitKey(1) & 0xFF) == ord('q'):
                    areaNumber = 0
                    cv2.destroyWindow('')
            time.sleep(0.001)

# Детектирование людей
def video_processing(test, edge_mas, time1_mas):
    test.send("I am ready for processing!")
    g = 0
    n = 0
    while True:
        if test.poll():
            reciev_pack = test.recv()
            data = reciev_pack
            (h, w) = data.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(data, (300, 300)),
                                         0.007843, (300, 300), 127.5)
            net.setInput(blob)
            detections = net.forward()
            counter = 0
            cnt = 0
            n += 1
            for i in np.arange(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.2:
                    idx = int(detections[0, 0, i, 1])
                    if CLASSES[idx] in IGNORE:
                        continue
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                    counter = counter + 1
                    cv2.rectangle(data, (startX, startY), (endX, endY), COLORS[idx], 2)
                    y = startY - 15 if startY - 15 > 15 else startY + 15
                    cv2.putText(data, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
            # Для снижения нагрузки, обработка всех кадров производится примерно 3 раза в секунду
            if n == time1_mas:
                g = cnt
                n = 0
            else:
                print("count")
            print(n)

            if g > edge_mas:
                print("ОЧЕРЕДЬ ПЕРЕПОЛНЕНА")
            else:
                print("wait")
            print(edge_mas, "|", time1_mas)


            test.send(counter)
            time.sleep(0.5)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.pushButton_4.clicked.connect(self.setArea)
        self.ui.pushButton_3.clicked.connect(self.videoProcessing)
        #self.ui.pushButton_2.clicked.connect(self.processingStop)

        #self.dialog = Dialog(self)
        #self.ui.pushButton_5.clicked.connect(self.dialog.exec)
        self.ui.pushButton_5.clicked.connect(self.AddRow)
        self.ui.pushButton_6.clicked.connect(self.ServerSend)
        self.ui.pushButton_1.clicked.connect(self.videoCapture)
        #self.ui.pushButton_2.setDisabled(True)
        self.ui.pushButton_3.setDisabled(True)
        self.ui.pushButton_4.setDisabled(True)

        self.ui.pushButton_7.clicked.connect(self.AddQueue)
        self.ui.pushButton_8.clicked.connect(self.AddAdress)
        self.ui.pushButton_9.clicked.connect(self.Info)

        self.edge_mas = [0, 0, 0, 0, 0, 0, 0, 0]
        self.time1_mas = [0, 0, 0, 0, 0, 0, 0, 0]

        for c in range(num_Procs):
            self.ui.comboBox.addItem(Camera_name[c])
        multiprocessing.freeze_support()  # For .exe work
        print(os.getpid())

    def videoCapture(self):
        print("Video capture start...\n")
        print("What address do you set?\n")
        print(Camera_address)
        self.communication = communication_thread()
        self.communication.procsNum.connect(self.setProcs)
        self.communication.start()
        time.sleep(3)
        self.ui.pushButton_3.setDisabled(False)
        self.ui.pushButton_4.setDisabled(False)

    def processingStop(self):
        print("Stop video processing...")

    def videoProcessing(self):
        print("Video processing start...")
        self.communication.initiat_processing(self.edge_mas, self.time1_mas)


    def setArea(self):
        print("Area setup start...")
        areaNumber = self.ui.comboBox.currentIndex()
        self.ui.table_modules.item(areaNumber, 6).setBackground(QtGui.QColor(0, 255, 0))
        self.communication.setAreainFrame(areaNumber)

    def Info(self):
        print("Info")
        self.dialog = showInfo(self)
        self.dialog.exec_()

    def AddAdress(self):
        print("I am in AddAdress")
        self.dialog = adressAdd(self)
        self.dialog.exec_()
        name = self.dialog.edit.text()
        if (name != ""):
            webhook_url[0] = name
        print("OK")
        print(str(webhook_url[0]))


    def AddQueue(self):

        print("Queue setup start...")
        areaNumber = self.ui.comboBox.currentIndex()

        self.dialog = PeopleNumbers(self)
        self.dialog.exec_()

        edge = self.dialog.edit.text()
        time1 = self.dialog.edit1.text()

        if (edge != "") and (time1 != ""):
            #self.ui.table_modules.setRowCount(CNumber)
            self.ui.table_modules.setItem(areaNumber, 7, QtWidgets.QTableWidgetItem(edge))
            self.ui.table_modules.item(areaNumber, 7).setTextAlignment(QtCore.Qt.AlignCenter)

            self.ui.table_modules.setItem(areaNumber, 8, QtWidgets.QTableWidgetItem(time1))
            self.ui.table_modules.item(areaNumber, 8).setTextAlignment(QtCore.Qt.AlignCenter)

            self.edge_mas[areaNumber] = int(edge)
            self.time1_mas[areaNumber] = int(time1)

        print("OK")
        print(self.edge_mas)
        print(self.time1_mas)


    def AddRow(self):
        print("I am in AddRow")
        self.dialog = Dialog(self)
        self.dialog.exec_()
        n = len(Camera_address)
        number = n
        CNumber = n + 1

        name = self.dialog.edit.text()
        camera_Num = self.dialog.edit1.text()
        address = self.dialog.edit2.text()
        if (name != "") & (camera_Num != "") & (address != ""):
            self.ui.table_modules.setRowCount(CNumber)
            self.ui.table_modules.setItem(number, 0, QtWidgets.QTableWidgetItem(str(CNumber)))
            self.ui.table_modules.item(number, 0).setTextAlignment(QtCore.Qt.AlignCenter)

            self.ui.table_modules.setItem(number, 1, QtWidgets.QTableWidgetItem(name))
            self.ui.table_modules.item(number, 1).setTextAlignment(QtCore.Qt.AlignCenter)

            self.ui.table_modules.setItem(number, 2, QtWidgets.QTableWidgetItem(camera_Num))
            self.ui.table_modules.item(number, 2).setTextAlignment(QtCore.Qt.AlignCenter)

            self.ui.table_modules.setItem(number, 3, QtWidgets.QTableWidgetItem(""))
            self.ui.table_modules.item(number, 3).setBackground(QtGui.QColor(255, 0, 0))

            self.ui.table_modules.setItem(number, 4, QtWidgets.QTableWidgetItem(""))
            self.ui.table_modules.item(number, 4).setBackground(QtGui.QColor(255, 0, 0))

            self.ui.table_modules.setItem(number, 5, QtWidgets.QTableWidgetItem(""))
            self.ui.table_modules.item(number, 5).setTextAlignment(QtCore.Qt.AlignCenter)

            self.ui.table_modules.setItem(number, 6, QtWidgets.QTableWidgetItem(""))
            self.ui.table_modules.item(number, 6).setBackground(QtGui.QColor(255, 0, 0))

            self.ui.table_modules.setItem(number, 7, QtWidgets.QTableWidgetItem("0"))
            self.ui.table_modules.item(number, 7).setTextAlignment(QtCore.Qt.AlignCenter)


            Camera_address.append(address)
            Camera_name.append(name)
            self.ui.comboBox.addItem(Camera_name[number])
            print("OK")

#---

    def ServerSend(self):
        current_time = str(datetime.datetime.now())[:19]    # текущие дата и время с точностью до секунд
        print(self.ui.table_modules.item(0, 0).text())
        for n in range(len(Camera_address)):
            fetch = "OK"
            if self.ui.table_modules.item(n, 5).text() > self.ui.table_modules.item(n, 7).text():
                fetch = "FULL"
            test_report = form_report(  # тестовый отчет
                self.ui.table_modules.item(n, 1).text(),
                self.ui.table_modules.item(n, 2).text(),
                current_time,
                'line',
                num_of_people=self.ui.table_modules.item(n, 5).text(),  # произвольные поля
                line_length=fetch  # произвольные поля
            )
            print(test_report)
            print(str(webhook_url[0]))
            res = send_report(str(webhook_url[0]), test_report)  # отправка отчета на сервер
            # ДЛЯ ОТЛАДКИ - ответ от тестового сервера
            #jres = res.text
            #print(jres)
            print(current_time)
#---

    @pyqtSlot(list)
    def setProcs(self, process_num):
        for k in range(len(Camera_address)):
            if process_num[0] == k:
                self.ui.table_modules.item(k, 5).setText(str(process_num[1][1]))
                self.ui.table_modules.item(k, 3).setBackground(QtGui.QColor(0, 255, 0))
                if process_num[1][0] == 1:
                    self.ui.table_modules.item(k, 4).setBackground(QtGui.QColor(0, 255, 0))


def form_report(location, camera_name, time, event_type, **kwargs):
    # функция формирует отчет в формате JSON с полями:
    # название локации, имя камеры,
    # времени регистрации события,
    # типа события,
    # также могут быть добавлены произвольные поля и значения с помощью аргумента kwargs

    report = {
        'location': location,
        'camera_name': camera_name,
        'time': time,
        #'event_type': event_type
    }
    for key in kwargs:
        report[key] = kwargs[key]
    return json.dumps(report)

def send_report(url, report):
    response = requests.post(
        url, data=report, json=report,
        headers={'Content-Type': 'application/json'}
    )
    return response


class Dialog(QtWidgets.QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        #self.mainWindow = root
        self.resize(150, 180)
        self.setWindowTitle("Add camera")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('Введите данные о камере:')
        label.setFont(QtGui.QFont('Times', 12))
        label1 = QtWidgets.QLabel('Название области расположения:')
        label1.setFont(QtGui.QFont('Times', 11))

        label2 = QtWidgets.QLabel('Номер камеры:')
        label2.setFont(QtGui.QFont('Times', 11))
        label3 = QtWidgets.QLabel('Адрес камеры:\n'
                                  'Форма записи: "rtsp://LOGIN:PASSWORD@IP:PORT"')
        label3.setFont(QtGui.QFont('Times', 11))

        self.edit = QtWidgets.QLineEdit()
        self.edit1 = QtWidgets.QLineEdit()
        self.edit2 = QtWidgets.QLineEdit()

        button = QtWidgets.QPushButton('Добавить камеру')
        button.clicked.connect(self.push)

        layout.addWidget(label)
        layout.addWidget(label1)
        layout.addWidget(self.edit)
        layout.addWidget(label2)
        layout.addWidget(self.edit1)
        layout.addWidget(label3)
        layout.addWidget(self.edit2)
        layout.addWidget(button)
        self.setLayout(layout)


    def push(self):
        self.close()

class showInfo(QtWidgets.QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        #self.mainWindow = root
        self.resize(600, 300)
        self.setWindowTitle("О программе")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Порядок работы:\n"
                                  "\n"
                            "1) Сперва добавляется камера (её местоположение, номер и адрес).\n"
                                 "\n"
                            "2) Далее производится включение камер.\n"
                                 "\n"
                            "3) После этого можно установить область или сразу же начать подсчёт людей.\n"
                                 "- выбор камеры производится из выпадающего списка;\n"
                                 "- после выбора области производится запуск процесса распознавания - ПКМ; \n"
                                 "- для выхода из режима выбора области необходимо нажать клавишу 'q' на английской раскладке.\n"
                                  "\n"
                            "4) Далее устанавливаются параметры: максимально допустимое число людей в очереди и время задержки вывода количества покупателей.\n"
                                  "\n"
                            "5) Задаётся адрес принимающего сервера.\n"
                                  "\n"
                            "6) Передача данных о потоках на указанный ранее сервер.\n"
                                 "\n"
                            " В посылке указывается местоположение камеры, её номер, текущее время, количество человек в очереди и флаг переполнения очереди:\n"
                            "      - OK - переполнения нет,\n"
                            "      - FULL - очередь переполнена.\n"
                                  "\n"
                                 "Замечания:\n"
                                 "      - если кнопка 'Установить параметры' была нажата, то ввести значения необходимо,\n"
                                 "      - значения устанавливаются для потока, который выбран из выпадающего меню.\n"
                                 )

        label2 = QtWidgets.QLabel("Система контроля торговых помещений\n"
                                  )
        label.setFont(QtGui.QFont('Times', 12))
        label2.setFont(QtGui.QFont('Times', 9))

        self.edit = QtWidgets.QLineEdit()

        layout.addWidget(label)
        layout.addWidget(label2)
        #layout.addWidget(self.edit)

        self.setLayout(layout)

class adressAdd(QtWidgets.QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        #self.mainWindow = root
        self.resize(150, 100)
        self.setWindowTitle("Адрес")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('Укажите адрес сервера')
        label.setFont(QtGui.QFont('Times', 12))

        self.edit = QtWidgets.QLineEdit()

        button = QtWidgets.QPushButton('ОК')
        button.clicked.connect(self.push2)

        layout.addWidget(label)
        layout.addWidget(self.edit)

        layout.addWidget(button)
        self.setLayout(layout)

    def push2(self):
        self.close()

class PeopleNumbers(QtWidgets.QDialog):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        #self.mainWindow = root
        self.resize(150, 180)
        self.setWindowTitle("Ограничения")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('Укажите данные срабатывания.')
        label.setFont(QtGui.QFont('Times', 11))
        label11 = QtWidgets.QLabel('Порог срабатывания:')
        label11.setFont(QtGui.QFont('Times', 11))

        label22 = QtWidgets.QLabel('Время фиксации:')
        label22.setFont(QtGui.QFont('Times', 11))

        self.edit = QtWidgets.QLineEdit()
        self.edit1 = QtWidgets.QLineEdit()

        button = QtWidgets.QPushButton('Установить')
        #button.clicked.connect(self.push3)

        layout.addWidget(label)
        layout.addWidget(label11)
        layout.addWidget(self.edit)
        layout.addWidget(label22)
        layout.addWidget(self.edit1)
        layout.addWidget(button)
        self.setLayout(layout)

    def push3(self):
        self.close()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


