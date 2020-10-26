# -*- coding: utf-8 -*-
'''
@File  : main_window.py
@Author: 刘政
@Date  : 2020/9/17 15:14
@Desc  : main window
'''

import os
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QMenu, \
    QFileDialog, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QFormLayout, \
    QMessageBox, QProgressBar, QInputDialog, QLineEdit, QWidget, QActionGroup
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QPixmap, QFont
from gui.my_thread import Import_Thread, Load_Epoched_Data_Thread, Resample_Thread, Filter_Thread
from mne import events_from_annotations
from gui.sub_window import Choose_Window, Event_Window, Select_Data, Epoch_Time
import mne
import numpy as np
import scipy.io as sio
import gc
from matplotlib import pyplot as plt


def get_file_size(file_path):
    if file_path[-3:] == 'set':
        try:
            file_path = file_path[:-3] + 'fdt'
            file_size = os.path.getsize(file_path)
        except FileNotFoundError:
            file_path = file_path[:-3] + 'set'
            file_size = os.path.getsize(file_path)
    else:
        file_size = os.path.getsize(file_path)
    file_size = file_size / float(1024 * 1024)
    return round(file_size, 2)


class MainWindow(QMainWindow):
    '''
    The main window
    '''

    data_info_signal = pyqtSignal(dict)


    def __init__(self):
        super(MainWindow, self).__init__()

        self.flag = 0
        self.current_data = {}
        self.data_info = {'data_path':'', 'epoch_number':'', 'sampling_rate':'',
                          'channel_number':'', 'epoch_start':'', 'epoch_end':'', 'event_class':'',
                          'time_point':'', 'events':'', 'event_number':'', 'data_size':'',}
        # raw_seeg: data get from the device
        self.seeg = {}
        self.data_action = []
        self.action_num = 0
        self.data_mode = 'raw'
        self.event_set = None
        self.event = None

        self.init_ui()


    def init_ui(self):
        self.setWindowIcon(QIcon('image/source.jpg'))
        self.resize(1000, 680)
        self.center()
        self.create_central_widget()
        self.create_status_bar()
        self.create_workers()
        self.create_actions()
        self.create_buttons()
        self.create_labels()
        self.create_group_box()
        self.create_menubar()
        self.create_layout()
        self.set_qt_style()
        self.show()


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def create_central_widget(self):
        '''create a central groupbox widget to house other two sub groupboxes'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)


    def create_status_bar(self):
        '''create the status bar'''
        self.statusBar().showMessage('Ready')


    def create_workers(self):
        '''create workers   '''
        self.import_worker = Import_Thread()
        self.import_worker.trigger.connect(self.get_seeg_data)
        self.load_epoched_data_worker = Load_Epoched_Data_Thread()
        self.load_epoched_data_worker.load.connect(self.get_seeg_data)
        self.resample_worker = Resample_Thread()
        self.resample_worker.resample.connect(self.get_seeg_data)
        self.filter_worker = Filter_Thread()
        self.filter_worker.filter_signal.connect(self.get_seeg_data)


    def create_sub_windows(self):

        self.fir_filter_window = Choose_Window('fir')
        self.fir_filter_window.signal.connect(self.filter_subwindow_para)
        self.fir_filter_window.notch_signal.connect(self.filter_subwindow_para)
        self.iir_filter_window = Choose_Window('iir')
        self.iir_filter_window.signal.connect(self.filter_subwindow_para)
        self.iir_filter_window.notch_signal.connect(self.filter_subwindow_para)


    def create_actions(self):
        '''create actions for menu bar'''

        # actions for File menu bar
        #
        # import data
        self.import_menu = QMenu('Import raw data', self)
        self.import_set_data_action = QAction('Import .set data', self,
                                              statusTip='Import .set sEEG data',
                                              triggered=self.execute_import_data)
        self.import_edf_data_action = QAction('Import .edf data', self,
                                              statusTip='Import .edf sEEG data',
                                              triggered=self.execute_import_data)
        self.import_fif_data_action = QAction('Import .fif data', self,
                                              statusTip='Import .mat sEEG data',
                                              triggered=self.execute_import_data)
        self.import_menu.addActions([self.import_set_data_action,
                                     self.import_edf_data_action,
                                     self.import_fif_data_action])


        # Load epoched data
        self.load_epoched_data_menu = QMenu('Load epoched data', self)
        self.load_epoched_set_data = QAction('Load epoched .set data', self,
                                            statusTip='Load epoched sEEG data',
                                            triggered=self.execute_load_epoched_data)
        self.load_epoched_fif_data = QAction('Load epoched .fif data', self,
                                             statusTip='Load epoched sEEG data',
                                             triggered=self.execute_load_epoched_data)
        self.load_epoched_data_menu.addActions([self.load_epoched_set_data,
                                                self.load_epoched_fif_data])


        # save data
        self.save_menu = QMenu('Save data', self)
        self.save_fif_data_action = QAction('Save as .fif file', self,
                                            statusTip='Save sEEG data in .fif format',
                                            triggered=self.save_fif_data)
        self.save_menu.addActions([self.save_fif_data_action])


        # export submenu
        self.export_menu = QMenu('Export data and events', self)
        self.export_npy_data = QAction('Export as .npy', self,
                                   statusTip='Export sEEG data and events as .npy',
                                   triggered=self.export_npy)
        self.export_mat_data = QAction('Export as .mat', self,
                                   statusTip='Export sEEG data and events as .mat',
                                   triggered=self.export_mat)
        self.export_menu.addActions([self.export_npy_data, self.export_mat_data])


        # delete data and clear the workshop
        self.delete_data = QAction('Delete some data', self,
                                   statusTip='Choose some data to Delete',
                                   triggered=self.del_data)
        self.clear_all = QAction('Clear all data', self,
                                 statusTip='Clear All Data',
                                 triggered=self.clear_all)


        # exit
        self.exit_action = QAction('Exit', self,
                                   shortcut=QKeySequence.Close,
                                   statusTip='Exit the Software',
                                   triggered=self.close)


        # actions for Edit menu bar
        #
        # select data
        self.select_data_action = QAction('Select Data', self,
                                          statusTip='Select Data',
                                          triggered=self.select_data)
        # set event id
        self.set_event_id_action = QAction('Set Event ID', self,
                                           statusTip='Set Event ID',
                                           triggered=self.get_event_id)
        self.set_marker_channel_action = QAction('Set Marker Channels', self,
                                               statusTip='Set Marker Channels',
                                                 triggered=self.set_marker_chan)
        self.rename_chan_action = QAction('Rename channels', self,
                                          statusTip='Rename channels by deleting POL',
                                          triggered=self.rename_chan)
        self.del_chan_menu = QMenu('Delete channels', self)
        self.del_ref_action = QAction('Delete Ref channels', self,
                                      statusTip='Delete Ref channels',
                                      triggered=self.del_ref_chan)
        self.del_mark_chan_action = QAction('Delete the Stim Channels', self,
                                            statusTip='Delete the Stimulus Channel',
                                            triggered=self.del_marker_chan)
        self.del_mark_chan_action.setEnabled(False)
        self.del_useless_chan_action = QAction('Delete useless channels', self,
                                               statusTip='Delete Useless channels',
                                               triggered=self.del_useless_chan)
        self.del_useless_chan_action.setEnabled(False)
        self.del_chan_menu.addActions([self.del_ref_action,
                                       self.del_mark_chan_action,
                                       self.del_useless_chan_action])

        # 计算码 -- 总医院数据需要
        self.calculate_marker_action = QAction('Calculate marker', self,
                                               statusTip='Calculate marker using marker channels',
                                               triggered=self.calculate_marker)
        # get epoch
        self.get_epoch_action = QAction('Get epoch', self,
                                        statusTip='Get epoch data after set event',
                                        triggered=self.get_epoch_time_range)


        # actions for Tool menu bar
        #
        # resample action
        self.resample_action = QAction('Resample the data', self,
                                       statusTip='Resample sEEG data',
                                       triggered=self.execute_resample_data)
        # filter submenu and actions
        self.filter_menu = QMenu('Filter the data', self)
        self.fir_filter = QAction('FIR filter', self,
                                  statusTip='Filt data with FIR filter',
                                  triggered=self.filter_data_fir)
        self.iir_filter = QAction('IIR filter', self,
                                  statusTip='Filt data with IIR filter',
                                  triggered=self.filter_data_iir)
        self.filter_menu.addActions([self.fir_filter,
                                     self.iir_filter])


        # actions for Analysis menu bar
        #
        # time-frequency analysis
        self.time_frequency_analysis_menu = QMenu('Time-Frequency Analysis', self)
        self.Hilbert_action = QAction('Hilbert', self,
                                      statusTip='Hilbert Methods',
                                    triggered=self.hilbert_method)
        self.Wavelet_action = QAction('Wavelet', self,
                                      statusTip='Wavelet Methods',
                                      triggered=self.wavelet_method)
        self.time_frequency_analysis_menu.addActions([self.Hilbert_action,
                                                      self.Wavelet_action])

        # spectral analyses
        self.spectral_analysis_menu = QMenu('Spectral Analysis', self)
        self.spectral_power_action = QAction('Spectral Power', self,
                                             statusTip='Spectral Power Measures',
                                             triggered=self.spectral_power)
        self.spectral_variance_action = QAction('Spectral Variance', self,
                                                statusTip='Spectral Variance Measures',
                                                triggered=self.spectral_variance)
        self.spectral_utilities_action = QAction('Spectral Utilities', self, statusTip='Spectral Utilities',
                                                 triggered=self.spectral_utilities)
        self.spectral_analysis_menu.addActions([self.spectral_power_action,
                                                self.spectral_variance_action,
                                                self.spectral_utilities_action])

        # actions for Plot menu barLa
        #
        # plot raw data
        self.plot_raw_action = QAction('Plot time-frequency data', self,
                                       statusTip='Plot data',
                                       triggered=self.plot_raw_data)
        self.plot_psd_action = QAction('Plot PSD across channels', self,
                                      statusTip='Plot data',
                                      triggered=self.plot_psd_func)

        # actions for Data menu bar
        #
        # action group
        self.data_action_group = QActionGroup(self)

        # actions for Help menu bar
        #
        #


    def create_buttons(self):
        '''create buttons'''
        # buttons for
        #
        #
        pass


    def create_progress_bar(self):
        '''create progress for needs'''
        self.import_bar = QProgressBar(self)
        self.filter_bar = QProgressBar(self)


    def create_labels(self):
        '''reate labels'''
        # labels for main window
        #
        # basic info of the subject
        self.file_name_label = QLabel('Filename', self)
        self.file_name_label.setProperty('name', 'group0')
        self.file_name_label.setFixedWidth(165)
        self.file_name_label.setAlignment(Qt.AlignLeft)

        self.file_name_content_label = QLabel(self)
        self.file_name_content_label.setProperty('name', 'group1')
        self.file_name_content_label.setAlignment(Qt.AlignCenter)
        self.file_name_content_label.setWordWrap(True)

        self.epoch_number_label = QLabel('Epochs', self)
        self.epoch_number_label.setProperty('name', 'group0')
        self.epoch_number_label.setFixedWidth(165)
        self.epoch_number_label.setAlignment(Qt.AlignLeft)

        self.epoch_num_content_label = QLabel(self)
        self.epoch_num_content_label.setProperty('name', 'group1')
        self.epoch_num_content_label.setAlignment(Qt.AlignCenter)
        self.epoch_num_content_label.setWordWrap(True)

        self.sampling_rate_label = QLabel('Sampling Rate (Hz)', self)
        self.sampling_rate_label.setFixedWidth(165)
        self.sampling_rate_label.setProperty('name', 'group0')
        self.sampling_rate_label.setAlignment(Qt.AlignLeft)

        self.sampling_rate_content_label = QLabel(self)
        self.sampling_rate_content_label.setProperty('name', 'group1')
        self.sampling_rate_content_label.setAlignment(Qt.AlignCenter)

        self.start_label = QLabel('Epoch Start (sec)', self)
        self.start_label.setProperty('name', 'group0')
        self.start_label.setFixedWidth(165)
        self.start_label.setAlignment(Qt.AlignLeft)

        self.start_content_label = QLabel(self)
        self.start_content_label.setProperty('name', 'group1')
        self.start_content_label.setAlignment(Qt.AlignCenter)

        self.end_label = QLabel('Epoch End (sec)', self)
        self.end_label.setProperty('name', 'group0')
        self.end_label.setFixedWidth(165)
        self.end_label.setAlignment(Qt.AlignLeft)

        self.end_content_label = QLabel(self)
        self.end_content_label.setProperty('name', 'group1')
        self.end_content_label.setAlignment(Qt.AlignCenter)

        self.channels_label = QLabel('Channel', self)
        self.channels_label.setFixedWidth(165)
        self.channels_label.setProperty('name', 'group0')
        self.channels_label.setAlignment(Qt.AlignLeft)

        self.channels_content_label = QLabel(self)
        self.channels_content_label.setProperty('name', 'group1')
        self.channels_content_label.setAlignment(Qt.AlignCenter)

        self.event_class_label = QLabel('Event Class', self)
        self.event_class_label.setFixedWidth(165)
        self.event_class_label.setProperty('name', 'group0')
        self.event_class_label.setAlignment(Qt.AlignLeft)

        self.event_class_content_label = QLabel(self)
        self.event_class_content_label.setProperty('name', 'group1')
        self.event_class_content_label.setAlignment(Qt.AlignCenter)

        self.event_number_label = QLabel('Event Number', self)
        self.event_number_label.setFixedWidth(165)
        self.event_number_label.setProperty('name', 'group0')
        self.event_number_label.setAlignment(Qt.AlignLeft)

        self.event_number_content_label = QLabel(self)
        self.event_number_content_label.setProperty('name', 'group1')
        self.event_number_content_label.setAlignment(Qt.AlignCenter)

        self.time_point_label = QLabel('Time Points', self)
        self.time_point_label.setFixedWidth(165)
        self.time_point_label.setProperty('name', 'group0')
        self.time_point_label.setAlignment(Qt.AlignLeft)

        self.time_point_content_label = QLabel(self)
        self.time_point_content_label.setProperty('name', 'group1')
        self.time_point_content_label.setAlignment(Qt.AlignCenter)

        self.data_size_label = QLabel('Data Size (MB)', self)
        self.data_size_label.setFixedWidth(165)
        self.data_size_label.setProperty('name', 'group0')
        self.data_size_label.setAlignment(Qt.AlignLeft)

        self.data_size_content_label = QLabel(self)
        self.data_size_content_label.setProperty('name', 'group1')
        self.data_size_content_label.setAlignment(Qt.AlignCenter)


        # 3—D image of brain altas and electrodes locations
        self.brain_loc_label = QLabel(self)
        # brain_loc_label_pic = QPixmap('./image/source.jpg')
        # self.brain_loc_label.setPixmap(brain_loc_label_pic)
        self.brain_loc_label.setAlignment(Qt.AlignJustify)


    def create_group_box(self):
        '''create group boxes for main window'''
        # subject info box
        self.data_info_box = QGroupBox('sEEG data information')
        # the brain template and electrodes locations
        self.brain_electrodes_box = QGroupBox('brain template and electrodes locations')
        #


    def create_menubar(self):
        '''create menu bars'''

        # file menu bar
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addMenu(self.import_menu)
        self.file_menu.addMenu(self.save_menu)
        self.file_menu.addMenu(self.load_epoched_data_menu)
        self.file_menu.addSeparator()
        self.file_menu.addMenu(self.export_menu)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.delete_data)
        self.file_menu.addAction(self.clear_all)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)


        # Edit menu bar
        self.edit_menu = self.menuBar().addMenu('Edit')
        self.edit_menu.addAction(self.select_data_action)
        self.edit_menu.addAction(self.set_event_id_action)
        self.edit_menu.addAction(self.rename_chan_action)
        self.edit_menu.addAction(self.calculate_marker_action)
        self.edit_menu.addMenu(self.del_chan_menu)
        self.edit_menu.addAction(self.get_epoch_action)
        self.edit_menu.setEnabled(False)


        # Tool menu bar
        self.tool_menu = self.menuBar().addMenu('Tool')
        self.tool_menu.addAction(self.resample_action)
        self.tool_menu.addMenu(self.filter_menu)
        self.tool_menu.setEnabled(False)

        # Analysis menu bar
        self.analysis_menu = self.menuBar().addMenu('Analysis')
        self.analysis_menu.addMenu(self.time_frequency_analysis_menu)
        self.analysis_menu.addMenu((self.spectral_analysis_menu))
        self.analysis_menu.setEnabled(False)

        # Plot menu bar
        self.plot_menu = self.menuBar().addMenu('Plot')
        self.plot_menu.addAction(self.plot_raw_action)
        self.plot_menu.setEnabled(False)

        # Data menu bar
        self.data_menu = self.menuBar().addMenu('Data')
        self.data_menu.setEnabled(False)


        # Help menu bar
        self.help_menu = self.menuBar().addMenu('Help')
        # help_menu.addAction(self.help0_action)


    def create_layout(self):
        '''set the layout for the app'''
        # layout for the main window
        #
        # layout for data info box
        info_form_layout = QFormLayout()
        info_form_layout.setVerticalSpacing(30)
        info_form_layout.setHorizontalSpacing(5)
        info_form_layout.addRow(self.file_name_label, self.file_name_content_label)
        info_form_layout.addRow(self.epoch_number_label, self.epoch_num_content_label)
        info_form_layout.addRow(self.sampling_rate_label, self.sampling_rate_content_label)
        info_form_layout.addRow(self.channels_label, self.channels_content_label)
        info_form_layout.addRow(self.start_label, self.start_content_label)
        info_form_layout.addRow(self.end_label, self.end_content_label)
        info_form_layout.addRow(self.event_class_label, self.event_class_content_label)
        info_form_layout.addRow(self.event_number_label, self.event_number_content_label)
        info_form_layout.addRow(self.time_point_label, self.time_point_content_label)
        info_form_layout.addRow(self.data_size_label, self.data_size_content_label)
        self.data_info_box.setLayout(info_form_layout)
        self.data_info_box.setFixedWidth(400)


        # layout for brain template and electrodes locations
        brain_electrode_vbox_layout = QVBoxLayout()
        brain_electrode_vbox_layout.addWidget(self.brain_loc_label)
        self.brain_electrodes_box.setLayout(brain_electrode_vbox_layout)

        # layout for main window
        main_window_layout = QHBoxLayout()
        main_window_layout.addWidget(self.data_info_box)
        main_window_layout.addWidget(self.brain_electrodes_box)
        self.center_widget.setLayout(main_window_layout)


    def set_qt_style(self):
        '''use QSS to beautify the interface'''

        # 备用字体：Arial、Consolas、Tahoma、Segoe UI、
        # Label
        self.setStyleSheet('''QLabel[name='group0']{color:black; font: bold 20px Times New Roman}
                              QLabel[name='group1']{color:rgb(46, 117, 182); font: bold 20px Arial}''')
        self.brain_loc_label.setStyleSheet('''QLabel{Background-color:rgb(180, 180, 180)}''')

        # set
        self.menuBar().setStyleSheet('''QMenuBar{border: 5px solid rgb(255, 255, 255)}''')

        # GroupBox
        self.data_info_box.setStyleSheet('''QGroupBox{font: bold 15px Arial; color:blue}''')
        self.brain_electrodes_box.setStyleSheet('''QGroupBox{font: bold 15px Arial; color:blue}''')

        # background
        self.center_widget.setStyleSheet('''QWidget{Background-color: white}''')




#*****************************************slot*****************************************

############################################# File ######################################################
    # File menu function
    #
    # import sEEG data
    def execute_import_data(self):
        '''execute import data worker'''
        self.data_path, _ = QFileDialog.getOpenFileName(self, 'Import data')
        if self.data_path[-3:] == 'set' or \
           self.data_path[-3:] == 'edf' or \
           self.data_path[-3:] == 'fif':
            self.import_worker.data_path = self.data_path
            self.import_worker.start()
            self.flag += 1
            self.data_mode = 'raw'
        elif self.flag == 0 and self.data_path:
            QMessageBox.warning(self, 'Data Format Error',
                                'Please select the right file!')

    def execute_load_epoched_data(self):
        '''execute load epoched data'''
        self.data_path, _ = QFileDialog.getOpenFileName(self, 'Import data')
        if self.data_path[-3:] == 'set' or \
           self.data_path[-3:] == 'fif':
            self.load_epoched_data_worker.data_path = self.data_path
            self.load_epoched_data_worker.start()
            self.flag += 1
            self.data_mode = 'epoch'
        elif self.flag == 0 and self.data_path:
            self.seeg_data = ''
            QMessageBox.warning(self, 'Data Format Error',
                                'Please select the right file!')


    def create_action_for_data(self, key):
        '''create action for data menu'''
        self.action_num += 1
        self.new_data_action = QAction('Data ' + str(self.action_num) + ': ' + key, self)
        self.new_data_action.setCheckable(True)
        self.new_data_action.setChecked(True)
        self.new_data_action.triggered.connect(lambda :self.set_current_data(key))
        # 将data的action添加到ActionGroup中，实现action的互斥属性
        self.data_action_group.addAction(self.new_data_action)
        if len(self.data_action):
            self.data_action[-1].setChecked(False)
        self.data_action.append(self.new_data_action)
        self.data_menu.addActions(self.data_action)


    def get_seeg_data(self, seeg_data):
        '''get seeg data'''
        if seeg_data.ch_names:
            self.key, _ = QInputDialog.getText(self, 'Name this Data', 'Please Name the Data',
                                          QLineEdit.Normal)
            if self.key:
                self.seeg[self.key] = {}
                self.seeg[self.key]['data'] =  seeg_data
                self.seeg[self.key]['data_path'] = self.data_path
                self.seeg[self.key]['data_mode'] = self.data_mode
                if self.data_mode == 'raw':
                    self.seeg[self.key]['event'], _ = mne.events_from_annotations(seeg_data)
                elif self.data_mode == 'epoch':
                    self.seeg[self.key]['event'], _ = mne.events_from_annotations(seeg_data._raw)
                self.event = self.seeg[self.key]['event']
                # print(self.seeg)
                self.set_current_data(key=self.key)
                del seeg_data
                gc.collect()
                print(self.key, type(self.key))
                self.create_action_for_data(key=self.key)
                self.edit_menu.setEnabled(True)
                self.tool_menu.setEnabled(True)
                self.analysis_menu.setEnabled(True)
                self.plot_menu.setEnabled(True)
                self.data_menu.setEnabled(True)
            else:
                QMessageBox.warning(self, 'Name Error',
                                    'Please name the data')
        else:
            QMessageBox.warning(self, 'Fromat Error', 'Data is Epoched')


    def set_current_data(self, key):
        '''set the curent seeg data'''
        self.current_data = self.seeg[key]
        print('set data', key)
        self.get_data_info()


    def get_data_info(self):
        '''get seeg data info'''
        if self.current_data['data'].ch_names:
            if self.data_mode == 'raw':
                self.data_info['data_path'] = self.current_data['data_path']
                self.data_info['epoch_number'] = 1
                self.data_info['sampling_rate'] = self.current_data['data'].info['sfreq']
                self.data_info['channel_name'] = self.current_data['data'].info['ch_names']
                self.data_info['channel_number'] = len(self.data_info['channel_name'])
                self.data_info['epoch_start'] = self.current_data['data']._first_time
                self.data_info['epoch_end'] = round(self.current_data['data']._last_time, 2)
                self.data_info['time_point'] = self.current_data['data'].n_times
                self.data_info['events'], _ = events_from_annotations(self.current_data['data'])
                self.data_info['event_class'] = len(set(self.data_info['events'][:,2]))
                self.data_info['event_number'] = len(self.data_info['events'])
                self.data_info['data_size'] = round(0.5 * (self.current_data['data']._size / ((2**10)**2)), 2)
            elif self.data_mode == 'epoch':
                self.data_info['data_path'] = self.current_data['data_path']
                self.data_info['sampling_rate'] = self.current_data['data']._raw.info['sfreq']
                self.data_info['channel_name'] = self.current_data['data']._raw.info['ch_names']
                self.data_info['channel_number'] = len(self.data_info['channel_name'])
                self.data_info['time_point'] = len(self.current_data['data']._raw_times)
                self.data_info['event_number'] = len(self.current_data['data'].events)
                self.data_info['data_size'] = round(0.5 * (self.current_data['data']._size / ((2 ** 10) ** 2)), 2)
        self.data_info_signal.connect(self.update_func)
        self.data_info_signal.emit(self.data_info)
        self.create_sub_windows()


    # save sEEG data
    def save_fif_data(self):
        '''save as .fif data'''
        if self.data_info['data_path']:
            self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            print(self.save_path)
            if self.save_path:
                self.current_data['data'].save(self.save_path + '.fif')
        else:
            QMessageBox.warning(self, 'Data Save Error', 'No data to be saved!')


    def export_npy(self):

        if self.current_data:
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            print(save_path)
        if save_path:
            np.save(save_path + '_data', self.current_data['data'])
            # try:
            np.save(save_path + '_label', self.current_data['event'])
            # except:
        else:
            QMessageBox.warning(self, 'Data Save Error', 'No data to be saved!')


    def export_mat(self):

        if self.current_data:
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            print(save_path)
        if save_path:
            sio.savemat(self.save_path + '_data.mat', {'seeg_data':self.current_data})
            sio.savemat(self.save_path + '.label', {'label':'event'})
        else:
            QMessageBox.warning(self, 'Data Save Error', 'No data to be saved!')


    def del_data(self):

        text = []
        length = list(range(len(self.data_action)))
        length = [str(i+1) for i in length]
        length = ','.join(length)
        num, _ = QInputDialog.getText(self, 'Delete Data', 'Please write the number of data',
                                    QLineEdit.Normal, length)

        if len(num) > 0:
            num = list(num.split(','))
        if len(length) == 0:
            if len(num) > 0:
                print(len(num))
                QMessageBox.warning(self, 'No Data Error', 'No Data to be deleted')
            elif not len(num):
                pass
        elif len(length) > 0:
            if len(num) > len(length):
                QMessageBox.warning(self, 'Delete Error', 'Too many numbers!')
            elif set(list(num)).issubset(set(list(length))):
                for i in num:
                    i = int(i)
                    index = self.data_action[i-1].text().find(':') + 2
                    name = self.data_action[i-1].text()[index:]
                    text = self.data_action[i-1].text()[:index] + '-----'
                    self.data_action[i-1] = QAction(text, self)
                    try:
                        del self.seeg[name]
                    except KeyError:
                        QMessageBox.warning(self, 'Data Error', 'No Data in Data ' + str(i))
            else:
                QMessageBox.warning(self, 'Number Error', 'Wrong number chosen')
        self.data_menu.clear()
        self.data_menu.addActions(self.data_action)


    def clear_all(self):
        '''clear the whole workshop'''
        if self.current_data['data'].ch_names:
            self.flag = 0
            del self.current_data
            del self.data_info
            del self.seeg
            del self.data_action
            del self.event
            self.data_info = {'data_path':'', 'sampling_rate':'',
                              'channel_number':'', 'time_point':'',
                              'events':'', 'event_number':'', 'data_size':'',}
            self.current_data = {}
            self.data_action = []
            self.seeg = {}
            self.event = None
            self.action_num = 0
            self.data_menu.clear()
            gc.collect()
            self.edit_menu.setEnabled(False)
            self.tool_menu.setEnabled(False)
            self.analysis_menu.setEnabled(False)
            self.plot_menu.setEnabled(False)
            self.data_menu.setEnabled(False)
            self.del_mark_chan_action.setEnabled(False)
            self.del_useless_chan_action.setEnabled(False)
            self.data_info_signal.emit(self.data_info)
        else:
            pass

############################################# Edit ######################################################
    # Edit menu function
    #
    # select data
    def select_data(self):

        if self.current_data['data_mode'] == 'raw':
            self.select_data_window = Select_Data(data_mode=self.current_data['data_mode'],
                                                  end_time=round(self.current_data['data']._last_time),
                                                  channel_name=self.data_info['channel_name'])
            self.select_data_window.time_signal.connect(self.get_time)
            self.select_data_window.chan_signal.connect(self.get_del_channel)
        elif self.current_data['data_mode'] == 'epoch':
            self.select_data_window = Select_Data(data_mode=self.current_data['data_mode'],
                                                  channel_name=self.data_info['channel_name'])
            self.select_data_window.time_signal.connect(self.get_time)
            self.select_data_window.chan_signal.connect(self.get_del_channel)

        self.select_data_window.show()


    def get_time(self, time):

        self.time_new = time
        print('main window', self.time_new)
        crop_data = self.current_data['data'].copy().crop(self.time_new[0], self.time_new[1])
        self.get_seeg_data(crop_data)


    def get_del_channel(self, channel):

        self.channel_new = channel
        print('main window', self.channel_new)
        del_channel_data = self.current_data['data'].copy().drop_channels(self.channel_new)
        self.get_seeg_data(del_channel_data)


    def rename_chan(self):
        '''delete the 'POL' in channels' name '''
        rename_chan_data = self.current_data['data'].copy().\
            rename_channels({chan: chan[4:] for chan in self.current_data['data'].ch_names
                             if 'POL' in chan})
        # print(rename_chan_data)
        self.get_seeg_data(rename_chan_data)


    def del_useless_chan(self):
        '''delete useless channels'''
        chans = self.current_data['data'].ch_names
        useless_chan = [chan for chan in chans if 'DC' in chan or 'BP' in chan
                        or 'EKG' in chan or 'EMG' in chan]
        print(useless_chan)
        del_useless_data = self.current_data['data'].copy().drop_channels(useless_chan)
        self.get_seeg_data(del_useless_data)


    def del_ref_chan(self):
        '''delete reference channels'''
        ref_channel = [ref_chan for ref_chan in self.current_data['data'].ch_names if ref_chan[-3:] == 'Ref']
        if ref_channel:
            del_ref_data = self.current_data['data'].copy().drop_channels(ref_channel)
            self.get_seeg_data(del_ref_data)


    def del_marker_chan(self):
        '''delete marker channels'''
        marker_channel = ['POL DC09', 'POL DC10', 'POL DC11', 'POL DC12',
                         'POL DC13', 'POL DC14', 'POL DC15']
        # try:
        del_stim_data = self.current_data['data'].copy().drop_channels(marker_channel)
        # except
        self.get_seeg_data(del_stim_data)


    def calculate_marker(self):
        '''calculate the markers for sEEG from Shenzhen University General Hosptial'''
        marker_channel = ['POL DC09', 'POL DC10', 'POL DC11', 'POL DC12',
                           'POL DC13', 'POL DC14', 'POL DC15']
        try:
            mark_data = self.current_data['data'].copy().pick_channels(marker_channel)._data * 1e6
        except ValueError:
            QMessageBox.warning(self, 'Marker Calculating Error', 'No channels match the selection')
        else:
            mark_data_mean = np.mean(mark_data, axis=1).reshape(7, 1)
            mark_data_mean = np.tile(mark_data_mean, (1, mark_data.shape[1]))  # 计算均值并拓展到和数据一样的维度
            mark_data = mark_data - mark_data_mean  # 去均值
            del mark_data_mean
            gc.collect()
            # ddof=1为计算样本方差，分母为N-1
            mark_var_1 = np.std(mark_data, 1, ddof=1).reshape(7, 1)
            max_var = 10 * mark_var_1.max()
            event = np.zeros(mark_data.shape)
            event[mark_data > max_var] = 1
            event_id_tmp = event[0, :] + event[1, :] * 2 + event[2, :] * 2 ** 2 + event[3, :] * 2 ** 3 + \
                           event[4, :] * 2 ** 4 + event[5, :] * 2 ** 5 + event[6, :] * 2 ** 6
            event_tmp = np.hstack([0, np.diff(event_id_tmp)])
            self.event_latency = np.array(np.where(event_tmp > 0), dtype=np.int64)
            self.event_id = event_id_tmp[self.event_latency].astype(np.int64)


            freq = self.current_data['data'].info['sfreq']
            event_onset = (self.event_latency / freq).astype(np.float64)
            self.my_annot = mne.Annotations(
                onset=event_onset[0, :], duration=np.zeros(event_onset[0, :].shape[0]),
                description=self.event_id[0, :])
            annot_data = self.current_data['data'].copy().set_annotations(self.my_annot)
            self.event, _ = mne.events_from_annotations(self.current_data['data'])

            self.event_test = np.zeros((self.event_id.shape[1], 3)).astype(np.int32)
            self.event_test[:, 0], self.event_test[:, 2] = self.event_latency, self.event_id

            if self.event.all() == self.event_test.all():
                print('码可通过')
            self.get_seeg_data(annot_data)
            self.del_mark_chan_action.setEnabled(True)
            self.del_useless_chan_action.setEnabled(True)


    # set event id_dict
    def get_event_id(self):

        para = list(set(self.current_data['event'][:, 2]))
        print(para)
        self.event_window = Event_Window(para)
        self.event_window.line_edit_signal.connect(self.set_event)
        self.event_window.show()


    def set_event(self, event_name, event_id):

        print('主界面', event_name, event_id)
        for i in range(len(event_name)):
            self.event_set[event_name[i]] = int(event_id[i])
        print(self.event_set)


    def get_epoch_time_range(self):

        self.epoch_time = Epoch_Time()
        self.epoch_time.time_signal.connect(self.get_epoch_data)
        self.epoch_time.show()


    def get_epoch_data(self, tmin, tmax):
        if self.current_data['event'].shape[1] == 3:
            if tmin < 0 and tmax >= 0:
                print(self.event_set)
                epoch_data = mne.Epochs(self.current_data['data'], self.current_data['event'], event_id=self.event_set,
                                        tmin=tmin, tmax=tmax)
                self.data_mode = 'epoch'
                self.get_seeg_data(epoch_data)
            elif tmin == 0:
                print(self.event_set)
                epoch_data = mne.Epochs(self.current_data['data'], self.current_data['event'], event_id=self.event_set,
                                        baseline=(0, 0))
                self.data_mode = 'epoch'
                self.get_seeg_data(epoch_data)

    def set_marker_chan(self):
        '''write marker channels' name'''
        pass

############################################# Tool ######################################################
    # Tool menu function
    #
    # resample the seeg data
    def execute_resample_data(self):
        if self.data_info['data_path']:
            self.resample_worker.resampling_rate,_ = self.value, _ = QInputDialog.getInt(self, 'Resample Data', 'Resample Rate (Hz)', 0, 0)
            print(self.resample_worker.resampling_rate)
            if self.resample_worker.resampling_rate > 0:
                print('开始重采样')
                self.resample_worker.data = self.current_data['data']
                self.resample_worker.start()

    # filt sEEG data with fir filter
    def filter_data_fir(self):

        self.filter_worker.filter_mode = 'fir'
        self.fir_filter_window.show()

    # filt sEEG data with iir filter
    def filter_data_iir(self):

        self.filter_worker.filter_mode = 'iir'
        self.iir_filter_window.show()

    def filter_subwindow_para(self, low_freq, high_freq, notch_freq):
        '''
        :param low_freq: lowpass cut frequency
        :param high_freq: highpass cut frequency
        :param notch_freq: notch frequency
        :return:
        '''
        print(low_freq, high_freq, notch_freq)
        if low_freq == 'None':
            low_freq = None
        elif low_freq:
            low_freq = float(low_freq)
        if high_freq == 'None':
            high_freq = None
        elif high_freq:
            high_freq = float(high_freq)
        if notch_freq == 'None':
            notch_freq = None
        elif notch_freq:
            notch_freq = float(notch_freq)
        self.filter_worker.low_freq = low_freq
        self.filter_worker.high_freq = high_freq
        self.filter_worker.notch_freq = notch_freq
        print('到这', type(self.filter_worker.low_freq), '\n',
              type(self.filter_worker.high_freq), '\n',
                type(self.filter_worker.notch_freq))
        print('到这', self.filter_worker.low_freq, '\n',
              self.filter_worker.high_freq, '\n',
              self.filter_worker.notch_freq)
        if self.filter_worker.low_freq or self.filter_worker.high_freq or \
            self.filter_worker.notch_freq:
            self.filter_worker.seeg_data = self.current_data['data']
            # self.filter_worker.filter_mode= 'fir'
            self.filter_worker.start()

    # Analysis menu function
    #
    # hilbert method for time-frequency analyses
    def hilbert_method(self):
        pass

    # wavelet method for time-frequency analyses
    def wavelet_method(self):
        pass

    # spectral power measures for spectral analyses
    def spectral_power(self):
        pass

    # spectral variance measures for spectral analyses
    def spectral_variance(self):
        pass

    # spectral utilities
    def spectral_utilities(self):
        pass

############################################# Plot ######################################################
    # Plot menu function
    #
    # plot raw data
    def plot_raw_data(self):
        if self.current_data['data_mode'] == 'raw':
            self.current_data['data'].plot(duration=5.0, n_channels=self.data_info['channel_number'], title='Raw sEEG data')
        elif self.current_data['data_mode'] == 'epoch':
            self.current_data['data'].plot(n_channels=self.data_info['channel_number'], title='Epoched sEEG data')

    # plot psd across channels
    def plot_psd_func(self):
        if self.current_data['data'].ch_names:
            self.current_data['data'].plot_psd()

    # Help menu function
    #



    def update_func(self, data_info):
        '''update label text'''
        try:
            if self.current_data['data'].ch_names:
                self.file_name_content_label.setText(str(data_info['data_path']))
                self.epoch_num_content_label.setText(str(data_info['epoch_number']))
                self.sampling_rate_content_label.setText(str(data_info['sampling_rate']))
                self.channels_content_label.setText(str(data_info['channel_number']))
                self.start_content_label.setText(str(data_info['epoch_start']))
                self.end_content_label.setText(str(data_info['epoch_end']))
                self.event_class_content_label.setText(str(data_info['event_class']))
                self.event_number_content_label.setText(str(data_info['event_number']))
                self.time_point_content_label.setText(str(data_info['time_point']))
                self.data_size_content_label.setText(str(data_info['data_size']))
        except:
            self.file_name_content_label.setText('')
            self.epoch_num_content_label.setText('')
            self.sampling_rate_content_label.setText('')
            self.channels_content_label.setText('')
            self.start_content_label.setText('')
            self.end_content_label.setText('')
            self.event_class_content_label.setText('')
            self.event_number_content_label.setText('')
            self.time_point_content_label.setText('')
            self.data_size_content_label.setText('')