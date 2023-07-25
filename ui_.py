import time
import os
import sys
import shutil
import struct
import wave

import cv2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from scipy.signal import detrend
from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
from midi2audio import FluidSynth

from detect import main,parse_opt
from play_main import make_midi

CurFolder=os.getcwd()
DefaultImFolder=CurFolder

chunk = 1024

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=7, height=6, dpi=100):
        fig = plt.figure(figsize=(width, height), dpi=dpi,facecolor='#ebe8ef')
        self.ax = fig.gca()
        self.ax.set_axis_off()
        self.ln, = self.ax.plot([], [],'gs', markersize=12)
        FigureCanvas.__init__(self, fig)

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(800, 900)
        self.setWindowTitle("古典钢琴音质的五线谱乐谱自动演奏软件V1.0")

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("back.png")))
        self.setPalette(palette)

        self.label1 = QLabel(self)
        self.label1.setText("                                待播放乐谱")
        self.label1.setFixedSize(450, 650)
        self.label1.move(100, 20)
        self.label1.setStyleSheet("QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;font-family:宋体;}")
        self.label1.setFrameShape(QtWidgets.QFrame.Box)
        self.label1.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label1.setLineWidth(3)

        self.label2 = QLabel(self)
        self.label2.setFixedSize(450, 150)
        self.label2.move(100, 670)
        self.label2.setStyleSheet("QLabel{color:rgb(300,300,300,120);font-size:20px;font-weight:bold;font-family:宋体;}")
        self.label2.setFrameShape(QtWidgets.QFrame.Box)
        self.label2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label2.setLineWidth(3)

        self.container = QtWidgets.QVBoxLayout(self.label2)
        self.container.setObjectName("container")

        OpenImgBtn = QPushButton(self)
        OpenImgBtn.setText("Open Score")
        OpenImgBtn.setStyleSheet(''' 
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : white;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        OpenImgBtn.setGeometry(620,50,100,40)

        PlayImgBtn = QPushButton(self)
        PlayImgBtn.setText("Play Score")
        PlayImgBtn.setStyleSheet('''
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : #7392FF;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        PlayImgBtn.setGeometry(620,400,100,40)

        StopImgBtn = QPushButton(self)
        StopImgBtn.setText("Stop Score")
        StopImgBtn.setStyleSheet('''
                                                            QPushButton
                                                            {text-align : center;
                                                            background-color : #7392FF;
                                                            font: bold;
                                                            border-color: gray;
                                                            border-width: 2px;
                                                            border-radius: 10px;
                                                            padding: 6px;
                                                            height : 14px;
                                                            border-style: outset;
                                                            font : 14px;}
                                                            QPushButton:pressed
                                                            {text-align : center;
                                                            background-color : light gray;
                                                            font: bold;
                                                            border-color: gray;
                                                            border-width: 2px;
                                                            border-radius: 10px;
                                                            padding: 6px;
                                                            height : 14px;
                                                            border-style: outset;
                                                            font : 14px;}
                                                            ''')
        StopImgBtn.setGeometry(620, 470, 100, 40)

        ExitBtn = QPushButton(self)
        ExitBtn.setText('Exit')
        ExitBtn.setStyleSheet(''' 
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : #006EFF;
                                                     color : #D4EBFF;
                                                     font: bold;
                                                     border-color: #006EFF;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        ExitBtn.setGeometry(620,750,100,40)

        OpenDirBtn = QPushButton(self)
        OpenDirBtn.setText('Open File')
        OpenDirBtn.setStyleSheet('''
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : white;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        OpenDirBtn.setGeometry(620,150,100,40)

        PerimgBtn = QPushButton(self)
        PerimgBtn.setText('Pre Score')
        PerimgBtn.setStyleSheet('''
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : white;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        PerimgBtn.setGeometry(620,220,100,40)

        NextimgBtn = QPushButton(self)
        NextimgBtn.setText('Next Score')
        NextimgBtn.setStyleSheet('''
                                                     QPushButton
                                                     {text-align : center;
                                                     background-color : white;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     QPushButton:pressed
                                                     {text-align : center;
                                                     background-color : light gray;
                                                     font: bold;
                                                     border-color: gray;
                                                     border-width: 2px;
                                                     border-radius: 10px;
                                                     padding: 6px;
                                                     height : 14px;
                                                     border-style: outset;
                                                     font : 14px;}
                                                     ''')
        NextimgBtn.setGeometry(620,290,100,40)


        OpenImgBtn.clicked.connect(self.openimage)
        PlayImgBtn.clicked.connect(self.play_music)
        StopImgBtn.clicked.connect(self.stop_music)
        OpenDirBtn.clicked.connect(self.OpenDirBntClicked)
        PerimgBtn.clicked.connect(self.PreImBntClicked)
        NextimgBtn.clicked.connect(self.NextImBntClicked)
        ExitBtn.clicked.connect(self.close_app)

        self.imgname1 = '0'    #图片路径
        self.img_name1 = '0'   #图片名称
        self.save_dir1 = '0'
        self.ImFolder = ''  # 图片文件夹路径
        self.ImNameSet = []  # 图片集合
        self.CurImId = 0  # 当前显示图在集合中的编号
        self.StopVis = False
        self.y_temp = np.zeros(chunk)

    def init_draw(self):
        self.canvas.ax.set_ylim(0, 0.2)
        self.canvas.ax.set_xlim(0, 0.5)
        self.canvas.ln.set_data(np.linspace(0, 2 * np.pi, chunk), np.zeros(chunk))
        return self.canvas.ln,

    # 坐标更新
    def update_line(self, frame):
        if self.StopVis is False:
            data = self.wf.readframes(chunk)
            data_int = struct.unpack(str(chunk * 4) + 'B', data)
            y_detrend = detrend(data_int)
            yft = np.abs(np.fft.fft(y_detrend))
            y_vals = yft[:chunk] / (chunk * chunk * 4)
            ind = np.where(y_vals > (np.max(y_vals) + np.min(y_vals)) / 2)
            y_vals[ind[0]] *= 3
            self.y_temp = y_vals
        else:
            y_vals = np.zeros(chunk)

        self.canvas.ln.set_ydata(y_vals)
        return self.canvas.ln,

    # 音乐可视化
    def visualization(self):
        self.canvas = MyMplCanvas(self.container, width=6, height=6, dpi=100)
        self.container.addWidget(self.canvas)
        self.ani = FuncAnimation(self.canvas.figure, self.update_line,
                                 init_func=self.init_draw, interval=32, blit=True)

    def openimage(self):
        imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg;;*.png;;All Files(*)")
        self.img_name1 = imgName.split("/")[-1]
        if imgName != '':
            self.imgname1 = imgName
            im0 = cv2.imread(imgName)
            width,height = im0.shape[1],im0.shape[0]
            width_new,height_new = 500,700
            if width / height >= width_new / height_new:
                show = cv2.resize(im0, (width_new, int(height * width_new / width)))
            else:
                show = cv2.resize(im0, (int(width * height_new / height), height_new))
            im0 = cv2.cvtColor(show, cv2.COLOR_RGB2BGR)
            showImage = QtGui.QImage(im0, im0.shape[1], im0.shape[0], 3 * im0.shape[1], QtGui.QImage.Format_RGB888)
            self.label1.setPixmap(QtGui.QPixmap.fromImage(showImage))

    def play_music(self):
        if self.imgname1 != '0':
            mid_filename = os.listdir('mid_file')
            mid_name = self.img_name1.replace('jpg','mid')
            mid_file_path = os.path.join('mid_file', mid_name)
            if mid_name not in mid_filename:
                opt = parse_opt(self.imgname1)
                im0, label, imgs_infor, save_dir = main(opt)
                txt_name = self.img_name1.replace('jpg', 'txt')
                mung_path = os.path.join(save_dir, "mung/{}".format(txt_name))
                meta_time = 60 * 60 * 10 / 75
                make_midi(mung_path, mid_file_path, meta_time, musical='Acoustic_Grand_Piano')
            soundfont = '.fluidsynth/default_sound_font.sf2'
            FluidSynth(soundfont).midi_to_audio(mid_file_path, 'music.wav')
            wav_name = 'music.wav'
            self.wf = wave.open(wav_name)
            self.sound = QSound('music.wav')
            self.visualization()
            self.sound.play()

            # if self.sound.stop():
            # if self.ImFolder:
            #     self.NextImBntClicked()
        else:
            QMessageBox.information(self, '错误', '请先选择一个乐谱文件', QMessageBox.Yes, QMessageBox.Yes)

    def stop_music(self):
        self.StopVis = True
        self.sound.stop()

    def OpenDirBntClicked(self):
        ImFolder = QtWidgets.QFileDialog.getExistingDirectory(None,"select folder", DefaultImFolder)
        if ImFolder!='':
            ImNameSet = os.listdir(ImFolder)
            if '.DS_Store' in ImNameSet:
                ImNameSet.remove('.DS_Store')
            ImNameSet.sort()
            ImPath = os.path.join(ImFolder, ImNameSet[0])
            self.imgname1 = ImPath
            img_name = ImPath.split('/')[-1]
            self.img_name1 = img_name
            im0 = cv2.imread(ImPath)
            width,height = im0.shape[1],im0.shape[0]
            width_new,height_new = 500,700
            if width / height >= width_new / height_new:
                show = cv2.resize(im0, (width_new, int(height * width_new / width)))
            else:
                show = cv2.resize(im0, (int(width * height_new / height), height_new))
            im0 = cv2.cvtColor(show, cv2.COLOR_RGB2BGR)
            showImage = QtGui.QImage(im0, im0.shape[1], im0.shape[0], 3 * im0.shape[1], QtGui.QImage.Format_RGB888)
            self.label1.setPixmap(QtGui.QPixmap.fromImage(showImage))
            self.ImFolder=ImFolder
            self.ImNameSet=ImNameSet
            self.CurImId=0
        else:
            print('请重新选择文件夹')

    def NextImBntClicked(self):
        ImFolder = self.ImFolder
        ImNameSet = self.ImNameSet
        CurImId = self.CurImId
        ImNum = len(ImNameSet)
        if CurImId < ImNum - 1:
            ImPath = os.path.join(ImFolder, ImNameSet[CurImId + 1])
            self.imgname1 = ImPath
            img_name = ImPath.split('/')[-1]
            self.img_name1 = img_name
            im0 = cv2.imread(ImPath)
            width,height = im0.shape[1],im0.shape[0]
            width_new,height_new = 500,700
            if width / height >= width_new / height_new:
                show = cv2.resize(im0, (width_new, int(height * width_new / width)))
            else:
                show = cv2.resize(im0, (int(width * height_new / height), height_new))
            im0 = cv2.cvtColor(show, cv2.COLOR_RGB2BGR)
            showImage = QtGui.QImage(im0, im0.shape[1], im0.shape[0], 3 * im0.shape[1], QtGui.QImage.Format_RGB888)
            self.label1.setPixmap(QtGui.QPixmap.fromImage(showImage))
            self.CurImId = CurImId + 1

    def PreImBntClicked(self):
        ImFolder = self.ImFolder
        ImNameSet = self.ImNameSet
        CurImId = self.CurImId
        ImNum = len(ImNameSet)
        if CurImId > 0:
            ImPath = os.path.join(ImFolder, ImNameSet[CurImId - 1])
            self.imgname1 = ImPath
            img_name = ImPath.split('/')[-1]
            self.img_name1 = img_name
            im0 = cv2.imread(ImPath)
            width,height = im0.shape[1],im0.shape[0]
            width_new,height_new = 500,700
            if width / height >= width_new / height_new:
                show = cv2.resize(im0, (width_new, int(height * width_new / width)))
            else:
                show = cv2.resize(im0, (int(width * height_new / height), height_new))
            im0 = cv2.cvtColor(show, cv2.COLOR_RGB2BGR)
            showImage = QtGui.QImage(im0, im0.shape[1], im0.shape[0], 3 * im0.shape[1], QtGui.QImage.Format_RGB888)
            self.label1.setPixmap(QtGui.QPixmap.fromImage(showImage))
            self.CurImId = CurImId - 1
        if self.CurImId < 0:
            self.CurImId = 0

    def close_app(self):
        app = QApplication.instance()
        app.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = QSplashScreen(QPixmap(".\\data\\source_image\\logo.png"))
    splash.setFont(QFont('Microsoft YaHei UI', 12))
    splash.show()
    ui_p = MainWindow()
    ui_p.show()
    splash.close()
    sys.exit(app.exec_())


