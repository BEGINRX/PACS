# -*- coding: utf-8 -*-
'''
@File  : main_window_new.py
@Author: 刘政
@Date  : 2020/9/17 15:14
@Desc  : new main window
'''

import os
import traceback
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt

import mne
mne.viz.set_3d_backend('pyvista')
import numpy as np
import pandas as pd
import scipy.io as sio
import gc

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QMenu, \
    QFileDialog, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout,  \
    QMessageBox, QInputDialog, QLineEdit, QWidget, QPushButton, QStyleFactory, \
    QApplication, QTreeWidget, QComboBox, QStackedWidget, QTreeWidgetItem, \
    QTreeWidgetItemIterator, QCheckBox, QSlider, QFormLayout, QSpinBox, QTableView, \
    QFrame, QTabWidget, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QKeySequence, QIcon, QDesktopServices
from mne import Annotations, events_from_annotations, BaseEpochs, Epochs
from mne.io import BaseRaw
from gui.my_thread import Import_Thread, Load_Epoched_Data_Thread, Resample_Thread, Filter_Thread, Calculate_Power, \
                          Brain_Win

from gui.sub_window import Choose_Window, Event_Window, Select_Time, Select_Chan, Select_Event, Epoch_Time, \
                           Refer_Window, Baseline_Time, My_Progress, Time_Freq_Win, Con_Win
from gui.re_ref import car_ref, gwr_ref, esr_ref, bipolar_ref, monopolar_ref, laplacian_ref
from gui.data_io import write_raw_edf, write_raw_set
from gui.my_class import Subject, SEEG, UiScreenshot
from visbrain.gui.brain.user import BrainUserMethods
from visbrain.objects.scene_obj import VisbrainCanvas
from visbrain.objects import BrainObj, CombineSources, RoiObj, SourceObj, ConnectObj
from vispy import scene
import vispy.visuals.transforms as vist
from visbrain.utils.guitools import fill_pyqt_table
from gui.re_ref import get_chan_group
from gui.my_func import u_color
import vispy.scene.cameras as viscam

class MainWindow(QMainWindow, BrainUserMethods, UiScreenshot):
    '''
    The main window
    '''

    data_info_signal = pyqtSignal(dict)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.flag = 0
        self.tree_dict = dict()
        # tree_item has the tree items of sEEG data
        self.tree_item = dict()
        # all the subjects information in this protocol
        # - key:subject name
        self.subject = dict()
        # data info save the basic information of sEEG data to show in the main window
        self.data_info = dict()
        # current_data tells us which seeg data we want to use by choosing
        # the 'key' in the subject
        self.current_data = dict()
        self.event_set = dict()
        self.event = None
        self.sources = None
        self.init_ui()


    def init_ui(self):
        self.setWindowIcon(QIcon('image/source.jpg'))
        self.frame()
        self.create_central_widget()
        self.create_worker()
        self.create_action()
        self.create_label()
        self.create_stack()
        self.create_combo_box()
        self.create_group_box()
        self.create_menubar()
        self.brain_ui()
        self.create_layout()
        self.set_qt_style()
        # QApplication.setStyle(QStyleFactory.create('Fusion'))


    def frame(self):
        '''set the app window to the full screen'''
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.desktop = QApplication.desktop()
        self.desktop_count = self.desktop.screenCount()
        self.fg = self.frameGeometry()
        self.rect = QDesktopWidget().availableGeometry(0)
        self.cp = self.rect.center()
        self.fg.moveCenter(self.cp)
        self.setGeometry(self.rect)  # 可避免遮挡任务栏
        self.showMaximized()


    def create_central_widget(self):
        '''create a central widget to house other sub groupboxes'''
        self.center_widget = QWidget()
        self.center_widget.setProperty('name', 'center')
        self.setCentralWidget(self.center_widget)
        self.statusBar().showMessage('Ready')


    def create_worker(self):
        '''create workers   '''
        self.import_worker = Import_Thread()
        self.import_worker.trigger.connect(self.get_seeg_data)
        self.load_epoched_data_worker = Load_Epoched_Data_Thread()
        self.load_epoched_data_worker.load.connect(self.get_seeg_data)
        self.resample_worker = Resample_Thread()
        self.resample_worker.resample.connect(self.get_seeg_data)
        self.filter_worker = Filter_Thread()
        self.filter_worker.filter_signal.connect(self.get_seeg_data)


    def create_action(self):
        '''create actions for menu bar'''

        # actions for File menu bar
        #
        self.create_subject_action = QAction('Create a subject', self,
                                      statusTip='Create a subject',
                                      triggered=self.create_subject)
        self.import_action = QAction('Import raw sEEG data', self,
                                     statusTip='Import raw sEEG data',
                                     triggered=self.execute_import_data)
        self.import_action.setEnabled(False)
        self.import_epoch_action = QAction('Import Epoch data', self,
                                           statusTip='Import Epoch data',
                                           triggered=self.execute_load_epoched_data)
        self.import_epoch_action.setEnabled(False)
        # triggered=self.create_ptc


        # delete data and clear the workshop
        self.clear_workshop_action = QAction('Clear the workshop', self,
                                      statusTip='Clear the workshop',
                                      triggered=self.clear_all)
        self.clear_all_action = QAction('Clear all', self,
                                 statusTip='Clear all workshops',
                                 triggered=self.clear_all)
        self.setting_action = QAction('Settings...', self,
                                      statusTip='Settings',
                                      triggered=self.show_setting)


        # exit
        self.exit_action = QAction('Exit', self,
                                   shortcut=QKeySequence.Close,
                                   statusTip='Exit the Software',
                                   triggered=self.close)


        # #########################################################################
        #                                Raw
        # ##########################################################################
        self.load_coord = QAction('Load MNI Coordinates', self,
                                       statusTip='Load MNI Coordinates',
                                       triggered=self.load_coordinate)
        self.load_coord.setEnabled(False)
        self.raw_action = dict()
        self.raw_action['rename_chan'] = QAction('Rename channels', self,
                                  statusTip='Rename channels',
                                  triggered=self.rename_chan)
        self.raw_action['cal_marker'] = QAction('Calculate and set up markers', self,
                                 statusTip='Calculate markers and delete useless channels',
                                 triggered=self.get_mark_del_chan)
        self.raw_action['resample'] = QAction('Resample', self,
                                statusTip='Resamle the sEEG data',
                                triggered=self.execute_resample_data)
        
        self.raw_action['re_ref_menu'] = QMenu('Re-reference', self)
        self.car = QAction('Common average reference(CAR)', self,
                                statusTip='Reference sEEG data using CAR',
                                triggered=self.car_reref)
        self.gwr = QAction('Gray-white matter reference(GWR)', self,
                                statusTip='Reference sEEG data using GWR',
                                triggered=self.gwr_reref)
        self.esr = QAction('Electrode shaft reference(ESR)', self,
                                statusTip='Reference sEEG data using ESR',
                                triggered=self.esr_reref)
        self.bipolar = QAction('Bipolar reference', self,
                                    statusTip='Reference sEEG data using Bipolar reference',
                                    triggered=self.bipolar_reref)
        self.monopolar = QAction('Monopolar reference', self,
                                statusTip='Reference sEEG data using Monopolar reference',
                                triggered=self.monopolar_reref)
        self.laplacian = QAction('Laplacian reference', self,
                                statusTip='Reference sEEG data using Laplacian reference',
                                triggered=self.laplacian_reref)
        self.raw_action['re_ref_menu'].addActions([self.car, self.gwr,
                                                   self.esr, self.bipolar,
                                                   self.monopolar, self.laplacian])
        
        self.raw_action['filter_sub_menu'] = QMenu('Filter', self)
        self.fir = QAction('FIR filter', self,
                          statusTip='Filter the sEEG data using fir',
                          triggered=self.filter_data_fir)
        self.iir = QAction('IIR filter', self,
                          statusTip='Filter the sEEG data using iir',
                          triggered=self.filter_data_iir)
        self.raw_action['filter_sub_menu'].addActions([self.fir, self.iir])

        self.raw_action['select_data_menu'] = QMenu('Select sub-sEEG data', self)
        self.select_time_action = QAction('Time', self,
                                         statusTip='Select sEEG data with time range',
                                         triggered=self.select_time)
        self.select_chan_action = QAction('Channels', self,
                                         statusTip='Select sEEG data with time range',
                                         triggered=self.select_chan)
        self.raw_action['select_data_menu'].addActions([self.select_time_action,
                                          self.select_chan_action])


        self.raw_action['plot_raw'] = QAction('Plot raw data', self,
                                             triggered=self.plot_raw_data)

        self.raw_action['remove_bad'] = QAction('Remove bad channels', self,
                                               triggered=self.drop_bad_chan)
        self.raw_action['interpolate_bad'] = QAction('Interpolate bad channels', self,
                                                    triggered=self.interpolate_bad)

        self.raw_action['get_epoch_menu'] = QMenu('Extract epoch', self)
        self.set_name = QAction('Set event name', self,
                               statusTip='Set event name corresponding to its event id',
                               triggered=self.get_event_name)
        self.get_epoch = QAction('Get epoch', self,
                                statusTip='Get epoch from raw data',
                                triggered=self.get_epoch_time_range)
        self.raw_action['get_epoch_menu'].addActions([self.set_name,
                                                      self.get_epoch])

        self.raw_action['save_menu'] = QMenu('Export data', self)
        self.save_fif_action = QAction('Save sEEG data as .fif data', self,
                                       statusTip='Save sEEG data in .fif format')
        self.save_edf_action = QAction('Save sEEG data as .edf data', self,
                                       statusTip='Save sEEG data in .edf format',
                                       triggered=self.save_edf)
        self.save_set_action = QAction('Save sEEG data as .set data', self,
                                       statusTip='Save sEEG data in .set format',
                                       triggered=self.save_set)
        self.raw_action['save_menu'].addActions([self.save_fif_action,
                                                 self.save_edf_action,
                                                 self.save_set_action])

        [self.raw_action[action].setEnabled(False) for action in  self.raw_action]

        # #########################################################################
        #                                Epoch
        # ##########################################################################
        self.epoch_action = dict()
        self.epoch_action['select_chan'] = QAction('Select sub channels', self,
                                          statusTip='Select sub channels',
                                          triggered=self.select_chan)
        self.epoch_action['select_event'] = QAction('Select specific events', self,
                                           statusTip='Select sub events',
                                           triggered=self.select_event)
        self.epoch_action['apply_baseline'] = QAction('Apply baseline to correct the epochs', self,
                                             statusTip='Correct the epochs with selected baseline',
                                             triggered=self.apply_base_win)
        self.epoch_action['visual_evoke_brain'] = QAction('Visualize Evoke data on a MNI brain_elements', self,
                                                 triggered=self.choose_evoke)
        self.epoch_action['plot_epoch'] = QAction('Plot epoch', self,
                                         triggered=self.plot_raw_data)
        self.epoch_action['drop_bad_chan'] = QAction('Drop bad channels', self,
                                            triggered=self.drop_bad_chan)
        self.epoch_action['drop_bad'] = QAction('Drop bad epochs', self,
                                       triggered=self.drop_bad_epochs)

        self.epoch_action['t_f'] = QAction('Time frequency analysis', self,
                                        triggered=self.show_tf_win)

        self.epoch_action['connect'] = QAction('Connectivity analysis', self,
                                            triggered=self.show_con_win)

        self.epoch_action['epoch_save_menu'] = QMenu('Export data', self)
        self.epoch_save_fif = QAction('Save sEEG data as .fif data', self,
                                       statusTip='Save sEEG data in .fif format')
        self.epoch_save_edf = QAction('Save sEEG data as .edf data', self,
                                       statusTip='Save sEEG data in .edf format',
                                       triggered=self.save_edf)
        self.epoch_save_set = QAction('Save sEEG data as .set data', self,
                                       statusTip='Save sEEG data in .set format',
                                       triggered=self.save_set)
        self.epoch_save_pd = QAction('Save sEEG data as PandasDataFrames', self,
                                       statusTip='Save sEEG data as PandasDataFrames',
                                       triggered=self.save_pd)
        self.epoch_action['epoch_save_menu'].addActions([self.epoch_save_fif,
                                                         self.epoch_save_edf,
                                                         self.epoch_save_set])
        
        [self.epoch_action[action].setEnabled(False) for action in self.epoch_action]


        # actions for Help menu bar
        #
        #  website
        self.website_action = QAction('SEEG_Cognition website', self,
                                      triggered=self.show_website)
        self.licence_action = QAction('Licence', self,
                                      triggered=self.show_licence)
        self.email_action = QAction('E-mail us', self,
                                    triggered=self.send_email)


    def create_stack(self):

        self.subject_stack = QStackedWidget()
        self.subject_stack.setProperty('name', 'ptc')
        self.subject_stack.addWidget(self.empty_label_0)


    def create_combo_box(self):

        self.subject_cb = QComboBox()
        self.subject_cb.activated.connect(self.change_sub_name)
        self.subject_cb.setProperty('name', 'ptc')
        self.subject_cb.setFixedHeight(35)
        # self.subject_cb.setEditable(True)


    def create_label(self):
        '''reate labels'''
        # labels for main window
        #
        # empty label
        self.empty_label_0 = QLabel('', self)
        self.empty_label_0.setProperty('name', 'empty')

        self.empty_label_1 = QLabel('', self)
        self.empty_label_1.setProperty('name', 'empty')

        # sEEG Data Information title
        self.data_info_label = QLabel('SEEG Data Information', self)
        self.data_info_label.setProperty('name', 'title')
        self.data_info_label.setAlignment(Qt.AlignHCenter)
        self.data_info_label.setFixedHeight(30)

        # basic info of the subject
        self.file_name_label = QLabel(' Filename', self)
        self.file_name_label.setAlignment(Qt.AlignLeft)
        self.file_name_label.setFixedSize(180, 33)

        self.file_name_cont_label = QLabel('', self)
        self.file_name_cont_label.setAlignment(Qt.AlignLeft)
        self.file_name_cont_label.setFixedHeight(33)

        self.epoch_num_label = QLabel('Epochs', self)
        self.epoch_num_label.setProperty('name', 'group0')
        self.epoch_num_label.setAlignment(Qt.AlignCenter)
        self.epoch_num_label.setFixedSize(105, 38)


        self.epoch_num_cont_label = QLabel('', self)
        self.epoch_num_cont_label.setProperty('name', 'group1')
        self.epoch_num_cont_label.setAlignment(Qt.AlignCenter)
        self.epoch_num_cont_label.setFixedSize(105, 38)
        # self.epoch_num_cont_label.setFixedSize(90, 38)

        self.samp_rate_label = QLabel('Sampling rate(Hz)', self)
        self.samp_rate_label.setProperty('name', 'group0')
        self.samp_rate_label.setAlignment(Qt.AlignCenter)
        self.samp_rate_label.setFixedSize(220, 38)

        self.samp_rate_cont_label = QLabel('', self)
        self.samp_rate_cont_label.setProperty('name', 'group1')
        self.samp_rate_cont_label.setAlignment(Qt.AlignCenter)
        self.samp_rate_cont_label.setFixedSize(220, 38)

        self.chan_label = QLabel('Channel', self)
        self.chan_label.setProperty('name', 'group0')
        self.chan_label.setAlignment(Qt.AlignCenter)
        self.chan_label.setFixedSize(120, 38)
        # self.chan_label.setFixedSize(90, 38)

        self.chan_cont_label = QLabel('', self)
        self.chan_cont_label.setProperty('name', 'group1')
        self.chan_cont_label.setAlignment(Qt.AlignCenter)
        self.chan_cont_label.setFixedSize(120, 38)
        # self.chan_cont_label.setFixedSize(90, 38)

        self.start_label = QLabel('Epoch start(sec)', self)
        self.start_label.setProperty('name', 'group0')
        self.start_label.setAlignment(Qt.AlignCenter)
        self.start_label.setFixedSize(220, 38)

        self.start_cont_label = QLabel('', self)
        self.start_cont_label.setProperty('name', 'group1')
        self.start_cont_label.setAlignment(Qt.AlignCenter)
        self.start_cont_label.setFixedSize(220, 38)

        self.end_label = QLabel('Epoch end(sec)', self)
        self.end_label.setProperty('name', 'group0')
        self.end_label.setAlignment(Qt.AlignCenter)
        self.end_label.setFixedSize(220, 38)

        self.end_cont_label = QLabel('', self)
        self.end_cont_label.setProperty('name', 'group1')
        self.end_cont_label.setAlignment(Qt.AlignCenter)
        self.end_cont_label.setFixedSize(220, 38)

        self.event_class_label = QLabel('Event class', self)
        self.event_class_label.setProperty('name', 'group0')
        self.event_class_label.setAlignment(Qt.AlignCenter)
        self.event_class_label.setFixedHeight(38)
        # self.event_class_label.setFixedSize(130, 38)

        self.event_class_cont_label = QLabel('', self)
        self.event_class_cont_label.setProperty('name', 'group1')
        self.event_class_cont_label.setAlignment(Qt.AlignCenter)
        self.event_class_cont_label.setFixedHeight(38)
        # self.event_class_cont_label.setFixedSize(130, 38)

        self.event_num_label = QLabel('Event number', self)
        self.event_num_label.setProperty('name', 'group0')
        self.event_num_label.setAlignment(Qt.AlignCenter)
        self.event_num_label.setFixedHeight(38)
        # self.event_num_label.setFixedSize(130, 38)

        self.event_num_cont_label = QLabel('', self)
        self.event_num_cont_label.setProperty('name', 'group1')
        self.event_num_cont_label.setAlignment(Qt.AlignCenter)
        self.event_class_label.setFixedHeight(38)
        # self.event_num_cont_label.setFixedSize(130, 38)

        self.time_point_label = QLabel('Time points', self)
        self.time_point_label.setProperty('name', 'group0')
        self.time_point_label.setAlignment(Qt.AlignCenter)
        self.time_point_label.setFixedHeight(38)
        # self.time_point_label.setFixedSize(130, 38)

        self.time_point_cont_label = QLabel('', self)
        self.time_point_cont_label.setProperty('name', 'group1')
        self.time_point_cont_label.setAlignment(Qt.AlignCenter)
        self.time_point_cont_label.setFixedHeight(38)
        # self.time_point_cont_label.setFixedSize(130, 38)

        self.data_size_label = QLabel('Data size(MB)', self)
        self.data_size_label.setProperty('name', 'group0')
        self.data_size_label.setAlignment(Qt.AlignCenter)
        self.data_size_label.setFixedSize(180, 38)
        # self.data_size_label.setFixedSize(130, 38)

        self.data_size_cont_label = QLabel('', self)
        self.data_size_cont_label.setProperty('name', 'group1')
        self.data_size_cont_label.setAlignment(Qt.AlignCenter)
        self.data_size_cont_label.setFixedSize(180, 38)
        # self.data_size_cont_label.setFixedSize(130, 38)

        # labels in electordes and activation
        self.electro_title_label = QLabel('Brain visualization', self)
        self.electro_title_label.setProperty('name', 'title')
        self.electro_title_label.setAlignment(Qt.AlignCenter)
        self.electro_title_label.setFixedHeight(30)

        # Protocol
        self.protocol_label = QLabel('Protocol', self)
        self.protocol_label.setProperty('name', 'title')
        self.protocol_label.setAlignment(Qt.AlignHCenter)
        self.protocol_label.setFixedHeight(30)


    def create_group_box(self):
        '''create group boxes for main window'''
        # subject seeg data infomation
        self.seeg_info_box = QGroupBox()
        self.seeg_info_box.setProperty('name', 'sub')
        self.button_func_box = QGroupBox()
        self.button_func_box.setProperty('name', 'sub')
        self.button_func_box.setContentsMargins(0,0,0,0)
        # sEEG electrodes Visualization and Activation
        self.vis_box = QGroupBox()
        self.vis_box.setProperty('name', 'sub')
        # right group box
        self.right_box = QGroupBox()
        self.right_box.setProperty('name', 'sub')
        # protocol
        self.protocol_box = QGroupBox('')
        self.protocol_box.setProperty('name', 'sub')
        self.protocol_box.setFixedWidth(300)


    def create_menubar(self):
        '''create menu bars'''

        # file menu bar
        self.file_menu = self.menuBar().addMenu('Subject')
        self.file_menu.addAction(self.create_subject_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.import_action)
        self.file_menu.addAction(self.import_epoch_action)
        self.file_menu.addAction(self.load_coord)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.clear_all_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.setting_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Raw menu bar
        self.raw_menu = self.menuBar().addMenu('Raw')
        self.raw_menu.addActions([self.raw_action['rename_chan'],
                                  self.raw_action['cal_marker'],
                                  self.raw_action['resample']])
        self.raw_menu.addMenu(self.raw_action['re_ref_menu'])
        self.raw_menu.addMenu(self.raw_action['filter_sub_menu'])
        self.raw_menu.addMenu(self.raw_action['select_data_menu'])
        self.raw_menu.addSeparator()
        self.raw_menu.addActions([self.raw_action['plot_raw'],
                                  self.raw_action['remove_bad'],
                                  self.raw_action['interpolate_bad']])
        self.raw_menu.addSeparator()
        self.raw_menu.addMenu(self.raw_action['get_epoch_menu'])
        self.raw_menu.addSeparator()
        self.raw_menu.addMenu(self.raw_action['save_menu'])


        # Epoch menu bar
        self.epoch_menu = self.menuBar().addMenu('Epoch')
        self.epoch_menu.addAction(self.epoch_action['apply_baseline'])
        self.epoch_menu.addActions([self.epoch_action['select_chan'],
                                    self.epoch_action['select_event']])
        self.epoch_menu.addActions([self.epoch_action['visual_evoke_brain'],
                                    self.epoch_action['plot_epoch'],
                                    self.epoch_action['drop_bad_chan'],
                                    self.epoch_action['drop_bad']])
        self.epoch_menu.addSeparator()
        self.epoch_menu.addActions([self.epoch_action['t_f'],
                                    self.epoch_action['connect']])
        self.epoch_menu.addMenu(self.epoch_action['epoch_save_menu'])


        # Help menu bar
        self.help_menu = self.menuBar().addMenu('Help')
        self.help_menu.addAction(self.website_action)
        self.help_menu.addAction(self.licence_action)
        self.help_menu.addAction(self.email_action)


    def brain_ui(self):
        self.cdict = {'bgcolor': '#dcdcdc', 'cargs': {'size':(1300, 600), 'dpi': 600,
                                                      'fullscreen': True, 'resizable': True}}
        self._gl_scale = 100
        self._camera = viscam.TurntableCamera(name='MainBrainCamera')
        self.s_kwargs = {}
        self.s_kwargs['symbol'] = 'hbar'
        self.s_kwargs['radius_min'] = 10
        self.s_kwargs['text_color'] = 'black'  # Set to black the text color
        self.s_kwargs['text_size'] = 25000  # Size of the text
        self.s_kwargs['text_translate'] =(0.5, 1.5, 0)
        self.s_kwargs['text_bold'] = True
        self.x = 90
        self.y = 120
        self.z = 85
        self._brain_ui()


    def _brain_ui(self):
        self.widget = QWidget()
        self._source_group = None

        # root node
        self._vbNode = scene.Node(name='Brain')
        self._vbNode.transform = vist.STTransform(scale=[self._gl_scale] * 3)

        object_lst = ['Brain', 'Sources', 'Region of Interest(ROI)']
        self._obj_type_lst = QComboBox()
        self._obj_type_lst.addItems(object_lst)
        self._obj_type_lst.currentTextChanged.connect(self.change_group)
        self._obj_type_lst.model().item(1).setEnabled(False)
        self._obj_type_lst.setFixedWidth(300)

        self._brain_widget()
        self._roi_widget()

        UiScreenshot.__init__(self)
        self.screenshot_btn = QPushButton('Screenshot')
        self.screenshot_btn.clicked.connect(self._fcn_show_screenshot)

        self.group_stack = QStackedWidget()
        self.group_stack.addWidget(self._brain_group)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self._obj_type_lst)
        left_layout.addWidget(self.group_stack)
        left_layout.addStretch(1000)
        left_layout.addWidget(self.screenshot_btn)

        self.view = VisbrainCanvas(name='MainCanvas', camera=self._camera,
                                    **self.cdict)
        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addWidget(self.view.canvas.native)
        self.widget.setLayout(layout)

        self.view.wc.camera = self._camera
        self._vbNode.parent = self.view.wc.scene
        self.atlas.camera = self._camera
        self.atlas._csize = self.view.canvas.size
        self.atlas.rotate('left')
        self.atlas.camera.set_default_state()


    def _brain_widget(self):

        self._brain_group = QGroupBox('Display Brain')
        self._brain_group.setFixedWidth(300)
        self._brain_group.setCheckable(True)
        self._brain_translucent = QCheckBox('Translucent')
        self._brain_alpha = QSlider()
        self._brain_alpha.setMaximum(10)
        self._brain_alpha.setSliderPosition(10)
        self._brain_alpha.setOrientation(Qt.Horizontal)
        self._template_label = QLabel('Template')
        self._brain_template = QComboBox()
        self._brain_template.addItems(['B1', 'B2', 'B3', 'inflated', 'white'])
        self._brain_template.setCurrentIndex(0)
        self._hemi_label = QLabel('Hemisphere')
        self._brain_hemi = QComboBox()
        self._brain_hemi.addItems(['both', 'left', 'right'])
        self._rotate_label = QLabel('Rotate')
        self._brain_rotate = QComboBox()
        rotate = ['Top', 'Bottom', 'Left', 'Right', 'Front', 'Back']
        self._brain_rotate.addItems(rotate)
        self._brain_rotate.setCurrentIndex(2)
        self._slice_label = QLabel('Slice')
        self._slice_sep = QFrame()
        self._slice_sep.setFrameShape(QFrame.VLine)
        self._slice_sep.setFrameShadow(QFrame.Sunken)
        self._xmin_label = QLabel('x-min')
        self._xmax_label = QLabel('x-max')
        self._ymin_label = QLabel('y-min')
        self._ymax_label = QLabel('y-max')
        self._zmin_label = QLabel('z-min')
        self._zmax_label = QLabel('z-max')
        self._brain_xmin = QSlider()
        self._brain_xmin.setMaximum(-self.x)
        self._brain_xmin.setSliderPosition(10)
        self._brain_xmin.setOrientation(Qt.Horizontal)
        self._brain_xmin.setInvertedAppearance(False)
        self._brain_xmin.setInvertedControls(True)
        self._brain_xmax = QSlider()
        self._brain_xmax.setMaximum(self.x)
        self._brain_xmax.setSliderPosition(10)
        self._brain_xmax.setOrientation(Qt.Horizontal)
        self._brain_xmax.setInvertedAppearance(False)
        self._brain_xmax.setInvertedControls(True)
        self._brain_ymin = QSlider()
        self._brain_ymin.setMaximum(-self.y)
        self._brain_ymin.setSliderPosition(10)
        self._brain_ymin.setOrientation(Qt.Horizontal)
        self._brain_ymin.setInvertedAppearance(False)
        self._brain_ymin.setInvertedControls(True)
        self._brain_ymax = QSlider()
        self._brain_ymax.setMaximum(self.y)
        self._brain_ymax.setSliderPosition(10)
        self._brain_ymax.setOrientation(Qt.Horizontal)
        self._brain_ymax.setInvertedAppearance(False)
        self._brain_ymax.setInvertedControls(True)
        self._brain_zmin = QSlider()
        self._brain_zmin.setMaximum(-self.z)
        self._brain_zmin.setSliderPosition(10)
        self._brain_zmin.setOrientation(Qt.Horizontal)
        self._brain_zmin.setInvertedAppearance(False)
        self._brain_zmin.setInvertedControls(True)
        self._brain_zmax = QSlider()
        self._brain_zmax.setMaximum(self.z)
        self._brain_zmax.setSliderPosition(10)
        self._brain_zmax.setOrientation(Qt.Horizontal)
        self._brain_zmax.setInvertedAppearance(False)
        self._brain_zmax.setInvertedControls(True)
        self._brain_inlight = QCheckBox('Inlight')

        b_layout_0 = QVBoxLayout()
        b_layout_1 = QFormLayout()
        b_layout_2 = QFormLayout()
        b_layout_3 = QHBoxLayout()
        b_layout_1.addRow(self._brain_translucent, self._brain_alpha)
        b_layout_1.addRow(self._template_label, self._brain_template)
        b_layout_1.addRow(self._hemi_label, self._brain_hemi)
        b_layout_1.addRow(self._rotate_label, self._brain_rotate)
        b_layout_2.addRow(self._xmin_label, self._brain_xmin)
        b_layout_2.addRow(self._xmax_label, self._brain_xmax)
        b_layout_2.addRow(self._ymin_label, self._brain_ymin)
        b_layout_2.addRow(self._ymax_label, self._brain_ymax)
        b_layout_2.addRow(self._zmin_label, self._brain_zmin)
        b_layout_2.addRow(self._zmax_label, self._brain_zmax)
        b_layout_3.addWidget(self._slice_label)
        b_layout_3.addWidget(self._slice_sep)
        b_layout_3.addLayout(b_layout_2)
        b_layout_0.addLayout(b_layout_1)
        b_layout_0.addLayout(b_layout_3)
        b_layout_0.addWidget(self._brain_inlight)
        b_layout_0.addStretch(1000)
        self._brain_group.setLayout(b_layout_0)

        self.atlas = BrainObj('B1')
        self.atlas.scale = self._gl_scale
        self.atlas.parent = self._vbNode
        self.atlas.visible_obj = False
        self._brain_group.setChecked(False)
        self._brain_translucent.setChecked(self.atlas.translucent)
        self._brain_group.clicked.connect(self._fcn_brain_visible)
        self._brain_template.currentTextChanged.connect(self._fcn_brain_template)
        self._brain_hemi.currentIndexChanged.connect(self._fcn_brain_hemisphere)
        self._brain_rotate.currentTextChanged.connect(self._fcn_brain_rotate)
        self._brain_translucent.clicked.connect(self._fcn_brain_translucent)
        self._brain_alpha.valueChanged.connect(self._fcn_brain_alpha)
        self._fcn_brain_reset_slider()
        self._brain_xmin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_xmax.valueChanged.connect(self._fcn_brain_slices)
        self._brain_ymin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_ymax.valueChanged.connect(self._fcn_brain_slices)
        self._brain_zmin.valueChanged.connect(self._fcn_brain_slices)
        self._brain_zmax.valueChanged.connect(self._fcn_brain_slices)
        self._brain_inlight.clicked.connect(self._fcn_brain_inlight)

    def _source_widget(self):
        
        self._source_group = QGroupBox('Source')
        self._source_group.setCheckable(True)
        self._source_tab = QTabWidget(self._source_group)
        self._source_tab1 = QWidget()
        self._obj_name_lst = QComboBox()
        if isinstance(self.group, list):
            self._obj_name_lst.addItems(sorted(self.group))
        self._obj_name_lst.setFixedWidth(200)
        self._source_vis = QCheckBox('Display the source')
        self._select_label = QLabel('Select')
        self._s_select = QComboBox()
        self._s_select.addItems(['All', 'Inside the brain', 'Outside the brain',
                                  'Left hemisphere', 'Right hemisphere', 'None'])
        self._s_select.setFixedWidth(200)
        self._symbol_label = QLabel('Symbol')
        self._s_symbol = QComboBox()
        self._s_symbol.setFixedWidth(200)
        symbol = ['hbar', 'vbar', 'disc', 'arrow', 'ring', 'clobber',
                  'square', 'diamond', 'cross']
        self._s_symbol.addItems(symbol)

        self._project_label = QLabel('Cortical projection')
        self._project_label.setStyleSheet("font: bold")
        self._projection = QComboBox()
        self._projection.addItems(['Modulation', 'Repartition'])
        self.project_btn = QPushButton('Run')

        s_layout_0 = QVBoxLayout()
        s_layout_1 = QHBoxLayout()
        s_layout_1.addWidget(self._obj_name_lst)
        s_layout_1.addStretch(100)
        s_layout_2 = QHBoxLayout ()
        s_layout_2.addWidget(self._select_label)
        s_layout_2.addStretch(100)
        s_layout_2.addWidget(self._s_select)
        s_layout_3 = QHBoxLayout()
        s_layout_3.addWidget(self._symbol_label)
        s_layout_3.addWidget(self._s_symbol)
        s_layout_4 = QHBoxLayout()
        s_layout_4.addWidget(self._projection)
        s_layout_4.addWidget(self.project_btn)
        s_layout_0.addLayout(s_layout_1)
        s_layout_0.addWidget(self._source_vis)
        s_layout_0.addLayout(s_layout_2)
        s_layout_0.addLayout(s_layout_3)
        s_layout_0.addWidget(self._project_label)
        s_layout_0.addLayout(s_layout_4)
        s_layout_0.addStretch(1000)
        self._source_tab1.setLayout(s_layout_0)

        self._source_tab2 = QWidget()
        self._s_table = QTableWidget()
        self._s_table.setFixedHeight(500)
        self._s_table.setFixedWidth(400)
        self._s_analyse_roi = QComboBox()
        self._s_analyse_roi.addItems(['Brodmann', 'AAL', 'Talairach'])
        self._s_analyse_run = QPushButton('Run')
        self._s_save = QPushButton('Save')

        s_layout_3 = QHBoxLayout()
        s_layout_4 = QVBoxLayout()
        s_layout_3.addWidget(self._s_analyse_roi)
        s_layout_3.addWidget(self._s_analyse_run)
        s_layout_3.addWidget(self._s_save)
        s_layout_4.addWidget(self._s_table)
        s_layout_4.addLayout(s_layout_3)
        self._source_tab2.setLayout(s_layout_4)

        self._source_tab.addTab(self._source_tab1, 'Properties')
        self._source_tab.addTab(self._source_tab2, 'Analysis')

        source_layout = QHBoxLayout()
        source_layout.addWidget(self._source_tab)
        self._source_group.setLayout(source_layout)

        self.sources = CombineSources(self.s_obj)
        if self.sources.name is None:
            self._obj_type_lst.model().item(1).setEnabled(False)
        self.sources.parent = self._vbNode
        name = self._obj_name_lst.currentText()
        self._source_group.setChecked(True)
        self._source_group.clicked.connect(self._fcn_vis_source)
        self._source_vis.setChecked(self.sources[name].visible_obj)
        self._source_vis.clicked.connect(self._fcn_source_visible)
        self._obj_name_lst.currentTextChanged.connect(self._fcn_change_name)
        self._s_select.currentIndexChanged.connect(self._fcn_source_select)
        self._s_symbol.currentIndexChanged.connect(self._fcn_source_symbol)
        self.project_btn.clicked.connect(self._fcn_source_proj)
        # == == == == == == == == == == == TABLE == == == == == == == == == == ==
        if self.sources.name is not None:
            # Get position / text :
            xyz, txt = self.sources._xyz, self.sources._text
            col = np.c_[txt, xyz].T.tolist()
            col_names = ['Channel', 'X', 'Y', 'Z']
            fill_pyqt_table(self._s_table, col_names, col)
            self._s_table.setEnabled(True)
        self._s_analyse_run.clicked.connect(self._fcn_analyse_sources)
        self._s_save.clicked.connect(self.save_df)

    def _roi_widget(self):
        self._roi_group = QGroupBox('Display ROI')
        self._roi_group.setFixedWidth(300)
        self._roi_group.setCheckable(True)
        self._roi_transp = QCheckBox('Translucent')
        self._roi_transp.setChecked(False)
        self._roi_label = QLabel('ROI')
        self._roi_div = QComboBox()
        self._roi_smooth = QCheckBox('Smooth')
        self._roi_smooth.setChecked(False)
        self._smooth_value = QSpinBox()
        self._smooth_value.setMinimum(3)
        self._smooth_value.setSingleStep(2)
        self._roi_uni_color = QCheckBox('Unique color')
        self._roi_uni_color.setChecked(False)
        self._roi_add = QTableView()
        self._roi_add.setFixedHeight(400)
        self._roi_apply = QPushButton('Apply')
        self._roi_rst = QPushButton('Reset')
        self._roi_label.setEnabled(False)
        self._roi_transp.setEnabled(False)
        self._roi_smooth.setEnabled(False)
        self._smooth_value.setEnabled(False)
        self._roi_div.setEnabled(False)
        self._roi_add.setEnabled(False)
        self._roi_apply.setEnabled(False)
        self._roi_rst.setEnabled(False)

        r_layout_0 = QFormLayout()
        r_layout_0.addRow(self._roi_label, self._roi_div)
        r_layout_0.addRow(self._roi_smooth, self._smooth_value)

        r_layout_1 = QHBoxLayout()
        r_layout_1.addWidget(self._roi_apply)
        r_layout_1.addWidget(self._roi_rst)

        r_layout_2 = QVBoxLayout()
        r_layout_2.addWidget(self._roi_transp)
        r_layout_2.addLayout(r_layout_0)
        r_layout_2.addWidget(self._roi_uni_color)
        r_layout_2.addWidget(self._roi_add)
        r_layout_2.addLayout(r_layout_1)
        self._roi_group.setLayout(r_layout_2)

        self.roi = RoiObj('brodmann')
        self.roi.visible_obj = False
        if self.roi.name not in self.roi.list():
            self.roi.save(tmpfile=True)
        self.roi.parent = self._vbNode
        self._roi_group.setChecked(self.roi.visible_obj)
        self._roi_group.clicked.connect(self._fcn_roi_visible)
        self._fcn_roi_visible()
        vol_list = self.roi.list()
        try:
            vol_list.remove('mist')
        except:
            pass
        self._roi_div.addItems(vol_list)
        self._roi_div.currentIndexChanged.connect(self._fcn_build_roi_list)
        self._roi_div.setCurrentIndex(vol_list.index(self.roi.name))
        self._roi_smooth.clicked.connect(self._fcn_roi_smooth)
        self._roi_apply.clicked.connect(self._fcn_apply_roi_selection)
        self._roi_rst.clicked.connect(self._fcn_reset_roi_list)
        self._roi_transp.clicked.connect(self._fcn_area_translucent)
        self._fcn_build_roi_list()

    def change_group(self):
        if self._obj_type_lst.currentText() == 'Brain':
            self.group_stack.removeWidget(self._source_group)
            self.group_stack.removeWidget(self._roi_group)
            self.group_stack.addWidget(self._brain_group)
        elif self._obj_type_lst.currentText() == 'Sources':
            self.group_stack.removeWidget(self._brain_group)
            self.group_stack.removeWidget(self._roi_group)
            self.group_stack.addWidget(self._source_group)
        elif self._obj_type_lst.currentText() == 'Region of Interest(ROI)':
            self.group_stack.removeWidget(self._brain_group)
            self.group_stack.removeWidget(self._source_group)
            self.group_stack.addWidget(self._roi_group)

    # ========================== Brain Slot ========================

    def _fcn_brain_visible(self):
        """Display / hide the brain."""
        viz = self._brain_group.isChecked()
        self.atlas.visible_obj = viz

    def _fcn_brain_template(self):
        template = str(self._brain_template.currentText())
        hemisphere = str(self._brain_hemi.currentText())
        if self.atlas.name != template:
            self.atlas.set_data(name=template, hemisphere=hemisphere)

        self.atlas.mesh.xmin = float(-self.x)
        self.atlas.mesh.xmax = float(self.x)
        self.atlas.mesh.ymin = float(-self.y)
        self.atlas.mesh.ymax = float(self.y)
        self.atlas.mesh.zmin = float(-self.z)
        self.atlas.mesh.zmax = float(self.z)
        self.atlas.scale = self._gl_scale
        self.atlas.reset_camera()
        self.atlas.rotate('left')
        self.atlas._name = template
        if self.atlas.hemisphere != hemisphere:
            self.atlas.hemisphere = hemisphere

    def _fcn_brain_hemisphere(self):
        """Change the hemisphere."""
        hemi = str(self._brain_hemi.currentText())
        self.atlas.mesh.hemisphere = hemi

    def _fcn_brain_translucent(self):
        """Use translucent or opaque brain."""
        viz = self._brain_translucent.isChecked()
        self.atlas.translucent = viz
        self._brain_alpha.setEnabled(viz)
        try:
            if viz:
                self.sources.set_visible_sources('all', self.atlas.vertices)
                for name in self.group:
                    self.sources[name]._sources_text.visible = True
            else:
                for name in self.group:
                    self.sources[name]._sources_text.visible = False
        except:
            pass
        self._fcn_brain_alpha()

    def _fcn_brain_alpha(self):
        """Update brain transparency."""
        alpha = self._brain_alpha.value() / 100.
        self.atlas.alpha = alpha
        self.atlas.mesh.update()

    def _fcn_brain_inlight(self):
        """Set light to be inside the brain."""
        self.atlas.mesh.inv_light = self._brain_inlight.isChecked()
        self.atlas.mesh.update()

    def _fcn_brain_rotate(self, text):
        self.atlas.rotate((text).lower())

    def _fcn_brain_reset_slider(self):
        """Reset min/max slice sliders."""
        n_cut = 1000
        xmin, xmax = -self.x, self.x
        ymin, ymax = -self.y, self.y
        zmin, zmax = -self.z, self.z
        # xmin
        self._brain_xmin.setMinimum(xmin)
        self._brain_xmin.setMaximum(xmax)
        self._brain_xmin.setSingleStep((xmin - xmax) / n_cut)
        self._brain_xmin.setValue(xmin)
        # xmax
        self._brain_xmax.setMinimum(xmin)
        self._brain_xmax.setMaximum(xmax)
        self._brain_xmax.setSingleStep((xmin - xmax) / n_cut)
        self._brain_xmax.setValue(xmax)
        # ymin
        self._brain_ymin.setMinimum(ymin)
        self._brain_ymin.setMaximum(ymax)
        self._brain_ymin.setSingleStep((ymin - ymax) / n_cut)
        self._brain_ymin.setValue(ymin)
        # ymax
        self._brain_ymax.setMinimum(ymin)
        self._brain_ymax.setMaximum(ymax)
        self._brain_ymax.setSingleStep((ymin - ymax) / n_cut)
        self._brain_ymax.setValue(ymax)
        # zmin
        self._brain_zmin.setMinimum(zmin)
        self._brain_zmin.setMaximum(zmax)
        self._brain_zmin.setSingleStep((zmin - zmax) / n_cut)
        self._brain_zmin.setValue(zmin)
        # zmax
        self._brain_zmax.setMinimum(zmin)
        self._brain_zmax.setMaximum(zmax)
        self._brain_zmax.setSingleStep((zmin - zmax) / n_cut)
        self._brain_zmax.setValue(zmax)

    def _fcn_brain_slices(self):
        """Slice the brain."""
        self.atlas.mesh.xmin = float(self._brain_xmin.value())
        self.atlas.mesh.xmax = float(self._brain_xmax.value())
        self.atlas.mesh.ymin = float(self._brain_ymin.value())
        self.atlas.mesh.ymax = float(self._brain_ymax.value())
        self.atlas.mesh.zmin = float(self._brain_zmin.value())
        self.atlas.mesh.zmax = float(self._brain_zmax.value())
        self.atlas.mesh.update()

    # ========================= Source Slot ========================
    def _fcn_vis_source(self):
        viz = self._source_group.isChecked()
        for name in self.group:
            self.sources[name].visible_obj = viz


    def _fcn_source_symbol(self):
        """Change the source symbol."""
        name = self._obj_name_lst.currentText()
        self.sources[name].symbol = self._s_symbol.currentText()

    def _fcn_source_select(self):
        """Select the source to display."""
        txt = self._s_select.currentText().split(' ')[0].lower()
        self.sources.set_visible_sources(txt, self.atlas.vertices)

    def _fcn_source_visible(self):
        """Display / hide source object."""
        viz = self._source_vis.isChecked()
        name = self._obj_name_lst.currentText()
        self.sources[name].visible_obj = viz
        self._select_label.setEnabled(viz)
        self._s_select.setEnabled(viz)
        self._symbol_label.setEnabled(viz)
        self._s_symbol.setEnabled(viz)
        self._project_label.setEnabled(viz)
        self._projection.setEnabled(viz)
        self.project_btn.setEnabled(viz)

    def _fcn_change_name(self):
        name = self._obj_name_lst.currentText()
        viz = self.sources[name].visible_obj
        self._source_vis.setChecked(viz)
        self._select_label.setEnabled(viz)
        self._s_select.setEnabled(viz)
        self._symbol_label.setEnabled(viz)
        self._s_symbol.setEnabled(viz)
        self._project_label.setEnabled(viz)
        self._projection.setEnabled(viz)
        self.project_btn.setEnabled(viz)

    def _fcn_source_proj(self, _, **kwargs):
        """Apply source projection."""
        b_obj = self.atlas
        radius = 10.0
        mask_color = 'gray'
        project = str(self._projection.currentText()).lower()
        self.sources.project_sources(b_obj, project=project, radius=radius,
                                      mask_color=mask_color, **kwargs)
        self.atlas.mesh.update()

    def _fcn_analyse_sources(self):
        """Analyse sources locations."""
        roi = self._s_analyse_roi.currentText()
        df = self.sources.analyse_sources(roi.lower())
        fill_pyqt_table(self._s_table, df=df)

    def save_df(self):
        roi = self._s_analyse_roi.currentText()
        df = self.sources.analyse_sources(roi.lower())
        filename, _ = QFileDialog.getSaveFileName(self, 'Save coordnitates information')
        df.to_csv(filename + '.csv')

    # =========================== ROI Slot =========================
    def _fcn_roi_visible(self):
        """Display or hide ROI."""
        viz = self._roi_group.isChecked()
        self.roi.visible_obj = viz
        self._roi_transp.setEnabled(viz)
        self._roi_label.setEnabled(viz)
        self._roi_smooth.setEnabled(viz)
        self._smooth_value.setEnabled(viz)
        self._roi_div.setEnabled(viz)
        self._roi_add.setEnabled(viz)
        self._roi_apply.setEnabled(viz)
        self._roi_rst.setEnabled(viz)
        self._roi_uni_color.setEnabled(viz)

    def _fcn_roi_smooth(self):
        """Enable ROI smoothing."""
        self._smooth_value.setEnabled(self._roi_smooth.isChecked())

    def _fcn_build_roi_list(self):
        """Build a list of checkable ROIs."""
        # Select volume :
        selected_roi = str(self._roi_div.currentText())
        print('Select roi is ', selected_roi)
        if self.roi.name != selected_roi:
            self.roi(selected_roi)
        # Clear widget list and add ROIs :
        self._roi_add.reset()
        df = self.roi.get_labels()
        col_names = list(df.keys())
        col_names.pop(col_names.index('index'))
        cols = [list(df[k]) for k in col_names if k not in ['', 'index']]
        # Build the table with the filter :

        self._roiModel = fill_pyqt_table(self._roi_add, col_names, cols,
                                          check=0, filter_col=0)
        # By default, uncheck items :
        self._fcn_reset_roi_list()

    def _fcn_reset_roi_list(self):
        """Reset ROIs selection."""
        # Unchecked all ROIs :
        for num in range(self._roiModel.rowCount()):
            self._roiModel.item(num, 0).setCheckState(Qt.Unchecked)

    def _fcn_get_selected_rois(self):
        """Get the list of selected ROIs."""
        _roitoadd = []
        all_idx = list(self.roi.get_labels()['index'])
        for num in range(self._roiModel.rowCount()):
            item = self._roiModel.item(num, 0)
            if item.checkState():
                _roitoadd.append(all_idx[num])
        return _roitoadd

    def _fcn_apply_roi_selection(self, _, roi_name='roi'):
        """Apply ROI selection."""
        # Get the list of selected ROIs :
        _roitoadd = self._fcn_get_selected_rois()
        smooth = self._smooth_value.value() * int(self._roi_smooth.isChecked())
        uni_col = bool(self._roi_uni_color.isChecked())

        if _roitoadd:
            self.roi.select_roi(_roitoadd, smooth=smooth, unique_color=uni_col)
            self.roi.camera = self._camera
            self._roi_transp.setEnabled(True)
            self._fcn_area_translucent()
        else:
            raise ValueError("No ROI selected.")

    def _fcn_area_translucent(self, *args):
        """Use opaque / translucent roi."""
        self.roi.mesh.translucent = self._roi_transp.isChecked()

    def _fcn_show_screenshot(self):
        """Display the screenshot GUI."""
        self._ssGui.show()



    def create_layout(self):
        '''set the layout for the app'''
        # layout for the main window
        #
        # layout for sEEG data infomation
        layout_0 = QVBoxLayout()
        layout_0.setSpacing(1)
        layout_0.addWidget(self.epoch_num_label)
        layout_0.addWidget(self.epoch_num_cont_label)

        layout_1 = QVBoxLayout()
        layout_1.setSpacing(1)
        layout_1.addWidget(self.samp_rate_label)
        layout_1.addWidget(self.samp_rate_cont_label)

        layout_2 = QVBoxLayout()
        layout_2.setSpacing(1)
        layout_2.addWidget(self.chan_label)
        layout_2.addWidget(self.chan_cont_label)

        layout_3 = QVBoxLayout()
        layout_3.setSpacing(1)
        layout_3.addWidget(self.start_label)
        layout_3.addWidget(self.start_cont_label)

        layout_4 = QVBoxLayout()
        layout_4.setSpacing(1)
        layout_4.addWidget(self.end_label)
        layout_4.addWidget(self.end_cont_label)

        layout_5 = QVBoxLayout()
        layout_5.setSpacing(1)
        layout_5.addWidget(self.event_class_label)
        layout_5.addWidget(self.event_class_cont_label)

        layout_6 = QVBoxLayout()
        layout_6.setSpacing(1)
        layout_6.addWidget(self.event_num_label)
        layout_6.addWidget(self.event_num_cont_label)

        layout_7 = QVBoxLayout()
        layout_7.setSpacing(1)
        layout_7.addWidget(self.time_point_label)
        layout_7.addWidget(self.time_point_cont_label)

        layout_8 = QVBoxLayout()
        layout_8.setSpacing(1)
        layout_8.addWidget(self.data_size_label)
        layout_8.addWidget(self.data_size_cont_label)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(0)
        info_layout.addLayout(layout_0)
        info_layout.addLayout(layout_1)
        info_layout.addLayout(layout_2)
        info_layout.addLayout(layout_3)
        info_layout.addLayout(layout_4)
        info_layout.addLayout(layout_5)
        info_layout.addLayout(layout_6)
        info_layout.addLayout(layout_7)
        info_layout.addLayout(layout_8)

        file_name_layout = QHBoxLayout()
        file_name_layout.setSpacing(0)
        file_name_layout.addWidget(self.file_name_label)
        file_name_layout.addWidget(self.file_name_cont_label)


        data_info_layout = QVBoxLayout()
        data_info_layout.setSpacing(4)
        data_info_layout.setContentsMargins(0, 0, 0, 4)
        data_info_layout.addWidget(self.data_info_label)
        data_info_layout.addLayout(file_name_layout)
        data_info_layout.addLayout(info_layout)

        self.seeg_info_box.setLayout(data_info_layout)

        # layout for sEEG Elaborate electrodes
        vis_layout = QVBoxLayout()
        vis_layout.setSpacing(4)
        vis_layout.setContentsMargins(0, 0, 0, 0)
        vis_layout.addWidget(self.electro_title_label)
        # vis_layout.addWidget(self.play_cb)
        vis_layout.addWidget(self.widget)
        self.vis_box.setLayout(vis_layout)

        # layout for protocol
        left_layout_0 = QVBoxLayout()
        left_layout_0.setContentsMargins(0, 0, 0, 0)
        left_layout_0.addWidget(self.protocol_label)
        left_layout_1 = QVBoxLayout()
        left_layout_1.setSpacing(0)
        left_layout_1.setContentsMargins(0, 0, 0, 0)
        left_layout_1.addWidget(self.subject_cb, stretch=1)
        left_layout_1.addWidget(self.subject_stack, stretch=100)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(3)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addLayout(left_layout_0, stretch=1)
        left_layout.addLayout(left_layout_1, stretch=100)
        self.protocol_box.setLayout(left_layout)

        # layout for main window
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        self.seeg_info_box.setAlignment(Qt.AlignTop)
        right_layout.addWidget(self.seeg_info_box, stretch=1)
        right_layout.addWidget(self.vis_box, stretch=100)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.addWidget(self.protocol_box)
        main_layout.addLayout(right_layout)
        self.center_widget.setLayout(main_layout)


    def set_qt_style(self):
        '''use QSS to beautify the interface'''

        # 备用字体：Arial、Consolas、Tahoma、Segoe UI、Sitka Text
        self.setStyleSheet('''         
                QLabel[name='title']{font: bold 15pt Times New Roman; 
                    color:rgb(0,120,215)} 
                QLabel[name='group0']{background-color:rgb(244,244,244);
                    font:bold 13pt Sitka Text}
                QLabel[name='group1']{background-color:rgb(244,244,244);
                    font:bold 13pt Sitka Text; color:rgb(97,38,33)}
                QLabel[name='electro']{background-color:rgb(244,244,244); font: bold 15pt Sitka Text}
                QLabel[name='electro_pic']{background-color:white;}
                QLabel[name='empty']{background-color:white}
                QPushButton[name='func']{background-color:rgb(244,244,244);
                    font:bold 12pt Sitka Text; border-radius: 6px}
                QPushButton[name='func']:hover{background-color:white}
                QPushButton[name='func']:pressed{background-color:white;
                    padding=left:3px; padding-top:3px}
                QGroupBox[name='sub']{background-color:rgb(207, 207, 207); border: 1px solid black}
                QGroupBox[name='ptc']{background-color:white; border: none}
                QWidget[name='center']{background-color:rgb(207, 207, 207)}
                QComboBox[name='ptc']{font:15pt Times New Roman}
                QTreeWidget[name='ptc']{font:13pt Times New Roman}
                
        ''')
        # ; border: none
        self.file_name_label.setStyleSheet('''
                QLabel{background-color:rgb(244,244,244); 
                    font: bold 17pt Sitka Text; color:rgb(0,0,0); }
        ''')
        self.file_name_cont_label.setStyleSheet('''
                QLabel{background-color:rgb(244,244,244); 
                    font: bold 17pt Sitka Text; color:rgb(97,38,33)}
        ''')
        self.menuBar().setStyleSheet('''
                QMenuBar{border: 3px solid rgb(207, 207, 207); font: 13pt}
        ''')


#*****************************************slot*****************************************

############################################# File ######################################################


    def show_error(self, error):
        print('*********************************************************************')
        print('Error is: ')
        traceback.print_exc()
        print('*********************************************************************')
        QMessageBox.warning(self, 'Error shows up!', error.args[0])


    # File menu function
    #
    # create qtreeview
    def create_subject(self):
        self.subject_name, _ = QInputDialog.getText(self, 'Subject name', 'Please Name this subject',
                                           QLineEdit.Normal)
        try:
            if self.subject_name:
                try:
                    self.subject_stack.removeWidget(self.empty_label_0)
                except Exception as error:
                    pass
                try:
                    self.subject_stack.removeWidget(self.tree)
                except Exception as error:
                    pass
                self.subject[self.subject_name] = Subject(name=self.subject_name)
                self.subject_cb.addItem(self.subject_name)
                self.subject_cb.setCurrentText(self.subject_name)
                self.tree = QTreeWidget()
                self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
                self.tree.setProperty('name', 'ptc')
                self.root = self.tree.invisibleRootItem()
                self.tree.setHeaderHidden(True)  # 隐藏列标题栏
                self.node_00 = QTreeWidgetItem(self.tree)
                self.node_00.setText(0, self.subject_name)
                self.node_00.setIcon(0, QIcon('image/subject.ico'))
                self.tree.expandAll()
                self.tree.itemChanged.connect(self.change_current_data)
                self.tree_dict[self.subject_name] = self.tree
                self.subject_stack.addWidget(self.tree)
                self.tree_item[self.subject_name] = dict()
                self.tree_item[self.subject_name]['root'] = self.node_00
                print('创建subject', self.subject_name)
                self.load_coord.setEnabled(True)
            self.import_action.setEnabled(True)
            self.import_epoch_action.setEnabled(True)
            self.elec_df = None
            self.reset_source(self.subject_name)
        except Exception as error:
            self.show_error(error)


    def reset_source(self, name):
        if self.sources is not None:
            try:
                self.group_stack.removeWidget(self._source_group)
                self.group_stack.addWidget(self._brain_group)
                self._obj_type_lst.setCurrentIndex(0)
                self._source_group = None
                self.sources.parent = None
                self.sources = None
            except:
                pass
        if self.elec_df is None:
            self._source_group = None
            try:
                self.sources.parent = None
                self.sources = None
            except:
                pass
            self.group = None
            self._obj_type_lst.model ().item (1).setEnabled (False)
        else:
            print('该被试的数据不为None', name)
            self.group = self.subject[name].group
            self.s_obj = self.subject[name].s_obj
            self._source_widget ()
            self._obj_type_lst.model().item (1).setEnabled(True)


    def change_sub_name(self, text):

        if len(self.tree_dict) == 0:
            pass
        else:
            self.subject_name = self.subject_cb.currentText()
            try:
                self.subject_stack.removeWidget(self.tree)
            except:
                pass
            self.tree = self.tree_dict[self.subject_name]
            self.subject_stack.addWidget(self.tree)
            self.s_obj = self.subject[self.subject_name].s_obj
            self.elec_df = self.subject[self.subject_name].coord
            self.reset_source(self.subject_name)





    def get_all_items(self):

        item = []
        child = []
        key = self.subject_cb.currentText()
        iterator = QTreeWidgetItemIterator(self.tree_dict[key], QTreeWidgetItemIterator.All)
        while iterator.value():
            node = iterator.value()
            name = iterator.value().text(0)
            print(name)
            if name not in [key, 'Raw sEEG' , 'Epoch sEEG']:
                item.append(node)
            child.append(name)
            iterator += 1
        print('all child name:', child)
        return child, item


    # import sEEG data
    def show_pbar(self):
        self.pbar = My_Progress()
        self.pbar.show()


    def execute_import_data(self):
        '''execute import data worker'''

        subject_name = self.subject_cb.currentText()
        if not subject_name:
            QMessageBox.warning(self,'Error', 'Please create a subject first')
        else:
            self.data_path, _ = QFileDialog.getOpenFileName(self, 'Import data')
            if 'set' == self.data_path[-3:] or \
               'edf' == self.data_path[-3:] or \
               'fif' == self.data_path[-3:] or \
               'vhdr' == self.data_path[-4:]:
                self.import_worker.data_path = self.data_path
                self.import_worker.start()
                self.flag += 1
                self.data_mode = 'raw'
                self.show_pbar()
            elif self.flag == 0 and self.data_path:
                QMessageBox.warning(self, 'Data Format Error',
                                    'Please select the right file!')


    def execute_load_epoched_data(self):
        '''execute load epoched data'''
        subject_name = self.subject_cb.currentText()
        if not subject_name:
            QMessageBox.warning(self, 'Error', 'Please create a subject first')
        else:
            self.data_path, _ = QFileDialog.getOpenFileName(self, 'Import epoch')
            try:
                if('set' == self.data_path[-3:])  or \
                 ('fif' == self.data_path[-3:]) or \
                 ('edf' == self.data_path[-3:]):
                    self.load_epoched_data_worker.data_path = self.data_path
                    self.load_epoched_data_worker.start()
                    self.flag += 1
                    self.data_mode = 'epoch'
                    self.show_pbar()
            except Exception as error:
                self.show_error(error)
                QMessageBox.warning(self, 'Data Format Error',
                                    'Please select the right file!')


    def get_seeg_data(self, seeg_data):
        '''get seeg data'''
        self.pbar.step = 100
        self.pbar.close()
        try:
            self.key, _ = QInputDialog.getText(self, 'Name this Data', 'Please Name the Data',
                                          QLineEdit.Normal)
            child, _ = self.get_all_items()
            if self.key:
                if self.data_mode == 'raw':
                    self.key += '_raw'
                    if self.key in child:
                        QMessageBox.warning(self, 'Name repeated', 'The name is already exists, please retype!')
                        self.key, _ = QInputDialog.getText(self, 'Name this Data', 'Please Name the Data',
                                                            QLineEdit.Normal)
                    else:
                        [self.raw_action[action].setEnabled(True) for action in self.raw_action]
                elif self.data_mode == 'epoch':
                    self.key += '_epoch'
                    if self.key in child:
                        QMessageBox.warning(self, 'Name repeated', 'The name is already exists, please retype!')
                        self.key, _ = QInputDialog.getText(self, 'Name this Data', 'Please Name the Data',
                                                            QLineEdit.Normal)
                    else:
                        [self.epoch_action[action].setEnabled(True) for action in self.epoch_action]
                subject_name = self.subject_cb.currentText()

                self.subject[subject_name].seeg[self.key] = SEEG(name=self.key, data=seeg_data,
                                                                 mode=self.data_mode)
                self.subject[subject_name].seeg[self.key].data_para['path'] = self.data_path
                if self.data_mode == 'raw':
                    des = list(set(seeg_data._annotations.description))
                    event_id = {str(mark): int(mark) for mark in des}
                    events, _ = mne.events_from_annotations(seeg_data, event_id=event_id)
                    self.subject[subject_name].seeg[self.key].events = events
                    if 'Raw sEEG' in child:
                        self.node_20 = QTreeWidgetItem(self.tree_item[subject_name]['raw'])
                        self.node_20.setText(0, self.key)
                        self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                        self.node_20.setCheckState(0, Qt.Checked)
                        self.tree.expandAll()
                    else:
                        self.node_10 = QTreeWidgetItem(self.tree_item[subject_name]['root'])
                        self.node_10.setText(0, 'Raw sEEG')
                        self.node_10.setIcon(0, QIcon('image/EEG.ico'))
                        self.node_20 = QTreeWidgetItem(self.node_10)
                        self.node_20.setText(0, self.key)
                        self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                        self.node_20.setCheckState(0, Qt.Checked)
                        self.tree_item[subject_name]['raw'] = self.node_10
                        self.tree.expandAll()
                elif self.data_mode == 'epoch':
                    self.subject[subject_name].seeg[self.key].events = seeg_data.events
                    if 'Epoch sEEG' in child:
                        self.node_20 = QTreeWidgetItem(self.tree_item[subject_name]['epoch'])
                        self.node_20.setText(0, self.key)
                        self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                        self.node_20.setCheckState(0, Qt.Checked)
                        self.tree.expandAll()
                    else:
                        self.node_11 = QTreeWidgetItem(self.tree_item[subject_name]['root'])
                        self.node_11.setText(0, 'Epoch sEEG')
                        self.node_11.setIcon(0, QIcon('image/EEG.ico'))
                        self.node_20 = QTreeWidgetItem(self.node_11)
                        self.node_20.setText(0, self.key)
                        self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                        self.node_20.setCheckState(0, Qt.Checked)
                        self.tree_item[subject_name]['epoch'] = self.node_11
                        self.tree.expandAll()
                self.subject[subject_name].seeg[self.key].get_para()
                self.event = self.subject[subject_name].seeg[self.key].events
                self.set_current_data(key=self.key)
                del seeg_data
                gc.collect()
            else:
                del seeg_data
        except Exception as error:
            if error.args[0] == "'str' object has no attribute 'annotations'":
                QMessageBox.warning(self, 'Data Error',
                                    'This is not raw data')
            elif error.args[0] == "'str' object has no attribute 'events'":
                QMessageBox.warning(self, 'Data Error',
                                    'This is not epoch data')
            else:
                self.show_error(error)


    def set_current_data(self, key):
        '''set the curent seeg data'''
        self.key = key
        subject_name = self.subject_cb.currentText()
        self.current_data = self.subject[subject_name].seeg[self.key]
        self.data_mode = self.subject[subject_name].seeg[self.key].mode
        print('----------------------------')
        print("current data\'s key:", key)
        print('----------------------------')
        self.data_info_signal.connect(self.update_func)
        self.data_info_signal.emit(self.current_data.data_para)
        if self.data_mode == 'raw':
            [self.raw_action[action].setEnabled(True) for action in self.raw_action]
            [self.epoch_action[action].setEnabled(False) for action in self.epoch_action]
        elif self.data_mode == 'epoch':
            [self.raw_action[action].setEnabled(False) for action in self.raw_action]
            [self.epoch_action[action].setEnabled(True) for action in self.epoch_action]


    def change_current_data(self, item, column):

        try:
            if item.checkState(column) == Qt.Checked:
                subject_name = self.subject_cb.currentText()
                self.current_sub = self.subject[subject_name]
                key = item.text(column)
                child, item_all = self.get_all_items()
                for i in item_all:
                    if i != item and(('raw' in item.text(column)) or('epoch' in item.text(column))):
                        i.setCheckState(0, Qt.Unchecked)
                self.set_current_data(key)

        except Exception as error:
            self.show_error(error)


    # save sEEG data

    def save_edf(self):

        self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data to EDF')
        try:
            write_raw_edf(self.save_path, self.current_data.data)
        except Exception as error:
            self.show_error(error)


    def save_set(self):

        self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data to EDF')
        try:
            write_raw_set(self.save_path + '.set', self.current_data.data)
        except Exception as error:
            self.show_error(error)


    def save_fif(self):
        '''save as .fif data'''
        self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
        if not self.save_path:
            try:
                self.current_data.data.save(self.save_path + '.fif', overwrite=True)
            except Exception as error:
                self.show_error(error)
        else:
            pass


    def save_pd(self):

        pass


    def export_npy(self):

        save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
        try:
            np.save(save_path + '_data', self.current_data.data)
            np.save(save_path + '_label', self.current_data.events)
        except Exception as error:
            self.show_error(error)


    def export_mat(self):

        try:
            self.current_data.data.load_data()
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            sio.savemat(self.save_path + '_data.mat', {'seeg_data':self.current_data.data._data})
            sio.savemat(self.save_path + '_label.mat', {'label':self.current_data.events})
        except Exception as error:
            self.show_error(error)


    def clear_all(self):
        '''clear the whole workshop'''
        try:
            del self.flag, self.tree_dict, self.tree_item, self.subject, self.event
            del self.current_data, self.data_mode, self.event_set
            gc.collect()
            self.tree_dict = dict()
            self.tree_item = dict()
            self.subject = dict()
            self.event_set = dict()
            self.subject_cb.clear()
            self.subject_cb.setCurrentText('')
            self.flag = 0
            self.data_mode = None
            self.event = None
            try:
                self.subject_stack.removeWidget(self.tree)
                self.subject_stack.addWidget(self.empty_label_0)
            except Exception as error:
                self.show_error(error)

            self.data_info_signal.connect(self.update_func)
            self.data_info_signal.emit(dict())
        except Exception as error:
            self.show_error(error)
        except Exception as error:
            self.show_error(error)


############################################# Raw ######################################################
    # Raw data function
    #
    # rereference sEEG data
    def choose_ref(self):
        '''choose reference using the refernce button'''
        self.ref_win = Refer_Window()
        self.ref_win.ref_signal.connect(self.execute_ref)
        self.ref_win.show()


    def execute_ref(self, ref_name):
        if ref_name == 'Common Average':
            self.car_reref()
        elif ref_name == 'Gray-white Matter':
            self.gwr_reref()
        elif ref_name == 'Electrode Shaft':
            self.esr_reref()
        elif ref_name == 'Bipolar':
            self.bipolar_reref()
        elif ref_name == 'Monopolar':
            self.monopolar_reref()
        elif ref_name == 'Laplacian':
            self.laplacian_reref()


    def car_reref(self):
        '''Reference sEEG data using Common Average Reference(CAR)'''
        data = self.current_data.data.copy()
        print(data)
        raw = car_ref(data, data_class=self.data_mode)
        self.get_seeg_data(raw)


    def gwr_reref(self):
        '''Reference sEEG data using Gray-white Matter Reference(GWR)'''
        data = self.current_data.data.copy()
        self.coord_path, _ = QFileDialog.getOpenFileName(self, 'Load MNI Coornidates')
        print(self.coord_path)
        try:
            raw = gwr_ref(data, data_class=self.data_mode, coord_path=self.coord_path)
            self.get_seeg_data(raw)
        except Exception as error:
            self.show_error(error)


    def esr_reref(self):
        '''Reference sEEG data using Electrode Shaft Reference(ESR)'''
        data = self.current_data.data.copy()
        try:
            raw = esr_ref(data, data_class=self.data_mode)
            self.get_seeg_data(raw)
        except Exception as error:
            self.show_error(error)


    def bipolar_reref(self):
        '''Reference sEEG data using Bipolar Reference'''
        data = self.current_data.data.copy()
        try:
            raw, _ = bipolar_ref(data, data_class=self.data_mode)
            self.get_seeg_data(raw)
        except Exception as error:
            self.show_error(error)


    def monopolar_reref(self):

        self.chan_win = Select_Chan(chan_name=self.current_data.data.ch_names)
        self.chan_win.chan_signal.connect(self.start_monopolar)
        self.chan_win.show()


    def start_monopolar(self, ref_chan):
        '''Reference sEEG data using Monopolar Reference'''
        data = self.current_data.data.copy()
        try:
            raw = monopolar_ref(data, data_class=self.data_mode, ref_chan=ref_chan)
            self.get_seeg_data(raw)
        except Exception as error:
            self.show_error(error)


    def laplacian_reref(self):
        '''Reference sEEG data using Laplacian Reference'''
        data = self.current_data.data.copy()
        try:
            raw, _ = laplacian_ref(data, data_class=self.data_mode)
            self.get_seeg_data(raw)
        except Exception as error:
            self.show_error(error)


    # select sub-time
    def select_time(self):

        time_end = round(self.current_data.data._last_time, 2)
        self.select_time_win = Select_Time(time_end)
        self.select_time_win.time_signal.connect(self.get_time)
        self.select_time_win.show()


    def get_time(self, time):

        self.time_new = time
        print('Time selected', self.time_new)
        crop_data = self.current_data.data.copy().crop(self.time_new[0], self.time_new[1])
        self.get_seeg_data(crop_data)


    def del_useless_chan(self, data):
        '''delete useless channels'''
        try:
            chans = data.ch_names
            useless_chan = [chan for chan in chans if 'DC' in chan or 'BP' in chan
                            or 'EKG' in chan or 'EMG' in chan]
            del_useless_data = data.copy().drop_channels(useless_chan)
            print('----------------------------')
            print('useless channles detected: ', useless_chan)
            print('----------------------------')
            print('delete useless channels finished')
            print('----------------------------')
            self.get_seeg_data(del_useless_data)
        except Exception as error:
            self.show_error(error)


    def calculate_marker(self):
        '''calculate the markers for sEEG from Shenzhen University General Hosptial'''
        marker_chan_0 = ['POL DC09', 'POL DC10', 'POL DC11', 'POL DC12',
                           'POL DC13', 'POL DC14', 'POL DC15']
        marker_chan_1 = ['DC09', 'DC10', 'DC11', 'DC12',
                         'DC13', 'DC14', 'DC15']
        try:
            mark_data = self.current_data.data.copy().pick_channels(marker_chan_0)._data * 1e6
        except Exception as error:
            QMessageBox.warning(self, 'Marker Calculating Error', 'No channels match the selection')
            print('*****************************')
            print('Error is:', type(error), error.args[0])
            print('*****************************')
        else:
            mark_data_mean = np.mean(mark_data, axis=1).reshape(7, 1)
            mark_data_mean = np.tile(mark_data_mean,(1, mark_data.shape[1]))  # 计算均值并拓展到和数据一样的维度
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

            freq = self.current_data.data.info['sfreq']
            event_onset =(self.event_latency / freq).astype(np.float64)
            self.my_annot = Annotations(
                onset=event_onset[0, :], duration=np.zeros(event_onset[0, :].shape[0]),
                description=self.event_id[0, :])
            annot_data = self.current_data.data.copy().set_annotations(self.my_annot)
            self.event, _ = events_from_annotations(self.current_data.data)

            self.event_test = np.zeros((self.event_id.shape[1], 3)).astype(np.int32)
            self.event_test[:, 0], self.event_test[:, 2] = self.event_latency, self.event_id

            if self.event.all() == self.event_test.all():
                print('码可通过')
            return annot_data


    def get_mark_del_chan(self):

        try:
            annot_data = self.calculate_marker()
            self.del_useless_chan(annot_data)
        except Exception as error:
            self.show_error(error)


    # set event id_dict
    def get_event_name(self):

        para = list(set(self.current_data.events[:, 2]))
        print(para)
        self.event_window = Event_Window(para)
        self.event_window.line_edit_signal.connect(self.set_event)
        self.event_window.show()


    def set_event(self, event_name, event_id):

        try:
            for i in range(len(event_name)):
                self.event_set[event_name[i]] = int(event_id[i])
            print(self.event_set)
        except Exception as error:
            self.show_error(error)


    def get_epoch_time_range(self):

        self.epoch_time = Epoch_Time()
        self.epoch_time.time_signal.connect(self.get_epoch_data)
        self.epoch_time.show()


    def get_epoch_data(self, tmin, tmax, base_tmin, base_tmax):

        try:
            if self.current_data.mode == 'raw':
                if tmin < 0 and tmax >= 0:
                    if len(self.event_set):
                        epoch_data = Epochs(self.current_data.data, self.current_data.events,
                                                event_id=self.event_set, tmin=tmin, tmax=tmax,
                                            baseline=(base_tmin, base_tmax))
                    else:
                        epoch_data = Epochs(self.current_data.data, self.current_data.events,
                                            tmin=tmin, tmax=tmax, baseline=(base_tmin, base_tmax))
                    self.data_mode = 'epoch'
                    self.get_seeg_data(epoch_data)
        except Exception as error:
            self.show_error(error)

############################################# Epoch #####################################################
    # Epoch function
    #
    # apply baseline to correct the epochs
    def apply_base_win(self):

        self.base_time_win = Baseline_Time()
        self.base_time_win.time_signal.connect(self.apply_base)
        self.base_time_win.show()


    def apply_base(self, tmin, tmax):

        raw = self.current_data.data.copy()
        data_mode = self.current_data.mode
        if data_mode == 'epoch':
            try:
                print('---------------correcting epochs---------------')
                raw.apply_baseline(baseline=(tmin, tmax))
                self.get_seeg_data(raw)
            except Exception as error:
                self.show_error(error)



    # select sub-event
    def select_event(self):

        event = list(set(self.current_data.events[:, 2]))
        self.select_event_win = Select_Event(event)
        self.select_event_win.event_signal.connect(self.get_event)
        self.select_event_win.show()


    def get_event(self, event_select):
        data = self.current_data.data
        print(len(event_select))
        if len(event_select) == 1:
            for i in data.event_id:
                if data.event_id[i] == int(event_select[0]):
                    data_sel =data[str(i)]
        else:
            pass
        self.get_seeg_data(data_sel)


    # Time analysis
    #
    # EP
    def choose_evoke(self):
        data = self.current_data.data.copy()
        self.event = data.event_id
        del data
        self.choose_evoke_win = Select_Event(list(self.event.keys()))
        self.choose_evoke_win.event_signal.connect(self.visual_evoke_brain)
        self.choose_evoke_win.show()


    def visual_evoke_brain(self, event):

        from mne.channels import compute_native_head_t
        from mne.coreg import get_mni_fiducials
        from mne.channels import make_dig_montage

        evoke = self.current_data.data[event].average()

        subjects_dir = 'datasets/subjects'
        subject = 'fsaverage'
        fname_src = os.path.join(subjects_dir, 'fsaverage', 'bem',
                    'fsaverage-vol-5-src.fif')

        subject_name = self.subject_cb.currentText()
        try:
            self.ch_coords = self.subject[subject_name].coord

            lpa, nasion, rpa = get_mni_fiducials(
                subject, subjects_dir=subjects_dir)
            lpa, nasion, rpa = lpa['r'], nasion['r'], rpa['r']
            montage = make_dig_montage(
                self.ch_coords, coord_frame='mri', nasion=nasion, lpa=lpa, rpa=rpa)
            trans = compute_native_head_t(montage)

            vol_src = mne.read_source_spaces(fname_src)
            stc = mne.stc_near_sensors(
                evoke, trans, subject, subjects_dir=subjects_dir, src=vol_src,
                verbose='error')
            stc = abs(stc)  # just look at magnitude
            clim = dict(kind='value', lims=np.percentile(abs(evoke.data), [10, 50, 75]))
            brain = stc.plot_3d(
                src=vol_src, subjects_dir=subjects_dir,
                view_layout='horizontal', views=['axial', 'coronal', 'sagittal'],
                size=(800, 300), show_traces=0.4, clim=clim,
                add_data_kwargs=dict(colorbar_kwargs=dict(label_font_size=8)))
        except Exception as error:
            if error.args[0] == "MNI":
                QMessageBox.warning(self, 'Mnotage error', 'Please import MNI Coordinates')
            else:
                self.show_error(error)


    def show_tf_win(self):
        data = self.current_data.data
        subject = self.subject_cb.currentText()
        self.tf_win = Time_Freq_Win(data, subject)
        self.tf_win.show()


    def show_con_win(self):
        data = self.current_data.data
        subject = self.subject_cb.currentText()
        self.con_win = Con_Win(data, subject)
        self.con_win.show()


############################################ Shared ####################################################

    # the functions shared between Raw data and Epoch data
    #
    # select sub-channel
    def select_chan(self):

        self.select_chan_win = Select_Chan(chan_name=self.current_data.data.ch_names)
        self.select_chan_win.chan_signal.connect(self.get_sel_chan)
        self.select_chan_win.show()


    def get_sel_chan(self, chan):

        self.chan_sel = chan
        self.current_data.data.load_data()
        sel_chan_data = self.current_data.data.copy().pick_channels(self.chan_sel)
        self.get_seeg_data(sel_chan_data)


    # rename the channels
    def rename_chan(self):
        '''delete the 'POL' in channels' name '''
        try:
            rename_chan_data = self.current_data.data.copy().\
                rename_channels({chan: chan[4:] for chan in self.current_data.data.ch_names
                                 if 'POL' in chan})
            rename_chan_data = rename_chan_data.rename_channels({chan: chan[4:6] for chan in rename_chan_data.ch_names
                                 if 'Ref' in chan})
            # print(rename_chan_data)
            self.get_seeg_data(rename_chan_data)
        except Exception as error:
            self.show_error(error)


    # resample the seeg data
    def execute_resample_data(self):

        try:
            if self.current_data.data is not None:
                self.resample_worker.resampling_rate,_ = self.value, _ = QInputDialog.getInt(self, 'Resample Data', 'Resample Rate(Hz)', 0, 0)
                print(self.resample_worker.resampling_rate)
                if self.resample_worker.resampling_rate > 0:
                    print('开始重采样')
                    self.resample_worker.data = self.current_data.data
                    self.resample_worker.start()
        except Exception as error:
            print('*********************************************************************')
            self.show_error(error)
            print('*********************************************************************')


    # filt sEEG data with fir filter
    def filter_data_fir(self):
        self.fir_filter_window = Choose_Window('fir')
        self.fir_filter_window.signal.connect(self.filter_subwindow_para)
        self.fir_filter_window.notch_signal.connect(self.filter_subwindow_para)
        self.filter_worker.filter_mode = 'fir'
        self.fir_filter_window.show()


    # filt sEEG data with iir filter
    def filter_data_iir(self):
        self.iir_filter_window = Choose_Window('iir')
        self.iir_filter_window.signal.connect(self.filter_subwindow_para)
        self.iir_filter_window.notch_signal.connect(self.filter_subwindow_para)
        self.filter_worker.filter_mode = 'iir'
        self.iir_filter_window.show()


    def filter_subwindow_para(self, low_freq, high_freq, notch_freq):
        '''
        :param low_freq: lowpass cut frequency
        :param high_freq: highpass cut frequency
        :param notch_freq: notch frequency
        :return:
        '''
        try:
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
                self.filter_worker.seeg_data = self.current_data.data
                self.filter_worker.start()
        except Exception as error:
            self.show_error(error)


    # plot raw data
    def plot_raw_data(self):

        try:
            if self.current_data.mode == 'raw':
                print('画图了')
                self.canvas = None
                self.current_data.data.plot(duration=5.0, n_channels=20, title='Raw sEEG')
                plt.get_current_fig_manager().window.showMaximized()
            elif self.current_data.mode == 'epoch':
                self.canvas = None
                self.current_data.data.plot(n_channels=20, n_epochs=5, scalings={'eeg':100e-6}, title='Epoched sEEG data')
                plt.get_current_fig_manager().window.showMaximized()
        except Exception as error:
            self.show_error(error)


    def drop_bad_chan(self):
        data = self.current_data.data.copy()
        if len(data.info['bads']):
            data.drop_channels(data.info['bads'])
            data.info['bads'] = []
            self.get_seeg_data(data)
        else:
            pass


    def drop_bad_epochs(self):
        data = self.current_data.data.copy()
        data.drop_bad()
        self.get_seeg_data(data)


    def interpolate_bad(self):
        data = self.current_data.data.copy()
        data.load_data()
        data.interpolate_bads()
        self.get_seeg_data(data)


    def plot_topo_psd(self):

        try:
            if self.current_data.mode:
                self.current_data.data.plot_psd_topo(n_jobs=2)
        except Exception as error:
            self.show_error(error)


    def load_coordinate(self):
        '''Electrodes Visualization'''
        subject_name = self.subject_cb.currentText()
        if not subject_name:
            QMessageBox.warning(self, 'Error', 'Please create a subject first')
        else:
            mni_path, _ = QFileDialog.getOpenFileName(self, 'Load MNI Coornidates')
            if mni_path:
                self.elec_df = pd.read_csv(mni_path, sep='\t', header=None, index_col=None)
                self.subject[subject_name].coord = self.elec_df
                self.ch_names = self.elec_df[0].tolist()
                self.ch_group = get_chan_group(chans=self.ch_names)
                self.group = list (self.ch_group.keys())
                self.subject[subject_name].group = self.group
                self.elec_df.set_index([0], inplace=True)
                self.ch_pos = self.elec_df[[1, 2, 3]].to_numpy(dtype=float)
                ch_coords = []
                [ch_coords.append(self.ch_group[group]) for group in self.ch_group]
                self.subject[subject_name].s_obj = self.s_obj = [SourceObj(str(group), xyz=self.elec_df.loc[self.ch_group[group]].to_numpy(dtype=float),
                                         text=self.ch_group[group], color=u_color[index % 15], **self.s_kwargs)
                              for index, group in enumerate(self.ch_group)]
                self._source_widget()
                self._obj_type_lst.model().item(1).setEnabled(True)
                # ch_names = coord[0].tolist()
                # data.info['bads'].extend([ch for ch in data.ch_names if ch not in ch_names])
                # data.drop_channels(data.info['bads'])



############################################# Help #####################################################
    # Help menu function
    #
    # show website
    def show_setting(self):
        pass


    def show_website(self):

        QDesktopServices.openUrl(QUrl("http://bme.szu.edu.cn/20161/0325/54.html"))


    def show_licence(self):

        pass


    def send_email(self):

        pass


    def update_func(self, para):
        '''update label text'''
        try:
            if len(para):
                self.file_name_cont_label.setText(para['path'])
                self.epoch_num_cont_label.setText(para['epoch_num'])
                self.samp_rate_cont_label.setText(para['sfreq'])
                self.chan_cont_label.setText(para['chan_num'])
                self.start_cont_label.setText(para['epoch_start'])
                self.end_cont_label.setText(para['epoch_end'])
                self.event_class_cont_label.setText(para['event_class'])
                self.event_num_cont_label.setText(para['event_num'])
                self.time_point_cont_label.setText(para['time_point'])
                self.data_size_cont_label.setText(para['data_size'])
            else:
                self.file_name_cont_label.setText('')
                self.epoch_num_cont_label.setText('')
                self.samp_rate_cont_label.setText('')
                self.chan_cont_label.setText('')
                self.start_cont_label.setText('')
                self.end_cont_label.setText('')
                self.event_class_cont_label.setText('')
                self.event_num_cont_label.setText('')
                self.time_point_cont_label.setText('')
                self.data_size_cont_label.setText('')
        except Exception as error:
            # self.show_error(error)
            pass










