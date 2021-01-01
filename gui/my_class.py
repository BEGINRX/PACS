# -*- coding: utf-8 -*-
'''
@File : my_class.py
@Author : BarryLiu
@Time : 2021/1/1 21:15
@Desc :
'''
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Change_Figure(FigureCanvas):

    def __init__(self, data, title):
        self.fig = Figure(constrained_layout=True)
        super(Change_Figure, self).__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.data = data
        if isinstance(title, str):
            self.title = title
        else:
            raise TypeError('title needed to be a string')
        if self.data.shape == 3:
            pass
        else:
            raise ValueError('It is not a 3-D data')
        self.num = 0
        self.data_plot = self.data[self.num, :, :]
        self.im = self.ax.matshow(self.data_plot)
        self.fig.colorbar(self.im)
        self.ax.set_title(self.title +  str(self.num))
        self.mpl_connect('key_press_event', self.on_move)
        self.mpl_connect(
            "button_press_event", lambda *args, **kwargs: print(args, kwargs)
        )


    def on_move(self, event):
        print(f"activate this {event.key}, {self.num}")
        if event.key == "left":
            if self.num == 0:
                self.num = 0
            else:
                self.num -= 1
        elif event.key == "right":
            if self.num == self.con_1.shape[2] - 1:
                self.num = 0
            else:
                self.num += 1
        else:
            pass
        self.data_plot = self.data[self.num, :, :]
        self.ax.set_data(self.data_plot)
        self.ax.set_title(self.title + str(self.num))
        self.draw_idle()
