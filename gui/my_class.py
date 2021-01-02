# -*- coding: utf-8 -*-
'''
@File : my_class.py
@Author : BarryLiu
@Time : 2021/1/1 21:15
@Desc :
'''
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class Change_Figure(Figure):

    def __init__(self, data, title, *args, **kwargs):

        super(Change_Figure, self).__init__(*args, **kwargs)
        self.ax = self.add_subplot()
        self.data = data
        if isinstance(title, str):
            self.title = title
        else:
            raise TypeError('title needs to be a string')
        if len(self.data.shape) == 3:
            pass
        else:
            raise ValueError('It is not a 3-D data')
        self.num = 0
        self.data_plot = self.data[self.num, :, :]
        self.im = self.ax.matshow(self.data_plot)
        self.colorbar(self.im)
        self.ax.set_title(self.title +  str(self.num))
        self.canvas.mpl_connect('key_press_event', self.on_move)
        self.canvas.mpl_connect(
            "button_press_event", lambda *args, **kwargs: print(args, kwargs)
        )
        plt.ion()

    def on_move(self, event):
        print(f"activate this {event.key}, {self.num}")
        print('here')
        self.draw_idle()
        plt.cla()
        if event.key == "left":
            if self.num == 0:
                self.num = 0
            else:
                self.num -= 1
        elif event.key == "right":
            if self.num == self.data.shape[2] - 1:
                self.num = 0
            else:
                self.num += 1
        else:
            pass
        self.data_plot = self.data[self.num, :, :]
        self.ax.matshow(self.data_plot)
        self.ax.set_title(self.title + str(self.num))

