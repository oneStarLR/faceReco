# -*- coding: utf-8 -*-

import sys
import cv2
import threading
from PyQt5.QtCore import QBasicTimer
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox, QGroupBox
from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PIL import Image
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QBrush, QPixmap
import os
import RPi.GPIO as GPIO

# 定义人脸标签和初始化标签对应的人物名称
id = 0
names = ['None', 'oneStar', 'denghaibo', 'zhangzhaohui', 'zhangchaoyang','guomo','yanjie','luochao','yanggong','gaogong']

# 导入GPIO
import RPi.GPIO as GPIO     
# 设置GPIO模式，BCM模式在所有数码派通用
GPIO.setmode(GPIO.BCM) 
# 设置GPIO25为电流输出  
GPIO.setup(25, GPIO.OUT)   


import time
import signal
import atexit
 
atexit.register(GPIO.cleanup)  
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT, initial=False)
p = GPIO.PWM(17,50) #50HZ
p.start(0)


# 导入OpenCV自带的数据集，定义多个是因为在后面有多次调用，用一个的话会报错
faceCascade = cv2.CascadeClassifier('/home/pi/Downloads/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml')
faceCascade2 = cv2.CascadeClassifier('/home/pi/Downloads/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml')
faceCascade3 = cv2.CascadeClassifier('/home/pi/Downloads/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml')

# 继承QLineEdit，重写mouseReleaseEvent函数
class mylineedit(QLineEdit):
    clicked = pyqtSignal()  # 定义clicked信号

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()  # 发送clicked信号


# 创建主界面类
class Ui_Menu(QWidget):
    def __init__(self):
        super(Ui_Menu, self).__init__()
        # 创建label并设置文本内容
        self.label = QLabel('欢迎使用人脸识别门禁系统', self)
        # 创建普通用户和管理员按键
        self.btn_ordinary = QPushButton('普通用户', self)
        self.btn_admin = QPushButton('管理员', self)

        # 初始化界面
        self.init_ui()

    def init_ui(self):
        # 设置窗口大小
        self.resize(1280, 800)
        # 设置label框的位置
        self.label.move(140, 200)
        
        # 设置按键框的位置和大小
        self.btn_ordinary.setGeometry(550, 420, 181, 61)
        self.btn_admin.setGeometry(550, 510, 181, 61)
        
        # 设置label样式（字体、大小、颜色等）
        self.label.setStyleSheet(
            "QLabel{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:82px;font-weight:bold;"  # 大小为70 加粗
            "font-family:Roman times;}")  # Roman times字体

        self.btn_ordinary.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        self.btn_admin.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 点击管理员按钮事件
        self.btn_admin.clicked.connect(self.slot_btn_admin)
        # 点击普通用户按钮事件
        self.btn_ordinary.clicked.connect(self.slot_btn_ordinary)

    # 点点击管理员按钮事件
    def slot_btn_admin(self):
        self.logon = Ui_logon()
        self.logon.show()
        self.hide()
        
    # 点击普通用户按钮事件
    def slot_btn_ordinary(self):
        self.face_reco = Ui_face_reco()
        self.face_reco.show()
        self.hide()


# 创建登录界面类
class Ui_logon(QWidget):
    clicked = pyqtSignal()

    def __init__(self):
        super(Ui_logon, self).__init__()
        
        # 初始化数值
        self.ID_num = ""
        self.key_num = ""
        
        # 创建账号、密码以、输入框以及登录返回等按键
        self.lab_ID = QLabel('账号', self)
        self.lab_key = QLabel('密码', self)
        self.Edit_ID = mylineedit(self)
        self.Edit_key = mylineedit(self)
        self.selected = self.Edit_ID    # 输入位置标识位
        self.btn_logon = QPushButton('登录', self)
        self.btn_back = QPushButton('返回', self)
        self.btn_1 = QPushButton('1', self)
        self.btn_2 = QPushButton('2', self)
        self.btn_3 = QPushButton('3', self)
        self.btn_4 = QPushButton('4', self)
        self.btn_5 = QPushButton('5', self)
        self.btn_6 = QPushButton('6', self)
        self.btn_7 = QPushButton('7', self)
        self.btn_8 = QPushButton('8', self)
        self.btn_9 = QPushButton('9', self)
        self.btn_0 = QPushButton('0', self) 
        self.btn_del = QPushButton('del', self)
        

        # 设置容器存放数字键，使用栅格布局
        self.layoutWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.layoutWidget)

        # 点击mylineedit事件
        self.Edit_ID.clicked.connect(self.changeEdit_ID)
        self.Edit_key.clicked.connect(self.changeEdit_key)

        # 初始化界面
        self.init_ui()

    # 点击Edit_ID事件
    def changeEdit_ID(self):
        self.selected = self.Edit_ID

    # 点击Edit_key事件
    def changeEdit_key(self):
        self.selected = self.Edit_key

    # 初始化界面
    def init_ui(self):
        # 设置窗口大小
        self.resize(1280, 800)
        # 设置lab_ID位置
        self.lab_ID.setGeometry(380, 130, 71, 41)
        self.lab_key.setGeometry(380, 200, 71, 41)
        self.Edit_ID.setGeometry(470, 130, 411, 41)
        self.Edit_key.setGeometry(470, 200, 411, 41)
        self.btn_logon.setGeometry(490, 270, 91, 51)
        self.btn_back.setGeometry(690, 270, 91, 51)

        # 设置数字键高度
        self.btn_0.setFixedHeight(50)
        self.btn_1.setFixedHeight(50)
        self.btn_2.setFixedHeight(50)
        self.btn_3.setFixedHeight(50)
        self.btn_4.setFixedHeight(50)
        self.btn_5.setFixedHeight(50)
        self.btn_6.setFixedHeight(50)
        self.btn_7.setFixedHeight(50)
        self.btn_8.setFixedHeight(50)
        self.btn_9.setFixedHeight(50)
        self.btn_del.setFixedHeight(50)

        # 设置容器位置
        # self.layoutWidget.setGeometry(230, 320, 806, 61)
        self.layoutWidget.setGeometry(491, 404, 291, 251)
        
        # 将数字存放进容器
        self.gridLayout.addWidget(self.btn_1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_2, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_3, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_4, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_5, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_6, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_7, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_8, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_9, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_0, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_del, 3, 1, 1, 2)

        # 对lab_ID字体大小进行设置
        self.lab_ID.setStyleSheet(
            "QLabel{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 对lab_key字体大小进行设置
        self.lab_key.setStyleSheet(
            "QLabel{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 对Edit_ID字体大小进行设置
        self.Edit_ID.setStyleSheet(
            "QLineEdit{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 对Edit_key字体大小进行设置
        self.Edit_key.setStyleSheet(
            "QLineEdit{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        # 设置密码隐藏
        self.Edit_key.setEchoMode(QLineEdit.Password)

        # 对数字按键字体大小进行设置
        self.btn_1.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_2.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_3.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_4.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_5.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_6.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_7.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_8.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_9.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_0.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_del.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 对登录返回按键字体大小进行设置
        self.btn_logon.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_back.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 点击返回按钮事件
        self.btn_back.clicked.connect(self.slot_btn_back)
        # 点击登录按钮事件
        self.btn_logon.clicked.connect(self.slot_btn_logon)

        # 点击数字按钮输入用户名和密码
        self.btn_0.clicked.connect(self.slot_btn_0)
        self.btn_1.clicked.connect(self.slot_btn_1)
        self.btn_2.clicked.connect(self.slot_btn_2)
        self.btn_3.clicked.connect(self.slot_btn_3)
        self.btn_4.clicked.connect(self.slot_btn_4)
        self.btn_5.clicked.connect(self.slot_btn_5)
        self.btn_6.clicked.connect(self.slot_btn_6)
        self.btn_7.clicked.connect(self.slot_btn_7)
        self.btn_8.clicked.connect(self.slot_btn_8)
        self.btn_9.clicked.connect(self.slot_btn_9)
        self.btn_del.clicked.connect(self.slot_btn_del)

    # 点击返回按钮事件
    def slot_btn_back(self):
        self.menu = Ui_Menu()
        self.menu.show()
        self.hide()

    # 点击登录按钮事件
    def slot_btn_logon(self):
        # 判断账号和密码是否输入正确
        if self.ID_num == "1" and self.key_num == "1":
            self.manager_face = Ui_manager_face()
            self.manager_face.show()
            self.hide()
        else:
            QMessageBox.warning(self, "提示", "账号或密码错误！", QMessageBox.Close)

    # 点击数字按钮输入用户名和密码
    def slot_btn_0(self):
        if self.selected == self.Edit_ID:
            ID_num0 = self.btn_0.text()
            self.ID_num = self.ID_num + ID_num0
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num0 = self.btn_0.text()
            self.key_num = self.key_num + key_num0
            self.selected.setText(self.key_num)

    def slot_btn_1(self):
        if self.selected == self.Edit_ID:
            ID_num1 = self.btn_1.text()
            self.ID_num = self.ID_num + ID_num1
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num1 = self.btn_1.text()
            self.key_num = self.key_num + key_num1
            self.selected.setText(self.key_num)

    def slot_btn_2(self):
        if self.selected == self.Edit_ID:
            ID_num2 = self.btn_2.text()
            self.ID_num = self.ID_num + ID_num2
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num2 = self.btn_2.text()
            self.key_num = self.key_num + key_num2
            self.selected.setText(self.key_num)

    def slot_btn_3(self):
        if self.selected == self.Edit_ID:
            ID_num3 = self.btn_3.text()
            self.ID_num = self.ID_num + ID_num3
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num3 = self.btn_3.text()
            self.key_num = self.key_num + key_num3
            self.selected.setText(self.key_num)

    def slot_btn_4(self):
        if self.selected == self.Edit_ID:
            ID_num4 = self.btn_4.text()
            self.ID_num = self.ID_num + ID_num4
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num4 = self.btn_4.text()
            self.key_num = self.key_num + key_num4
            self.selected.setText(self.key_num)

    def slot_btn_5(self):
        if self.selected == self.Edit_ID:
            ID_num5 = self.btn_5.text()
            self.ID_num = self.ID_num + ID_num5
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num5 = self.btn_5.text()
            self.key_num = self.key_num + key_num5
            self.selected.setText(self.key_num)

    def slot_btn_6(self):
        if self.selected == self.Edit_ID:
            ID_num6 = self.btn_6.text()
            self.ID_num = self.ID_num + ID_num6
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num6 = self.btn_6.text()
            self.key_num = self.key_num + key_num6
            self.selected.setText(self.key_num)

    def slot_btn_7(self):
        if self.selected == self.Edit_ID:
            ID_num7 = self.btn_7.text()
            self.ID_num = self.ID_num + ID_num7
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num7 = self.btn_7.text()
            self.key_num = self.key_num + key_num7
            self.selected.setText(self.key_num)

    def slot_btn_8(self):
        if self.selected == self.Edit_ID:
            ID_num8 = self.btn_8.text()
            self.ID_num = self.ID_num + ID_num8
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num8 = self.btn_8.text()
            self.key_num = self.key_num + key_num8
            self.selected.setText(self.key_num)

    def slot_btn_9(self):
        if self.selected == self.Edit_ID:
            ID_num9 = self.btn_9.text()
            self.ID_num = self.ID_num + ID_num9
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            key_num9 = self.btn_9.text()
            self.key_num = self.key_num + key_num9
            self.selected.setText(self.key_num)

    # 将字符串从最后一位开始删除
    def slot_btn_del(self):
        if self.selected == self.Edit_ID:
            self.ID_num = self.ID_num[:-1]
            self.selected.setText(self.ID_num)

        if self.selected == self.Edit_key:
            self.key_num = self.key_num[:-1]
            self.selected.setText(self.key_num)


# 创建管理人脸数据界面类
class Ui_manager_face(QWidget):
    def __init__(self):
        super(Ui_manager_face, self).__init__()
        
        # 初始化 ID
        self.ID_num = ""
        self.lab_face = QLabel(self)
        
        # 初始化进度条定时器
        self.timer = QBasicTimer()
        self.step = 0

        # 创建数字按键
        self.btn_1 = QPushButton('1', self)
        self.btn_2 = QPushButton('2', self)
        self.btn_3 = QPushButton('3', self)
        self.btn_4 = QPushButton('4', self)
        self.btn_5 = QPushButton('5', self)
        self.btn_6 = QPushButton('6', self)
        self.btn_7 = QPushButton('7', self)
        self.btn_8 = QPushButton('8', self)
        self.btn_9 = QPushButton('9', self)
        self.btn_0 = QPushButton('0', self)
        self.btn_del = QPushButton('del', self)

        # 创建容器存放数字键，使用栅格布局
        self.layoutWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.layoutWidget)

        # 创建groupBox控件
        self.groupBox = QtWidgets.QGroupBox(self)

        # 创建lab_ID控件
        self.lab_ID = QLabel(self.groupBox)
        self.Edit_ID = QLineEdit(self.groupBox)
        self.btn_enter = QPushButton(self.groupBox)
        self.progressBar = QtWidgets.QProgressBar(self.groupBox)
        self.btn_back = QPushButton(self)
        
        # 创建定时器
        self.timer_camera = QtCore.QTimer()
        
        # 初始化摄像头数据
        self.camera_init()

        # 初始化界面
        self.init_ui()
        
        # 显示人脸识别视频界面
        self.face_rec()
        
        # 定时器函数
        self.timer_camera.timeout.connect(self.show_camera)
        
        # 点击按钮开启线程
        self.btn_enter.clicked.connect(self.slot_btn_enter)

    # 初始化摄像头数据
    def camera_init(self):
        # 打开设置摄像头对象
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.__flag_work = 0
        self.x =0
        self.count = 0
        self.cap.set(4,951) # set Width
        self.cap.set(3,761) # set Height

    # 初始化界面
    def init_ui(self):
        self.resize(1280, 800)
        self.lab_face.setGeometry(15, 40, 960, 720)
        self.lab_face.setFrameShape(QtWidgets.QFrame.Box)
        self.lab_face.setText("")
        self.lab_ID.setGeometry(10, 40, 31, 41)

        # 设置容器位置
        self.layoutWidget.setGeometry(1010, 350, 231, 251)

        # 设置数字键高度
        self.btn_0.setFixedHeight(50)
        self.btn_1.setFixedHeight(50)
        self.btn_2.setFixedHeight(50)
        self.btn_3.setFixedHeight(50)
        self.btn_4.setFixedHeight(50)
        self.btn_5.setFixedHeight(50)
        self.btn_6.setFixedHeight(50)
        self.btn_7.setFixedHeight(50)
        self.btn_8.setFixedHeight(50)
        self.btn_9.setFixedHeight(50)
        self.btn_del.setFixedHeight(50)

        # 对数字按键字体大小进行设置
        self.btn_1.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_2.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_3.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_4.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_5.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_6.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_7.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_8.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_9.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_0.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体
        self.btn_del.setStyleSheet(
            "QPushButton{color:rgb(0,0,0,255);"  # 字体颜色为黑色
            "font-size:30px;"  # 大小为30 
            "font-family:Roman times;}")  # Roman times字体

        # 将数字存放进容器
        self.gridLayout.addWidget(self.btn_1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_2, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_3, 0, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_4, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_5, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_6, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_7, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_8, 2, 1, 1, 1)
        self.gridLayout.addWidget(self.btn_9, 2, 2, 1, 1)
        self.gridLayout.addWidget(self.btn_0, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.btn_del, 3, 1, 1, 2)

        # 对groupBox进行设置
        self.groupBox.setTitle("录入人脸")
        self.groupBox.setGeometry(990, 120, 281, 191)
        self.groupBox.setStyleSheet(
            "QGroupBox {\n"
            "border-width:2px;\n"
            "border-style:solid;\n"
            "border-color:lightGray;\n"
            "font: 75 20pt \"Aharoni\";\n"
            "margin-top: 0.5ex;\n"
            "}\n"
            "QGroupBox::title {\n"
            "subcontrol-origin: margin;\n"
            "subcontrol-position: top left;\n"
            "left:10px;\n"
            "margin-left: 0px;\n"
            "padding:0px;\n"
            "}")

        # 设置groupBox里面的控件
        self.lab_ID.setText("ID")
        self.lab_ID.setGeometry(10, 40, 31, 41)
        self.lab_ID.setStyleSheet("font: 18pt;")

        self.Edit_ID.setGeometry(50, 40, 221, 41)
        self.Edit_ID.setStyleSheet("font: 18pt;")

        self.btn_enter.setText("开始录入")
        self.btn_enter.setGeometry(80, 90, 121, 51)
        self.btn_enter.setStyleSheet("font: 75 16pt;")

        self.progressBar.setGeometry(10, 150, 261, 31)
        # self.progressBar.setProperty("value", 0)

        self.btn_back.setText("返回")
        self.btn_back.setGeometry(1090, 670, 81, 51)
        self.btn_back.setStyleSheet("font: 75 16pt;")

        # 点击数字按钮输入用户名和密码
        self.btn_0.clicked.connect(self.slot_btn_0)
        self.btn_1.clicked.connect(self.slot_btn_1)
        self.btn_2.clicked.connect(self.slot_btn_2)
        self.btn_3.clicked.connect(self.slot_btn_3)
        self.btn_4.clicked.connect(self.slot_btn_4)
        self.btn_5.clicked.connect(self.slot_btn_5)
        self.btn_6.clicked.connect(self.slot_btn_6)
        self.btn_7.clicked.connect(self.slot_btn_7)
        self.btn_8.clicked.connect(self.slot_btn_8)
        self.btn_9.clicked.connect(self.slot_btn_9)
        self.btn_del.clicked.connect(self.slot_btn_del)

        # 点击返回按键返回上一界面
        self.btn_back.clicked.connect(self.slot_btn_back)

    # 点击数字按钮输入用户名和密码
    def slot_btn_0(self):
        ID_num0 = self.btn_0.text()
        self.ID_num = self.ID_num + ID_num0
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_1(self):
        ID_num1 = self.btn_1.text()
        self.ID_num = self.ID_num + ID_num1
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_2(self):
        ID_num2 = self.btn_2.text()
        self.ID_num = self.ID_num + ID_num2
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_3(self):
        ID_num3 = self.btn_3.text()
        self.ID_num = self.ID_num + ID_num3
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_4(self):
        ID_num4 = self.btn_4.text()
        self.ID_num = self.ID_num + ID_num4
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_5(self):
        ID_num5 = self.btn_5.text()
        self.ID_num = self.ID_num + ID_num5
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_6(self):
        ID_num6 = self.btn_6.text()
        self.ID_num = self.ID_num + ID_num6
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_7(self):
        ID_num7 = self.btn_7.text()
        self.ID_num = self.ID_num + ID_num7
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_8(self):
        ID_num8 = self.btn_8.text()
        self.ID_num = self.ID_num + ID_num8
        self.Edit_ID.setText(self.ID_num)

    def slot_btn_9(self):
        ID_num9 = self.btn_9.text()
        self.ID_num = self.ID_num + ID_num9
        self.Edit_ID.setText(self.ID_num)

    # 将字符串从最后一位开始删除
    def slot_btn_del(self):
        self.ID_num = self.ID_num[:-1]
        self.Edit_ID.setText(self.ID_num)

    # 点击返回按键返回上一界面
    def slot_btn_back(self):
        self.logon = Ui_logon()
        self.logon.show()
        self.timer_camera.stop()
        self.cap.release()
        self.hide()
        
    # 显示人脸识别视频界面
    def face_rec(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(30)
        else:
            self.timer_camera.stop()
            self.cap.release()
            
    def show_camera(self):
        flag, self.image = self.cap.read()
        self.image = cv2.flip(self.image, -1)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )
        for (x,y,w,h) in faces:
            cv2.rectangle(self.image,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = self.image[y:y+h, x:x+w]
            
            
        # 将视频显示在了label上
        show = cv2.resize(self.image, (960,720))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.lab_face.setPixmap(QtGui.QPixmap.fromImage(showImage))

        
    # 点击按钮开启线程
    def slot_btn_enter(self):
        self.count = 0
        self.step = 0
        # 创建线程并开启
        self.thread = threading.Thread(target=self.thread_pic)
        self.thread.start()
        
        # 开启进度条定时器
        self.timer.start(100, self)
    
    # 加载进度条
    def timerEvent(self, e):
        if self.step > 58:
            self.timer.stop()
            return
        self.step = self.count+1
        self.progressBar.setValue(self.count)

    
    # 录入人脸线程
    def thread_pic(self):
        print("线程出没！！！")
        print(self.Edit_ID.text())

        # 创建目录，将获取的人脸照片放入指定的文件夹
        self.file = "./Face_data/"
        
        while(True):
            ret, self.img = self.cap.read()
            # 垂直翻转视频图像
            self.img = cv2.flip(self.img, -1)
            # 灰度化处理
            gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade2.detectMultiScale(gray, 1.3, 5)
            
            # 判断是否存在文件夹如果不存在则创建为文件夹
            self.folder = os.path.exists(self.file)
            if not self.folder:  
                # makedirs 满权限创建文件时如果路径不存在会创建这个路径
                os.makedirs(self.file)  
                os.chmod(self.file,0777)
            
            for (x,y,w,h) in faces:
                cv2.rectangle(self.img, (x,y), (x+w,y+h), (255,0,0), 2)     
                self.count += 1
                # 将捕获的图像保存到指定的文件夹中
                bool = cv2.imwrite(self.file + "/User." + str(self.Edit_ID.text()) + '.' + str(self.count) + ".png", gray[y:y+h,x:x+w])
                
            # 取60张人脸样本，停止录像
            if self.count >= 60: 
                print("OK!")
                break
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # 函数获取图像和标签数据
        def getImagesAndLabels(path):
            imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
            faceSamples=[]
            ids = []
            self.progressBar.setProperty("value", 65)
            for imagePath in imagePaths:
                # 转换为灰度
                PIL_img = Image.open(imagePath).convert('L') 
                img_numpy = np.array(PIL_img,'uint8')
                id = int(os.path.split(imagePath)[-1].split(".")[1])

                faces = faceCascade3.detectMultiScale(img_numpy)
                for (x,y,w,h) in faces:
                    faceSamples.append(img_numpy[y:y+h,x:x+w])
                    ids.append(id)
            return faceSamples,ids
        self.progressBar.setProperty("value", 75)
        print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        
        # 调用函数，传递文件夹路径参数
        faces,ids = getImagesAndLabels(self.file)
        self.recognizer.train(faces, np.array(ids))
        self.progressBar.setProperty("value", 85)
        
        # 创建文件夹
        self.triningfile = "./Face_training/"
        self.folder1 = os.path.exists(self.triningfile)
        if not self.folder1:  
            os.makedirs(self.triningfile)  
            os.chmod(self.triningfile,0777)
            
        # 将训练好的数据保存到指定文件夹中
        self.recognizer.write(self.triningfile + "/trainer.yml")
        
        # 打印经过训练的人脸编号和结束程序
        print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
        self.progressBar.setProperty("value", 100)


# 创建人脸识别通用户界面类
class Ui_face_reco(QWidget):
    def __init__(self):
        super(Ui_face_reco, self).__init__()

        # 创建控件
        self.lab_face = QLabel(self)
        self.btn_back = QPushButton(self)
        self.lab_pic = QLabel(self)
        self.lab_body = QLabel(self)
        self.lab_ID = QLabel(self)
        self.lab_ID_E = QLabel(self)
        self.lab_T_F = QLabel(self)
        
        # 创建定时器
        self.timer_camera = QtCore.QTimer()
        self.user = []
        
        # 初始化摄像头数据
        self.camera_init()
        
        # 初始化界面
        self.init_ui()
        
        # 点击返回按键返回上一界面
        self.btn_back.clicked.connect(self.slot_btn_back)
        
        # 显示人脸识别视频界面
        self.face_rec()
        
        # 定时器函数
        self.timer_camera.timeout.connect(self.show_camera)
        
        # 将照片显示在lab上
        self.show_pic()
        
        
        
        
        
        # self.User = Ui_manager_face()
        # print(self.User.Edit_ID.text())
    def camera_init(self):
        # 打开设置摄像头对象
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.__flag_work = 0
        self.x =0
        self.count = 0
        self.minW = 0.1*self.cap.get(3)
        self.minH = 0.1*self.cap.get(4)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        # 读取训练好的数据
        self.recognizer.read('./Face_training//trainer.yml')
        self.cascadePath = "/home/pi/Downloads/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml"
        self.faceCascade4 = cv2.CascadeClassifier(self.cascadePath);
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        


    # 初始化界面
    def init_ui(self):
        # 设置控件位置
        self.lab_face.setGeometry(15, 40, 960, 720)
        self.btn_back.setGeometry(1090, 670, 81, 51)
        self.lab_pic.setGeometry(1060, 160, 160, 140)
        self.lab_body.setGeometry(1000, 350, 281, 91)
        self.lab_ID.setGeometry(1070, 320, 35, 21)
        self.lab_ID_E.setGeometry(1108, 320, 91, 21)
        self.lab_T_F.setGeometry(1060, 450, 171, 81)

        # 设置lab有边框
        self.lab_face.setFrameShape(QtWidgets.QFrame.Box)

        # 设置返回按钮
        self.btn_back.setText("返回")
        self.btn_back.setStyleSheet("font: 75 16pt;")
        
        self.lab_body.setStyleSheet("font: 75 48pt \"Aharoni\";")
        self.lab_body.setText("身份认证")
        
        self.lab_ID.setStyleSheet("font: 75 16pt \"Aharoni\";")
        self.lab_ID_E.setStyleSheet("font: 75 16pt \"Aharoni\";")
        self.lab_T_F.setStyleSheet("font: 75 48pt \"Aharoni\";")
        
        self.lab_ID.setText("ID：")


    # 点击返回按键返回上一界面
    def slot_btn_back(self):
        self.logon = Ui_Menu()
        self.logon.show()
        self.timer_camera.stop()
        self.cap.release()
        self.hide()
        
    # 显示人脸识别视频界面
    def face_rec(self):
        # 先对摄像头设备进行检测，没有则弹出提示信息
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确", buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(10)
        else:
            self.timer_camera.stop()
            self.cap.release()
            
    def show_camera(self):
        
        flag, self.image =self.cap.read()
        # 垂直翻转
        self.image = cv2.flip(self.image, -1) 
        
        # 将图片变化成灰度图
        gray = cv2.cvtColor(self.image,cv2.COLOR_BGR2GRAY)
        
        # 探测图片中的人脸
        faces = self.faceCascade4.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(self.minW), int(self.minH)),
           )
           
        # 判断是否检测到人脸，没检测到设置为低电平
        # 检测的时候当矩阵为空的时候能执行代码，当矩阵不为空的时候会有异常，这里将异常抛出
        try:
            if any(faces) == False:
                p.ChangeDutyCycle(2.5 + 10 * 100 / 180)
                time.sleep(0.2)   
                p.ChangeDutyCycle(0) 
        except Exception as e:
            print(e)
            
        # faces中的四个量分别为左上角的横坐标、纵坐标、宽度、长度
        for(x,y,w,h) in faces:
            
            # 围绕脸的框
            cv2.rectangle(self.image, (x,y), (x+w,y+h), (0,255,0), 2)
            # 把要分析的面部的捕获部分作为参数，并将返回其可能的所有者，指示其ID以及识别器与该匹配相关的置信度
            id, confidence = self.recognizer.predict(gray[y:y+h,x:x+w])
            
            # 对置信度进行判断，高于预定值显示出提示信息，并控制GPIO输出高低电平来控制门的开关
            if (confidence < 90):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
                # GPIO.output(25, GPIO.HIGH)   #GPIO25 输出3.3V
                self.lab_T_F.setText( "成功！")
                self.lab_ID_E.setText(str(id)) 
                p.ChangeDutyCycle(2.5)
                time.sleep(0.2)   
                p.ChangeDutyCycle(0)   
            else:
                id = "unknown"
                # GPIO.output(25, GPIO.LOW)   #GPIO25 输出0.0V
                
                confidence = "  {0}%".format(round(100 - confidence))
                self.lab_T_F.setText( "失败！")
                self.lab_ID_E.setText("无法识别")
                p.ChangeDutyCycle(2.5 + 10 * 100 / 180)
                time.sleep(0.2)   
                p.ChangeDutyCycle(0)
                
            # 给图片添加文本 图片矩阵, 添加文本名称, 设置文本显示位置,
            # 字体样式, 字体大小, 字体颜色, 字体粗细
            cv2.putText(self.image, str(id), (x+5,y-5), self.font, 1, (255,255,255), 2)
            cv2.putText(self.image, str(confidence), (x+5,y+h-5), self.font, 1, (255,255,0), 1)   
             
        # 将视频显示在了label上
        show = cv2.resize(self.image, (960,720))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.lab_face.setPixmap(QtGui.QPixmap.fromImage(showImage))
        k = cv2.waitKey(10) & 0xff

    # 显示照片
    def show_pic(self):
        pix = QPixmap('/home/pi/Desktop/Face_data/User.1.40.png')
        self.lab_pic.setPixmap(pix)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Ui_Menu()
    w.show()
    sys.exit(app.exec_())

