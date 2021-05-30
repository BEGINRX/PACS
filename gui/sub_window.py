"""
@File: sub_window.py
@Author: BarryLiu
@Time: 2020/9/21 22:58
@Desc: sub windows
"""
import numpy as np
import sys
import traceback
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QPushButton,\
    QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, \
    QInputDialog, QLineEdit, QApplication, QScrollArea, QWidget, \
    QMessageBox, QStyleFactory, QListWidget, QAbstractItemView, \
    QStackedWidget, QGroupBox, QComboBox, QCheckBox, QProgressBar
from PyQt5.QtCore import pyqtSignal, Qt, QBasicTimer, QSize
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator, QPixmap
from mne import BaseEpochs
from mne.io import BaseRaw
import mne
try:
    from gui.re_ref import get_chan_group
    from gui.my_func import new_layout
    from gui.my_thread import Calculate_Power, Calculate_PSD, Cal_Spec_Con, Cal_Dir_Con
except:
    from re_ref import get_chan_group
    from my_func import new_layout
    from my_thread import Calculate_Power, Calculate_PSD, Cal_Spec_Con, Cal_Dir_Con

def show_error(error):
    print('*********************************************************************')
    print('Error is: ')
    traceback.print_exc()
    print('*********************************************************************')



class My_Progress(QMainWindow):

    def __init__(self, delay=0):

        super(My_Progress, self).__init__()
        self.step = 0
        self.delay = delay
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
            time.sleep(self.delay)



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

        self.event_name_label = QLabel('Marker', self)
        self.event_name_label.setAlignment(Qt.AlignCenter)
        self.event_id_label = QLabel('Event', self)
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

        self.line_edit_layout = QFormLayout()
        for i in range(len(self.event_name_edit_group)):
            self.line_edit_layout.addRow(self.event_name_edit_group[i],
                                         self.event_id_edit_group[i])
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

    def __init__(self, chan_name=None, multi=True):

        super(Select_Chan, self).__init__()
        self.chan_len = len(chan_name)
        self.chan_name = chan_name
        self.chan_sel = []
        self.setWindowTitle('Channel')
        self.multi = multi
        # self.setWindowIcon()
        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(170)
        self.setMinimumHeight(750)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
        self.create_layout()
        self.set_style()
        self.setWindowFlags(Qt.FramelessWindowHint)


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


    def create_widget(self):
        self.tip_label = QLabel('Please select the channels you want to use!', self)
        self.tip_label.setWordWrap(True)

        self.list_wid = QListWidget()
        self.list_wid.addItems(self.chan_name)
        if self.multi:
            self.list_wid.setSelectionMode(QAbstractItemView.ExtendedSelection)

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
        if len(self.event_select):
            self.event_signal.emit(self.event_select)
        else:
            self.close()


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



class Evoke_Chan_WiN(QMainWindow):

    erp_signal = pyqtSignal(str, object)

    def __init__(self, event, chan):
        super(Evoke_Chan_WiN, self).__init__()
        self.event = event
        self.chan = chan
        self.ch_name = None

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(200)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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


    def create_widget(self):
        self.event_label = QLabel('Event')
        self.event_label.setAlignment(Qt.AlignLeft)
        self.event_label.setFixedWidth(80)
        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)
        self.event_combo.setFixedWidth(90)

        self.chan_label = QLabel('Channel')
        self.chan_label.setAlignment(Qt.AlignLeft)
        self.chan_label.setFixedWidth(80)
        self.chan_btn = QPushButton(self)
        self.chan_btn.setText('···')
        self.chan_btn.setFixedWidth(90)
        self.chan_btn.clicked.connect(self.choose_chan)


        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)


    def choose_chan(self):
        self.chan_win = Select_Chan(self.chan)
        self.chan_win.chan_signal.connect(self.set_chan)
        self.chan_win.show()


    def set_chan(self, chan):
        self.ch_name = chan


    def ok_func(self):
        self.event_sel = self.event_combo.currentText()
        print(self.event_sel, self.ch_name)
        self.erp_signal.emit(self.event_sel, self.ch_name)
        self.close()


    def create_layout(self):

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.chan_label)
        layout_0.addWidget(self.chan_btn)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addWidget(self.event_combo)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_0)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
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


class ERP_Image_Topo(QMainWindow):

    erp_signal = pyqtSignal(str, list)

    def __init__(self, event):
        super(ERP_Image_Topo, self).__init__()
        self.event = event
        self.vmin = None
        self.vmax = None

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(380)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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



    def create_widget(self):
        self.event_label = QLabel('Event')
        self.event_label.setAlignment(Qt.AlignLeft)
        self.event_label.setFixedWidth(90)
        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)
        # self.event_combo.setFixedWidth(90)

        self.value_label = QLabel('Value(μV)', self)
        self.value_label.setFixedWidth(90)
        self.vmin_edit = QLineEdit()
        self.vmin_edit.setAlignment(Qt.AlignCenter)
        self.vmin_edit.setFixedWidth(115)
        self.vmin_edit.setValidator(QDoubleValidator())
        self.vmin_edit.setText('default')
        self.vmax_edit = QLineEdit()
        self.vmax_edit.setAlignment(Qt.AlignCenter)
        self.vmax_edit.setFixedWidth(115)
        self.vmax_edit.setValidator(QDoubleValidator())
        self.vmax_edit.setText('default')
        self.line_label = QLabel(' - ', self)
        self.line_label.setFixedWidth(20)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)

    def ok_func(self):
        self.event_sel = self.event_combo.currentText()
        if self.vmin_edit.text() == 'default' and self.vmax_edit.text() == 'default':
            self.vmin = None
            self.vmax = None
        else:
            self.vmin = float(self.vmin_edit.text())
            self.vmax = float(self.vmax_edit.text())
        print(self.event_sel, self.vmin, self.vmax)
        self.erp_signal.emit(self.event_sel, [self.vmin, self.vmax])
        self.close()


    def create_layout(self):

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)

        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.event_label)
        layout_0.addWidget(self.event_combo)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.vmin_edit)
        layout_1.addWidget(self.line_label)
        layout_1.addWidget(self.vmax_edit)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.value_label)
        layout_2.addLayout(layout_1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_2)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Change_Pic(QMainWindow):

    def __init__(self, matrix, title, n_times=None, diagonal=False):

        super(Change_Pic, self).__init__()
        self.num = 0
        self.diagonal = diagonal
        if isinstance(matrix, np.ndarray):
            self.matrix = matrix
        self.matrix_plot = self.matrix[self.num, :, :]
        if self.diagonal:
            self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.title = title
        if not n_times:
            self.n_times = np.arange(self.matrix_plot.shape[0])
        else:
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
        self.num_line_edit.setPlaceholderText(str(self.matrix.shape[0]))
        self.num_line_edit.returnPressed.connect(self.go_move)
        self.num_line_edit.clearFocus()

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
        self.image = self.ax.matshow(self.matrix_plot)
        self.canvas.fig.colorbar(self.image)
        self.canvas.mpl_connect('key_press_event', self.on_move)
        self.ax.set_title(self.title + ' ' + '(' + str(self.n_times[self.num].astype(np.float16)) + ')')
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas_stack = QStackedWidget()
        self.canvas_stack.addWidget(self.canvas)
        self.toolbar_stack = QStackedWidget()
        self.toolbar_stack.addWidget(self.toolbar)
        self.toolbar_stack.setFixedHeight(38)

    def change_canvas(self):
        self.matrix_plot = self.matrix[self.num, :, :]
        if self.diagonal:
            self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.image.set_data(self.matrix_plot)
        self.ax.set_title(self.title + ' ' + '(' + 'time:' + '' +
                          str(self.n_times[self.num].astype(np.float16)) + 's' + ')')
        self.canvas.draw_idle()
        self.num_line_edit.setText(str(self.num))

    def go_move(self):
        if self.num_line_edit.text() == '':
            self.num = self.matrix.shape[2] - 1
        else:
            self.num = int(self.num_line_edit.text())
        if self.num >= self.matrix.shape[2]:
            self.num = self.matrix.shape[2] - 1
            self.num_line_edit.setText(str(self.matrix.shape[0]))
        self.change_canvas()

    def on_move(self, event):
        print('activcate this')
        if event.key is 'down':
            if self.num == 0:
                self.num = 0
            else:
                self.num -= 1
        elif event.key is 'up':
            if self.num == self.matrix.shape[0] - 1:
                self.num = 0
            else:
                self.num += 1
        self.change_canvas()

    def left_move(self):

        if self.num == 0:
            pass
        else:
            self.num -= 1
        self.change_canvas()

    def right_move(self):
        if self.num == self.matrix.shape[0] - 1:
            self.num = 0
        else:
            self.num += 1
        self.change_canvas()

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
        pass
        '''
        if event.key() == Qt.Key_Up:
            self.right_move()
        elif event.key() == Qt.Key_Down:
            self.left_move()
        elif event.key() == Qt.Key_Enter:
            print('here')
            self.go_move()
        '''

    def set_style(self):
        pass



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



class CSD_Para_Win(QMainWindow):

    power_signal = pyqtSignal(str, object, int, list, tuple, str)

    def __init__(self, event):
        super(CSD_Para_Win, self).__init__()
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
        self.create_widget()
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


    def create_widget(self):
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

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.chan_label = QLabel('Channel', self)
        self.chan_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.value_label = QLabel('Value', self)
        self.value_label.setFixedWidth(100)
        self.baseline_label = QLabel('Baseline', self)
        self.baseline_label.setFixedWidth(100)
        self.line_label_0 = QLabel(' - ', self)
        self.line_label_0.setFixedWidth(20)
        self.line_label_1 = QLabel(' - ', self)
        self.line_label_1.setFixedWidth(20)
        self.line_label_2 = QLabel(' - ', self)
        self.line_label_2.setFixedWidth(20)

        self.chan_edit = QLineEdit('0')
        self.chan_edit.setAlignment(Qt.AlignCenter)
        self.chan_edit.setFixedWidth(93)
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



class Topo_TFR_Itc_Win(QMainWindow):

    power_signal = pyqtSignal(str, str, list, tuple, bool, bool)

    def __init__(self, event, ):
        super(Topo_TFR_Itc_Win, self).__init__()
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
        self.create_widget()
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


    def create_widget(self):
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
        else:
            self.fmin = None
            self.fmax = None
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



class Time_Freq_Win(QMainWindow):

    def __init__(self, data, subject):
        super(Time_Freq_Win, self).__init__()
        if isinstance(data, BaseEpochs):
            self.data = data
        else:
            raise TypeError('This is not an epoch data')
        if isinstance(subject, str):
            self.subject = subject
        else:
            print('subject name error')
        self.group = len(get_chan_group(self.data))
        self.init_ui()


    def init_ui(self):
        self.setFixedSize(650, 320)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
        self.create_layout()
        self.set_style()
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle('Time-Frequency Analysis')


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
        self.center_widget.setProperty('group', 'center')


    def create_widget(self):
        self.data_box = QGroupBox('Data Information')
        self.data_box.setProperty('group', 'box')
        self.name_label = QLabel(self.subject)
        self.name_label.setProperty('group', 'label_00')
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.name_label.setFixedWidth(600)
        self.sfreq_label = QLabel('Sampling Rate')
        self.sfreq_label.setProperty('group', 'label_0')
        self.sfreq_label.setAlignment(Qt.AlignLeft)
        self.sfreq_label.setFixedWidth(120)
        self.sfreq_con_label = QLabel(str(round(self.data.info['sfreq'])))
        self.sfreq_con_label.setProperty('group', 'label')
        self.sfreq_con_label.setAlignment(Qt.AlignHCenter)
        self.sfreq_con_label.setFixedWidth(60)
        self.group_label = QLabel('Group')
        self.group_label.setProperty('group', 'label_0')
        self.group_label.setAlignment(Qt.AlignLeft)
        self.group_label.setFixedWidth(60)
        self.group_con_label = QLabel(str(self.group))
        self.group_con_label.setProperty('group', 'label')
        self.group_con_label.setAlignment(Qt.AlignHCenter)
        self.group_con_label.setFixedWidth(60)
        self.chan_label = QLabel('Channel')
        self.chan_label.setProperty('group', 'label_0')
        self.chan_label.setAlignment(Qt.AlignLeft)
        self.chan_label.setFixedWidth(90)
        self.chan_len_label = QLabel(str(len(self.data.ch_names)))
        self.chan_len_label.setProperty('group', 'label')
        self.chan_len_label.setAlignment(Qt.AlignHCenter)
        self.chan_len_label.setFixedWidth(100)
        self.event_label = QLabel('Event')
        self.event_label.setProperty('group', 'label_0')
        self.event_label.setAlignment(Qt.AlignLeft)
        self.event_label.setFixedWidth(120)
        self.event_num_label = QLabel(str(len(self.data.event_id)))
        self.event_num_label.setProperty('group', 'label')
        self.event_num_label.setAlignment(Qt.AlignHCenter)
        self.event_num_label.setFixedWidth(60)
        self.epoch_label = QLabel('Epoch')
        self.epoch_label.setProperty('group', 'label_0')
        self.epoch_label.setAlignment(Qt.AlignLeft)
        self.epoch_label.setFixedWidth(60)
        self.epoch_num_label = QLabel(str(len(self.data)))
        self.epoch_num_label.setProperty('group', 'label')
        self.epoch_num_label.setAlignment(Qt.AlignHCenter)
        self.epoch_num_label.setFixedWidth(60)
        self.time_epoch_label = QLabel('Time epoch')
        self.time_epoch_label.setProperty('group', 'label_0')
        self.time_epoch_label.setAlignment(Qt.AlignLeft)
        self.time_epoch_label.setFixedWidth(90)
        self.time_range_label = QLabel(str(self.data.tmin) + ' - ' + str(self.data.tmax))
        self.time_range_label.setProperty('group', 'label')
        self.time_range_label.setAlignment(Qt.AlignHCenter)
        self.time_range_label.setFixedWidth(100)

        self.tf_label = QLabel('Time Frequency Analysis')
        self.tf_label.setProperty('group', 'label_2')

        self.image_plot_btn = QPushButton(self)
        self.image_plot_btn.setText('ERP Image')
        self.image_plot_btn.setFixedSize(180, 28)
        self.image_plot_btn.clicked.connect(self.image_map)
        self.erpim_topo_btn = QPushButton(self)
        self.erpim_topo_btn.setText('ERP Image topograph')
        self.erpim_topo_btn.setFixedSize(180, 28)
        self.erpim_topo_btn.clicked.connect(self.erpim_topo)

        self.erp_topo_btn = QPushButton(self)
        self.erp_topo_btn.setText('ERP topomap')
        self.erp_topo_btn.setFixedSize(180, 28)
        self.erp_topo_btn.clicked.connect(self.erp_topo)
        self.psd_btn = QPushButton(self)
        self.psd_btn.setText('Power Spectral Density')
        self.psd_btn.setFixedSize(180, 28)
        self.psd_btn.clicked.connect(self.psd)

        self.tfr_btn = QPushButton(self)
        self.tfr_btn.setText('Time-Frequency Response')
        self.tfr_btn.setFixedSize(180, 28)
        self.tfr_btn.clicked.connect(self.tfr)
        self.tfr_topo_btn = QPushButton(self)
        self.tfr_topo_btn.setText('TFR topomap')
        self.tfr_topo_btn.setFixedSize(180, 28)
        self.tfr_topo_btn.clicked.connect(self.tfr_topo)



    def create_layout(self):
        layout_1 = QHBoxLayout()
        layout_1.setContentsMargins(0, 0, 0, 0)
        layout_1.addWidget(self.sfreq_label)
        layout_1.addWidget(self.sfreq_con_label)
        layout_1.addWidget(self.group_label)
        layout_1.addWidget(self.group_con_label)
        layout_1.addWidget(self.chan_label)
        layout_1.addWidget(self.chan_len_label)
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.event_label)
        layout_2.addWidget(self.event_num_label)
        layout_2.addWidget(self.epoch_label)
        layout_2.addWidget(self.epoch_num_label)
        layout_2.addWidget(self.time_epoch_label)
        layout_2.addWidget(self.time_range_label)
        layout_3 = QVBoxLayout()
        layout_3.addWidget(self.name_label)
        layout_3.addLayout(layout_1)
        layout_3.addLayout(layout_2)
        self.data_box.setLayout(layout_3)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.tf_label)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.image_plot_btn)
        layout_5.addWidget(self.tfr_topo_btn)
        layout_5.addWidget(self.erp_topo_btn)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.tfr_btn)
        layout_6.addWidget(self.erpim_topo_btn)
        layout_6.addWidget(self.psd_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.data_box)
        main_layout.addLayout(layout_4)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_6)
        self.center_widget.setLayout(main_layout)


    def set_style(self):
        self.setStyleSheet(''' 
            QLabel[group='label_00']{font:10pt Consolas; background-color: rgb(207, 207, 207);
            color: black}
            QLabel[group='label_0']{font:10pt Consolas;
            color: black}
            QLabel[group='label']{font: bold 10pt Consolas;
            color: black}
            QGroupBox[group='box']{font: bold 13pt Consolas;
            color: black}
            QLabel[group='label_2']{font: bold 13pt Consolas;
            color: black}
            QPushButton{background-color: rgb(210, 210, 210); font: 10pt Consolas; color: black}
            QPushButton:hover{background-color:white}
            QPushButton:pressed{background-color:white;
                    padding=left:3px; padding-top:3px}
            QWidget[group='center']{background-color: white}
        ''')
        self.psd_btn.setStyleSheet("QPushButton{font-size: 8pt}")
        self.tfr_btn.setStyleSheet("QPushButton{font-size: 8pt}")
        self.erpim_topo_btn.setStyleSheet("QPushButton{font-size: 8pt}")


    def show_pbar(self):
        self.pbar = My_Progress()
        self.pbar.show()


    def image_map(self):
        self.event = self.data.event_id
        event = list(self.event.keys())
        self.event_win = Evoke_Chan_WiN(event=event, chan = self.data.ch_names)
        self.event_win.erp_signal.connect(self.plot_image_map)
        self.event_win.show()


    def plot_image_map(self, event, ch_name):
        if ch_name == None:
            pass
        else:
            for i in range(len(ch_name)):
                mne.viz.plot_epochs_image(self.data[event].pick_channels([ch_name[i]]),
                                          combine='mean', picks='seeg', title=ch_name[i])


    def erpim_topo(self):
        self.event = self.data.event_id
        event = list(self.event.keys())
        self.event_win = ERP_Image_Topo(event=event)
        self.event_win.erp_signal.connect(self.plot_erpim_topo)
        self.event_win.show()


    def plot_erpim_topo(self, event, value):
        try:
            if not value[0] and not value[1]:
                mne.viz.plot_topo_image_epochs(self.data[event])
            else:
                mne.viz.plot_topo_image_epochs(self.data[event],
                                               vmin=value[0], vmax=value[1])
        except Exception as error:
            if error.args[0] == "ValueError: Cannot determine location of MEG/EOG/ECG channels " \
                                "using digitization points.":
                QMessageBox.warning(self, 'No location','Please load MNI coordinates')



    def erp_topo(self):
        self.event = self.data.event_id
        self.erp_win = ERP_WIN(list(self.event.keys()))
        self.erp_win.erp_signal.connect(self.plot_erp_topo)
        self.erp_win.show()

    def plot_erp_topo(self, event, mode):
        try:
            if mode == 'standard':
                layout = new_layout(self.data.ch_names)
                if len(event) > 1:
                    evokeds = [self.data[name].average().pick_types(seeg=True) for name in event]
                    mne.viz.plot_evoked_topo(evokeds, background_color='w', layout=layout, layout_scale=1)
                elif len(event) == 1:
                    print('到这')
                    evokeds = self.data[event].average().pick_types(seeg=True, eeg=True)
                    mne.viz.plot_evoked_topo(evokeds, background_color='w', layout=layout, layout_scale=1)
            else:
                if len(event) > 1:
                    evokeds = [self.data[name].average().pick_types(seeg=True) for name in event]
                    mne.viz.plot_evoked_topo(evokeds, background_color='w')
                elif len(event) == 1:
                    print('到这')
                    evokeds = self.data[event].average().pick_types(seeg=True, eeg=True)
                    mne.viz.plot_evoked_topo(evokeds, background_color='w')
        except Exception as error:
            if error.args[0] == "Cannot determine location of MEG/EOG/ECG channels using digitization points.":
                QMessageBox.warning(self, 'Value Error', 'Please set montage first using MNI coornidates')


    def tfr(self):

        data = self.data
        event_id = data.event_id
        self.tfr_para_win = TFR_Win(list(event_id.keys()))
        self.tfr_para_win.power_signal.connect(self.cal_tfr)
        self.tfr_para_win.show()

    def cal_tfr(self, method, event, chan_num, freq, time, use_fft, show_itc):
        if None in freq:
            pass
        else:
            self.show_pbar()
            data = self.data[event]
            self.calcu_psd_thread = Calculate_Power(data=data, method=method, chan_num=chan_num, freq=freq, time=time,
                                                  use_fft=use_fft, show_itc=show_itc)
            self.calcu_psd_thread.power_signal.connect(self.plot_tfr)
            self.calcu_psd_thread.start()

    def plot_tfr(self, power, chan_num, time, itc):
        self.pbar.step = 100
        power.plot([chan_num], baseline=time, mode='mean', vmin=0.,
           title='Time-Frequency Response', cmap='bwr')
        if itc is not None:
            itc.plot([chan_num], title='Inter-Trial coherence', vmin=0., vmax=1., cmap='Reds')


    def tfr_topo(self):

        data = self.data
        event_id = data.event_id
        self.tfr_para_win = Topo_TFR_Itc_Win(list(event_id.keys()))
        self.tfr_para_win.power_signal.connect(self.cal_tfr_topo)
        self.tfr_para_win.show()

    def cal_tfr_topo(self, method, event, freq, time, use_fft, show_itc):
        self.show_pbar()
        data = self.data
        if None in freq:
            pass
        else:
            if isinstance(data, BaseEpochs):
                self.power_thread = Calculate_Power(data=data, method=method, chan_num=None, freq=freq,
                                                    time=time, use_fft=use_fft, show_itc=show_itc)
                self.power_thread.power_signal.connect(self.plot_tfr_topo)
                self.power_thread.start()

    def plot_tfr_topo(self, power, chan_num, baseline, itc):
        self.pbar.step = 100
        power.plot_topo(baseline=baseline,
                        mode='logratio', title='Average power')
        if itc is not None:
            itc.plot_topo(title='Inter-Trial coherence', vmin=0., vmax=1., cmap='Reds')


    def psd(self):
        self.psd_win = PSD_Para_Win(list(self.data.event_id.keys()))
        self.psd_win.power_signal.connect(self.cal_psd)
        self.psd_win.show()

    def cal_psd(self, method, event, nfft, freq, time, average):
        if None in freq:
            pass
        else:
            self.show_pbar()
            self.calcu_psd_thread = Calculate_PSD(self.data, method, freq, time, nfft, average)
            self.calcu_psd_thread.psd_signal.connect(self.plot_psd)
            self.calcu_psd_thread.start()

    def plot_psd(self, method, psds_mean, psds_std, freqs):
        self.pbar.step = 100
        try:
            from matplotlib import pyplot as plt
            f, ax = plt.subplots()
            ax.plot(freqs, psds_mean, color='k')
            ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
                            color='k', alpha=.5)
            if method == 'Multitaper':
                ax.set(title='Multitaper PSD', xlabel='Frequency (Hz)',
                       ylabel='Power Spectral Density (dB)')
            elif method == 'Welch':
                ax.set(title='Welch PSD', xlabel='Frequency (Hz)',
                       ylabel='Power Spectral Density (dB)')
            plt.show()
        except Exception as error:
            self.show_error(error)


    def csd(self):
        pass

    def cal_csd(self, freq):
        if None in freq:
            pass
        else:
            pass

    def plot_csd(self):
        pass



from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
        NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
class My_Figure(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super(My_Figure, self).__init__(self.fig)
        self.ax = self.fig.add_subplot(111)



class Pic_Change(QMainWindow):

    def __init__(self, matrix, title, n_times=None, diagonal=True, domain='time'):

        super(Pic_Change, self).__init__()
        self.num = 0
        self.diagonal = diagonal
        if isinstance(matrix, np.ndarray):
            self.matrix = matrix
        self.matrix_plot = self.matrix[:, :, self.num]
        if not self.diagonal: # if the data has not been diagnoaled yet, then do it
            self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.title = title
        if n_times.any():
            self.n_times = np.array(n_times)
        else:
            self.n_times = np.arange (self.matrix_plot.shape[2])
        self.domain = domain
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
        self.num_line_edit.returnPressed.connect(self.go_move)
        self.num_line_edit.clearFocus()

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
        self.image = self.ax.matshow(self.matrix_plot)
        self.canvas.fig.colorbar(self.image)
        self.canvas.mpl_connect('key_press_event', self.on_move)
        if self.domain == 'time':
            self.ax.set_title(self.title + ' ' + '(' + 'time:' + '' +
                          str(self.n_times[self.num].astype(np.float16)) + 's' + ')')
        else:
            self.ax.set_title (self.title + ' ' + '(' + 'frequency: ' +
                               str (self.n_times[self.num].astype (np.float16)) + 'Hz' + ')')
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.toolbar = NavigationToolbar(self.canvas, self)

        self.canvas_stack = QStackedWidget()
        self.canvas_stack.addWidget(self.canvas)
        self.toolbar_stack = QStackedWidget()
        self.toolbar_stack.addWidget(self.toolbar)
        self.toolbar_stack.setFixedHeight(38)

    def change_canvas(self):
        self.matrix_plot = self.matrix[:, :, self.num]
        if not self.diagonal:
            self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.image.set_data(self.matrix_plot)
        if self.domain == 'time':
            self.ax.set_title(self.title + ' ' + '(' + 'time:' + '' +
                          str(self.n_times[self.num].astype(np.float16)) + 's' + ')')
        else:
            self.ax.set_title (self.title + ' ' + '(' + 'frequency: ' +
                               str (self.n_times[self.num].astype (np.float16)) + 'Hz' + ')')
        self.canvas.draw_idle()
        self.num_line_edit.setText(str(self.num))

    def go_move(self):
        if self.num_line_edit.text() == '':
            self.num = self.matrix.shape[2] - 1
        else:
            self.num = int(self.num_line_edit.text())
        if self.num >= self.matrix.shape[2]:
            self.num = self.matrix.shape[2] - 1
            self.num_line_edit.setText(str(self.matrix.shape[2]))
        self.change_canvas()

    def on_move(self, event):
        print('activcate this')
        if event.key is 'down':
            if self.num == 0:
                self.num = 0
            else:
                self.num -= 1
        elif event.key is 'up':
            if self.num == self.matrix.shape[2] - 1:
                self.num = 0
            else:
                self.num += 1
        else:
            pass
        self.change_canvas()

    def left_move(self):

        if self.num == 0:
            pass
        else:
            self.num -= 1
        self.change_canvas()

    def right_move(self):
        if self.num == self.matrix.shape[2] - 1:
            self.num = 0
        else:
            self.num += 1
        self.change_canvas()

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
        pass
        '''
        if event.key() == Qt.Key_Up:
            self.right_move()
        elif event.key() == Qt.Key_Down:
            self.left_move()
        elif event.key() == Qt.Key_Enter:
            print('here')
            self.go_move()
        '''

    def set_style(self):
        pass



class Multitaper_Con_Win(QMainWindow):

    spec_con_signal = pyqtSignal(dict, str)

    def __init__(self, event, chan, time):
        '''
        :param event:
        :param method: which method to calculate spectral connectivity
        '''
        super(Multitaper_Con_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.time = time
        self.para = dict()
        self.para['chan'] = None
        self.plot_3d = False
        self.all_plot = False
        self.chanx_get, self.chany_get = None, None
        self.average = False
        self.dura = None
        self.step = None
        self.mode = 'Multitaper'

        self.init_ui()


    def init_ui(self):

        self.setFixedWidth(375)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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


    def create_widget(self):
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)
        self.event_combo.setFixedWidth(100)

        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(100)
        self.fmin_edit.setValidator(QDoubleValidator())
        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(100)
        self.fmax_edit.setValidator(QDoubleValidator())
        self.line1_label = QLabel(' - ', self)
        self.line1_label.setFixedWidth(20)

        self.time_label = QLabel('Time', self)
        self.time_label.setFixedWidth(100)
        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(100)
        self.tmin_edit.setValidator(QDoubleValidator())
        self.tmin_edit.setText(str(self.time[0]))
        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(100)
        self.tmax_edit.setValidator(QDoubleValidator())
        self.tmax_edit.setText(str(self.time[1]))
        self.line2_label = QLabel(' - ', self)
        self.line2_label.setFixedWidth(20)

        self.bandwidth_label = QLabel('Band Width(Hz)')
        self.bandwidth_label.setFixedWidth(140)
        self.bandwidth_edit = QLineEdit()
        self.bandwidth_edit.setAlignment(Qt.AlignCenter)
        self.bandwidth_edit.setFixedWidth(100)
        self.bandwidth_edit.setValidator(QIntValidator())

        self.des_label = QLabel('Select the Channels you want to use', self)
        self.des_label.setWordWrap(True)
        self.chanx_label = QLabel('Channel X', self)
        self.chanx_label.setFixedWidth(90)
        self.chanx_btn = QPushButton('···')
        self.chanx_btn.clicked.connect(self.chanx)
        self.chanx_btn.setFixedWidth(100)
        self.chany_label = QLabel('Channel Y', self)
        self.chany_label.setFixedWidth(90)
        self.chany_btn = QPushButton('···')
        self.chany_btn.clicked.connect(self.chany)
        self.chany_btn.setFixedWidth(100)

        self.win_cb = QCheckBox('use sliding windows')
        self.win_cb.stateChanged.connect(self.use_win)
        self.win_dura_label = QLabel('Window duration(s)')
        self.win_dura_label.setFixedWidth(170)
        self.win_dura = QLineEdit()
        self.win_dura.setAlignment(Qt.AlignCenter)
        self.win_dura.setFixedWidth(100)
        self.win_dura.setValidator(QDoubleValidator())
        self.win_dura.setEnabled(False)
        self.win_step_label = QLabel ('Window Step(s)')
        self.win_step_label.setFixedWidth(160)
        self.win_step = QLineEdit()
        self.win_step.setAlignment(Qt.AlignCenter)
        self.win_step.setFixedWidth(100)
        self.win_step.setValidator(QDoubleValidator())
        self.win_step.setEnabled(False)

        self.average_cb = QCheckBox('Average')
        self.average_cb.stateChanged.connect (self.use_average)
        self.plot_all_cb = QCheckBox('All channels')
        self.plot_all_cb.stateChanged.connect(self.all_chan)
        self.plot_3d_cb = QCheckBox('3D Viewer')
        self.plot_3d_cb.setEnabled(False)
        self.plot_3d_cb.stateChanged.connect(self.use_3d)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.setProperty('group', 'bottom')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.setFixedWidth(60)
        self.cancel_button.setProperty('group', 'bottom')
        self.cancel_button.clicked.connect(self.close)


    def use_win(self):
        if self.win_cb.isChecked():
            self.win_dura.setEnabled(True)
            self.win_step.setEnabled(True)
            self.average_cb.setEnabled(False)
        else:
            self.win_dura.setEnabled(False)
            self.win_step.setEnabled(False)
            try:
                if len(self.chanx_get) == 1 and len (self.chany_get) >= 1:
                    self.average_cb.setChecked(False)
                    self.average_cb.setEnabled(False)
                else:
                    self.average_cb.setEnabled(True)
            except:
                pass

    def chanx(self):
        self.chanx_win = Select_Chan(self.chan, multi=True)
        self.get_chan = 'x'
        self.chanx_win.chan_signal.connect(self.get_chan_func)
        self.chanx_win.show()

    def chany(self):
        self.chany_win = Select_Chan(self.chan)
        self.get_chan = 'y'
        self.chany_win.chan_signal.connect(self.get_chan_func)
        self.chany_win.show()


    def get_chan_func(self, chan):
        if self.get_chan == 'x':
            self.chanx_get = chan
            if len(self.chanx_get) > 1:
                self.chany_btn.setEnabled(False)
                self.chany_get = None
            else:
                self.chany_btn.setEnabled(True)
        elif self.get_chan == 'y':
            self.chany_get = chan
        try:
            if len(self.chanx_get) == 1 and len(self.chany_get) >= 1:
                self.average_cb.setChecked(False)
                self.average_cb.setEnabled(False)
            else:
                self.average_cb.setEnabled(True)
        except:
            pass


    def all_chan(self):
        if self.plot_all_cb.isChecked():
            self.all_plot = True
            self.chanx_get, self.chany_get = None, None
            self.plot_3d_cb.setEnabled(True)
            self.average_cb.setEnabled(True)
            self.win_cb.setChecked(False)
            self.win_cb.setEnabled(False)
        else:
            self.all_plot = False
            self.plot_3d_cb.setEnabled(False)
            try:
                if len (self.chanx_get) == 1 and len (self.chany_get) >= 1:
                    self.average_cb.setChecked (False)
                    self.average_cb.setEnabled (False)
                else:
                    self.average_cb.setChecked (True)
                    self.average_cb.setEnabled (True)
            except:
                pass


    def use_average(self):
        if self.average_cb.isChecked():
            self.average = True
        else:
            self.average = False


    def use_3d(self):
        if self.plot_3d_cb.isChecked():
            self.plot_3d = True
            self.average_cb.setChecked(True)
            self.average_cb.setEnabled(True)
            self.average = True
        else:
            self.plot_3d = False
            self.average_cb.setEnabled(False)


    def create_layout(self):

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.event_label)
        layout_1.addStretch(100)
        layout_1.addWidget(self.event_combo)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.fmin_edit)
        layout_2.addWidget(self.line1_label)
        layout_2.addWidget(self.fmax_edit)

        layout_20 = QHBoxLayout()
        layout_20.addWidget(self.freq_label)
        layout_20.addStretch(100)
        layout_20.addLayout(layout_2)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.tmin_edit)
        layout_3.addWidget(self.line2_label)
        layout_3.addWidget(self.tmax_edit)

        layout_30 = QHBoxLayout()
        layout_30.addWidget(self.time_label)
        layout_30.addStretch(100)
        layout_30.addLayout(layout_3)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.bandwidth_label)
        layout_4.addStretch(100)
        layout_4.addWidget(self.bandwidth_edit)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.average_cb)
        layout_5.addStretch(100)
        layout_5.addWidget(self.plot_3d_cb)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.plot_all_cb)
        layout_6.addStretch(100)

        layout_7 = QHBoxLayout()
        layout_7.addWidget(self.chanx_label)
        layout_7.addStretch(100)
        layout_7.addWidget(self.chanx_btn)
        layout_8 = QHBoxLayout()
        layout_8.addWidget(self.chany_label)
        layout_8.addStretch(100)
        layout_8.addWidget(self.chany_btn)

        layout_91 = QHBoxLayout()
        layout_91.addWidget(self.win_dura_label)
        layout_91.addStretch(10)
        layout_91.addWidget(self.win_dura)

        layout_92 = QHBoxLayout()
        layout_92.addWidget(self.win_step_label)
        layout_92.addStretch(10)
        layout_92.addWidget(self.win_step)

        button_layout = QHBoxLayout()
        button_layout.addStretch(100)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_20)
        main_layout.addLayout(layout_30)
        main_layout.addWidget(self.des_label)
        main_layout.addLayout(layout_7)
        main_layout.addLayout(layout_8)
        main_layout.addLayout(layout_4)
        main_layout.addWidget(self.win_cb)
        main_layout.addLayout(layout_91)
        main_layout.addLayout(layout_92)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_6)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def ok_func(self):
        self.event_chosen = self.event_combo.currentText()
        self.para['event'] = self.event_chosen
        if self.fmin_edit.text() and self.fmax_edit.text():
            try:
                self.fmin = float(self.fmin_edit.text())
                self.fmax = float(self.fmax_edit.text())
                self.para['freq'] = [self.fmin, self.fmax]
            except:
                self.close()
        else:
            self.para['freq'] = None
            self.close()
        if self.tmin_edit.text() and self.tmax_edit.text():
            self.tmin = float(self.tmin_edit.text())
            self.tmax = float(self.tmax_edit.text())
            self.para['time'] = [self.tmin, self.tmax]
        else:
            self.para['time'] = None
            self.close()
        if self.win_cb.isChecked():
            try:
                self.dura = float(self.win_dura.text())
                self.step = float(self.win_step.text ())
            except:
                self.dura = None
                self.step = None
        if self.bandwidth_edit.text():
            self.para['bandwidth'] = float(self.bandwidth_edit.text())
        else:
            self.para['bandwidth'] = 3  #若用户没输入bandwidth, 则默认为3
        self.para['plot_mode'] = [self.all_plot, self.plot_3d]
        self.para['chan'] = [self.chanx_get, self.chany_get]
        self.para['average'] = self.average
        print('是否Sliding: ' + str(self.win_cb.isChecked()))
        self.para['sliding'] = [self.win_cb.isChecked(), self.dura, self.step]
        self.spec_con_signal.emit(self.para, self.mode)
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton[group='bottom']{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')


class Morlet_Con_Win(QMainWindow):

    spec_con_signal = pyqtSignal(dict, str)

    def __init__(self, event, chan, time):
        super(Morlet_Con_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.time = time
        self.para = dict()
        self.para['chan'] = None
        self.plot_3d = False
        self.all_plot = False
        self.chanx_get, self.chany_get = None, None
        self.mode = 'Morlet'
        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(390)
        self.setMinimumHeight(300)
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
        self.name_label = QLabel('Morlet Wavelets Parameters')
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setProperty('group', 'name')

        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.event_cb = QComboBox()
        self.event_cb.addItems(self.event)
        self.event_cb.setFixedWidth(93)

        self.freq_label = QLabel('Frequency(Hz)', self)
        self.freq_label.setFixedWidth(130)
        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())
        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())
        self.line1_label = QLabel(' - ', self)
        self.line1_label.setFixedWidth(20)

        self.time_label = QLabel('Time(s)', self)
        self.time_label.setFixedWidth(100)
        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(93)
        self.tmin_edit.setValidator(QDoubleValidator())
        self.tmin_edit.setText(str(self.time[0]))
        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(93)
        self.tmax_edit.setValidator(QDoubleValidator())
        self.tmax_edit.setText(str(self.time[1]))
        self.line2_label = QLabel(' - ', self)
        self.line2_label.setFixedWidth(20)

        self.choose_chan_label = QLabel('Choose sub_channels to calculate, otherwise all')
        # self.choose_chan_label.setFixedWidth(300)
        self.choose_chan_label.setWordWrap(True)
        self.chanx_label= QLabel('Channel X')
        self.chanx_label.setFixedWidth(100)
        self.choose_chanx_btn = QPushButton(self)
        self.choose_chanx_btn.setText('···')
        self.choose_chanx_btn.clicked.connect(self.chanx)
        self.choose_chanx_btn.setFixedWidth(100)
        self.chany_label = QLabel ('Channel X')
        self.chany_label.setFixedWidth(90)
        self.choose_chany_btn = QPushButton(self)
        self.choose_chany_btn.setText('···')
        self.choose_chany_btn.clicked.connect(self.chany)
        self.choose_chany_btn.setFixedWidth(100)

        self.plot_all_cb = QCheckBox('All channels')
        self.plot_all_cb.stateChanged.connect(self.all_chan)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.setProperty('group', 'bottom')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setProperty('group', 'bottom')

    def create_layout(self):
        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.event_label)
        layout_0.addStretch(100)
        layout_0.addWidget(self.event_cb)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.fmin_edit)
        layout_1.addWidget(self.line1_label)
        layout_1.addWidget(self.fmax_edit)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.tmin_edit)
        layout_2.addWidget(self.line2_label)
        layout_2.addWidget(self.tmax_edit)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.freq_label)
        layout_3.addStretch(10)
        layout_3.addLayout(layout_1)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.time_label)
        layout_4.addStretch(10)
        layout_4.addLayout(layout_2)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.chanx_label)
        layout_5.addStretch(10)
        layout_5.addWidget(self.choose_chanx_btn)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.chany_label)
        layout_6.addStretch(10)
        layout_6.addWidget(self.choose_chany_btn)

        layout_7 = QHBoxLayout()
        layout_7.addStretch(11)
        layout_7.addWidget(self.ok_button)
        layout_7.addWidget(self.cancel_button)

        layout_8 = QHBoxLayout()
        layout_8.addWidget(self.plot_all_cb)
        layout_8.addStretch(100)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_4)
        main_layout.addWidget(self.choose_chan_label)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_6)
        main_layout.addLayout(layout_8)
        main_layout.addLayout(layout_7)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        pass


    def chanx(self):
        self.chanx_win = Select_Chan(self.chan, multi=True)
        self.get_chan = 'x'
        self.chanx_win.chan_signal.connect(self.get_chan_func)
        self.chanx_win.show()

    def chany(self):
        self.chany_win = Select_Chan(self.chan)
        self.get_chan = 'y'
        self.chany_win.chan_signal.connect(self.get_chan_func)
        self.chany_win.show()


    def get_chan_func(self, chan):
        if self.get_chan == 'x':
            self.chanx_get = chan
            if len(chan) > 1:
                self.choose_chany_btn.setEnabled(False)
                self.chany_get = None
            else:
                self.choose_chany_btn.setEnabled(True)
        elif self.get_chan == 'y':
            self.chany_get = chan


    def all_chan(self):
        if self.plot_all_cb.isChecked():
            self.all_plot = True
            self.chanx_get, self.chany_get = None, None
            self.choose_chanx_btn.setEnabled(False)
            self.choose_chany_btn.setEnabled(False)
        else:
            self.all_plot = False
            self.choose_chanx_btn.setEnabled(True)
            self.choose_chany_btn.setEnabled(True)


    def ok_func(self):
        self.event_chosen = self.event_cb.currentText ()
        self.para['event'] = self.event_chosen
        if self.fmin_edit.text () and self.fmax_edit.text ():
            try:
                self.fmin = float (self.fmin_edit.text ())
                self.fmax = float (self.fmax_edit.text ())
                self.para['freq'] = [self.fmin, self.fmax]
            except:
                self.close ()
        else:
            self.para['freq'] = None
            self.close ()
        if self.tmin_edit.text () and self.tmax_edit.text ():
            self.tmin = float (self.tmin_edit.text ())
            self.tmax = float (self.tmax_edit.text ())
            self.para['time'] = [self.tmin, self.tmax]
        else:
            self.para['time'] = None
            self.close ()
        self.para['plot_all'] = self.all_plot
        self.para['chan'] = [self.chanx_get, self.chany_get]
        self.spec_con_signal.emit (self.para, self.mode)
        self.close ()


class Freq_Con_Method_Win(QMainWindow):

    con_signal = pyqtSignal(dict, str)

    def __init__(self, event, chan, time, con_method):

        super(Freq_Con_Method_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.time = time
        self.con_method = con_method

        self.init_ui()

    def init_ui(self):

        self.setFixedWidth(150)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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


    def create_widget(self):
        self.taper_btn = QPushButton(self)
        self.taper_btn.setText('Multitaper')
        self.taper_btn.clicked.connect(self.taper_win)
        self.taper_btn.setFixedWidth(120)
        self.morlet_btn = QPushButton(self)
        self.morlet_btn.setText('Morlet')
        self.morlet_btn.clicked.connect(self.morlet_win)
        self.morlet_btn.setFixedWidth(120)


    def create_layout(self):
        layout_0 = QVBoxLayout()
        layout_0.addWidget(self.taper_btn)
        layout_0.addWidget(self.morlet_btn)
        self.center_widget.setLayout(layout_0)


    def taper_win(self):
        self.multi_taper_win = Multitaper_Con_Win(event=self.event, chan=self.chan,
                                                  time=self.time)
        self.multi_taper_win.spec_con_signal.connect(self.get_para)
        self.multi_taper_win.show()
        self.close()

    def morlet_win(self):
        self.morlet_win = Morlet_Con_Win(event=self.event, chan=self.chan,
                                        time=self.time)
        self.morlet_win.spec_con_signal.connect(self.get_para)
        self.morlet_win.show()
        self.close()


    def get_para(self, para, mode):
        print('here here')
        self.con_signal.emit(para, mode)


    def set_style(self):
        pass


class Con_Win(QMainWindow):

    def __init__(self, data, subject):
        super(Con_Win, self).__init__()
        if isinstance(data, BaseEpochs):
            self.data = data
        else:
            raise TypeError('This is not an epoch data')
        self.subject = subject
        self.group = len(get_chan_group(self.data))
        self.spec_con_method = dict()
        self.spec_con_method['coh'] = 'Coherence'
        self.spec_con_method['imcoh'] = 'Imaginary Coherence'
        self.spec_con_method['plv'] = 'Phase-Locking Value (PLV)'
        self.spec_con_method['ciplv'] = 'corrected imaginary PLV'
        self.spec_con_method['ppc'] = 'Pairwise Phase Consistency (PPC)'
        self.spec_con_method['pli'] = 'Phase Lag Index (PLI)'
        self.spec_con_method['pli2_unbiased'] = 'Unbiased estimator of squared PLI'
        self.spec_con_method['wpli'] = 'Weighted Phase Lag Index (WPLI)'
        self.spec_con_method['wpli2_debiased'] = 'Debiased estimator of squared WPLI'
        self.spec_con_method['psi'] = 'Phase Slope Index'
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('Connectivity Analysis')
        self.setFixedHeight(290)
        self.setFixedWidth(930)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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
        # self.center_widget.setFont(self.font)
        self.center_widget.setProperty('group', 'center')
        self.setCentralWidget(self.center_widget)


    def create_widget(self):
        self.data_box = QGroupBox('Data Information')
        self.data_box.setProperty('group', 'box')
        self.name_label = QLabel(self.subject)
        self.name_label.setProperty('group', 'label_00')
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.name_label.setFixedWidth(580)
        self.samplingr_label = QLabel('Sampling Rate')
        self.samplingr_label.setProperty('group', 'label_0')
        self.samplingr_label.setAlignment(Qt.AlignLeft)
        self.samplingr_label.setFixedWidth(110)
        self.samplingr_con_label = QLabel(str(round(self.data.info['sfreq'])))
        self.samplingr_con_label.setProperty('group', 'label')
        self.samplingr_con_label.setAlignment(Qt.AlignHCenter)
        self.samplingr_con_label.setFixedWidth(60)
        self.group_label = QLabel('Group')
        self.group_label.setProperty('group', 'label_0')
        self.group_label.setAlignment(Qt.AlignLeft)
        self.group_label.setFixedWidth(55)
        self.group_con_label = QLabel(str(self.group))
        self.group_con_label.setProperty('group', 'label')
        self.group_con_label.setAlignment(Qt.AlignHCenter)
        self.group_con_label.setFixedWidth(35)
        self.chan_label = QLabel('Channel')
        self.chan_label.setProperty('group', 'label_0')
        self.chan_label.setAlignment(Qt.AlignLeft)
        self.chan_label.setFixedWidth(90)
        self.chan_len_label = QLabel(str(len(self.data.ch_names)))
        self.chan_len_label.setProperty('group', 'label')
        self.chan_len_label.setAlignment(Qt.AlignHCenter)
        self.chan_len_label.setFixedWidth(100)
        self.event_label = QLabel('Event')
        self.event_label.setProperty('group', 'label_0')
        self.event_label.setAlignment(Qt.AlignLeft)
        self.event_label.setFixedWidth(110)
        self.event_num_label = QLabel(str(len(self.data.event_id)))
        self.event_num_label.setProperty('group', 'label')
        self.event_num_label.setAlignment(Qt.AlignHCenter)
        self.event_num_label.setFixedWidth(60)
        self.epoch_label = QLabel('Epoch')
        self.epoch_label.setProperty('group', 'label_0')
        self.epoch_label.setAlignment(Qt.AlignLeft)
        self.epoch_label.setFixedWidth(55)
        self.epoch_num_label = QLabel(str(len(self.data)))
        self.epoch_num_label.setProperty('group', 'label')
        self.epoch_num_label.setAlignment(Qt.AlignHCenter)
        self.epoch_num_label.setFixedWidth(35)
        self.time_epoch_label = QLabel('Time epoch')
        self.time_epoch_label.setProperty('group', 'label_0')
        self.time_epoch_label.setAlignment(Qt.AlignLeft)
        self.time_epoch_label.setFixedWidth(90)
        self.time_range_label = QLabel(str(self.data.tmin) + ' - ' + str(self.data.tmax))
        self.time_range_label.setProperty('group', 'label')
        self.time_range_label.setAlignment(Qt.AlignHCenter)
        self.time_range_label.setFixedWidth(100)

        self.con_measure_bx = QGroupBox('Connectivity Measurements')
        self.con_measure_bx.setProperty('group', 'box')


        self.pic_label = QLabel()
        # pixmap = QPixmap("../image/connectivity_use.png").scaled(QSize(140, 140), Qt.KeepAspectRatioByExpanding)
        pixmap = QPixmap("image/connectivity_use.png").scaled(QSize(140, 140), Qt.KeepAspectRatioByExpanding)
        self.pic_label.resize(150, 150)
        self.pic_label.setPixmap(pixmap)
        self.pic_label.setAlignment(Qt.AlignCenter)
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Frequency Domain                                                        #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        # functional
        self.coher_btn = QPushButton(self)
        self.coher_btn.setText('Coherence')
        self.coher_btn.setFixedSize(210, 28)
        self.coher_btn.clicked.connect(self.use_coherence)
        self.plv_btn = QPushButton(self)
        self.plv_btn.setText('Phase-Locking Value')
        self.plv_btn.setFixedSize(210, 28)
        self.plv_btn.clicked.connect(self.use_plv)
        self.pli_btn = QPushButton(self)
        self.pli_btn.setText('Phase-Lag Index')
        self.pli_btn.setFixedSize(210, 28)
        self.pli_btn.clicked.connect(self.use_pli)
        self.imag_coher_btn = QPushButton(self)
        self.imag_coher_btn.setText('Imaginary Coherence')
        self.imag_coher_btn.setFixedSize(210, 28)
        self.imag_coher_btn.clicked.connect(self.use_imaginary_coh)
        self.ppc_btn = QPushButton(self)
        self.ppc_btn.setText('Pairwise Phase Consistency')
        self.ppc_btn.setFixedSize(210, 28)
        self.ppc_btn.setProperty('group', 'big')
        self.ppc_btn.clicked.connect(self.use_ppc)
        self.wpli_btn = QPushButton(self)
        self.wpli_btn.setText('Weighted PLI')
        self.wpli_btn.setFixedSize(210, 28)
        self.wpli_btn.clicked.connect(self.use_wpli)
        self.uspli_btn = QPushButton(self)
        self.uspli_btn.setText('Unbiased Squared PLI')
        self.uspli_btn.setFixedSize(210, 28)
        self.uspli_btn.clicked.connect(self.use_unbiased_pli)
        self.dswpli_btn = QPushButton(self)
        self.dswpli_btn.setText('Unbiased Squared WPLI')
        self.dswpli_btn.setFixedSize(210, 28)
        self.dswpli_btn.clicked.connect(self.use_debiased_wpli)


    def create_layout(self):

        layout_1 = QHBoxLayout()
        layout_1.setContentsMargins(0,0,0,0)
        layout_1.addWidget(self.samplingr_label)
        layout_1.addWidget(self.samplingr_con_label)
        layout_1.addWidget(self.group_label)
        layout_1.addWidget(self.group_con_label)
        layout_1.addWidget(self.chan_label)
        layout_1.addWidget(self.chan_len_label)
        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.event_label)
        layout_2.addWidget(self.event_num_label)
        layout_2.addWidget(self.epoch_label)
        layout_2.addWidget(self.epoch_num_label)
        layout_2.addWidget(self.time_epoch_label)
        layout_2.addWidget(self.time_range_label)
        layout_3 = QVBoxLayout()
        layout_3.addWidget(self.name_label)
        layout_3.addLayout(layout_1)
        layout_3.addLayout(layout_2)
        self.data_box.setLayout(layout_3)

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.data_box, stretch=1)
        info_layout.addWidget(self.pic_label, stretch=1000)

        freq_layout_0 = QFormLayout()
        freq_layout_0.addRow(self.coher_btn, self.wpli_btn)
        freq_layout_0.addRow(self.pli_btn, self.imag_coher_btn)
        freq_layout_1 = QFormLayout()
        freq_layout_1.addRow(self.uspli_btn, self.plv_btn)
        freq_layout_1.addRow(self.dswpli_btn, self.ppc_btn)

        freq_layout_2 = QHBoxLayout()
        freq_layout_2.addLayout(freq_layout_0)
        freq_layout_2.addLayout(freq_layout_1)
        freq_layout_2.addStretch(1000)

        self.con_measure_bx.setLayout(freq_layout_2)

        layout_4 = QVBoxLayout()
        layout_4.addLayout(info_layout)
        layout_4.addWidget(self.con_measure_bx)
        self.center_widget.setLayout(layout_4)


    def set_style(self):
        self.setStyleSheet(''' 
            QLabel[group='label_00']{font:10pt Consolas; background-color: rgb(207, 207, 207);
            color: black}
            QLabel[group='label_0']{font:10pt Consolas;
            color: black}
            QLabel[group='label']{font:bold 10pt Consolas;
            color: black}
            QGroupBox[group='box']{font: bold 13pt Consolas;
            color: black}
            QGroupBox[group='box_1']{font: bold 11pt Consolas;
            color: black}
            QLabel[group='label_11']{font: bold 11pt Consolas;
            color: black; border: none}
            QGroupBox[group='box_12']{font: 9pt Consolas;
            color: black}
            QPushButton{background-color: rgb(210, 210, 210); font: 10pt Consolas; color: black}
            QPushButton:hover{background-color:white}
            QPushButton:pressed{background-color:white;
                                padding=left:3px; padding-top:3px}       
            QPushButton[group='big']{background-color: rgb(210, 210, 210); font: 9pt Consolas bold; color: black}
            QPushButton[group='big']:hover{background-color:white}
            QPushButton[group='big']:pressed{background-color:white;
                                             padding=left:3px; padding-top:3px}
            QWidget[group='center']{background-color: white}
        ''')

    # Connecivity analysis
    #
    # Time domain connecivity
    def show_pbar(self):
        self.pbar = My_Progress()
        self.pbar.show()


    # Frequency domain connectivity (Spectral)
    '''
        'coh' : Coherence given by::

                 | E[Sxy] |
        C = ---------------------
            sqrt(E[Sxx] * E[Syy])
    '''

    def use_coherence(self):
        self.method = 'coh'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    def use_canonical_coh(self):
        pass

    '''
        'imcoh' : Imaginary coherence [1]_ given by::

                  Im(E[Sxy])
        C = ----------------------
            sqrt(E[Sxx] * E[Syy])
    '''

    def use_imaginary_coh(self):
        self.method = 'imcoh'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    '''
        'plv' : Phase-Locking Value (PLV) [2]_ given by::

         PLV = |E[Sxy/|Sxy|]|
    '''

    def use_plv(self):
        self.method = 'plv'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    '''
        'ciplv' : corrected imaginary PLV (icPLV) [3]_ given by::

                         |E[Im(Sxy/|Sxy|)]|
        ciPLV = ------------------------------------
                 sqrt(1 - |E[real(Sxy/|Sxy|)]| ** 2)
    '''

    def use_ciplv(self):
        self.method = 'ciplv'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    '''
       'ppc' : Pairwise Phase Consistency (PPC), an unbiased estimator
        of squared PLV
    '''

    def use_ppc(self):
        self.method = 'ppc'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    '''
        'pli' : Phase Lag Index (PLI) [5]_ given by::

         PLI = |E[sign(Im(Sxy))]|
    '''

    def use_pli(self):
        self.method = 'pli'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    # 'pli2_unbiased' : Unbiased estimator of squared PLI
    def use_unbiased_pli(self):
        self.method = 'pli2_unbiased'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    def use_wpli(self):
        self.method = 'wpli'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    def use_debiased_wpli(self):
        self.method = 'wpli2_debiased'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method, time=[self.data.tmin, self.data.tmax])
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()


    def calculate_con(self, para, mode):
        self.show_pbar()
        epoch = self.data[para['event']]
        self.para = para
        if mode == 'Multitaper':
            self.calcu_con = Cal_Spec_Con(epoch, para=self.para, method=self.method, mode=mode)
            self.calcu_con.spec_con_signal.connect(self.plot_spec_con)
            self.calcu_con.start()
        else:
            self.calcu_con = Cal_Spec_Con(epoch, para=self.para, method=self.method, mode=mode)
            self.calcu_con.spec_con_signal.connect(self.plot_morlet_con)
            self.calcu_con.start()


    def plot_time(self, con_list):
        import matplotlib.pyplot as plt
        from itertools import product
        if len(self.para['chan'][0]) == 1:
            result = con_list[0]
            time_extent = (self.para['time'][0], self.para['time'][1])
            data = con_list[1]
            times = con_list[2]
            for i in range (len (result)):
                con = result[i][0]
                m = result[i][1]
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots (nrows=2, ncols=1, figsize=(15, 9))
                ax[0].set_title('Stereo-EEG: ' + str(self.para['chan'][0][0]) + '—' +
                                str(self.para['chan'][1][i]), fontweight='bold')
                ax[0].plot(times, data[i][:, :, 0], color='b')
                ax[0].plot(times, data[i][:, :, 1], color='g')
                ax[0].set_xlabel('Time(s)')
                ax[0].set_ylabel('Amplitude')
                ax[0].set_xlim(time_extent)
                ax[0].axvline(0., color='black')

                time_grid, freq_grid = np.meshgrid (
                    np.append(con.time, time_extent[-1]),
                    np.append(con.frequencies, m.nyquist_frequency))
                if self.method == 'coh':
                    con_ = con.coherence_magnitude ()[..., 0, 1].squeeze ().T
                elif self.method == 'imcoh':
                    con_ = con.imaginary_coherence ()[..., 0, 1].squeeze ().T
                elif self.method == 'plv':
                    con_ = abs(con.phase_locking_value ())[..., 0, 1].squeeze ().T
                elif self.method == 'ciplv':
                    pass
                elif self.method == 'ppc':
                    con_ = con.pairwise_phase_consistency ()[..., 0, 1].squeeze ().T
                elif self.method == 'pli':
                    con_ = con.phase_lag_index ()[..., 0, 1].squeeze ().T
                elif self.method == 'pli2_unbiased':
                    con_ = con.debiased_squared_phase_lag_index()[..., 0, 1].squeeze ().T
                elif self.method == 'wpli':
                    con_ = con.weighted_phase_lag_index ()[..., 0, 1].squeeze ().T
                elif self.method == 'wpli2_debiased':
                    con_ = con.debiased_squared_weighted_phase_lag_index ()[..., 0, 1].squeeze ().T
                mesh = ax[1].pcolormesh (time_grid, freq_grid, con_,
                                         vmin=0.0, vmax=1.0, cmap='viridis')
                ax[1].set_ylim((0, 300))
                ax[1].set_xlim(time_extent)
                ax[1].axvline(0., color='black')
                ax[1].set_xlabel('Time(s)')
                ax[1].set_ylabel('Frequency(Hz)')
                ax[1].set_ylim((self.para['freq'][0], self.para['freq'][1]))
                ax[1].set_title('Connectivity', fontweight='bold')
                fig.tight_layout(pad=4)
                cb = fig.colorbar(mesh, ax=ax.ravel ().tolist (), orientation='horizontal',
                                   shrink=.5, aspect=15, pad=0.1, label=self.spec_con_method[self.method])
                cb.outline.set_linewidth(0)
                fig.show()
        else:
            con = con_list[0]
            m = con_list[1]
            n_signals = len(self.para['chan'][0])
            time_extent = (self.para['time'][0], self.para['time'][1])
            time_grid, freq_grid = np.meshgrid (
                np.append(con.time, time_extent[-1]),
                np.append(con.frequencies, m.nyquist_frequency))
            fig, axes = plt.subplots(nrows=n_signals, ncols=n_signals, figsize=(15, 9))
            meshes = list ()
            for ind1, ind2 in product(range(n_signals), range(n_signals)):
                if ind1 == ind2:
                    vmin, vmax = con.power().min(), con.power().max()
                else:
                    vmin, vmax = 0, 1.
                if self.method == 'coh':
                    con_ = con.coherence_magnitude()[..., ind1, ind2].squeeze().T
                elif self.method == 'imcoh':
                    con_ = con.imaginary_coherence()[..., ind1, ind2].squeeze().T
                elif self.method == 'plv':
                    con_ = abs(con.phase_locking_value())[..., ind1, ind2].squeeze().T
                elif self.method == 'ciplv':
                    pass
                elif self.method == 'ppc':
                    con_ = con.pairwise_phase_consistency()[..., ind1, ind2].squeeze().T
                elif self.method == 'pli':
                    con_ = con.phase_lag_index()[..., ind1, ind2].squeeze().T
                elif self.method == 'pli2_unbiased':
                    con_ = con.debiased_squared_phase_lag_index()[..., ind1, ind2].squeeze().T
                elif self.method == 'wpli':
                    con_ = con.weighted_phase_lag_index()[..., ind1, ind2].squeeze().T
                elif self.method == 'wpli2_debiased':
                    con_ = con.debiased_squared_weighted_phase_lag_index()[..., ind1, ind2].squeeze().T
                mesh = axes[ind1, ind2].pcolormesh(
                    time_grid, freq_grid, con_,
                    vmin=vmin, vmax=vmax, cmap='viridis')
                meshes.append(mesh)
                axes[ind1, ind2].set_ylim((0, 300))
                axes[ind1, ind2].set_xlim(time_extent)
                axes[ind1, ind2].axvline(0., color='black')
                if ind1 == 0:
                    axes[ind1, ind2].set_title(self.para['chan'][0][ind2])
                if ind2 == 0:
                    axes[ind1, ind2].set_title(self.para['chan'][0][ind1], x=0.2, y=1)
            plt.tight_layout (pad=2)
            cb = fig.colorbar (meshes[-2], ax=axes.ravel().tolist(), orientation='horizontal',
                               shrink=.5, aspect=15, pad=0.1, label=self.spec_con_method[self.method])
            cb.outline.set_linewidth (0)
            fig.show()


    def plot_notime(self, con_list):
        from matplotlib import pyplot as plt
        if self.para['average']:
            if self.para['plot_mode'][1]:
                con = con_list[0]
                mne.viz.plot_sensors_connectivity(self.data.info, con)
            else:
                con = con_list[0]
                fig, ax = plt.subplots()
                image = ax.matshow(con[:, :])
                fig.colorbar(image)
                ax.set_title(self.spec_con_method[self.method])
                fig.show()
        else:
            print(self.para['chan'])
            con = con_list[0]
            if not self.para['chan'][1]:
                print('在这')
                pic_win = Pic_Change(matrix=con, title=self.spec_con_method[self.method],
                                     n_times=con_list[1], diagonal=True, domain='freq')
                pic_win.show()
            else:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                for i in range(con.shape[0]):
                    ax.plot (con[i, :], label = self.para['chan'][0][0] + '—' +
                                                str(self.para['chan'][1][i]), marker='o',
                             markerfacecolor='black', markersize=3)
                    ax.legend(bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0)
                ax.set_xlim((con_list[1][0], con_list[1][-1]))
                plt.title(self.spec_con_method[self.method])
                ax.set_xlabel('Frequency (Hz)')
                ax.set_ylabel('Connectivity')
                fig.show()


    def plot_spec_con(self, con_list):
        '''
        :param con_list: list
                There are two modes of conlist:
                1. [con, m] for one-one, one-multi, multi-self channels with the time information
                2. [con, freqs] for one-one, one-multi, multi-self channels without the time information
        '''
        self.pbar.step = 100
        from numpy import ndarray
        if isinstance(con_list[1], (ndarray, list)):
            self.plot_notime(con_list)
        else:
            self.plot_time(con_list)


    def plot_morlet_con(self, con_list):
        self.pbar.step = 100
        if (self.para['chan'][0] == None) or (len(self.para['chan'][0]) > 1):
            con = con_list[0]
            times = con_list[1]
            pic_win = Pic_Change(matrix=con, title=self.spec_con_method[self.method],
                                  n_times=times, diagonal=True, domain='time')
            pic_win.show()
        else:
            con = con_list[0]
            times = con_list[1] + self.para['time'][0]
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots ()
            print(self.para['time'], len(times), len(con[0, :]))
            for i in range (len(con)):
                ax.plot(times, con[i, :], label=self.para['chan'][0][0] + '—' + self.para['chan'][1][i])
            ax.legend(bbox_to_anchor=(1.01, 0), loc=3, borderaxespad=0)
            ax.set_title(self.spec_con_method[self.method], fontweight='bold', fontsize=17)
            ax.set_xlim ((times[0], times[-1]))
            ax.set_ylim((-0., 1.1))
            ax.axvline (0., color='black')
            ax.set_xlabel('Time(s)')
            ax.set_ylabel('Connectivity')
            fig.show()


    def dir_con(self):
        self.method = 'psi'
        event_id = list (self.data.event_id.keys ())
        self.con_win = Multitaper_Con_Win(event=event_id, chan=self.data.ch_names,
                                            time=[self.data.tmin, self.data.tmax])
        self.con_win.spec_con_signal.connect(self.cal_dir_con)
        self.con_win.show ()


    def cal_dir_con(self, para, mode):
        self.show_pbar()
        epoch = self.data[para['event']]
        self.para = para
        self.cal_con = Cal_Dir_Con(data=epoch, para=para)
        self.cal_con.spec_con_signal.connect(self.plot_dir_con)
        self.cal_con.start()


    def plot_dir_con(self, con_list):
        self.pbar.step = 100
        import matplotlib.pyplot as plt
        if not self.para['sliding'][0]:
            result = con_list[0]
            data = con_list[1]
            times = con_list[2]
            time_extent = (self.para['time'][0], self.para['time'][1])
            for i in range(len(result)):
                con = result[i][0]
                m = result[i][1]
                fig, ax = plt.subplots(2, 1, figsize=(12, 9))
                ax[0].set_title('Stereo-EEG: ' + str(self.para['chan'][0][0]) + '—' +
                                    str(self.para['chan'][1][i]), fontweight='bold')
                ax[0].plot(times, data[i][:, :, 0], color='blue')
                ax[0].plot(times, data[i][:, :, 1], color='green')
                ax[0].set_xlabel('Time(s)')
                ax[0].set_ylabel('Amplitude')
                ax[0].set_xlim(time_extent)
                ax[0].axvline(0, color='black')

                freq = self.para['freq']
                if self.method == 'psi':
                    psi = con.phase_slope_index(frequencies_of_interest=freq, frequency_resolution=m.frequency_resolution)
                    ax[1].bar([1, 2], [psi[..., 0, 1].squeeze(), psi[..., 1, 0].squeeze()], color=['b', 'g'])
                ax[1].set_title(self.spec_con_method[self.method])
                ax[1].set_xlim(time_extent)
                ax[1].axhline(0, color='black')
                plt.tight_layout(pad=2)
                fig.show()
        else:
            result = con_list[0]
            data = con_list[1]
            times = con_list[2]










if __name__ == "__main__":
    app = QApplication(sys.argv)
    import mne
    data = mne.read_epochs('D:\SEEG_Cognition\data\color_epoch.fif')
    # data = mne.read_epochs('D:\SEEG_Cognition\data\simulated_epochs.fif')
    # data = mne.io.read_epochs_eeglab('D:\SEEG_Cognition\data\yangtingtingFear+甲.set')
    GUI = Con_Win(data=data, subject='曹海娟')
    # GUI = Time_Freq_Win (data=data, subject='曹海娟')
    GUI.show()
    app.exec_()


