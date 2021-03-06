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


def main():
    my_app = QApplication(sys.argv)
    splash = SplashPanel()
    my_app.processEvents()
    my_app.setApplicationName('SEEG_Cognition')

    GUI = MainWindow()
    splash.finish(GUI)
    splash.deleteLater()
    sys.exit(my_app.exec())
    # my_app.exec_()



if __name__ == "__main__":

    main()




