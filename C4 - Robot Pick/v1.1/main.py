#Libraries
from concurrent.futures import thread
import sys
import os
import goto
import pyodbc as odbc
import pandas as pd
import time
import cv2
import argparse
import numpy as np
import imutils
from imutils import perspective
from imutils import contours
from scipy.spatial import distance as dist
import pickle
import math
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from ui_main import Ui_MainWindow
from pyzbar.pyzbar import decode

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):

        self.cam_class()

        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.par_read()
        self.live = False

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(100)

        """-------------------PAGE BUTTONS-------------------"""
        
        self.ui.btn_main.clicked.connect(self.btn_main)
        self.ui.btn_variant.clicked.connect(self.btn_variant)
        self.ui.btn_cali.clicked.connect(self.btn_cali)
        self.ui.btn_live.clicked.connect(self.btn_live)
        self.ui.btn_export.clicked.connect(self.btn_export)
        self.ui.btn_exit.clicked.connect(self.btn_page_exit)

        """-------------------VARIANT PAGE BUTTONS--------------"""
        
        self.ui.btn_find.clicked.connect(self.btn_find)
        self.ui.btn_pick.clicked.connect(self.btn_pick)
        

        """-------------------BARCODE PAGE BUTTONS--------------"""
        
        self.ui.btn_snap.clicked.connect(self.bar_snap)
        

        """--------------CALIBRATION PAGE BUTTONS----------------"""

        self.ui.btn_test.clicked.connect(self.calib_test)
        self.ui.btn_calib.clicked.connect(self.calib_cam)
        self.ui.btn_reset.clicked.connect(self.calib_reset)

        """-------------------LIVE PAGE BUTTONS-------------------"""

        self.ui.btn_start_live.clicked.connect(self.live_start)
        self.ui.btn_stop_live.clicked.connect(self.live_stop)
        
    def update(self):
        if self.live:
            imageq = self.img
            imageq = cv2.flip(imageq, 1)
            imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
            if self.ui.box_redline.isChecked() == True:
                a = imageq.shape
                (tl, tr, br, bl) = ((0,0),(0,a[0]),(a[1],a[0]),(a[1],0))
                (tltrX, tltrY) = self.midpoint(tl, tr)
                (blbrX, blbrY) = self.midpoint(bl, br)
                (tlblX, tlblY) = self.midpoint(tl, bl)
                (trbrX, trbrY) = self.midpoint(tr, br)
                cv2.line(imageq, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),(255, 0, 0), 1)
                cv2.line(imageq, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),(255, 0, 0), 1)
                imageq = QImage(imageq.data, imageq.shape[1], imageq.shape[0], QImage.Format_RGB888)
                self.ui.img_live.setPixmap(QPixmap.fromImage(imageq))
            else:
                imageq = QImage(imageq.data, imageq.shape[1], imageq.shape[0], QImage.Format_RGB888)
                self.ui.img_live.setPixmap(QPixmap.fromImage(imageq))
                
    def btn_main(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_main)
        except Exception as e:
            print(e)
        
    def btn_variant(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_var)
        except Exception as e:
            print(e)
        
    def btn_barc(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_barcode)

        except Exception as e:
            print(e)

    def btn_cali(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_cali)
            a = ("%.2f" % round(self.parameter[0], 2))
            a1 = ("%.2f" % round((1/self.parameter[0]), 2))

            self.ui.val_pixpermm.setText(str(a)+(" pix/mm"))
            self.ui.val_mmperpix.setText(str(a1)+(" mm/pix"))

        except Exception as e:
            print(e)
        
    def btn_live(self):
        try:
            self.live_stop()
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_live)
        except Exception as e:
            print(e)
        
    def btn_export(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_export)
        except Exception as e:
            print(e)
        
    def btn_page_exit(self):
        try:
            print('EXITING...')
            time.sleep(1)
            self.Worker1.stop()
            sys.exit()
        except Exception as e:
            print(e)
        
    def cam_class(self):
        self.Worker1 = Worker1()
        self.Worker1.start()
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        
    def ImageUpdateSlot(self, Image):
        Image = Image.convertToFormat(4)
        width = Image.width()
        height = Image.height()
        ptr = Image.bits()
        ptr.setsize(Image.byteCount())
        self.img = np.array(ptr).reshape(height, width, 4)

    def midpoint(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def live_start(self):
        self.live = True
        #self.add_par()
        
    def live_stop(self):
        self.live = False
        #self.remove_par()
        
    def par_read(self):
        pickle_in = open("parameter.dat","rb")
        self.parameter = pickle.load(pickle_in)
        print("Param-",self.parameter)
        self.pixpermm = self.parameter[0]

    def par_write(self,a):
        self.parameter = a
        print(self.parameter)
        pickle_out = open("parameter.dat","wb")
        pickle.dump(self.parameter, pickle_out)
        pickle_out.close()

    def add_par(self):
        print("add par")
        pickle_in = open("parameter.dat","rb")
        self.parameter = pickle.load(pickle_in)
        print('Before-',self.parameter)
        self.parameter.append(0)
        print('After-',self.parameter)
        pickle_out = open("parameter.dat","wb")
        pickle.dump(self.parameter, pickle_out)
        pickle_out.close()

    def remove_par(self):
        pickle_in = open("parameter.dat","rb")
        self.parameter = pickle.load(pickle_in)
        l = len(self.parameter)
        print('Before-',self.parameter)
        self.parameter.pop(l-1)
        print('After-',self.parameter)
        pickle_out = open("parameter.dat","wb")
        pickle.dump(self.parameter, pickle_out)
        pickle_out.close()

    def calib_reset(self):
        self.ui.calib_error.clear()
    
    def calib_cam(self):
        try: 
            imageq = self.img
            imageq = cv2.flip(imageq, 1)
            imageq2 = imageq
            imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(imageq, cv2.COLOR_BGR2GRAY)  	    
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            edged = cv2.Canny(gray, 50, 100)   
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            cnts = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            (cnts, _) = contours.sort_contours(cnts)
            number = 0
            for c in cnts:
                if cv2.contourArea(c) < 1500:
                    continue
                number = number +1
            if number == 1:
                self.ui.calib_error.setText("Calibrating....")
                a = [0,0,0,0]
                for c in cnts:
                    if cv2.contourArea(c) < 1500:
                        continue
                    box = cv2.minAreaRect(c)
                    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                    box = np.array(box, dtype="int")
                    box = perspective.order_points(box)
                    a[0] = math.dist(box[0],box[1])
                    a[1] = math.dist(box[1],box[2])
                    a[2] = math.dist(box[2],box[3])
                    a[3] = math.dist(box[3],box[0])
                    a.sort()
                    if (a[len(a)-1]-a[0]) <=2:
                        dim =self.ui.calib_meas.text()
                        if dim == '':
                            self.ui.calib_error.setText("Measurement not entered")
                        else:
                            dim = float(dim)
                            self.pixpermm = (sum(a)/float(len(a)))/float(dim)
                            print(self.pixpermm)
                    else:
                        print("Pixel variation is more than 2")
                self.parameter[0] = self.pixpermm
                self.par_write(self.parameter)
                self.par_read()
                cv2.drawContours(imageq2, [box.astype("int")], -1, (0, 255, 0), 2)
                imageq2 = cv2.cvtColor(imageq2, cv2.COLOR_BGR2RGB)
                imageq2 = QImage(imageq2.data, imageq2.shape[1], imageq2.shape[0], QImage.Format_RGB888)
                self.ui.img_cali.setPixmap(QPixmap.fromImage(imageq2))
                a = ("%.2f" % round(self.parameter[0], 2))
                self.ui.val_pixpermm.setText(str(a)+(" pix/mm"))
            elif number == 0:
                self.ui.img_cali.clear()
                self.ui.calib_error.setText("No part")
            else:
                self.ui.img_cali.clear()
                self.ui.calib_error.setText("No part -"+str(number))
        except Exception as e:
            print(e)

    def calib_test(self):
        try:
            imageq = self.img
            imageq = cv2.flip(imageq, 1)
            imageq2 = imageq
            imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(imageq, cv2.COLOR_BGR2GRAY)  	    
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            edged = cv2.Canny(gray, 50, 100)   
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            cnts = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            (cnts, _) = contours.sort_contours(cnts)
            #number = 0
            for c in cnts:
                    if cv2.contourArea(c) < 1500:
                        continue
                    #number = number +1
                    box = cv2.minAreaRect(c)
                    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                    box = np.array(box, dtype="int")
                    box = perspective.order_points(box)
                    cv2.drawContours(imageq2, [box.astype("int")], -1, (0, 255, 0), 2)
            imageq2 = cv2.cvtColor(imageq2, cv2.COLOR_BGR2RGB)
            imageq2 = QImage(imageq2.data, imageq2.shape[1], imageq2.shape[0], QImage.Format_RGB888)
            self.ui.img_cali.setPixmap(QPixmap.fromImage(imageq2))
        except Exception as e:
            print(e)

    def bar_snap(self):
        try:
            imageq = self.img
            imageq = cv2.flip(imageq, 1)
            detectedBarcodes = decode(imageq)
            if not detectedBarcodes:
                self.ui.bar_value.setText("Not Detected")
                self.ui.bar_type.setText("")
                imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
                imageq = QImage(imageq.data, imageq.shape[1], imageq.shape[0], QImage.Format_RGB888)
                self.ui.img_bar.setPixmap(QPixmap.fromImage(imageq))
                
            else:
                for barcode in detectedBarcodes:
                        if barcode.data!="":
                            (x, y, w, h) = barcode.rect
                            cv2.rectangle(imageq, (x-10, y-10),(x + w+10, y + h+10),(255, 0, 0), 2)
                            imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
                            imageq = QImage(imageq.data, imageq.shape[1], imageq.shape[0], QImage.Format_RGB888)
                            self.ui.img_bar.setPixmap(QPixmap.fromImage(imageq))
                            bd = str(barcode.data)
                            bd = bd[:-1]
                            bd = bd[2:]
                            bt = str(barcode.type)
                            self.ui.bar_value.setText(bd)
                            self.ui.bar_type.setText(bt)
        except Exception as e:
            print(e)
            
    def btn_find(self):
        print("Find")
        try:
            imageq = self.img
            imageq = cv2.flip(imageq, 1)
            imageq2 = imageq
            imageq = cv2.cvtColor(imageq, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(imageq, cv2.COLOR_BGR2GRAY)  	    
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            edged = cv2.Canny(gray, 50, 100)   
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            cnts = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            (cnts, _) = contours.sort_contours(cnts)
            cn = 0
            for c in cnts:
                if cv2.contourArea(c) < 1500:
                    continue
                box = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
                cv2.drawContours(imageq2, [box.astype("int")], -1, (0, 255, 0), 2)
                imageq2 = cv2.cvtColor(imageq2, cv2.COLOR_BGR2RGB)
                imageq2 = QImage(imageq2.data, imageq2.shape[1], imageq2.shape[0], QImage.Format_RGB888)
                self.ui.img_var.setPixmap(QPixmap.fromImage(imageq2))
                break
            
        except Exception as e:
            print(e)
            
    def btn_pick(self):
        print("Find")

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        Capture = cv2.VideoCapture(0)
        print("Running camera thread")
        while self.ThreadActive:
            ret, frame = Capture.read()
            if ret:
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                Image = cv2.flip(Image, 1)
                Image = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                #Image = Image.scaled(640, 480, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(Image)
                
    def stop(self):
        self.ThreadActive = False
        self.quit()

def gui():
    app = QtWidgets.QApplication([])
    application = mywindow()
    # application.showFullScreen()
    application.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    gui()
    print("Hai")
