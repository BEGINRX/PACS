"""
@File: thread.py
@Author: BarryLiu
@Time: 2020/9/18 18:04
@Desc: create the threads for the main window
"""

import traceback
import numpy as np
from mne import io
from PyQt5.QtCore import QThread, pyqtSignal
import mne
from mne.time_frequency import tfr_morlet, psd_multitaper, psd_welch, \
                            tfr_stockwell, tfr_multitaper, csd_fourier, \
                            csd_multitaper, csd_morlet
from mne.connectivity import spectral_connectivity


def show_error(error):
    print('*********************************************************************')
    print('Error is: ')
    traceback.print_exc()
    print('*********************************************************************')

class Import_Thread(QThread):
    '''one thread for import data'''

    trigger = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Import_Thread, self).__init__(parent)
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
            self.seeg_data = io.read_raw_fif(self.data_path, preload=True)
        elif self.data_path[-4:] == 'vhdr':
            self.seeg_data = io.read_raw_brainvision(self.data_path, preload=True)


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

    def __init__(self, parent=None):
        super(Load_Epoched_Data_Thread, self).__init__(parent)
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

    def __init__(self, parent=None):
        super(Resample_Thread, self).__init__(parent)
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

    def __init__(self, parent=None):
        super(Filter_Thread, self).__init__(parent)

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

    power_signal = pyqtSignal(object, int, tuple, object)

    def __init__(self, data, method, chan_num, freq, time, use_fft, show_itc, parent=None):
        super(Calculate_Power, self).__init__(parent)
        self.data = data
        self.method = method
        self.chan_num = chan_num
        self.freq = freq
        self.time = time
        self.use_fft = use_fft
        self.show_itc = show_itc
        self.itc = None



    def run(self):
        if self.method == 'Multitaper transform':
            freqs = np.logspace(*np.log10(self.freq), num=8)
            n_cycles = freqs / 2.  # different number of cycle per frequency
            time_bandwidth = 2.0
            if self.show_itc:
                power, self.itc = tfr_multitaper(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=self.use_fft,
                                    time_bandwidth=time_bandwidth, decim=3)
            else:
                power = tfr_multitaper(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=self.use_fft,
                                       time_bandwidth=time_bandwidth, decim=3, return_itc=False)
        elif self.method == 'Stockwell transform':
            width = 3.
            if self.show_itc:
                power, self.itc = tfr_stockwell(self.data, fmin=self.freq[0], fmax=self.freq[1], width=width, return_itc=True)
            else:
                power = tfr_stockwell(self.data, fmin=self.freq[0], fmax=self.freq[1], width=width)
        elif self.method == 'Morlet Wavelets':
            freqs = np.logspace(*np.log10(self.freq), num=8)
            n_cycles = freqs / 2.  # different number of cycle per frequency
            if self.show_itc:
                power, self.itc = tfr_morlet(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=self.use_fft,
                                        decim=3)
            else:
                power = tfr_morlet(self.data, freqs=freqs, n_cycles=n_cycles, use_fft=self.use_fft,
                                   decim=3, return_itc=False)
        self.power_signal.emit(power, self.chan_num, self.time, self.itc)



class Calculate_PSD(QThread):

    psd_signal = pyqtSignal(str, object, object, object)

    def __init__(self, data, method, freq, time, nfft, average, parent=None):

        super(Calculate_PSD, self).__init__(parent)

        self.data = data
        self.method = method
        self.freq = freq
        self.time = time
        self.nfft = nfft
        self.average = average


    def run(self):
        if self.method == 'Multitaper':
            psds, freqs = psd_multitaper(self.data, fmin=self.freq[0], fmax=self.freq[1],
                                    tmin=self.time[0], tmax=self.time[1], n_jobs=2)
        elif self.method == 'Welch':
            psds, freqs = psd_welch(self.data, fmin=self.freq[0], fmax=self.freq[1],
                                    tmin=self.time[0], tmax=self.time[1], n_fft=self.nfft,
                                    average=self.average, n_jobs=2)
        psds = 10. * np.log10(psds)
        psds_mean = psds.mean(0).mean(0)
        psds_std = psds.mean(0).std(0)

        self.psd_signal.emit(self.method, psds_mean, psds_std, freqs)



class Cal_Spec_Con(QThread):

    spec_con_signal = pyqtSignal(list, list)

    def __init__(self, data, para, method, mode):
        super(Cal_Spec_Con, self).__init__()
        '''
        para['freq'] = [fmin, fmax]                 [float, float]
        para['time'] = [tmin, tmax]                 [float, float]
        para['bandwidth'] = bandwidth               float
        para['adaptive'] = use_adaptive             bool
        para['chan'] = [chanx_get, chany_get]       
        '''
        self.data = data
        self.para = para
        self.method = method
        self.sfreq = self.data.info['sfreq']
        self.mode = mode
        chan = self.data.ch_names
        self.indices = None
        if not para['chan']:
            self.indices = None
        else:
            chanx_index = np.array([chan.index(str(para['chan'][0][0]))] * len(para['chan'][1]))
            chany_index = np.array([chan.index (i) for i in para['chan'][1]])
            self.indices = (chanx_index, chany_index)

    def run(self):

        self.data.load_data()
        if self.mode == 'Multitaper':
            con, freqs, times, n_epochs, n_tapers = spectral_connectivity(
                self.data, method=self.method, mode='multitaper', sfreq=self.sfreq,
                fmin=self.para['freq'][0], fmax=self.para['freq'][1], faverage=True, tmin=self.para['time'][0],
                tmax=self.para['time'][1], mt_adaptive=self.para['adaptive'], indices=self.indices)
        elif self.mode == 'Fourier':
            con, freqs, times, n_epochs, n_tapers = spectral_connectivity(
                self.data, method=self.method, mode='fourier', sfreq=self.sfreq,
                fmin=self.para['freq'][0], fmax=self.para['freq'][1], faverage=True,
                tmin=self.para['time'][0], tmax=self.para['time'][1], indices=self.indices)
        elif self.mode == 'Morlet':
            self.cwt_freq = np.arange(self.freq, num=self.num)
            con, freqs, times, n_epochs, n_tapers = spectral_connectivity(
                self.data, method=self.method, mode='cwt_morlet', sfreq=self.sfreq, cwt_freqs=self.cwt_freq,
                cwt_n_cycles=self.cwt_freq/2, faverage=True, tmin=0., indices=self.indices)
        if len(con.shape) == 3:
            con = con[:, :, 0]
            con += con.T - np.diag (con.diagonal ())
        else:
            con = con.reshape(1, -1)

        self.spec_con_signal.emit([con, times], self.para['plot_mode'])



class Cal_Time_Con(QThread):
    from numpy import ndarray
    con_signal = pyqtSignal(ndarray, list, list)

    def __init__(self, data, method, para):
        super(Cal_Time_Con, self).__init__()
        self.data = data
        self.method = method
        self.para = para

    def run(self):
        try:
            from gui.my_func import get_pearson, get_spec_pearson, get_corr
        except:
            from my_func import get_pearson, get_spec_pearson, get_corr
        if self.method == 'pearson':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_spec_pearson(epochx, epochy)
            else:
                epochx, epochy = data, data
                con = get_pearson(data)
        elif self.method == 'envelope':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_spec_pearson(epochx, epochy)
            else:
                epochx, epochy = data, data
                con = mne.connectivity.envelope_correlation(data)
        elif self.method == 'mutual information':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_corr(epochx, epochy, baseline=self.para['baseline'])
            else:
                epochx, epochy = data, data
                con = get_corr(data, data)
        elif self.method == 'cross correlation':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_corr(epochx, epochy, baseline=self.para['baseline'], mode='full')
            else:
                epochx, epochy = data, data
                con = get_corr(data, data, baseline=self.para['baseline'], mode='full')
        elif self.method == 'granger causality':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_corr(epochx, epochy, baseline=self.para['baseline'])
            else:
                epochx, epochy = data, data
                con = get_corr(data, data)
        elif self.method == 'transfer entropy':
            data = self.data[self.para['event']]
            if not self.para['plot_mode'][0]:
                epochx = data.copy().pick_channels(self.para['chan'][0])
                epochy = data.copy().pick_channels(self.para['chan'][1])
                con = get_corr(epochx, epochy, baseline=self.para['baseline'])
            else:
                epochx, epochy = data, data
                con = get_corr(data, data)
        self.con_signal.emit(con, epochx.ch_names, epochy.ch_names)
