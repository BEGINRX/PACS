# -*- coding: utf-8 -*-
'''
@File  : main_window_new.py
@Author: 刘政
@Date  : 2020/9/17 15:14
@Desc  : new main window
'''

import traceback
import matplotlib
import mne
import numpy as np
import scipy.io as sio
import gc

matplotlib.use('Qt5Agg')

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QAction, QMenu, \
    QFileDialog, QLabel, QGroupBox, QVBoxLayout, QHBoxLayout,  \
    QMessageBox, QInputDialog, QLineEdit, QWidget, QPushButton, QStyleFactory, \
    QApplication, QTreeWidget, QComboBox, QStackedWidget, QTreeWidgetItem, \
    QTreeWidgetItemIterator
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.Qt import QCursor
from PyQt5.QtGui import QKeySequence, QIcon, QDesktopServices
from gui.my_thread import Import_Thread, Load_Epoched_Data_Thread, Resample_Thread, Filter_Thread
from gui.sub_window import Choose_Window, Event_Window, Select_Time, Select_Chan, Epoch_Time
from mne import events_from_annotations



class MainWindow(QMainWindow):
    '''
    The main window
    '''

    data_info_signal = pyqtSignal(dict)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.flag = 0
        self.tree_dict = dict()
        # tree_raw_item has the tree items in raw sEEG data
        self.tree_item = dict()
        # data info save the basic information of sEEG data to show in the main window
        self.data_info = dict()
        # subject dict should have this structure:
        # 1. key(subject) - the name of the subject
        # 2. seeg(dict) - the sEEG data structure
        # 4. MRI - the MRI of this subject
        # 5. MNI coordinates - to plot the depth electrodes on 'fsaverage' brain
        self.subject_data = dict()
        # sEEG dict should have this structure:
        # key0(user set) - data's name
        # key0-data(dict) - sEEG data; sEEG's path; sEEG's mode(raw or epoch)
        # key1(user set) - processed data's name
        # key1-data(dict) - processed sEEG data; processed sEEG's path; processed sEEG's mode(raw or epoch)
        # key2 ...
        self.seeg = dict()
        # current_data tells us which seeg data we want to use by choosing
        # the 'key' in current subject's protocol
        self.current_data = dict()
        # mri dict should have this structure:
        # key0 - mri_0
        # key1 - mri_1
        # key2 ...
        self.mri = dict()
        # current mri tells us which mri we wnt to use by choosing the 'key'
        # in current subject's protocol
        self.current_mri = dict()
        # tell us the mode of the target sEEG data(raw or epoch)
        self.data_mode = None
        self.event_set = None
        self.event = None

        self.init_ui()


    def init_ui(self):
        self.setWindowIcon(QIcon('image/source.jpg'))
        self.frame()
        self.create_central_widget()
        self.create_worker()
        self.create_action()
        self.create_label()
        self.create_stack()
        self.create_button()
        self.create_combo_box()
        self.create_group_box()
        self.create_menubar()
        self.create_layout()
        self.set_qt_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def frame(self):
        '''set the app window to the center of the displayer of the computer'''
        # self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        fg= self.frameGeometry()
        self.rect = QDesktopWidget().availableGeometry()
        cp = self.rect.center()
        fg.moveCenter(cp)
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


    def create_sub_windows(self):

        self.fir_filter_window = Choose_Window('fir')
        self.fir_filter_window.signal.connect(self.filter_subwindow_para)
        self.fir_filter_window.notch_signal.connect(self.filter_subwindow_para)
        self.iir_filter_window = Choose_Window('iir')
        self.iir_filter_window.signal.connect(self.filter_subwindow_para)
        self.iir_filter_window.notch_signal.connect(self.filter_subwindow_para)


    def create_action(self):
        '''create actions for menu bar'''

        # actions for File menu bar
        #
        self.create_subject = QAction('Create a subject', self,
                                statusTip='Create a subject',
                                triggered=self.create_subject)
        # triggered=self.create_ptc


        # delete data and clear the workshop
        self.clear_workshop = QAction('Clear the workshop', self,
                                 statusTip='Clear the workshop',
                                 triggered=self.clear_all)
        self.clear_all = QAction('Clear all', self,
                                 statusTip='Clear all workshops',
                                 triggered=self.clear_all)


        # exit
        self.exit_action = QAction('Exit', self,
                                   shortcut=QKeySequence.Close,
                                   statusTip='Exit the Software',
                                   triggered=self.close)


        # actions for Help menu bar
        #
        #  website
        self.website_action = QAction('sEEGPA website', self,
                               triggered=self.show_website)
        self.licence_action = QAction('Licence', self,
                                      triggered=self.show_licence)
        self.email_action = QAction('E-mail us', self,
                                    triggered=self.send_email)


    def create_stack(self):

        self.ptc_stack = QStackedWidget()
        self.ptc_stack.setProperty('name', 'ptc')
        self.ptc_stack.addWidget(self.empty_label)


    def create_button(self):
        '''create buttons'''
        # buttons for func
        self.re_ref_button = QPushButton(self)
        self.re_ref_button.setText('Re-reference')
        self.re_ref_button.setToolTip('Re-reference sEEG data')
        self.re_ref_button.setProperty('name', 'func')
        self.re_ref_button.setEnabled(False)
        self.re_ref_button.setFixedSize(135, 38)
        self.re_ref_button.clicked.connect(self.re_ref)

        self.resample_button = QPushButton(self)
        self.resample_button.setText('Resample')
        self.resample_button.setToolTip('Resample the sEEG data')
        self.resample_button.setProperty('name', 'func')
        self.resample_button.setEnabled(False)
        self.resample_button.setFixedSize(130, 38)
        self.resample_button.clicked.connect(self.execute_resample_data)

        self.filter_button = QPushButton(self)
        self.filter_button.setText('Filter')
        self.filter_button.setToolTip('Basic iir filter')
        self.filter_button.setProperty('name', 'func')
        self.filter_button.setEnabled(False)
        self.filter_button.setFixedSize(130, 38)
        self.filter_button.clicked.connect(self.filter_data_iir)

        self.time_button = QPushButton(self)
        self.time_button.setText('Time')
        self.time_button.setToolTip('Select time range')
        self.time_button.setProperty('name', 'func')
        self.time_button.setEnabled(False)
        self.time_button.setFixedSize(130, 38)
        self.time_button.clicked.connect(self.select_time)

        self.chan_button = QPushButton(self)
        self.chan_button.setText('Channel')
        self.chan_button.setToolTip('Select the channels')
        self.chan_button.setProperty('name', 'func')
        self.chan_button.setEnabled(False)
        self.chan_button.setFixedSize(130, 38)
        self.chan_button.clicked.connect(self.select_chan)

        self.plot_button = QPushButton(self)
        self.plot_button.setText('Plot')
        self.plot_button.setToolTip('Plot raw data')
        self.plot_button.setProperty('name', 'func')
        self.plot_button.setEnabled(False)
        self.plot_button.setFixedSize(130, 38)
        self.plot_button.clicked.connect(self.plot_raw_data)

        self.event_button = QPushButton(self)
        self.event_button.setText('Event')
        self.event_button.setToolTip('Select the events')
        self.event_button.setProperty('name', 'func')
        self.event_button.setEnabled(False)
        self.event_button.setFixedSize(130, 38)
        self.event_button.clicked.connect(self.select_event)

        self.save_button = QPushButton(self)
        self.save_button.setText('Save')
        self.save_button.setToolTip('Save raw data in .fif format')
        self.save_button.setProperty('name', 'func')
        self.save_button.setEnabled(False)
        self.save_button.setFixedSize(130, 38)
        self.save_button.clicked.connect(self.save_fif)


    def create_progress_bar(self):
        '''create progress for needs'''

        pass


    def create_combo_box(self):

        self.ptc_cb = QComboBox()
        self.ptc_cb.activated.connect(self.change_ptc)
        self.ptc_cb.setProperty('name', 'ptc')
        self.ptc_cb.setFixedHeight(35)


    def create_label(self):
        '''reate labels'''
        # labels for main window
        #
        # empty label
        self.empty_label = QLabel('', self)
        self.empty_label.setProperty('name', 'empty')

        # sEEG Data Information title
        self.data_info_label = QLabel('sEEG Data Information', self)
        self.data_info_label.setProperty('name', 'title')
        self.data_info_label.setAlignment(Qt.AlignHCenter)
        self.data_info_label.setFixedHeight(38)

        # basic info of the subject
        self.file_name_label = QLabel(' Filename', self)
        self.file_name_label.setAlignment(Qt.AlignLeft)
        self.file_name_label.setFixedSize(180, 38)

        self.file_name_cont_label = QLabel('', self)
        self.file_name_cont_label.setAlignment(Qt.AlignLeft)
        self.file_name_cont_label.setFixedHeight(38)

        self.epoch_num_label = QLabel('Epochs', self)
        self.epoch_num_label.setProperty('name', 'group0')
        self.epoch_num_label.setAlignment(Qt.AlignCenter)
        self.epoch_num_label.setFixedSize(105, 38)
        # self.epoch_num_label.setFixedSize(90, 38)

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
        self.electro_title_label = QLabel('sEEG Electrodes Location and Activation', self)
        self.electro_title_label.setProperty('name', 'title')
        self.electro_title_label.setAlignment(Qt.AlignCenter)
        self.electro_title_label.setFixedHeight(38)

        self.electro_loac_label = QLabel('Electrodes Location')
        self.electro_loac_label.setProperty('name', 'electro')
        self.electro_loac_label.setAlignment(Qt.AlignCenter)
        self.electro_loac_label.setFixedHeight(38)

        self.activate_label = QLabel('Activation')
        self.activate_label.setProperty('name', 'electro')
        self.activate_label.setAlignment(Qt.AlignCenter)
        self.activate_label.setFixedHeight(38)


        self.electro_loac_pic_label = QLabel('')
        self.electro_loac_pic_label.setProperty('name', 'electro_pic')
        self.electro_loac_pic_label.setAlignment(Qt.AlignCenter)

        self.activate_pic_label = QLabel('')
        self.activate_pic_label.setProperty('name', 'electro_pic')
        self.activate_pic_label.setAlignment(Qt.AlignCenter)

        # Protocol
        self.protocol_label = QLabel('Protocol', self)
        self.protocol_label.setProperty('name', 'title')
        self.protocol_label.setAlignment(Qt.AlignHCenter)


    def create_group_box(self):
        '''create group boxes for main window'''
        # subject seeg data infomation
        self.seeg_info_box = QGroupBox()
        self.seeg_info_box.setProperty('name', 'sub')
        self.button_func_box = QGroupBox()
        self.button_func_box.setProperty('name', 'sub')
        self.button_func_box.setContentsMargins(0,0,0,0)
        # sEEG electrodes Visualization and Activation
        self.brain_electrodes_box = QGroupBox()
        self.brain_electrodes_box.setProperty('name', 'sub')
        # right group box
        self.right_box = QGroupBox()
        self.right_box.setProperty('name', 'sub')
        # protocol
        self.protocol_box = QGroupBox('')
        self.protocol_box.setProperty('name', 'sub')
        self.protocol_box.setFixedWidth(350)


    def create_menubar(self):
        '''create menu bars'''

        # file menu bar
        self.file_menu = self.menuBar().addMenu('File')
        self.file_menu.addAction(self.create_subject)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.clear_all)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        # Help menu bar
        self.help_menu = self.menuBar().addMenu('Help')
        self.help_menu.addAction(self.website_action)
        self.help_menu.addAction(self.licence_action)
        self.help_menu.addAction(self.email_action)


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

        data_button_layout = QHBoxLayout()
        data_button_layout.setContentsMargins(0, 0, 0, 0)
        data_button_layout.addWidget(self.re_ref_button, stretch=0)
        data_button_layout.addWidget(self.resample_button, stretch=0)
        data_button_layout.addWidget(self.filter_button, stretch=0)
        data_button_layout.addWidget(self.time_button, stretch=0)
        data_button_layout.addWidget(self.chan_button, stretch=0)
        data_button_layout.addWidget(self.event_button, stretch=0)
        data_button_layout.addWidget(self.plot_button, stretch=0)
        data_button_layout.addWidget(self.save_button, stretch=0)

        data_info_layout = QVBoxLayout()
        data_info_layout.setSpacing(4)
        data_info_layout.setContentsMargins(0, 0, 0, 4)
        data_info_layout.addWidget(self.data_info_label)
        data_info_layout.addLayout(file_name_layout)
        data_info_layout.addLayout(info_layout)
        data_info_layout.addLayout(data_button_layout)

        self.seeg_info_box.setLayout(data_info_layout)

        # layout for electrodes locations and activation in the fsaverage brain
        pic_layout_0 = QVBoxLayout()
        pic_layout_0.setSpacing(1)
        pic_layout_0.setContentsMargins(0, 0, 0, 0)
        pic_layout_0.addWidget(self.electro_loac_label)
        pic_layout_0.addWidget(self.electro_loac_pic_label)

        pic_layout_1 = QVBoxLayout()
        pic_layout_1.setSpacing(1)
        pic_layout_1.setContentsMargins(0, 0, 0, 0)
        pic_layout_1.addWidget(self.activate_label)
        pic_layout_1.addWidget(self.activate_pic_label)

        pic_layout_2 = QHBoxLayout()
        pic_layout_2.setSpacing(2)
        pic_layout_2.setContentsMargins(0, 0, 0, 0)
        pic_layout_2.addLayout(pic_layout_0)
        pic_layout_2.addLayout(pic_layout_1)

        electro_layout = QVBoxLayout(self)
        electro_layout.setSpacing(0)
        electro_layout.setContentsMargins(0, 0, 0, 0)
        electro_layout.addWidget(self.electro_title_label)
        electro_layout.addLayout(pic_layout_2)

        self.brain_electrodes_box.setLayout(electro_layout)

        # layout for protocol
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(self.protocol_label, stretch=1)
        left_layout.addWidget(self.ptc_cb, stretch=1)
        left_layout.addWidget(self.ptc_stack, stretch=100)
        self.protocol_box.setLayout(left_layout)

        # layout for main window
        right_layout = QVBoxLayout()
        right_layout.setSpacing(6)
        self.seeg_info_box.setAlignment(Qt.AlignTop)
        right_layout.addWidget(self.seeg_info_box, stretch=5)
        right_layout.addWidget(self.brain_electrodes_box, stretch=25)

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
                QLabel[name='title']{font: bold 17pt Times New Roman; 
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
    # File menu function
    #
    # create qtreeview
    def create_subject(self):

        self.ptc_name, _ = QInputDialog.getText(self, 'Protocol name', 'Please Name this protocol',
                                           QLineEdit.Normal)

        if self.ptc_name:
            try:
                self.ptc_stack.removeWidget(self.empty_label)
            except:
                pass
            try:
                self.ptc_stack.removeWidget(self.tree)
            except:
                pass
            self.subject_data[self.ptc_name] = dict()
            self.subject_data[self.ptc_name]['sEEG'] = dict()
            self.ptc_cb.addItem(self.ptc_name)
            self.ptc_cb.setCurrentText(self.ptc_name)
            self.tree = QTreeWidget()
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.right_menu)
            self.tree.setProperty('name', 'ptc')
            self.root = self.tree.invisibleRootItem()
            self.tree.setHeaderHidden(True)  # 隐藏列标题栏
            self.node_00 = QTreeWidgetItem(self.tree)
            self.node_00.setText(0, self.ptc_name)
            self.node_00.setIcon(0, QIcon('image/subject.ico'))
            self.tree.expandAll()
            self.tree.clicked.connect(self.change_current_data)
            self.tree_dict[self.ptc_name] = self.tree
            self.ptc_stack.addWidget(self.tree)
            self.tree_item[self.ptc_name] = dict()
            self.tree_item[self.ptc_name]['root'] = self.node_00
        else:
            pass


    def change_ptc(self, index):

        key = self.ptc_cb.currentText()
        try:
            self.ptc_stack.removeWidget(self.tree)
        except:
            pass
        self.tree = self.tree_dict[key]
        self.ptc_stack.addWidget(self.tree)


    # right click menu
    def subject_rmenu(self):

        self.rename_action = QAction('Rename the subject', self,
                                     statusTip='Rename the subject')
        self.import_action = QAction('Import raw sEEG data', self,
                                     statusTip='Import raw sEEG data',
                                     triggered=self.execute_import_data)
        self.import_epoch_action = QAction('Import Epoch data', self,
                                           statusTip='Import Epoch data',
                                           triggered=self.execute_load_epoched_data)
        self.import_mni_action = QAction("Load electrodes' MNI coonidates", self,
                                         statusTip='Load MNI coornidates',
                                         triggered=self.load_mni)
        self.import_mri_action = QAction("Import MRI / CT", self,
                                         statusTip="Import subject's pre-surhery MRI/post-surery CT",
                                         triggered=self.import_mri_ct)


    def raw_data_rmenu(self):

        self.rename_chan_action = QAction('Rename channels', self,
                                          statusTip='Rename channels',
                                          triggered=self.rename_chan)
        self.cal_marker_action = QAction('Calculate markers and delete useless channels', self,
                                  statusTip='Calculate markers and delete useless channels',
                                  triggered=self.get_mark_del_chan)
        self.resample_action = QAction('Resample the sEEG data', self,
                                       statusTip='Resamle the sEEG data',
                                       triggered=self.execute_resample_data)
        self.re_ref_action = QAction('Re-reference the sEEG data', self,
                                     statusTip='Re-reference the sEEG data',
                                     triggered=self.re_ref)
        self.filter_sub_menu = QMenu('Filter', self)
        self.fir_action = QAction('Filter the sEEG data using fir', self,
                                     statusTip='Filter the sEEG data using fir',
                                     triggered=self.filter_data_fir)
        self.iir_action = QAction('Filter the sEEG data using iir', self,
                                     statusTip='Filter the sEEG data using iir',
                                     triggered=self.filter_data_iir)
        self.filter_sub_menu.addActions([self.fir_action, self.iir_action])
        self.select_data_menu = QMenu('Select sub sEEG data', self)
        self.select_time_action = QAction('Select sEEG data by time range', self,
                                     statusTip='Select sEEG data with time range',
                                     triggered=self.select_time)
        self.select_chan_action = QAction('Select sEEG data by channels', self,
                                     statusTip='Select sEEG data with time range',
                                     triggered=self.select_chan)
        self.select_data_menu.addActions([self.select_time_action,
                                          self.select_chan_action])
        self.plot_menu = QMenu('Plot', self)
        self.plot_raw_action = QAction('Plot time-frequency', self,
                                       statusTip='Plot time-frequency',
                                       triggered=self.plot_raw_data)
        self.plot_psd_action = QAction('Plot psd across channels', self,
                                       statusTip='Plot psd across channels',
                                       triggered=self.plot_psd)
        self.plot_psd_topo_action = QAction('Plot topo psd', self,
                                       statusTip='Plot topo psd',
                                       triggered=self.plot_topo_psd)
        self.plot_menu.addActions([self.plot_raw_action,
                                   self.plot_psd_action,
                                   self.plot_psd_topo_action])
        self.get_epoch_action = QAction('Get epoch', self,
                                        statusTip='Get epoch',
                                        triggered=self.get_epoch_data)
        self.save_menu = QMenu('Export data', self)
        self.save_fif_action = QAction('Save sEEG data as .fif data', self,
                                       statusTip='Save sEEG data in .fif format')
        self.save_edf_action = QAction('Save sEEG data as .edf data', self,
                                       statusTip='Save sEEG data in .edf format',
                                       triggered=self.save_edf)
        self.save_set_action = QAction('Save sEEG data as .set data', self,
                                       statusTip='Save sEEG data in .set format',
                                       triggered=self.save_set)
        self.save_menu.addActions([self.save_fif_action,
                                   self.save_edf_action,
                                   self.save_set_action])
        self.analysis_menu = QMenu('Analysis', self)


    def epoch_rmenu(self):

        self.select_chan_action = QAction('Select sub channels', self,
                                          statusTip='Select sub channels',
                                          triggered=self.select_chan)
        self.select_event_action = QAction('Select specific events', self,
                                           statusTip='Select sub events',
                                           triggered=self.select_event)
        self.epoch_plot_menu = QMenu('Plot epoch', self)
        self.plot_epoch_action = QAction('Plot time-frequency', self,
                                         statusTip='Plot time-frequency',
                                         triggered=self.plot_raw_data)
        self.epoch_psd_action = QAction('Plot psd across channels', self,
                                        statusTip='Plot psd across channels',
                                        triggered=self.plot_psd)
        self.epoch_psd_topo_action = QAction('Plot topo psd', self,
                                             statusTip='Plot topo psd',
                                             triggered=self.plot_topo_psd)
        self.epoch_plot_menu.addActions([self.plot_epoch_action,
                                         self.epoch_psd_action,
                                         self.epoch_psd_action])
        self.epoch_analysis_menu = QMenu('Analysis', self)


    def mni_rmenu(self):

        self.display_electro_action = QAction('Display depth electrodes', self,
                                       statusTip='Display depth electrodes',
                                       triggered=self.load_mni)


    def right_menu(self, point):

        try:
            # index = self.tree.indexAt(point)
            item = self.tree.itemAt(point)
            self.name = item.text(0)
            print('node name: ', self.name)
            try:
                item_parent = item.parent().text(0)
                print('parent name:', item_parent)
            except AttributeError:
                item_parent = None
            self.tree_right_menu = QMenu(self)
            if not item_parent:
                self.subject_rmenu()
                self.tree_right_menu.addAction(self.rename_action)
                self.tree_right_menu.addSeparator()
                self.tree_right_menu.addActions([self.import_action,
                                                 self.import_epoch_action,
                                                 self.import_mri_action,
                                                 self.import_mni_action])
            elif item_parent == 'raw sEEG data':
                self.raw_data_rmenu()
                self.tree_right_menu.addActions([self.rename_chan_action,
                                                 self.cal_marker_action,
                                                 self.rename_chan_action,
                                                 self.re_ref_action])
                self.tree_right_menu.addMenu(self.filter_sub_menu)
                self.tree_right_menu.addMenu(self.select_data_menu)
                self.tree_right_menu.addMenu(self.plot_menu)
                self.tree_right_menu.addActions([self.get_epoch_action])
                self.tree_right_menu.addMenu(self.save_menu)
                self.tree_right_menu.addMenu(self.analysis_menu)
            elif item_parent == 'Epoch sEEG data':
                self.epoch_rmenu()
                self.tree_right_menu.addActions([self.select_chan_action,
                                                 self.select_event_action])
                self.tree_right_menu.addMenu(self.epoch_plot_menu)
                self.tree_right_menu.addMenu(self.epoch_analysis_menu)
            elif self.name == 'MNI Coornidates':
                self.mni_rmenu()
                self.tree_right_menu.addActions([self.load_mni_action])
            elif item_parent == 'MRI or CT':
                pass
            self.tree_right_menu.exec_(QCursor.pos())
        except Exception as error:
            print('*********************************************************************')
            print('Error is: ')
            traceback.print_exc()
            print('*********************************************************************')


    def get_all_items(self):

        child = []
        key = self.ptc_cb.currentText()
        iterator = QTreeWidgetItemIterator(self.tree_dict[key], QTreeWidgetItemIterator.All)
        while iterator.value():
            name = iterator.value().text(0)
            print(name)
            child.append(name)
            iterator += 1
        print('all child name:', child)
        return child


    # import sEEG data
    def execute_import_data(self):
        '''execute import data worker'''
        self.data_path, _ = QFileDialog.getOpenFileName(self, 'Import data')
        if ('set' or 'edf' or 'fif') == self.data_path[-3:]:
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
        if ('set' or 'fif' or 'edf') == self.data_path[-3:]:
            self.load_epoched_data_worker.data_path = self.data_path
            self.load_epoched_data_worker.start()
            self.flag += 1
            self.data_mode = 'epoch'
        elif self.flag == 0 and self.data_path:
            self.seeg_data = dict()
            print('*********************************************************************')
            print('Error is: ')
            traceback.print_exc()
            print('*********************************************************************')
            QMessageBox.warning(self, 'Data Format Error',
                                'Please select the right file!')


    def get_seeg_data(self, seeg_data):
        '''get seeg data'''
        try:
            if seeg_data.ch_names:
                # seeg_data.set_channel_types({ch_name: 'seeg' for ch_name in seeg_data.ch_names})
                self.key, _ = QInputDialog.getText(self, 'Name this Data', 'Please Name the Data',
                                              QLineEdit.Normal)
                if self.key:
                    self.seeg[self.key] = dict()
                    self.seeg[self.key]['data'] =  seeg_data
                    self.seeg[self.key]['data_path'] = self.data_path
                    self.seeg[self.key]['data_mode'] = self.data_mode
                    subject_name = self.ptc_cb.currentText()
                    child = self.get_all_items()
                    if self.data_mode == 'raw':
                        self.seeg[self.key]['event'], _ = mne.events_from_annotations(seeg_data)
                        if 'raw sEEG data' in child:
                            name = self.ptc_cb.currentText()
                            self.node_20 = QTreeWidgetItem(self.tree_item[name]['raw'])
                            self.node_20.setText(0, self.key)
                            self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                            self.tree.expandAll()
                        else:
                            name = self.ptc_cb.currentText()
                            self.node_10 = QTreeWidgetItem(self.tree_item[name]['root'])
                            self.node_10.setText(0, 'raw sEEG data')
                            self.node_10.setIcon(0, QIcon('image/EEG.ico'))
                            self.node_20 = QTreeWidgetItem(self.node_10)
                            self.node_20.setText(0, self.key)
                            self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                            self.tree_item[name]['raw'] = self.node_10
                            self.tree.expandAll()
                    elif self.data_mode == 'epoch':
                        self.seeg[self.key]['event'], _ = seeg_data.events
                        if 'Epoch sEEG data' in child:
                            name = self.ptc_cb.currentText()
                            self.node_20 = QTreeWidgetItem(self.tree_item[name]['epoch'])
                            self.node_20.setText(0, self.key)
                            self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                            self.tree.expandAll()
                        else:
                            name = self.ptc_cb.currentText()
                            self.node_10 = QTreeWidgetItem(self.tree_item[name]['root'])
                            self.node_10.setText(0, 'Epoch sEEG data')
                            self.node_20 = QTreeWidgetItem(self.node_10)
                            self.node_20.setText(0, self.key)
                            self.node_20.setIcon(0, QIcon('image/sEEG.jpg'))
                            self.tree_item[name]['epoch'] = self.node_10
                            self.tree.expandAll()
                    self.event = self.seeg[self.key]['event']
                    self.subject_data[subject_name]['sEEG'][self.key] = self.seeg[self.key]
                    self.set_current_data(key=self.key)
                    del seeg_data
                    gc.collect()
                    print(self.key, type(self.key))
                else:
                    pass
        except Exception as error:
            print('*********************************************************************')
            print('Error is: ')
            traceback.print_exc()
            print('*********************************************************************')
            QMessageBox.warning(self, 'Format Error', error.args[0])


    def set_current_data(self, key):
        '''set the curent seeg data'''
        self.current_data = self.seeg[key]
        print('----------------------------')
        print("current data\'s key:", key)
        print('current data: ', self.current_data)
        print('----------------------------')
        if self.current_data['data_mode'] == 'raw':
            self.re_ref_button.setEnabled(True)
            self.resample_button.setEnabled(True)
            self.filter_button.setEnabled(True)
            self.time_button.setEnabled(True)
            self.chan_button.setEnabled(True)
            self.plot_button.setEnabled(True)
            self.event_button.setEnabled(False)
            self.save_button.setEnabled(True)
        else:
            self.re_ref_button.setEnabled(True)
            self.resample_button.setEnabled(True)
            self.filter_button.setEnabled(True)
            self.time_button.setEnabled(False)
            self.chan_button.setEnabled(True)
            self.plot_button.setEnabled(True)
            self.event_button.setEnabled(True)
            self.save_button.setEnabled(True)
        self.get_data_info()


    def change_current_data(self, index):

        try:
            parent = self.tree.currentItem().parent().text(0)
            if ('raw sEEG data' or 'Epoch sEEG data') == parent:
                subject_name = self.ptc_cb.currentText()
                self.current_sub = self.subject_data[subject_name]
                key = self.tree.currentItem().text(0)
                self.current_data = self.current_sub['sEEG'][key]
                print('----------------------------')
                print('change current data to ', key)
                print('----------------------------')
                print('current data : ', self.current_data)
                print('----------------------------')
                if self.current_data['data_mode'] == 'raw':
                    self.re_ref_button.setEnabled(True)
                    self.resample_button.setEnabled(True)
                    self.filter_button.setEnabled(True)
                    self.time_button.setEnabled(True)
                    self.chan_button.setEnabled(True)
                    self.plot_button.setEnabled(True)
                    self.event_button.setEnabled(False)
                    self.save_button.setEnabled(True)
                else:
                    self.re_ref_button.setEnabled(True)
                    self.resample_button.setEnabled(True)
                    self.filter_button.setEnabled(True)
                    self.time_button.setEnabled(False)
                    self.chan_button.setEnabled(True)
                    self.plot_button.setEnabled(True)
                    self.event_button.setEnabled(True)
                    self.save_button.setEnabled(True)
                self.get_data_info()
            if 'MRI or CT' == parent:
                pass
        except Exception as error:
            print('*********************************************************************')
            print('Error is: ')
            traceback.print_exc()
            print('*********************************************************************')


    def get_data_info(self):
        '''get seeg data information'''
        if self.current_data['data_mode']:
            if self.current_data['data_mode'] == 'raw':
                self.data_info['data_path'] = self.current_data['data_path']
                self.data_info['epoch_number'] = 1
                self.data_info['sampling_rate'] = self.current_data['data'].info['sfreq']
                self.data_info['chan_number'] = str(self.current_data['data'].info['nchan'])
                self.data_info['epoch_start'] = self.current_data['data']._first_time
                self.data_info['epoch_end'] = round(self.current_data['data']._last_time, 2)
                self.data_info['time_point'] = self.current_data['data'].n_times
                self.data_info['events'], _ = events_from_annotations(self.current_data['data'])
                self.data_info['event_class'] = len(set(self.data_info['events'][:,2]))
                self.data_info['event_number'] = len(self.data_info['events'])
                self.data_info['data_size'] = round(0.5 * (self.current_data['data']._size / ((2**10)**2)), 2)
            elif self.current_data['data_mode'] == 'epoch':
                self.data_info['data_path'] = self.current_data['data_path']
                self.data_info['epoch_number'] = self.current_data['data'].events.shape[0]
                self.data_info['sampling_rate'] = self.current_data['data'].info['sfreq']
                self.data_info['chan_number'] = self.current_data['data'].info['nchan']
                self.data_info['epoch_start'] = self.current_data['data'].tmin
                self.data_info['epoch_end'] = self.current_data['data'].tmax
                self.data_info['time_point'] = len(self.current_data['data']._raw_times)
                self.data_info['event_class'] = len(set(self.current_data['data'].events[:, 2]))
                self.data_info['event_number'] = len(self.current_data['data'].events)
                self.data_info['data_size'] = round(0.5 * (self.current_data['data']._size / ((2 ** 10) ** 2)), 2)
        self.data_info_signal.connect(self.update_func)
        self.data_info_signal.emit(self.data_info)
        self.create_sub_windows()


    def load_mni(self):

        pass


    def import_mri_ct(self):

        pass


    # save sEEG data
    def write_edf(self, fname, raw):
        """Export raw to EDF/BDF file (requires pyEDFlib)."""
        from pathlib import Path
        import pyedflib

        ext = "".join(Path(fname).suffixes)
        if ext == ".edf":
            filetype = pyedflib.FILETYPE_EDFPLUS
            dmin, dmax = -32768, 32767
        elif ext == ".bdf":
            filetype = pyedflib.FILETYPE_BDFPLUS
            dmin, dmax = -8388608, 8388607
        data = raw.get_data() * 1e6  # convert to microvolts
        fs = raw.info["sfreq"]
        nchan = raw.info["nchan"]
        ch_names = raw.info["ch_names"]
        if raw.info["meas_date"] is not None:
            meas_date = raw.info["meas_date"]
        else:
            meas_date = None
        prefilter = (f"{raw.info['highpass']}Hz - "
                     f"{raw.info['lowpass']}")
        pmin, pmax = data.min(axis=1), data.max(axis=1)
        f = pyedflib.EdfWriter(fname, nchan, filetype)
        channel_info = []
        data_list = []
        for i in range(nchan):
            channel_info.append(dict(label=ch_names[i],
                                     dimension="uV",
                                     sample_rate=fs,
                                     physical_min=pmin[i],
                                     physical_max=pmax[i],
                                     digital_min=dmin,
                                     digital_max=dmax,
                                     transducer="",
                                     prefilter=prefilter))
            data_list.append(data[i])
        f.setTechnician("Exported by MNELAB")
        f.setSignalHeaders(channel_info)
        if raw.info["meas_date"] is not None:
            f.setStartdatetime(meas_date)
        # note that currently, only blocks of whole seconds can be written
        f.writeSamples(data_list)
        for ann in raw.annotations:
            f.writeAnnotation(ann["onset"], ann["duration"], ann["description"])

    def save_edf(self):

        self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data to EDF')
        try:
            self.write_edf(self.save_path, self.current_data['data'])
        except Exception as error:
            print('Error is:', type(error), error.args[0])
            QMessageBox.warning(self, 'Data Save to EDF Error', error.args[0])

    def write_set(self, fname, raw):
        """Export raw to EEGLAB .set file."""
        from numpy.core.records import fromarrays
        data = raw.get_data() * 1e6  # convert to microvolts
        fs = raw.info["sfreq"]
        times = raw.times
        ch_names = raw.info["ch_names"]
        chanlocs = fromarrays([ch_names], names=["labels"])
        events = fromarrays([raw.annotations.description,
                             raw.annotations.onset * fs + 1,
                             raw.annotations.duration * fs],
                            names=["type", "latency", "duration"])
        sio.savemat(fname, dict(EEG=dict(data=data,
                                     setname=fname,
                                     nbchan=data.shape[0],
                                     pnts=data.shape[1],
                                     trials=1,
                                     srate=fs,
                                     xmin=times[0],
                                     xmax=times[-1],
                                     chanlocs=chanlocs,
                                     event=events,
                                     icawinv=[],
                                     icasphere=[],
                                     icaweights=[])),
                appendmat=False)

    def save_set(self):

        self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data to EDF')
        try:
            self.write_set(self.save_path + '.set', self.current_data['data'])
        except Exception as error:
            print('Error is:', type(error), error.args[0])
            QMessageBox.warning(self, 'Data Save to EDF Error', error.args[0])


    def save_fif(self):
        '''save as .fif data'''
        if self.current_data['data_mode']:
            self.save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            try:
                self.current_data['data'].save(self.save_path + '.fif')
            except Exception as error:
                print('Error is:', type(error), error.args[0])
                QMessageBox.warning(self, 'Data Save Error', error.args[0])


    def export_npy(self):

        if self.current_data['data_mode']:
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            try:
                np.save(save_path + '_data', self.current_data['data'])
                # try:
                np.save(save_path + '_label', self.current_data['event'])
                # except:
            except Exception as error:
                print('Error is:', type(error), error.args[0])
                QMessageBox.warning(self, 'Data Save Error', error.args[0])


    def export_mat(self):

        if self.current_data:
            save_path, _ = QFileDialog.getSaveFileName(self, 'Save data')
            print(save_path)
        if save_path:
            sio.savemat(self.save_path + '_data.mat', {'seeg_data':self.current_data})
            sio.savemat(self.save_path + '.label', {'label':'event'})
        else:
            QMessageBox.warning(self, 'Data Save Error', 'No data to be saved!')

    def clear_all(self):
        '''clear the whole workshop'''
        if self.current_data:
            self.flag = 0
            del self.current_data
            del self.data_info
            del self.seeg
            del self.event
            self.data_info = dict()
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
    # select sub-channel
    def select_chan(self):

        self.select_chan_win = Select_Chan(chan_name=self.current_data['data'].ch_names)
        self.select_chan_win.chan_signal.connect(self.get_del_chan)
        self.select_chan_win.show()


    def get_del_chan(self, chan):

        self.chan_del = chan
        print('chans to delete', self.chan_del)
        del_chan_data = self.current_data['data'].copy().drop_channels(self.chan_del)
        self.get_seeg_data(del_chan_data)


    # select sub-time
    def select_time(self):

        time_end = round(self.current_data['data']._last_time, 2)
        self.select_time_win = Select_Time(time_end)
        self.select_time_win.time_signal.connect(self.get_time)
        self.select_time_win.show()


    def get_time(self, time):

        self.time_new = time
        print('Time selected', self.time_new)
        crop_data = self.current_data['data'].copy().crop(self.time_new[0], self.time_new[1])
        self.get_seeg_data(crop_data)


    # select sub-event
    def select_event(self):

        pass


    # re-ref
    def re_ref(self):

        pass


    def rename_chan(self):
        '''delete the 'POL' in channels' name '''
        rename_chan_data = self.current_data['data'].copy().\
            rename_channels({chan: chan[4:] for chan in self.current_data['data'].ch_names
                             if 'POL' in chan})
        # print(rename_chan_data)
        self.get_seeg_data(rename_chan_data)


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
            print('*****************************')
            print('Error is:', type(error), error)
            print('*****************************')


    def del_ref_chan(self, data):
        '''delete reference channels'''
        try:
            ref_channel = [ref_chan for ref_chan in data.ch_names if ref_chan[-3:] == 'Ref']
            if ref_channel:
                del_ref_data = data.copy().drop_channels(ref_channel)
            return del_ref_data
        except Exception as error:
            print('*****************************')
            print('Error is:', type(error), error.args[0])
            print('*****************************')


    def calculate_marker(self):
        '''calculate the markers for sEEG from Shenzhen University General Hosptial'''
        marker_channel = ['POL DC09', 'POL DC10', 'POL DC11', 'POL DC12',
                           'POL DC13', 'POL DC14', 'POL DC15']
        try:
            mark_data = self.current_data['data'].copy().pick_channels(marker_channel)._data * 1e6
        except Exception as error:
            QMessageBox.warning(self, 'Marker Calculating Error', 'No channels match the selection')
            print('*****************************')
            print('Error is:', type(error), error.args[0])
            print('*****************************')
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
            return annot_data


    def get_mark_del_chan(self):

        self.annot_data = self.calculate_marker()
        del_ref_data = self.del_ref_chan(self.annot_data)
        self.del_useless_chan(del_ref_data)


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
            print('画图了')
            self.current_data['data'].plot(duration=5.0, n_channels=self.current_data['data'].info['nchan'], title='Raw sEEG data')
            # plt.show()
        elif self.current_data['data_mode'] == 'epoch':
            self.current_data['data'].plot(n_channels=self.current_data['data'].info['nchan'], title='Epoched sEEG data')
            # plt.show()


    # plot psd across channels
    def plot_psd(self):
        if self.current_data['data'].ch_names:
            self.current_data['data'].plot_psd()


    def plot_topo_psd(self):

        pass

    # Help menu function
    #
    # show website
    def show_website(self):

        QDesktopServices.openUrl(QUrl("http://www.baidu.com"))


    def show_licence(self):

        pass


    def send_email(self):

        pass



    def update_func(self, data_info):
        '''update label text'''
        try:
            if self.current_data['data'].ch_names:
                self.file_name_cont_label.setText(str(data_info['data_path']))
                self.epoch_num_cont_label.setText(str(data_info['epoch_number']))
                self.samp_rate_cont_label.setText(str(data_info['sampling_rate']))
                self.chan_cont_label.setText(str(data_info['chan_number']))
                self.start_cont_label.setText(str(data_info['epoch_start']))
                self.end_cont_label.setText(str(data_info['epoch_end']))
                self.event_class_cont_label.setText(str(data_info['event_class']))
                self.event_num_cont_label.setText(str(data_info['event_number']))
                self.time_point_cont_label.setText(str(data_info['time_point']))
                self.data_size_cont_label.setText(str(data_info['data_size']))
        except:
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