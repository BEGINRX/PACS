"""
@File: thread.py
@Author: BarryLiu
@Time: 2020/9/18 18:04
@Desc: create the threads for the main window
"""


from PyQt5.QtCore import QThread, pyqtSignal
from mne import io


class Import_Thread(QThread):
    '''one thread for import data'''

    trigger = pyqtSignal(object)

    def __init__(self):
        super(Import_Thread, self).__init__()
        # 数据路径
        self.data_path = ''
        self.seeg_data = ''


    def import_data(self):
        '''import data selected'''
        if self.data_path[-3:] == 'set':
            self.seeg_data = io.read_raw_eeglab(self.data_path, preload=True)
        elif self.data_path[-3:] == 'edf':
            self.seeg_data = io.read_raw_edf(self.data_path, preload=True)
        elif self.data_path[-3:] == 'fif':
            self.seeg_data = io.read_raw_fif(self.data_path, preload=True)


    def run(self):
        '''rewrite run'''
        try:
            self.import_data()
            print('data loaded')
            self.seeg_data.set_channel_types({ch_name: 'seeg' for ch_name in self.seeg_data.ch_names})
            self.seeg_data.set_channel_types({ch_name: 'misc' for ch_name in self.seeg_data.ch_names
                                              if 'DC' or 'Ref' in ch_name})
            self.trigger.emit(self.seeg_data)
            self.data_path = ''
            self.seeg_data = ''
        except TypeError:
            print('This is Type Error')
            self.trigger.emit(self.seeg_data)



class Load_Epoched_Data_Thread(QThread):
    '''a thread for loading epoched data'''

    load = pyqtSignal(object)

    def __init__(self):
        super(Load_Epoched_Data_Thread, self).__init__()
        self.data_path = ''
        self.seeg_data = ''

    def load_data(self):
        '''load epoched data'''
        if self.data_path[-3:] == 'set':
            self.seeg_data = io.read_epochs_eeglab(self.data_path)
        elif self.data_path[-3:] == 'fif':
            self.seeg_data = io.read_epochs(self.data_path)


    def run(self):
        '''rewrite run'''
        try:
            self.load_data()
            print('data loaded')
            self.load.emit(self.seeg_data)
            self.data_path = ''
            self.seeg_data = ''
        except AttributeError as error:
            print(error)
            self.load.emit(self.seeg_data)




class Resample_Thread(QThread):

    resample = pyqtSignal(object)

    def __init__(self):
        super(Resample_Thread, self).__init__()
        self.data = ''
        self.resampling_rate = ''


    def run(self):
        '''rewrite run'''
        if self.resampling_rate > 0:
            self.resample_data = self.data.copy().resample(self.resampling_rate)
            print('重采样结束')
            self.resample.emit(self.resample_data)
            self.data = ''
            self.resample_data = ''


class Filter_Thread(QThread):
    '''a thread for filters'''

    filter_signal = pyqtSignal(object)

    def __init__(self):
        super(Filter_Thread, self).__init__()

        self.seeg_data = None
        self.filter_mode = None
        self.low_freq = None
        self.high_freq = None
        self.notch_freq = None


    def run(self):
        '''重写run'''
        if self.seeg_data:
            if self.filter_mode == 'fir':
                if self.notch_freq and (not self.low_freq) and (not self.high_freq):
                    # 陷波
                    print('fir 陷波')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.notch_filter(self.notch_freq)
                elif (not self.notch_freq) and self.low_freq and (not self.high_freq):
                    # 高通
                    print('fir 高通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq,
                                                             self.high_freq)
                elif (not self.notch_freq) and (not self.low_freq) and self.high_freq:
                    # 低通
                    print('fir 低通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq,
                                                             self.high_freq)
                elif (not self.notch_freq) and self.low_freq and self.high_freq:
                    # 带通
                    print('fir 带通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq,
                                                             self.high_freq)
            elif self.filter_mode == 'iir':
                if self.notch_freq and (not self.low_freq) and (not self.high_freq):
                    # 陷波
                    print('iir 陷波')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.notch_filter(self.notch_freq,
                                                                   method='iir')
                elif (not self.notch_freq) and self.low_freq and (not self.high_freq):
                    # 高通
                    print('iir 高通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq, self.high_freq,
                                                             method='iir')
                elif (not self.notch_freq) and (not self.low_freq) and self.high_freq:
                    # 低通
                    print('iir 低通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq, self.high_freq,
                                                             method='iir')
                elif (not self.notch_freq) and self.low_freq and self.high_freq:
                    # 带通
                    print('iir 带通')
                    print('low_freq:', self.low_freq)
                    print('high_freq:', self.high_freq)
                    print('notch_freq:', self.notch_freq)
                    self.filter_data = self.seeg_data.filter(self.low_freq, self.high_freq,
                                                             method='iir')
            print('滤波结束')
            self.filter_signal.emit(self.filter_data)
            self.seeg_data = None
            self.low_freq = None
            self.high_freq = None
            self.notch_freq = None