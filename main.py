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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName('sEEG_Cognition')
    GUI = MainWindow()
    # sys.exit(app.exec_())
    app.exec_()




