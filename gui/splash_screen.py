# -*- coding: utf-8 -*-
'''
@File : splash_screen.py
@Author : BarryLiu
@Time : 2020/12/30 19:36
@Desc :
'''
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QSplashScreen, QDesktopWidget
import time

class SplashPanel(QSplashScreen):
    
    def __init__(self):
        
        super(SplashPanel, self).__init__()

        self.setFixedSize(360, 200)
        message_font = QFont()
        message_font.setBold(True)
        message_font.setPointSize(10)
        self.setFont(message_font)
        print('here')
        pixmap = QPixmap("image/brain_title_use.png").scaled(QSize(800, 200), Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.center()
        self.show()
        for i in range(1, 5):
            self.showMessage('软件初始化{}'.format('.' * i), alignment=Qt.AlignBottom, color=Qt.black)
            time.sleep(0.2)

    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        pass
        # 重写鼠标点击事件，防止点击后消失

    def mouseDoubleClickEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，防止出现卡顿现象

    def enterEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，防止出现卡顿现象

    def mouseMoveEvent(self, *args, **kwargs):
        pass
        # 重写鼠标移动事件，防止出现卡顿现象