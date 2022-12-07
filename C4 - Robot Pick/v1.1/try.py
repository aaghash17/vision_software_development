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


def add_par():
    pickle_in = open("parameter.dat","rb")
    parameter = pickle.load(pickle_in)
    print('Before-',parameter)
    parameter.append(0)
    print('After-',parameter)
    pickle_out = open("parameter.dat","wb")
    pickle.dump(parameter, pickle_out)
    pickle_out.close()

def remove_par():
    pickle_in = open("parameter.dat","rb")
    self.parameter = pickle.load(pickle_in)
    l = len(self.parameter)
    print('Before-',self.parameter)
    self.parameter.pop(l-1)
    print('After-',self.parameter)
    pickle_out = open("parameter.dat","wb")
    pickle.dump(self.parameter, pickle_out)
    pickle_out.close()


if __name__ == "__main__":
    add_par()
