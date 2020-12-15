"""
@File: thread.py
@Author: BarryLiu
@Time: 2020/9/18 18:04
@Desc: create the threads for the main window
"""

import traceback
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from mne import io
import mne
from mne.time_frequency import tfr_morlet, psd_multitaper, tfr_stockwell, tfr_multitaper
import numpy as np

def show_error(error):
    print('*********************************************************************')
    print('Error is: ')
    traceback.print_exc()
    print('*********************************************************************')

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
        print(self.data_path)
        if self.data_path[-3:] == 'set':
            self.seeg_data = io.read_raw_eeglab(self.data_path, preload=True)
        elif self.data_path[-3:] == 'edf':
            self.seeg_data = io.read_raw_edf(self.data_path, preload=True)
        elif self.data_path[-3:] == 'fif':
            self.seeg_data = io.read_raw_fif(self.data_path)


    def run(self):
        '''rewrite run'''
        try:
            self.import_data()
            print('data loaded')
            self.seeg_data.set_channel_types({ch_name: 'seeg' for ch_name in self.seeg_data.ch_names})
            self.trigger.emit(self.seeg_data)
            self.data_path = ''
            self.seeg_data = ''
        except Exception as error:
            show_error(error)
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
            self.seeg_data = mne.read_epochs(self.data_path)


    def run(self):
        '''rewrite run'''
        try:
            self.load_data()
            print('data loaded')
            self.load.emit(self.seeg_data)
            self.data_path = ''
            self.seeg_data = ''
        except Exception as error:
            show_error(error)
            self.load.emit(self.seeg_data)



class Resample_Thread(QThread):

    resample = pyqtSignal(object)

    def __init__(self):
        super(Resample_Thread, self).__init__()
        self.data = ''
        self.resampling_rate = ''


    def run(self):
        '''rewrite run'''
        try:
            if self.resampling_rate > 0:
                self.resample_data = self.data.copy().resample(self.resampling_rate)
                print('重采样结束')
                self.resample.emit(self.resample_data)
                self.data = ''
                self.resample_data = ''
        except Exception as error:
            show_error(error)



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
        try:
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
        except Exception as error:
            show_error(error)



class Calculate_Power(QThread):

    power_signal = pyqtSignal(object, list, list)

    def __init__(self, data, method, freq, time, chan_num):
        super(Calculate_Power, self).__init__()
        self.data = data
        self.method = method
        self.freq = freq
        self.time = time
        self.chan_num = chan_num



    def run(self):
        if self.method == 'Multitaper transform':
            freqs = np.logspace(*np.log10(self.freq), num=8)
            n_cycles = freqs / 2.  # different number of cycle per frequency
            time_bandwidth = 2.0
            power, itc = tfr_multitaper(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=True,
                                    time_bandwidth=time_bandwidth, decim=3, return_itc=False)
        elif self.method == 'Stockwell transform':
            width = 3.
            power = tfr_stockwell(self.data, fmin=self.freq[0], fmax=self.freq[1], width=width)
        elif self.method == 'Morlet Wavelets':
            freqs = np.logspace(*np.log10(self.freq), num=8)
            n_cycles = freqs / 2.  # different number of cycle per frequency
            power, itc = tfr_morlet(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=True,
                                    decim=3, return_itc=False)
        self.power_signal.emit(power, self.chan_num, self.time)



class Calculate_PSD(QThread):

    psd_signal = pyqtSignal(object, object, object)

    def __init__(self, data, fmin, fmax):

        super(Calculate_PSD, self).__init__()

        self.data = data
        self.fmin = fmin
        self.fmax = fmax


    def run(self):
        psds, freqs = psd_multitaper(self.data, fmin=self.fmin,
                                     fmax=self.fmax, n_jobs=2)
        psds = 10. * np.log10(psds)
        psds_mean = psds.mean(0).mean(0)
        psds_std = psds.mean(0).std(0)

        self.psd_signal.emit(psds_mean, psds_std, freqs)
