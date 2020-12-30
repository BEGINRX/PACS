"""
@File: sub_window.py
@Author: BarryLiu
@Time: 2020/9/21 22:58
@Desc: sub windows
"""
import numpy as np
import sys
import traceback
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QPushButton,\
    QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, \
    QInputDialog, QLineEdit, QApplication, QScrollArea, QWidget, \
    QMessageBox, QStyleFactory, QListWidget, QAbstractItemView, \
    QStackedWidget, QGroupBox, QComboBox, QCheckBox, QProgressBar
from PyQt5.QtCore import pyqtSignal, Qt, QBasicTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QRegExpValidator
from mne import BaseEpochs


def show_error(error):
    print('*********************************************************************')
    print('Error is: ')
    traceback.print_exc()
    print('*********************************************************************')



class Filter_Window(QMainWindow):

    iir_signal = pyqtSignal()
    freq_signal = pyqtSignal(object, object)

    def __init__(self, mode, mode_1):
        super(Filter_Window, self).__init__()

        self.filter_mode = mode   # fir or iir
        self.filter_mode_1 = mode_1
        self.low_freq = None
        self.high_freq = None

        self.init_ui()


    def init_ui(self):

        self.setFixedSize(400,150)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_box()
        self.create_button()
        self.fir_text()
        self.create_line_edit()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_box(self):
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)


    def fir_text(self):

        self.low_freq_label = QLabel(self)
        self.high_freq_label = QLabel(self)
        self.low_freq_label.setText('Lower pass-band edge(Hz)')
        self.high_freq_label.setText('Higher pass-band edge(Hz)')
        self.iir_signal.connect(self.iir_text)
        if self.filter_mode == 'iir':
            self.iir_signal.emit()


    def iir_text(self):

        self.low_freq_label.setText('Lower Cutoff Frequency')
        self.high_freq_label.setText('Upper Cutoff Frequency')


    def create_line_edit(self):

        self.low_freq_edit = QLineEdit(self)
        self.low_freq_edit.setAlignment(Qt.AlignCenter)

        self.high_freq_edit = QLineEdit(self)
        self.high_freq_edit.setAlignment(Qt.AlignCenter)

        if self.filter_mode_1 == 'low':
            self.low_freq_edit.setPlaceholderText('None')
            self.low_freq_edit.setReadOnly(True)
        elif self.filter_mode_1 == 'high':
            self.high_freq_edit.setPlaceholderText('None')
            self.high_freq_edit.setReadOnly(True)
        elif self.filter_mode_1 == 'band':
            pass
        self.set_freq()


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setAutoDefault(True)
        self.ok_button.clicked.connect(self.set_freq)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        freq_layout = QFormLayout()
        freq_layout.addRow(self.low_freq_label, self.low_freq_edit)
        freq_layout.addRow(self.high_freq_label, self.high_freq_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(freq_layout)
        main_layout.addLayout(button_layout)
        self.center_widget.setLayout(main_layout)
        self.center_widget.setFont(self.font)


    def set_freq(self):
        self.low_freq = self.low_freq_edit.text()
        self.high_freq = self.high_freq_edit.text()
        if (self.low_freq == ''): self.low_freq = 'None'
        if (self.high_freq == ''): self.high_freq = 'None'
        self.freq_signal.emit(self.low_freq, self.high_freq)
        self.low_freq_edit.setText(None)
        self.high_freq_edit.setText(None)


    def set_style(self):
        pass



class Choose_Window(QMainWindow):

    signal = pyqtSignal(object, object,object)
    notch_signal = pyqtSignal(object, object, object)

    def __init__(self, mode):

        super(Choose_Window, self).__init__()

        self.filter_mode = mode
        self.filter_mode_1 = None
        self.low_freq = None
        self.high_freq = None
        self.notch_freq = None
        self.init_ui()


    def init_ui(self):
        '''initlize the ui'''
        self.setFixedSize(400, 250)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)


    def create_button(self):
        '''create buttons'''
        self.low_pass_button = QPushButton(self)
        self.low_pass_button.setText('Low Pass Filter')
        self.low_pass_button.setFixedSize(180, 60)
        self.low_pass_button.clicked.connect(self.low_pass_window)
        self.high_pass_button = QPushButton(self)
        self.high_pass_button.setText('High Pass Filter')
        self.high_pass_button.setFixedSize(180, 60)
        self.high_pass_button.clicked.connect(self.high_pass_window)
        self.band_pass_button = QPushButton()
        self.band_pass_button.setText('Band Pass Filter')
        self.band_pass_button.setFixedSize(180, 60)
        self.band_pass_button.clicked.connect(self.band_pass_window)
        self.notch_button = QPushButton(self)
        self.notch_button.setText('Notch Filter')
        self.notch_button.setFixedSize(180, 60)
        self.notch_button.clicked.connect(self.notch_window)


    def create_layout(self):
        '''create the layout'''
        button_layout_0 = QHBoxLayout()
        button_layout_0.addWidget(self.low_pass_button)
        button_layout_0.addSpacing(1)
        button_layout_0.addWidget(self.high_pass_button)
        button_layout_0.addSpacing(1)


        button_layout_1 = QHBoxLayout()
        button_layout_1.addWidget(self.band_pass_button)
        button_layout_0.addSpacing(1)
        button_layout_1.addWidget(self.notch_button)
        button_layout_0.addSpacing(1)

        button_layout = QVBoxLayout()
        button_layout.addLayout(button_layout_0)
        button_layout.addLayout(button_layout_1)
        self.center_widget.setLayout(button_layout)
        self.center_widget.setFont(self.font)


    def low_pass_window(self):
        '''show the low pass window'''
        self.filter_mode_1 = 'low'
        self.filter_window = Filter_Window(self.filter_mode,
                                           self.filter_mode_1)
        self.filter_window.freq_signal.connect(self.update_freq)
        self.filter_window.show()


    def high_pass_window(self):
        '''show the high pass window'''
        self.filter_mode_1 = 'high'
        self.filter_window = Filter_Window(self.filter_mode,
                                           self.filter_mode_1)
        self.filter_window.freq_signal.connect(self.update_freq)
        self.filter_window.show()


    def band_pass_window(self):
        '''show the band pass window'''
        self.filter_mode_1 = 'band'
        self.filter_window = Filter_Window(self.filter_mode,
                                           self.filter_mode_1)
        self.filter_window.freq_signal.connect(self.update_freq)
        self.filter_window.show()



    def notch_window(self):
        '''get notch filter frequency'''
        self.filter_mode_1 = 'notch'
        self.notch_freq, _ = QInputDialog.getText(self, 'Notch Filter', 'Notch Frequency(Hz)',
                                                  QLineEdit.Normal, None)
        if self.notch_freq:
            self.notch_signal.emit(self.low_freq, self.high_freq, self.notch_freq)
        self.notch_freq = None


    def update_freq(self, low_freq, high_freq):
        self.low_freq = low_freq
        self.high_freq = high_freq
        self.signal.emit(self.low_freq, self.high_freq, self.notch_freq)
        self.low_freq = None
        self.high_freq = None


    def set_style(self):
        pass



class Event_Window(QMainWindow):
    
    line_edit_signal = pyqtSignal(list, list)

    def __init__(self, event_id):
        
        super(Event_Window, self).__init__()

        print(event_id)
        self.add_num = 0
        self.event_name = []
        self.event_id = event_id
        self.event_name_edit_group = []
        self.event_id_edit_group = []
        self.init_ui()


    def init_ui(self):

        self.setWindowTitle('Generate event dict')
        self.setFixedWidth(400)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.create_center_widget()
        self.set_font()
        self.create_labels()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)

        self.stack_wid = QStackedWidget()

        self.stack_widgets = QWidget()
        self.stack_wid.addWidget(self.stack_widgets)


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.get_info)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_labels(self):

        self.event_name_label = QLabel('Event Name', self)
        self.event_name_label.setAlignment(Qt.AlignCenter)
        self.event_id_label = QLabel('Event ID', self)
        self.event_id_label.setAlignment(Qt.AlignCenter)


    def create_line_edit(self):

        for i in range(len(self.event_id)):
            self.event_name_edit = QLineEdit()
            self.event_name_edit.setAlignment(Qt.AlignCenter)
            self.event_id_edit = QLineEdit()
            self.event_id_edit.setText(str(self.event_id[i]))
            self.event_id_edit.setReadOnly(True)
            self.event_id_edit.setAlignment(Qt.AlignCenter)
            self.event_name_edit_group.append(self.event_name_edit)
            self.event_id_edit_group.append(self.event_id_edit)


    def create_layout(self):



        self.label_layout = QHBoxLayout()
        self.label_layout.addWidget(self.event_name_label)
        self.label_layout.addWidget(self.event_id_label)

        self.line_edit_layout = QFormLayout(self)
        for i in range(len(self.event_name_edit_group)):
            self.line_edit_layout.addRow(self.event_id_edit_group[i],
                                         self.event_name_edit_group[i])
        self.stack_widgets.setLayout(self.line_edit_layout)

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.label_layout, stretch=1)
        self.main_layout.addWidget(self.stack_wid, stretch=100)
        self.main_layout.addLayout(self.button_layout,stretch=1)

        self.center_widget.setLayout(self.main_layout)
        self.center_widget.setFont(self.font)


    def get_info(self):

        event_id = []
        for i in range(len(self.event_name_edit_group)):
            self.event_name.append(self.event_name_edit_group[i].text())
            event_id.append(self.event_id_edit_group[i].text())
        print(event_id)
        print(self.event_name, self.event_id)
        self.line_edit_signal.emit(self.event_name, self.event_id)


    def set_style(self):

        pass



class Select_Time(QMainWindow):

    time_signal= pyqtSignal(list)

    def __init__(self, end_time=None):

        super(Select_Time, self).__init__()
        self.end_time = end_time
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(300, 120)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setFont(self.font)


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_label(self):

        self.start_time_label = QLabel('Start Time(s)', self)
        self.start_time_label.setAlignment(Qt.AlignCenter)
        self.end_time_label = QLabel('End Time(s)', self)
        self.end_time_label.setAlignment(Qt.AlignCenter)


    def create_line_edit(self):
        self.start_time_text = QLineEdit()
        self.start_time_text.setPlaceholderText('0')
        self.end_time_text = QLineEdit()
        self.end_time_text.setPlaceholderText(str(self.end_time))


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        label_layout = QHBoxLayout()
        label_layout.addWidget(self.start_time_label)
        label_layout.addWidget(self.end_time_label)

        line_edit_layout = QHBoxLayout()
        line_edit_layout.addWidget(self.start_time_text)
        line_edit_layout.addWidget(self.end_time_text)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(label_layout)
        main_layout.addLayout(line_edit_layout)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def ok_func(self):

        if not self.start_time_text.text() and self.end_time_text.text():
            self.start_time = 0.
            self.end_time = float(self.end_time_text.text())
        elif self.start_time_text.text() and not self.end_time_text.text():
            self.start_time = self.start_time_text.text()
            self.end_time = self.end_time
        elif not self.end_time_text.text() and not self.end_time_text.text():
            self.start_time = 0.
            self.end_time = self.end_time
        elif self.start_time_text.text() and self.end_time_text.text():
            self.start_time = float(self.start_time_text.text())
            self.end_time = float(self.end_time_text.text())
        if float(self.start_time) > float(self.end_time):
            QMessageBox.warning(self, 'Value Error', 'The Start Time Value is bigger than '
                                                      'The End Time Value')
        else:
            self.time_signal.emit([self.start_time, self.end_time])
            print('choose time window', [type(self.start_time), type(self.end_time)])


    def set_style(self):
        pass



class Select_Chan(QMainWindow):

    chan_signal = pyqtSignal(list)

    def __init__(self, chan_name=None):

        super(Select_Chan, self).__init__()
        self.chan_len = len(chan_name)
        self.chan_name = chan_name
        self.chan_sel = []
        self.setWindowTitle('Channel')
        # self.setWindowIcon()
        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(170)
        self.setMinimumHeight(950)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_list_widget()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setProperty('name', 'center')
        self.center_widget.setFont(self.font)


    def create_list_widget(self):

        self.tip_label = QLabel('Please select the channels you want to use!', self)
        self.tip_label.setWordWrap(True)

        self.list_wid = QListWidget()
        self.list_wid.addItems(self.chan_name)
        self.list_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        chan_sel = self.list_wid.selectedItems()
        self.chan_sel.append([item.text() for item in list(chan_sel)])
        self.chan_sel = self.chan_sel[0]
        self.chan_signal.emit(self.chan_sel)


    def create_layout(self):

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.tip_label)
        v_layout.addWidget(self.list_wid)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.ok_button)
        h_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(v_layout)
        main_layout.addLayout(h_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet('''
                        QLabel{background-color:rgb(242,242,242) ;font:10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QWidget[name='center']{background-color:rgb(242,242,242)}
        ''')
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(Qt.WindowCloseButtonHint)



class Select_Event(QMainWindow):
    
    event_signal = pyqtSignal(list)

    def __init__(self, event=None):
        
        super(Select_Event, self).__init__()
        self.event = [str(element) for element in event]
        self.event_select = list()
        self.setWindowTitle('Event')

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(170)
        # self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_list_widget()
        self.create_button()
        self.create_layout()
        self.set_style()
        # QApplication.setStyle(QStyleFactory.create('Fusion'))



    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setProperty('name', 'center')
        self.center_widget.setFont(self.font)


    def create_list_widget(self):

        self.tip_label = QLabel('Please select the event(s)', self)
        self.tip_label.setWordWrap(True)

        self.list_wid = QListWidget()
        print(self.event)
        self.list_wid.addItems(self.event)
        self.list_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        event_select = self.list_wid.selectedItems()
        self.event_select.append([item.text() for item in list(event_select)])
        self.event_select = self.event_select[0]
        print(self.event_select)
        self.event_signal.emit(self.event_select)


    def create_layout(self):

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.tip_label)
        v_layout.addWidget(self.list_wid)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.ok_button)
        h_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(v_layout)
        main_layout.addLayout(h_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet('''
                        QLabel{background-color:rgb(242,242,242) ;font:10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QWidget[name='center']{background-color:rgb(242,242,242)}
        ''')
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowMaximizeButtonHint)
        self.setWindowFlags(Qt.WindowCloseButtonHint)



class Epoch_Time(QMainWindow):

    time_signal = pyqtSignal(float, float, float, float)

    def __init__(self):

        super(Epoch_Time, self).__init__()
        self.tmin = 0.
        self.tmax = 0.
        self.base_tmin = 0.
        self.base_tmax = 0.

        self.init_ui()


    def init_ui(self):
        # self.setFixedSize(250, 140)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_label()
        self.create_qedit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setFont(self.font)


    def create_label(self):

        self.time_range_label = QLabel('Time range')
        self.time_range_label.setProperty('group', 'title')
        self.time_range_label.setAlignment(Qt.AlignCenter)

        self.tmin_label = QLabel('tmin  (sec)')
        self.tmin_label.setProperty('group', 'time')
        self.tmax_label = QLabel('tmax (sec)')
        self.tmax_label.setProperty('group', 'time')

        self.base_label = QLabel('Baseline')
        self.base_label.setProperty('group', 'title')
        self.base_label.setAlignment(Qt.AlignCenter)

        self.base_tmin_label = QLabel('tmin  (sec)')
        self.base_tmin_label.setProperty('group', 'time')
        self.base_tmax_label = QLabel('tmax (sec)')
        self.base_tmax_label.setProperty('group', 'time')


    def create_qedit(self):

        self.tmin_qedit = QLineEdit()
        self.tmin_qedit.setAlignment(Qt.AlignCenter)
        self.tmin_qedit.setValidator(QDoubleValidator())

        self.tmax_qedit = QLineEdit()
        self.tmax_qedit.setAlignment(Qt.AlignCenter)
        self.tmax_qedit.setValidator(QDoubleValidator())

        self.base_tmin_qedit = QLineEdit()
        self.base_tmin_qedit.setAlignment(Qt.AlignCenter)
        self.base_tmin_qedit.setValidator(QDoubleValidator())

        self.base_tmax_qedit = QLineEdit()
        self.base_tmax_qedit.setAlignment(Qt.AlignCenter)
        self.base_tmax_qedit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        if not (self.tmin_qedit.text() and self.tmax_qedit.text()):
            self.tmin = 0.
            self.tmax = 0.
        else:
            self.tmin = float(self.tmin_qedit.text())
            self.tmax = float(self.tmax_qedit.text())
        if not (self.base_tmax_qedit.text() and self.base_tmax_qedit.text()):
            self.base_tmin = 0.
            self.base_tmax = 0.
        else:
            self.base_tmin = float(self.base_tmax_qedit.text())
            self.base_tmax = float(self.base_tmax_qedit.text())
        print(self.tmin, self.tmax)
        print(self.base_tmin, self.base_tmax)
        self.time_signal.emit(self.tmin, self.tmax, self.base_tmin, self.base_tmax)
        self.close()


    def create_layout(self):

        time_layout_0 = QFormLayout()
        time_layout_0.addRow(self.tmin_label, self.tmin_qedit)
        time_layout_0.addRow(self.tmax_label, self.tmax_qedit)

        time_layout_1  = QFormLayout()
        time_layout_1.addRow(self.base_tmin_label, self.base_tmin_qedit)
        time_layout_1.addRow(self.base_tmax_label, self.base_tmax_qedit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.time_range_label)
        main_layout.addLayout(time_layout_0)
        main_layout.addWidget(self.base_label)
        main_layout.addLayout(time_layout_1)
        main_layout.addLayout(button_layout)
        self.center_widget.setLayout(main_layout)


    def set_style(self):

        self.setStyleSheet('''QLabel{font: 20px Arial}
                              ''')



class Refer_Window(QMainWindow):

    ref_signal = pyqtSignal(str)

    def __init__(self, chan_name=None):
        super(Refer_Window, self).__init__()

        self.setWindowTitle('Re-reference')
        self.ref_method = ['Common Average', 'Gray-white Matter',
                           'Electrode Shaft', 'Bipolar', 'Monopolar', 'Laplacian']
        self.ref_sel = []
        # self.setWindowIcon()
        self.init_ui()


    def init_ui(self):
        self.setFixedWidth(200)
        # self.setMinimumHeight(950)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_list_widget()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setProperty('name', 'center')
        self.center_widget.setFont(self.font)


    def create_list_widget(self):

        self.list_wid = QListWidget()
        self.list_wid.addItems(self.ref_method)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.ok_button)
        h_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.list_wid)
        main_layout.addLayout(h_layout)

        self.center_widget.setLayout(main_layout)


    def ok_func(self):

        ref_sel = self.list_wid.selectedItems()[0]
        self.ref_sel = ref_sel.text()
        print(self.ref_sel)
        self.ref_signal.emit(self.ref_sel)



    def set_style(self):
        self.setStyleSheet('''
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QWidget[name='center']{background-color:rgb(242,242,242)}
        ''')



class Baseline_Time(QMainWindow):

    time_signal = pyqtSignal(float, float)

    def __init__(self):

        super(Baseline_Time, self).__init__()
        self.tmin = 0.
        self.tmax = 0.

        self.init_ui()


    def init_ui(self):
        self.setFixedSize(250, 140)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_label()
        self.create_qedit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setFont(self.font)


    def create_label(self):

        self.tmin_label = QLabel('tmin  (sec)')
        self.tmax_label = QLabel('tmax (sec)')


    def create_qedit(self):

        self.tmin_qedit = QLineEdit()
        self.tmin_qedit.setAlignment(Qt.AlignCenter)
        self.tmin_qedit.setValidator(QDoubleValidator())

        self.tmax_qedit = QLineEdit()
        self.tmax_qedit.setAlignment(Qt.AlignCenter)
        self.tmax_qedit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        if not (self.tmin_qedit.text() and self.tmax_qedit.text()):
            self.tmin = 0.
            self.tmax = 0.
        else:
            self.tmin = float(self.tmin_qedit.text())
            self.tmax = float(self.tmax_qedit.text())
        print(self.tmin, self.tmax)
        self.time_signal.emit(self.tmin, self.tmax)
        self.close()


    def create_layout(self):

        time_layout = QFormLayout()
        time_layout.addRow(self.tmin_label, self.tmin_qedit)
        time_layout.addRow(self.tmax_label, self.tmax_qedit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)
        self.center_widget.setLayout(main_layout)


    def set_style(self):

        self.setStyleSheet('''QLabel{font: 20px Arial}
                              ''')



class ERP_WIN(QMainWindow):

    erp_signal = pyqtSignal(list, str)

    def __init__(self, event):
        super(ERP_WIN, self).__init__()

        self.event = event
        self.event_sel = []
        self.mode = 'montage'

        self.init_ui()

    def init_ui(self):

        self.setFixedWidth(190)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_list_widget()
        self.create_check_box()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_list_widget(self):
        self.list_wid = QListWidget()
        self.list_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_wid.addItems(self.event)
        [self.list_wid.item(index).setTextAlignment(Qt.AlignCenter)
         for index in range(self.list_wid.count())]


    def create_check_box(self):
        self.standard_layout_button = QCheckBox('Standard layout')
        self.standard_layout_button.stateChanged.connect(self.choose_layout)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)


    def choose_layout(self):
        if self.standard_layout_button.isChecked():
            self.mode = 'standard'


    def ok_func(self):
        event_sel = self.list_wid.selectedItems()
        self.event_sel.append([item.text() for item in list(event_sel)])
        self.event_sel = self.event_sel[0]
        self.erp_signal.emit(self.event_sel, self.mode)
        self.close()


    def create_layout(self):

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.list_wid)
        main_layout.addWidget(self.standard_layout_button)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Power_Para_WIN(QMainWindow):

    freq_signal = pyqtSignal(float, float)

    def __init__(self):

        super(Power_Para_WIN, self).__init__()
        self.fmin = 0.
        self.fmax = 0.

        self.init_ui()


    def init_ui(self):
        self.setFixedSize(250, 140)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_label()
        self.create_qedit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.setCentralWidget(self.center_widget)
        self.center_widget.setFont(self.font)


    def create_label(self):

        self.fmin_label = QLabel('fmin Hz')
        self.fmax_label = QLabel('fmax Hz')


    def create_qedit(self):

        self.fmin_qedit = QLineEdit()
        self.fmin_qedit.setAlignment(Qt.AlignCenter)
        self.fmin_qedit.setValidator(QDoubleValidator())

        self.fmax_qedit = QLineEdit()
        self.fmax_qedit.setAlignment(Qt.AlignCenter)
        self.fmax_qedit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        if not (self.fmin_qedit.text() and self.fmax_qedit.text()):
            self.fmin = 0.
            self.fmax = 0.
        else:
            self.fmin = float(self.fmin_qedit.text())
            self.fmax = float(self.fmax_qedit.text())
        print(self.fmin, self.fmax)
        self.freq_signal.emit(self.fmin, self.fmax)
        self.close()


    def create_layout(self):

        time_layout = QFormLayout()
        time_layout.addRow(self.fmin_label, self.fmin_qedit)
        time_layout.addRow(self.fmax_label, self.fmax_qedit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_layout)
        main_layout.addLayout(button_layout)
        self.center_widget.setLayout(main_layout)


    def set_style(self):

        self.setStyleSheet('''QLabel{font: 20px Arial}
                              ''')



class PSD_Para_Win(QMainWindow):

    power_signal = pyqtSignal(str, object, int, list, tuple, str)

    def __init__(self, event):
        super(PSD_Para_Win, self).__init__()
        self.event = event
        self.method = None
        self.nfft = None
        self.average = None

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_combobox()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_combobox(self):

        self.method_combo = QComboBox(self)

        self.method_combo.addItems(['Welch',
                            'Multitaper'])
        self.method_combo.currentIndexChanged.connect(self.deactivate_fft)

        self.event_combo = QComboBox(self)
        if self.event is not None:
            self.event_combo.addItems(self.event)

        self.average_combo = QComboBox(self)
        self.average_combo.addItems(['mean',
                                     'median'])


    def create_label(self):

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.nfft_label = QLabel('nFFT', self)
        self.nfft_label.setFixedWidth(100)
        self.average_label = QLabel('Avergae', self)
        self.average_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.time_label = QLabel('Time', self)
        self.time_label.setFixedWidth(100)
        self.line_label_0 = QLabel(' - ', self)
        self.line_label_0.setFixedWidth(20)
        self.line_label_1 = QLabel(' - ', self)
        self.line_label_1.setFixedWidth(20)


    def create_line_edit(self):
        self.nfft_edit = QLineEdit('256')
        self.nfft_edit.setAlignment(Qt.AlignCenter)
        self.nfft_edit.setFixedWidth(93)
        self.nfft_edit.setValidator(QDoubleValidator())

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())

        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(93)
        self.tmin_edit.setValidator(QDoubleValidator())

        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(93)
        self.tmax_edit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.method_label)
        layout_0.addWidget(self.method_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.nfft_label)
        layout_2.addStretch(1)
        layout_2.addWidget(self.nfft_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.average_label)
        layout_3.addWidget(self.average_combo)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.fmin_edit)
        layout_4.addWidget(self.line_label_0)
        layout_4.addWidget(self.fmax_edit)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.freq_label)
        layout_5.addLayout(layout_4)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.tmin_edit)
        layout_6.addWidget(self.line_label_1)
        layout_6.addWidget(self.tmax_edit)

        layout_7 = QHBoxLayout()
        layout_7.addWidget(self.time_label)
        layout_7.addLayout(layout_6)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_2)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_7)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def deactivate_fft(self):
        if self.method_combo.currentText() == 'Multitaper':
            self.nfft_edit.setEnabled(False)
            self.average_combo.setEnabled(False)
        else:
            self.nfft_edit.setEnabled(True)
            self.average_combo.setEnabled(True)


    def ok_func(self):
        try:
            self.method = self.method_combo.currentText()
            self.event = self.event_combo.currentText()
            self.nfft = int(self.nfft_edit.text())
            self.average = self.average_combo.currentText()
            if self.fmin_edit.text() and self.fmax_edit.text() and \
               self.tmin_edit.text() and self.tmax_edit.text():
                self.fmin = float(self.fmin_edit.text())
                self.fmax = float(self.fmax_edit.text())
                self.tmin = float(self.tmin_edit.text())
                self.tmax = float(self.tmax_edit.text())
                # print(self.method, type(self.method))
                # print(self.event, type(self.event))
                # print([self.fmin, self.fmax], type(self.fmin))
                # print([self.tmin, self.tmax], type(self.tmin))
                # print(self.nfft, self.average)
                self.power_signal.emit(self.method, self.event, self.nfft,
                                   [self.fmin, self.fmax], (self.tmin, self.tmax), self.average)
            self.close()
        except Exception as error:
            show_error(error)


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class TFR_Win(QMainWindow):

    power_signal = pyqtSignal(str, str, int, list, tuple, bool, bool)

    def __init__(self, event):
        super(TFR_Win, self).__init__()
        self.event = event
        self.use_fft = True
        self.show_itc = False

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_combobox()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_combobox(self):

        self.method_combo = QComboBox(self)
        self.method_combo.addItems(['Multitaper transform',
                                    'Stockwell transform',
                                    'Morlet Wavelets'])
        self.method_combo.currentIndexChanged.connect(self.deactivate_fft)

        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)

        self.itc_check_box = QCheckBox('Show ITC', self)
        self.itc_check_box.stateChanged.connect(self.change_itc)

        self.fft_check_box = QCheckBox('Use FFT', self)
        self.fft_check_box.setChecked(True)
        self.fft_check_box.stateChanged.connect(self.change_fft)


    def create_label(self):

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.chan_label = QLabel('Channel', self)
        self.chan_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.baseline_label = QLabel('Baseline', self)
        self.baseline_label.setFixedWidth(100)
        self.line_label_0 = QLabel(' - ', self)
        self.line_label_0.setFixedWidth(20)
        self.line_label_1 = QLabel(' - ', self)
        self.line_label_1.setFixedWidth(20)


    def create_line_edit(self):
        self.chan_edit = QLineEdit('0')
        self.chan_edit.setAlignment(Qt.AlignCenter)
        self.chan_edit.setFixedWidth(93)
        # self.chan_edit.set
        self.chan_edit.setValidator(QDoubleValidator())

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())

        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(93)
        self.tmin_edit.setValidator(QDoubleValidator())

        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(93)
        self.tmax_edit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.method_label)
        layout_0.addWidget(self.method_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.fmin_edit)
        layout_2.addWidget(self.line_label_0)
        layout_2.addWidget(self.fmax_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.freq_label)
        layout_3.addLayout(layout_2)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.tmin_edit)
        layout_4.addWidget(self.line_label_1)
        layout_4.addWidget(self.tmax_edit)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.baseline_label)
        layout_5.addLayout(layout_4)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.chan_label)
        layout_6.addStretch(1)
        layout_6.addWidget(self.chan_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        check_layout = QHBoxLayout()
        check_layout.addWidget(self.fft_check_box)
        check_layout.addStretch(1)
        check_layout.addWidget(self.itc_check_box)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_6)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(check_layout)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def deactivate_fft(self):
        if self.method_combo.currentText() == 'Stockwell transform':
            self.fft_check_box.setEnabled(False)
        else:
            self.fft_check_box.setEnabled(True)


    def change_fft(self):
        if self.fft_check_box.isChecked():
            self.use_fft = True
        else:
            self.use_fft = False


    def change_itc(self):

        if self.itc_check_box.isChecked():
            self.show_itc = True
        else:
            self.show_itc = False


    def ok_func(self):
        self.method_chosen = self.method_combo.currentText()
        self.event_chosen = self.event_combo.currentText()
        self.chan_num = int(self.chan_edit.text())
        if self.fmin_edit.text() and self.fmax_edit.text() and \
           self.tmin_edit.text() and self.tmax_edit.text():
            self.fmin = float(self.fmin_edit.text())
            self.fmax = float(self.fmax_edit.text())
            self.tmin = float(self.tmin_edit.text())
            self.tmax = float(self.tmax_edit.text())
            # print(self.method_chosen, type(self.method_chosen))
            # print(self.event_chosen, type(self.event_chosen))
            # print([self.fmin, self.fmax], type(self.fmin))
            # print([self.tmin, self.tmax], type(self.tmin))
            # print(self.use_fft, self.show_itc)
            self.power_signal.emit(self.method_chosen, self.event_chosen, self.chan_num,
                               [self.fmin, self.fmax], (self.tmin, self.tmax), self.use_fft, self.show_itc)
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Topo_Power_Itc_Win(QMainWindow):

    power_signal = pyqtSignal(str, str, list, tuple, bool, bool)

    def __init__(self, event, ):
        super(Topo_Power_Itc_Win, self).__init__()
        self.event = event
        self.use_fft = True
        self.show_itc = False

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_combobox()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_combobox(self):

        self.method_combo = QComboBox(self)
        self.method_combo.addItems(['Multitaper transform',
                                    'Stockwell transform',
                                    'Morlet Wavelets'])
        self.method_combo.currentIndexChanged.connect(self.deactivate_fft)

        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)

        self.itc_check_box = QCheckBox('Show ITC', self)
        self.itc_check_box.stateChanged.connect(self.change_itc)

        self.fft_check_box = QCheckBox('Use FFT', self)
        self.fft_check_box.setChecked(True)
        self.fft_check_box.stateChanged.connect(self.change_fft)


    def create_label(self):

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.baseline_label = QLabel('Baseline', self)
        self.baseline_label.setFixedWidth(100)
        self.line_label_0 = QLabel(' - ', self)
        self.line_label_0.setFixedWidth(20)
        self.line_label_1 = QLabel(' - ', self)
        self.line_label_1.setFixedWidth(20)


    def create_line_edit(self):
        self.chan_edit = QLineEdit('0')
        self.chan_edit.setAlignment(Qt.AlignCenter)
        self.chan_edit.setFixedWidth(93)
        # self.chan_edit.set
        self.chan_edit.setValidator(QDoubleValidator())

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())

        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(93)
        self.tmin_edit.setValidator(QDoubleValidator())

        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(93)
        self.tmax_edit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.method_label)
        layout_0.addWidget(self.method_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.fmin_edit)
        layout_2.addWidget(self.line_label_0)
        layout_2.addWidget(self.fmax_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.freq_label)
        layout_3.addLayout(layout_2)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.tmin_edit)
        layout_4.addWidget(self.line_label_1)
        layout_4.addWidget(self.tmax_edit)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.baseline_label)
        layout_5.addLayout(layout_4)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.fft_check_box)
        layout_6.addStretch(1)
        layout_6.addWidget(self.itc_check_box)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_6)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def change_fft(self):
        if self.fft_check_box.isChecked():
            self.use_fft = True
        else:
            self.use_fft = False


    def change_itc(self):

        if self.itc_check_box.isChecked():
            self.show_itc = True
        else:
            self.show_itc = False


    def deactivate_fft(self):
        if self.method_combo.currentText() == 'Stockwell transform':
            self.fft_check_box.setEnabled(False)
        else:
            self.fft_check_box.setEnabled(True)


    def ok_func(self):
        self.method_chosen = self.method_combo.currentText()
        self.event_chosen = self.event_combo.currentText()
        if self.fmin_edit.text() and self.fmax_edit.text() and \
           self.tmin_edit.text() and self.tmax_edit.text():
            self.fmin = float(self.fmin_edit.text())
            self.fmax = float(self.fmax_edit.text())
            self.tmin = float(self.tmin_edit.text())
            self.tmax = float(self.tmax_edit.text())
        # print(self.method_chosen, type(self.method_chosen))
        # print(self.event_chosen, type(self.event_chosen))
        # print([self.fmin, self.fmax], type(self.fmin))
        # print([self.tmin, self.tmax], type(self.tmin))
        self.power_signal.emit(self.method_chosen, self.event_chosen, [self.fmin, self.fmax],
                               (self.tmin, self.tmax), self.use_fft, self.show_itc)
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class CSD_Win(QMainWindow):

    csd_signal = pyqtSignal(str, list, list, int, bool)

    def __init__(self, event):
        super(CSD_Win, self).__init__()
        self.event = event
        self.use_fft = True
        self.n_fft = 0

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_combobox()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_combobox(self):

        self.method_combo = QComboBox(self)
        self.method_combo.addItems(['Short-term Fourier',
                                    'Multitaper',
                                    'Morlet Wavelets'])
        self.method_combo.currentIndexChanged.connect(self.deactivate_fft)

        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)

        self.fft_check_box = QCheckBox('Use FFT', self)
        self.fft_check_box.setChecked(True)
        self.fft_check_box.stateChanged.connect(self.change_fft)
        self.fft_check_box.setEnabled(False)


    def create_label(self):

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.n_fft_label = QLabel('n_FFT', self)
        self.n_fft_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.line_label_0 = QLabel(' - ', self)
        self.line_label_0.setFixedWidth(20)
        self.line_label_1 = QLabel(' - ', self)
        self.line_label_1.setFixedWidth(20)


    def create_line_edit(self):
        self.n_fft_edit = QLineEdit('512')
        self.n_fft_edit.setAlignment(Qt.AlignCenter)
        self.n_fft_edit.setFixedWidth(93)
        self.n_fft_edit.setValidator(QDoubleValidator())

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.method_label)
        layout_0.addWidget(self.method_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.fmin_edit)
        layout_2.addWidget(self.line_label_0)
        layout_2.addWidget(self.fmax_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.freq_label)
        layout_3.addLayout(layout_2)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.n_fft_label)
        layout_4.addStretch(1)
        layout_4.addWidget(self.n_fft_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_4)
        main_layout.addWidget(self.fft_check_box)
        main_layout.addLayout(button_layout)


        self.center_widget.setLayout(main_layout)


    def deactivate_fft(self):
        if self.method_combo.currentText() == 'Short-term Fourier' or \
           self.method_combo.currentText() == 'Multitaper':
            self.fft_check_box.setEnabled(False)
            self.n_fft_edit.setEnabled(True)
        else:
            self.fft_check_box.setEnabled(True)
            self.n_fft_edit.setEnabled(False)


    def change_fft(self):
        if self.fft_check_box.isChecked():
            self.use_fft = True
        else:
            self.use_fft = False


    def ok_func(self):
        self.method_chosen = self.method_combo.currentText()
        self.event_chosen = self.event_combo.currentText()
        self.n_fft = int(self.n_fft_edit.text())
        if self.fmin_edit.text() and self.fmax_edit.text():
            self.fmin = float(self.fmin_edit.text())
            self.fmax = float(self.fmax_edit.text())
            # print(self.method_chosen, type(self.method_chosen))
            # print(self.event_chosen, type(self.event_chosen))
            # print([self.fmin, self.fmax], type(self.fmin))
            # print([self.tmin, self.tmax], type(self.tmin))
            # print(self.use_fft, self.show_itc)
            self.csd_signal.emit(self.method_chosen, [self.event_chosen],
                                   [self.fmin, self.fmax], self.n_fft, self.use_fft)
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Spectral_Connect_Win(QMainWindow):

    spectral_connect_signal = pyqtSignal(str, str, str, list)

    def __init__(self, event, method):
        super(Spectral_Connect_Win, self).__init__()
        self.event = event
        self.method = method
        self.mode = None

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_combobox()
        self.create_label()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_combobox(self):
        self.method_combo = QComboBox(self)
        self.method_combo.addItems(['Fourier',
                                    'Multitaper'])

        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)


    def create_label(self):
        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.line_label = QLabel(' - ', self)
        self.line_label.setFixedWidth(20)


    def create_line_edit(self):
        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.method_label)
        layout_0.addWidget(self.method_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.fmin_edit)
        layout_2.addWidget(self.line_label)
        layout_2.addWidget(self.fmax_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.freq_label)
        layout_3.addLayout(layout_2)


        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def ok_func(self):
        self.mode = self.method_combo.currentText()
        self.event_chosen = self.event_combo.currentText()
        if self.fmin_edit.text() and self.fmax_edit.text():
            self.fmin = float(self.fmin_edit.text())
            self.fmax = float(self.fmax_edit.text())
            # print(self.method_chosen, type(self.method_chosen))
            # print(self.event_chosen, type(self.event_chosen))
            # print([self.fmin, self.fmax], type(self.fmin))
            self.spectral_connect_signal.emit(self.method, self.mode, self.event_chosen,
                                 [self.fmin, self.fmax])
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')
        
        
        
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
                                               NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
class My_Figure(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super(My_Figure, self).__init__(self.fig)
        self.ax = self.fig.add_subplot(111)



class Morlet_Connectivity_Win(QMainWindow):
    
    def __init__(self, matrix, title, n_times):
        
        super(Morlet_Connectivity_Win, self).__init__()
        self.num = 0
        if isinstance(matrix, np.ndarray):
            self.matrix = matrix
        self.matrix_plot = self.matrix[:, :, self.num]
        # self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.title = title
        self.n_times = n_times
        self.init_ui()
    
    def init_ui(self):
        
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
        self.create_layout()
        self.set_style()
        
        
    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_widget(self):

        self.num_line_edit = QLineEdit()
        self.num_line_edit.setAlignment(Qt.AlignCenter)
        self.num_line_edit.setFixedWidth(120)
        self.num_line_edit.setValidator(QIntValidator())
        self.num_line_edit.setPlaceholderText(str(self.matrix.shape[2]))

        self.left_button = QPushButton(self)
        self.left_button.setText('Previous')
        self.left_button.setFixedWidth(100)
        self.left_button.clicked.connect(self.left_move)
        self.go_button = QPushButton(self)
        self.go_button.setText('Go')
        self.go_button.setFixedWidth(80)
        self.go_button.clicked.connect(self.go_move)
        self.right_button = QPushButton(self)
        self.right_button.setText('Next')
        self.right_button.setFixedWidth(100)
        self.right_button.clicked.connect(self.right_move)

        self.canvas = My_Figure()
        self.ax = self.canvas.ax
        image = self.ax.matshow(self.matrix_plot)
        self.canvas.fig.colorbar(image)
        self.ax.set_title(self.title + ' ' + '(' + str(self.n_times[self.num].astype(np.float16)) + ')')

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas_stack = QStackedWidget()
        self.canvas_stack.addWidget(self.canvas)
        self.toolbar_stack = QStackedWidget()
        self.toolbar_stack.addWidget(self.toolbar)
        self.toolbar_stack.setFixedHeight(38)


    def change_canvas(self, num):
        self.matrix_plot = self.matrix[:, :, num]
        # self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.canvas = My_Figure()
        self.ax = self.canvas.ax
        image = self.ax.matshow(self.matrix_plot)
        self.canvas.fig.colorbar(image)
        self.ax.set_title(self.title + ' ' + '(' + 'time:' + '' +str(self.n_times[num].astype(np.float16)) + 's' + ')')
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.canvas_stack.addWidget(self.canvas)
        self.toolbar_stack.addWidget(self.toolbar)



    def go_move(self):
        if self.num_line_edit.text() == '':
            self.num = self.matrix.shape[2] - 1
        else:
            self.num = int(self.num_line_edit.text())
        if self.num >= self.matrix.shape[2]:
            self.num = self.matrix.shape[2] - 1
        self.canvas_stack.removeWidget(self.canvas)
        self.toolbar_stack.removeWidget(self.toolbar)
        self.change_canvas(self.num)


    def left_move(self):

        if self.num == 0:
            pass
        else:
            self.canvas_stack.removeWidget(self.canvas)
            self.toolbar_stack.removeWidget(self.toolbar)
            self.num -= 1
            self.change_canvas(self.num)


    def right_move(self):
        self.canvas_stack.removeWidget(self.canvas)
        self.toolbar_stack.removeWidget(self.toolbar)
        if self.num == self.matrix.shape[2] - 1:
            self.num = 0
            self.change_canvas(self.num)
        else:
            self.num += 1
            self.change_canvas(self.num)


    def create_layout(self):
        layout_0 = QHBoxLayout()
        layout_0.addStretch(1000)
        layout_0.addWidget(self.left_button, stretch=1)
        layout_0.setSpacing(3)
        layout_0.addWidget(self.num_line_edit, stretch=3)
        layout_0.setSpacing(3)
        layout_0.addWidget(self.go_button, stretch=1)
        layout_0.setSpacing(3)
        layout_0.addWidget(self.right_button, stretch=1)
        layout_0.addStretch(1000)

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.toolbar_stack)
        layout_main.addWidget(self.canvas_stack)
        layout_main.addLayout(layout_0)

        self.center_widget.setLayout(layout_main)


    def keyPressEvent(self, event):
        print(str(event.key()))
        if event.key() == Qt.Key_Up:
            self.right_move()
        elif event.key() == Qt.Key_Down:
            self.left_move()
        elif event.key() == Qt.Key_Enter:
            print('here')
            self.go_move()


    def set_style(self):
        pass



class Connectivity_Win(QMainWindow):

    def __init(self, data, subject):
        if isinstance(data, BaseEpochs):
            self.data = data
        else:
            raise TypeError('This is not an epoch data')
        self.subject = subject

        self.init_ui()

    def init_ui(self):
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)



    def create_widget(self):

        self.time_box = QGroupBox('Data')
        self.connect_box = QGroupBox('Connectivity Measures')




class My_Progress(QMainWindow):

    def __init__(self):
        
        super(My_Progress, self).__init__()
        self.step = 0
        self.init_ui()


    def init_ui(self):

        self.setFixedHeight(50)
        self.setFixedWidth(500)
        self.setStyleSheet("background-color:gray")
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                            Qt.FramelessWindowHint)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
        self.create_layout()


    def center(self):
        '''set the app window to the center of the displayer of the computer'''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def set_font(self):
        '''set the font'''
        self.font = QFont()
        self.font.setFamily('Arial')
        self.font.setPointSize(12)


    def create_center_widget(self):
        '''create center widget'''
        self.center_widget = QWidget()
        self.center_widget.setFont(self.font)
        self.setCentralWidget(self.center_widget)


    def create_widget(self):

        self.pbar = QProgressBar()
        self.pbar.setValue(0)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)

        self.wait_label = QLabel('Running: ')

        self.timer = QBasicTimer()
        self.timer.start(100, self)


    def create_layout(self):

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.wait_label)
        layout_0.addWidget(self.pbar)

        self.center_widget.setLayout(layout_0)


    def timerEvent(self, event):

        self.pbar.setValue(self.step)
        if self.step >= 100:
            self.timer.stop()
            self.step = 0
            self.close()
        if self.step < 90:
            self.step += 1









if __name__ == "__main__":
    app = QApplication(sys.argv)
    chan = ['POL A5', 'POL A6', 'POL A7', 'POL A8', 'POL A9',
                    'POL A10', 'POL A13', 'POL A14', 'POL H1', 'POL H2', 'POL H3', 'POL H4', 'POL H5', 'POL H6']
    # GUI = Select_Chan(chan_name=chan)
    # GUI = Event_Window([1, 2, 3, 4, 5, 6])
    # GUI = Epoch_Time()
    # GUI = Select_Event(event=['1', '2'])
    # GUI = Refer_Window()
    # GUI = Spectral_Connect_Win(['blue', 'red'], 'pli')
    con = np.arange(12000).reshape((30, 40, 10))
    times = np.arange(10).reshape(10, 1)
    # import mne
    # from mne.connectivity import spectral_connectivity
    # import numpy as np
    # fpath = 'D:\SEEG_Cognition\data\color_epoch.fif'
    # epoch = mne.read_epochs(fpath, preload=True)
    # epoch = epoch['blue']
    # fmin, fmax = 3., 9.
    # freqs = np.arange(fmin, fmax, 2)
    # sfreq = epoch.info['sfreq']  # the sampling frequency
    # epoch.load_data()
    # con, freqs, times, n_epochs, n_tapers = spectral_connectivity(
    #     epoch, method='pli', mode='cwt_morlet', sfreq=sfreq,
    #     faverage=True, tmin=0., mt_adaptive=False, n_jobs=1, cwt_freqs=freqs, cwt_n_cycles=freqs / 2)
    # con = con[:, :, 0, :]
    # GUI = Morlet_Connectivity_Win(con, 'Phase Lag Index', times)
    GUI = My_Progress()
    GUI.show()
    app.exec_()





