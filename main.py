# -*- coding: utf-8 -*-
'''
@File  : main.py
@Author: 刘政
@Date  : 2020/9/7 19:14
@Desc  :
'''

import sys
from qtpy.QtWidgets import QApplication
from gui.main_window import MainWindow


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setApplicationName('sEEGPA')
    GUI = MainWindow()
    # sys.exit(app.exec_())
    app.exec_()




