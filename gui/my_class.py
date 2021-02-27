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
from mne import BaseEpochs
from mne.io import BaseRaw


class SEEG(object):

    def __init__(self, name=None, data=None, events=None, mode=None):
        super(SEEG, self).__init__()
        self.name = name
        self.data = data
        self.mode = mode
        self.events = events
        self.data_para = dict()



    def get_para(self):
        if self.mode == 'raw':
            self.data_para['epoch_num'] = str(1)
            self.data_para['sfreq'] = str(self.data.info['sfreq'])
            self.data_para['chan_num'] = str(self.data.info['nchan'])
            self.data_para['epoch_start'] = str(self.data._first_time)
            self.data_para['epoch_end'] = str(round(self.data._last_time, 2))
            self.data_para['time_point'] = str(self.data.n_times)
            self.data_para['event_class'] = str(len(set(self.events[:, 2])))
            self.data_para['event_num'] = str(len(self.events))
            self.data_para['data_size'] = str(round(0.5 *(self.data._size /((2 ** 10) ** 2)), 2))
        else:
            self.data_para['epoch_num'] = str(self.events.shape[0])
            self.data_para['sfreq'] = str(self.data.info['sfreq'])
            self.data_para['chan_num'] = str(self.data.info['nchan'])
            self.data_para['epoch_start'] = str(self.data.tmin)
            self.data_para['epoch_end'] = str(self.data.tmax)
            self.data_para['time_point'] = str(len(self.data._raw_times))
            self.data_para['event_class'] = str(len(set(self.events[:, 2])))
            self.data_para['event_num'] = str(len(self.events))
            self.data_para['data_size'] = str(round(0.5 *(self.data._size /((2 ** 10) ** 2)), 2))



class Subject(object):

    def __init__(self, name=None, coord=None, group=None,
                 b_obj=None, s_obj=None, c_obj=None):

        super(Subject, self).__init__()
        # key in seeg is the name of the data
        self.seeg = dict()
        self.name = name
        self.coord = coord
        self.group = group
        self.image = dict()
        self.s_obj = s_obj
        self.c_obj = c_obj





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




"""Screenshot window and related functions."""
from visbrain.io import write_fig_pyqt, dialog_save
from visbrain.utils import ScreenshotPopup
class UiScreenshot(object):
    """Initialize the screenshot GUI and functions to apply it."""

    def __init__(self):
        """Init."""
        canvas_names = ['main']
        self._ssGui = ScreenshotPopup(self._fcn_run_screenshot,
                                      canvas_names=canvas_names)

    def show_gui_screenshot(self):
        """Display the GUI screenhot."""
        self._ssGui.show()

    def _fcn_run_screenshot(self):
        """Run the screenshot."""
        # Get filename :
        filename = dialog_save(self, 'Screenshot', 'screenshot', "PNG(*.PNG)"
                               ";;TIFF(*.tiff);;JPG(*.jpg);;"
                               "All files(*.*)")
        # Get screenshot arguments :
        kwargs = self._ssGui.to_kwargs()

        if kwargs['entire']:  # Screenshot of the entire window
            self._ssGui._ss.close()
            write_fig_pyqt(self, filename)
        else:  # Screenshot of selected canvas
            # Remove unsed entries :
            del kwargs['entire']
            self.screenshot(filename, **kwargs)



