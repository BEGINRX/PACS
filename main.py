# -*- coding: utf-8 -*-
'''
@File  : main.py
@Author: 刘政
@Date  : 2020/9/7 19:14
@Desc  :
'''

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from gui.main_window import MainWindow
from gui.splash_screen import SplashPanel


if __name__ == "__main__":
    '''
    该代码需在创建QApplication实例之前
    解决在ubuntu系统下出现的报错：具体如下：
    [xcb] Unknown request in queue while appending request [xcb] Most likely this is a multi-threaded client and XInitThreads has not been called [xcb]
    Aborting, sorry about that.
    python: ../../src/xcb_io.c:151:
    append_pending_request: Assertion `!xcb_xlib_unknown_req_pending'
    failed
    参考自https://forum.qt.io/topic/85774/qt-application-crash/6
    '''

    QCoreApplication.setAttribute (Qt.AA_X11InitThreads)

    my_app = QApplication (sys.argv)
    splash = SplashPanel ()
    my_app.processEvents ()
    my_app.setApplicationName ('SEEG_Cognition')

    GUI = MainWindow ()
    splash.finish (GUI)
    splash.deleteLater ()
    sys.exit (my_app.exec ())
    # my_app.exec_()




