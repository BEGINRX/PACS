# -*- coding: utf-8 -*-
'''
@File  : main.py
@Author: 刘政
@Date  : 2020/9/7 19:14
@Desc  :
'''

import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.splash_screen import SplashPanel


if __name__ == "__main__":

    app = QApplication(sys.argv)
    splash = SplashPanel()
    app.processEvents()
    app.setApplicationName('SEEG_Cognition')
    GUI = MainWindow()
    splash.finish(GUI)
    splash.deleteLater()
    # sys.exit(app.exec_())
    app.exec_()




