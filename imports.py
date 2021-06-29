import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import font
import sys
import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
import math
import scipy
import requests
import tarfile

import time

import matplotlib
from pylab import MaxNLocator
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use("ggplot")

import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.models import Sequential, clone_model
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, InputLayer
from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
import tensorflow_model_optimization as tfmot

import threading
# FOR EXE
import hexdump
import sklearn.utils._weight_vector
#

import platform
import subprocess
from urllib.request import urlretrieve
import zipfile
import shutil

import platform
from time import sleep
import serial
import wave
import audioop


# wd is sys._MEIPASS for exe
try:
    wd = sys._MEIPASS
except AttributeError:
    wd = os.getcwd()

if os.name == "nt":
    text_color = "#ffffff"

    menu_color = "#08646c"

    background_color = "#03989e"

    button_color = "#03989e"
else:
    text_color = "#000000"

    menu_color = "#ececec"

    background_color = "#ececec"

    button_color = "#ececec"

home_window_size = "512x380"

data_window_size = "680x260"

processing_window_size = "680x260"

training_window_size = "960x360"

arduino_window_size = "960x360"