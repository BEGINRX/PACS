"""
@File: sub_window.py
@Author: BarryLiu
@Time: 2020/9/21 22:58
@Desc: sub windows
"""
import numpy as np
import sys
import traceback
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
    from gui.my_thread import Cal_Spec_Con
except:
    from re_ref import get_chan_group
    from my_func import new_layout
    from my_thread import Calculate_Power, Calculate_PSD, Cal_Spec_Con

def show_error(error):
    print('*********************************************************************')
    print('Error is: ')
    traceback.print_exc()
    print('*********************************************************************')



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
        self.setMinimumHeight(950)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_widget()
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
        self.setFixedSize(940,320)
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
        self.center_widget.setProperty('group', 'center')


    def create_widget(self):
        self.data_box = QGroupBox('Data Information')
        self.data_box.setProperty('group', 'box')
        self.name_label = QLabel(self.subject)
        self.name_label.setProperty('group', 'label_00')
        self.name_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.name_label.setFixedWidth(700)
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

        self.pic_label = QLabel()
        pixmap = QPixmap("../image/tf.png").scaled(QSize(130, 130), Qt.KeepAspectRatioByExpanding)
        # pixmap = QPixmap("image/connectivity_use.png").scaled(QSize(150, 150), Qt.KeepAspectRatioByExpanding)
        self.pic_label.resize(150, 150)
        self.pic_label.setPixmap(pixmap)
        self.pic_label.setAlignment(Qt.AlignCenter)

        self.tf_label = QLabel('Time Frequency Analysis')
        self.tf_label.setProperty('group', 'label_2')
        self.evoke_joint_btn = QPushButton(self)
        self.evoke_joint_btn.setText('Evoke Joint')
        self.evoke_joint_btn.setFixedSize(200, 28)
        self.evoke_joint_btn.clicked.connect(self.evoke_joint)
        self.evoke_cmp_btn = QPushButton(self)
        self.evoke_cmp_btn.setText('Compare Evokes')
        self.evoke_cmp_btn.setFixedSize(200, 28)
        self.evoke_cmp_btn.clicked.connect(self.evoke_cmp)
        self.erp_btn = QPushButton(self)
        self.erp_btn.setText('Channel(s) Evoke')
        self.erp_btn.setFixedSize(220, 28)
        self.erp_btn.clicked.connect(self.evoke)
        self.erp_topo_btn = QPushButton(self)
        self.erp_topo_btn.setText('ERP topomap')
        self.erp_topo_btn.setFixedSize(180, 28)
        self.erp_topo_btn.clicked.connect(self.erp_topo)
        self.tfr_btn = QPushButton(self)
        self.tfr_btn.setText('Time-Frequency Response')
        self.tfr_btn.setFixedSize(220, 28)
        self.tfr_btn.clicked.connect(self.tfr)
        self.tfr_topo_btn = QPushButton(self)
        self.tfr_topo_btn.setText('TFR topomap')
        self.tfr_topo_btn.setFixedSize(180, 28)
        self.tfr_topo_btn.clicked.connect(self.tfr_topo)
        self.psd_btn = QPushButton(self)
        self.psd_btn.setText('Power Spectral Density')
        self.psd_btn.setFixedSize(210, 28)
        self.psd_btn.clicked.connect(self.psd)
        self.csd_btn = QPushButton(self)
        self.csd_btn.setText('Cross-Spectral Density')
        self.csd_btn.setFixedSize(210, 28)
        self.csd_btn.clicked.connect(self.csd)
        self.image_plot_btn = QPushButton(self)
        self.image_plot_btn.setText('ERP Image')
        self.image_plot_btn.setFixedSize(200, 28)
        self.image_plot_btn.clicked.connect(self.image_map)
        self.erpim_topo_btn = QPushButton(self)
        self.erpim_topo_btn.setText('ERP Image topograph')
        self.erpim_topo_btn.setFixedSize(220, 28)
        self.erpim_topo_btn.clicked.connect(self.erpim_topo)


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

        info_layout = QHBoxLayout()
        info_layout.addWidget(self.data_box, stretch=1)
        info_layout.addWidget(self.pic_label, stretch=1000)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.evoke_joint_btn)
        layout_4.addWidget(self.erp_btn)
        layout_4.addWidget(self.erp_topo_btn)
        layout_4.addWidget(self.psd_btn)
        layout_4.addStretch(100)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.evoke_cmp_btn)
        layout_5.addWidget(self.tfr_btn)
        layout_5.addWidget(self.tfr_topo_btn)
        layout_5.addWidget(self.csd_btn)
        layout_5.addStretch(100)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.image_plot_btn)
        layout_6.addWidget(self.erpim_topo_btn)
        # layout_6.addWidget(self.tfr_topo_btn)
        # layout_6.addWidget(self.csd_btn)
        layout_6.addStretch(100)

        main_layout = QVBoxLayout()
        main_layout.addLayout(info_layout)
        main_layout.addWidget(self.tf_label)
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
            mne.viz.plot_epochs_image(data[event].pick_channels(ch_name), combine='mean', picks='seeg')


    def erpim_topo(self):
        self.event = self.data.event_id
        event = list(self.event.keys())
        self.event_win = ERP_Image_Topo(event=event)
        self.event_win.erp_signal.connect(self.plot_erpim_topo)
        self.event_win.show()

    def plot_erpim_topo(self, event, value):
        if not value[0] and not value[1]:
            mne.viz.plot_topo_image_epochs(self.data[event])
        else:
            mne.viz.plot_topo_image_epochs(self.data[event],
                                           vmin=value[0], vmax=value[1])


    def evoke_joint(self):
        self.event = self.data.event_id
        event = list(self.event.keys())
        self.erp_win = Evoke_Chan_WiN(event=event, chan = self.data.ch_names)
        self.erp_win.erp_signal.connect(self.plot_evoke_joint)
        self.erp_win.show()

    def plot_evoke_joint(self, event, ch_name):
        import matplotlib.pyplot as plt
        if ch_name == None:
            pass
        else:
            try:
                if event:
                    mne.viz.plot_evoked_joint(self.data[event].average().pick_channels(ch_name), picks='seeg')
            except Exception as error:
                if error.args[0] == "ValueError: meg value must be one of " \
                                    "['grad', 'mag', 'planar1', 'planar2'] or bool, not seeg":
                    pass


    def evoke(self):
        self.event = self.data.event_id
        event = list(self.event.keys())
        self.erp_win = Evoke_Chan_WiN(event=event, chan = self.data.ch_names)
        self.erp_win.erp_signal.connect(self.plot_evoke)
        self.erp_win.show()

    def plot_evoke(self, event, ch_name):
        if ch_name == None:
            pass
        else:
            if len(ch_name) == 1:
                evoke = self.data[event].average().pick_types(seeg=True).pick_channels(ch_name)
                mne.viz.plot_evoked(evoke, titles='Evoke: ' + str(ch_name), picks='seeg', spatial_colors=True)
            else:
                evoke = self.data[event].average().pick_types(seeg=True).pick_channels(ch_name)
                mne.viz.plot_evoked(evoke, picks='seeg', spatial_colors=True)


    def evoke_cmp(self):
        event_id = self.data.event_id
        event = list(event_id.keys())
        self.evoke_cmp_win = Evoke_Chan_WiN(event, self.data.ch_names)
        self.evoke_cmp_win.erp_signal.connect(self.plot_evoke_cmp)
        self.evoke_cmp_win.show()

    def plot_evoke_cmp(self, event_id, ch_name):
        if ch_name == None:
            pass
        else:
            self.event = self.data.event_id
            event_id = list(self.event.keys())
            evokes = [self.data[event].average() for event in event_id]
            [evoke.pick_channels(ch_name) for evoke in evokes]
            combine = 'mean'
            if len(ch_name) == 1:
                mne.viz.plot_compare_evokeds(evokes, picks='seeg', combine=combine, title=str(ch_name))
            else:
                mne.viz.plot_compare_evokeds(evokes, picks='seeg', combine=combine)


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



class Morlet_Con_Pic(QMainWindow):

    def __init__(self, matrix, title, n_times=None, diagonal=True):

        super(Morlet_Con_Pic, self).__init__()
        self.num = 0
        self.diagonal = diagonal
        if isinstance(matrix, np.ndarray):
            self.matrix = matrix
        self.matrix_plot = self.matrix[:, :, self.num]
        if self.diagonal:
            self.matrix_plot += self.matrix_plot.T - np.diag(self.matrix_plot.diagonal())
        self.title = title
        if not n_times:
            self.n_times = np.arange(self.matrix_plot.shape[2])
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
        self.matrix_plot = self.matrix[:, :, self.num]
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

    spec_con_signal = pyqtSignal(dict)

    def __init__(self, event, chan, time, con_method):
        '''
        :param event:
        :param method: which method to calculate spectral connectivity
        '''
        super(Multitaper_Con_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.con_method = con_method
        self.time = time
        self.para = dict()
        self.plot_2d = False
        self.plot_3d = False


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

        self.bandwidth_label = QLabel('Band Width(Hz) ')
        self.bandwidth_label.setFixedWidth(135)
        self.bandwidth_edit = QLineEdit()
        self.bandwidth_edit.setAlignment(Qt.AlignCenter)
        self.bandwidth_edit.setFixedWidth(100)
        self.bandwidth_edit.setValidator(QDoubleValidator())

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

        self.adapt_cb = QCheckBox('Use Adaptive weights')
        self.adapt_cb.stateChanged.connect(self.use_adaptive_func)
        self.plot_2d_cb = QCheckBox('2D Viewer')
        self.plot_2d_cb.stateChanged.connect(self.use_2d)
        self.plot_all_cb = QCheckBox('Using all channels')
        self.plot_all_cb.stateChanged.connect(self.all_chan)
        self.plot_3d_cb = QCheckBox('3D Viewer')
        self.plot_3d_cb.stateChanged.connect(self.use_3d)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.setProperty('group', 'bottom')
        self.ok_button.clicked.connect(self.ok_func)


    def chanx(self):
        self.chanx_win = Select_Chan(self.chan)
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
        elif self.get_chan == 'y':
            self.chany_get = chan


    def all_chan(self):
        if self.plot_all_cb.isChecked():
            self.all_plot = True
            self.plot_2d_cb.setChecked(True)
            self.plot_2d_cb.setEnabled(False)
            self.plot_2d = True
        else:
            self.all_plot = False
            self.plot_2d_cb.setChecked(False)
            self.plot_2d_cb.setEnabled(True)
            self.plot_2d = False


    def use_2d(self):
        if self.plot_2d_cb.isChecked():
            self.plot_2d = True
            self.plot_3d_cb.setEnabled(False)
            self.plot_3d = False
        else:
            self.plot_2d = False
            self.plot_3d_cb.setEnabled(True)


    def use_3d(self):
        if self.plot_3d_cb.isChecked():
            self.plot_3d = True
            self.plot_2d_cb.setEnabled(False)
            self.plot_2d = False
        else:
            self.plot_3d = False
            self.plot_2d_cb.setEnabled(True)


    def use_adaptive_func(self):
        self.use_adaptive = True


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
        layout_5.addWidget(self.adapt_cb)
        layout_5.addWidget(self.plot_2d_cb)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.plot_all_cb)
        layout_6.addStretch(100)
        layout_6.addWidget(self.plot_3d_cb)

        layout_7 = QHBoxLayout()
        layout_7.addWidget(self.chanx_label)
        layout_7.addStretch(100)
        layout_7.addWidget(self.chanx_btn)
        layout_8 = QHBoxLayout()
        layout_8.addWidget(self.chany_label)
        layout_8.addStretch(100)
        layout_8.addWidget(self.chany_btn)

        button_layout = QHBoxLayout()
        button_layout.addStretch(100)
        button_layout.addWidget(self.ok_button)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_20)
        main_layout.addLayout(layout_30)
        main_layout.addWidget(self.des_label)
        main_layout.addLayout(layout_7)
        main_layout.addLayout(layout_8)
        main_layout.addLayout(layout_4)
        main_layout.addLayout(layout_5)
        main_layout.addLayout(layout_6)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def ok_func(self):
        self.event_chosen = self.event_combo.currentText()
        self.para['event'] = self.event
        if self.fmin_edit.text() and self.fmax_edit.text():
            self.fmin = float(self.fmin_edit.text())
            self.fmax = float(self.fmax_edit.text())
            self.para['freq'] = [self.fmin, self.fmax]
        else:
            self.close()
        if self.tmin_edit.text() and self.tmax_edit.text():
            self.tmin = float(self.tmin_edit.text())
            self.tmax = float(self.tmax_edit.text())
            self.para['time'] = [self.tmin, self.tmax]
        else:
            self.close()
        if self.bandwidth_edit.text():
            self.bandwidth = float(self.bandwidth_edit.text())
            self.para['bandwidth'] = self.bandwidth
        else:
            self.close()
        self.para['adaptive'] = self.use_adaptive
        self.para['plot_mode'] = [self.all_plot, self.plot_2d, self.plot_3d]
        if not self.all_plot:
            self.para['chan'] = [self.chanx_get, self.chany_get]
        self.spec_con_signal.emit(self.para)
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton[group='bottom']{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Morlet_Con_Win(QMainWindow):

    def __init__(self, event, chan, con_method):
        super(Morlet_Con_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.con_method = con_method
        self.init_ui()

    def init_ui(self):
        self.setMinimumWidth(400)
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
        self.name_label = QLabel('Morlet Parameters')
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setProperty('group', 'name')

        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.line_label = QLabel(' - ', self)
        self.line_label.setFixedWidth(20)

        self.choose_chan_label = QLabel('Choose sub_channels to calculate, otherwise all')
        self.choose_chan_label.setFixedWidth(330)
        self.choose_chan_label.setWordWrap(True)

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())

        self.choose_chanx_btn = QPushButton(self)
        self.choose_chanx_btn.setText('Channel x')
        self.choose_chanx_btn.clicked.connect(self.choose_x)
        self.choose_chany_btn = QPushButton(self)
        self.choose_chany_btn.setText('Channel y')
        self.choose_chany_btn.clicked.connect(self.choose_y)

        self.morlet_btn = QPushButton(self)
        self.morlet_btn.setText('Use Morlet')

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.setProperty('group', 'bottom')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setProperty('group', 'bottom')

    def set_style(self):
        pass



class Fourier_Con_Win(QMainWindow):

    spec_con_signal = pyqtSignal(str, str, str, list)

    def __init__(self, event, chan, con_method):
        '''
        :param event:
        :param method: which method to calculate spectral connectivity
        '''
        super(Fourier_Con_Win, self).__init__()
        self.event = event
        self.chan = chan
        self.con_method = con_method
        self.mode = None
        self.plot_mode = 'normal'

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
        self.method_combo.addItems(['Fourier',
                                    'Multitaper'])

        self.event_combo = QComboBox(self)
        self.event_combo.addItems(self.event)

        self.matrix_check_box = QCheckBox('Plot in matrix')
        self.matrix_check_box.stateChanged.connect(self.plot_mode_change)
        self.method_label = QLabel('Method', self)
        self.method_label.setFixedWidth(100)
        self.event_label = QLabel('Event', self)
        self.event_label.setFixedWidth(100)
        self.freq_label = QLabel('Frequency', self)
        self.freq_label.setFixedWidth(100)
        self.line_label = QLabel(' - ', self)
        self.line_label.setFixedWidth(20)

        self.choose_chan_label = QLabel('Choose sub_channels to calculate, otherwise all')
        self.choose_chan_label.setFixedWidth(330)
        self.choose_chan_label.setWordWrap(True)

        self.fmin_edit = QLineEdit()
        self.fmin_edit.setAlignment(Qt.AlignCenter)
        self.fmin_edit.setFixedWidth(93)
        self.fmin_edit.setValidator(QDoubleValidator())

        self.fmax_edit = QLineEdit()
        self.fmax_edit.setAlignment(Qt.AlignCenter)
        self.fmax_edit.setFixedWidth(93)
        self.fmax_edit.setValidator(QDoubleValidator())

        self.choose_chanx_btn = QPushButton(self)
        self.choose_chanx_btn.setText('Channel x')
        self.choose_chanx_btn.clicked.connect(self.choose_x)
        self.choose_chany_btn = QPushButton(self)
        self.choose_chany_btn.setText('Channel y')
        self.choose_chany_btn.clicked.connect(self.choose_y)

        self.morlet_btn = QPushButton(self)
        self.morlet_btn.setText('Use Morlet')

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.setProperty('group', 'bottom')
        self.ok_button.clicked.connect(self.ok_func)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)
        self.cancel_button.setProperty('group', 'bottom')


    def plot_mode_change(self):
        if self.matrix_check_box.isChecked():
            self.plot_mode = 'matrix'


    def choose_x(self):
        pass


    def choose_y(self):
        pass


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

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.choose_chanx_btn)
        layout_4.addWidget(self.choose_chany_btn)


        button_layout = QHBoxLayout()
        button_layout.addWidget(self.morlet_btn)
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)


        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_3)
        main_layout.addWidget(self.choose_chan_label)
        main_layout.addLayout(layout_4)
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
            self.spec_con_signal.emit(self.method, self.mode, self.event_chosen,
                                 [self.fmin, self.fmax])
        self.close()


    def set_style(self):
        self.setStyleSheet('''
                        QPushButton[group='bottom']{font: 10pt Times New Roman}
                        QListWidget{background-color:white ;font: 13pt Times New Roman}
                        QListWidget:item{height:28px}
                        QGroupBox{background-color:rgb(242,242,242)}
        ''')



class Freq_Con_Method_Win(QMainWindow):

    con_signal = pyqtSignal(para)

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
        self.fft_btn = QPushButton(self)
        self.fft_btn.setText('Fourier')
        self.fft_btn.clicked.connect(self.fft_win)
        self.fft_btn.setFixedWidth(120)


    def create_layout(self):
        layout_0 = QVBoxLayout()
        layout_0.addWidget(self.taper_btn)
        layout_0.addWidget(self.morlet_btn)
        layout_0.addWidget(self.fft_btn)
        self.center_widget.setLayout(layout_0)


    def taper_win(self):
        self.multi_taper_win = Multitaper_Con_Win(event=self.event, chan=self.chan,
                                                  time=self.time, con_method=self.con_method)
        self.multi_taper_win.spec_con_signal.connect(self.get_para)
        self.multi_taper_win.show()
        self.close()

    def morlet_win(self):
        self.morlet_win = Morlet_Con_Win()
        self.morlet_win.spec_con_signal.connect(self.get_para)
        self.morlet_win.show()
        self.close()

    def fft_win(self):
        self.fft_win = Fourier_Con_Win()
        self.fft_win.spec_con_signal.connect(self.get_para)
        self.fft_win.show()
        self.close()

    def get_para(self, para):
        self.para = para
        self.con_signal.emit(self.para)


    def set_style(self):
        pass



class Time_Con_Win(QMainWindow):

    para_signal = pyqtSignal(dict)

    def __init__(self, data, event, con_method, multi=True):

        super(Time_Con_Win, self).__init__()
        self.data = data
        self.event = event
        self.chan = self.data.ch_names
        self.multi = multi
        self.con_method = con_method
        self.all_plot = False
        self.chanx_get = None
        self.chany_get = None
        self.plot_2d = False
        self.plot_3d = False

        self.init_ui()

    def init_ui(self):

        self.setFixedWidth(280)
        self.setFixedHeight(340)
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
        self.event_cb = QComboBox(self)
        self.event_cb.addItems(self.event)
        self.event_cb.setFixedWidth(110)

        self.des_label = QLabel('Select the Channels you want to use', self)
        self.des_label.setWordWrap(True)
        # self.des_label.setFixedWidth(100)
        self.chanx_label = QLabel('Channel X', self)
        self.chanx_label.setFixedWidth(90)
        self.chanx_btn = QPushButton('···')
        self.chanx_btn.clicked.connect(self.chanx)
        self.chanx_btn.setFixedWidth(80)
        self.chany_label = QLabel('Channel Y', self)
        self.chany_label.setFixedWidth(90)
        self.chany_btn = QPushButton('···')
        self.chany_btn.clicked.connect(self.chany)
        self.chany_btn.setFixedWidth(80)
        self.base_label = QLabel('Baseline', self)
        self.base_label.setFixedWidth(90)
        self.line_label = QLabel(' - ', self)
        self.line_label.setFixedWidth(20)

        self.tmin_edit = QLineEdit()
        self.tmin_edit.setAlignment(Qt.AlignCenter)
        self.tmin_edit.setFixedWidth(65)
        self.tmin_edit.setText(str(self.data.tmin))
        self.tmin_edit.setValidator(QDoubleValidator())
        self.tmax_edit = QLineEdit()
        self.tmax_edit.setAlignment(Qt.AlignCenter)
        self.tmax_edit.setFixedWidth(65)
        self.tmax_edit.setText('0')
        self.tmax_edit.setValidator(QDoubleValidator())

        self.plot_all_cb = QCheckBox('Using all channels')
        self.plot_all_cb.stateChanged.connect(self.all_chan)
        self.plot_2d_cb = QCheckBox('2D Viewer')
        self.plot_2d_cb.stateChanged.connect(self.use_2d)
        self.plot_3d_cb = QCheckBox('3D Viewer')
        self.plot_3d_cb.stateChanged.connect(self.use_3d)
        if self.con_method == 'cross correlation':
            self.plot_all_cb.setEnabled(False)
            self.plot_2d_cb.setEnabled(False)
            self.plot_3d_cb.setEnabled(False)


        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.setFixedWidth(60)
        self.ok_button.clicked.connect(self.ok_func)


    def create_layout(self):
        layout_0 = QHBoxLayout()
        layout_0.addWidget(self.event_label)
        layout_0.addStretch(10)
        layout_0.addWidget(self.event_cb)

        layout_1 = QHBoxLayout()
        layout_1.addWidget(self.chanx_label)
        layout_1.addStretch(10)
        layout_1.addWidget(self.chanx_btn)

        layout_2 = QHBoxLayout()
        layout_2.addWidget(self.chany_label)
        layout_2.addStretch(10)
        layout_2.addWidget(self.chany_btn)

        layout_3 = QHBoxLayout()
        layout_3.addWidget(self.plot_2d_cb)
        layout_3.addWidget(self.plot_3d_cb)

        layout_4 = QHBoxLayout()
        layout_4.addWidget(self.tmin_edit)
        layout_4.addWidget(self.line_label)
        layout_4.addWidget(self.tmax_edit)

        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.base_label)
        layout_5.addLayout(layout_4)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(100)
        btn_layout.addWidget(self.ok_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout_0)
        main_layout.addWidget(self.des_label)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_2)
        main_layout.addLayout(layout_5)
        main_layout.addWidget(self.plot_all_cb)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(btn_layout)

        self.center_widget.setLayout(main_layout)


    def chanx(self):
        self.chanx_win = Select_Chan(self.chan, multi=self.multi)
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
        elif self.get_chan == 'y':
            self.chany_get = chan


    def all_chan(self):
        if self.plot_all_cb.isChecked():
            self.all_plot = True
        else:
            self.all_plot = False


    def use_2d(self):
        if self.plot_2d_cb.isChecked():
            self.plot_2d = True
        else:
            self.plot_2d = False


    def use_3d(self):
        if self.plot_3d_cb.isChecked():
            self.plot_3d = True
        else:
            self.plot_3d = False


    def ok_func(self):
        try:
            self.para = dict()
            self.para['event'] = self.event_cb.currentText()
            self.para['chan'] = [self.chanx_get, self.chany_get]
            self.para['plot_mode'] = [self.all_plot, self.plot_2d, self.plot_3d]
            print(self.tmin_edit.text())
            if not self.tmin_edit.text():
                self.tmin = float(self.tmin_edit.text())
                try:
                    self.tmax = float(self.tmax_edit.text())
                except:
                    self.tmax = 0
                print(self.tmin, self.tmax)
            else:
                self.tmin = None
                self.tmax = None
            self.para['baseline'] = [self.tmin, self.tmax]
            self.para_signal.emit(self.para)
            self.close()
        except Exception:
            traceback.print_exc()

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

        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('Connectivity Analysis')
        self.setFixedHeight(590)
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
        self.name_label.setFixedWidth(700)
        self.samplingr_label = QLabel('Sampling Rate')
        self.samplingr_label.setProperty('group', 'label_0')
        self.samplingr_label.setAlignment(Qt.AlignLeft)
        self.samplingr_label.setFixedWidth(120)
        self.samplingr_con_label = QLabel(str(round(self.data.info['sfreq'])))
        self.samplingr_con_label.setProperty('group', 'label')
        self.samplingr_con_label.setAlignment(Qt.AlignHCenter)
        self.samplingr_con_label.setFixedWidth(60)
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

        self.pic_label = QLabel()
        pixmap = QPixmap("../image/connectivity_use.png").scaled(QSize(150, 150), Qt.KeepAspectRatioByExpanding)
        # pixmap = QPixmap("image/connectivity_use.png").scaled(QSize(150, 150), Qt.KeepAspectRatioByExpanding)
        self.pic_label.resize(150, 150)
        self.pic_label.setPixmap(pixmap)
        self.pic_label.setAlignment(Qt.AlignCenter)

        self.connect_box = QGroupBox('Connectivity Measures')
        self.connect_box.setProperty('group', 'box')

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Time Domain                                                             #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        self.time_box = QLabel('Time Domain')
        self.time_box.setProperty('group', 'label_11')
        self.func0_box = QGroupBox('Functional Connectivity')
        self.func0_box.setProperty('group', 'box_12')
        self.direct0_box = QGroupBox('Directional Connectivity')
        self.direct0_box.setProperty('group', 'box_12')
        # functional
        self.pearson_corre_btn = QPushButton(self)
        self.pearson_corre_btn.setText('Pearson Correlation')
        self.pearson_corre_btn.setFixedSize(200, 28)
        self.pearson_corre_btn.clicked.connect(self.use_pearson)
        self.enve_coore_btn = QPushButton(self)
        self.enve_coore_btn.setText('Envelope Correlation')
        self.enve_coore_btn.setFixedSize(200, 28)
        self.enve_coore_btn.clicked.connect(self.use_enve)
        self.mutual_info_btn = QPushButton(self)
        self.mutual_info_btn.setText('Mutual Information')
        self.mutual_info_btn.setFixedSize(200, 28)
        self.mutual_info_btn.clicked.connect(self.use_mutul_info)
        # directional
        self.cross_corre_btn = QPushButton(self)
        self.cross_corre_btn.setText('Cross-Correlation')
        self.cross_corre_btn.setFixedSize(200, 28)
        self.cross_corre_btn.clicked.connect(self.use_cross_corre)
        self.granger_causa0_btn = QPushButton(self)
        self.granger_causa0_btn.setText('Granger Causality')
        self.granger_causa0_btn.setFixedSize(200, 28)
        self.granger_causa0_btn.clicked.connect(self.use_gc)
        self.trans_entropy_btn = QPushButton(self)
        self.trans_entropy_btn.setText('Transfer Entropy')
        self.trans_entropy_btn.setFixedSize(200, 28)
        self.trans_entropy_btn.clicked.connect(self.use_te)


        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Frequency Domain                                                        #
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        #
        self.freq_box = QLabel('Frequency Domain')
        self.freq_box.setProperty('group', 'label')
        self.func1_box = QGroupBox('Functional Connectivity')
        self.func1_box.setProperty('group', 'box_12')
        self.direct1_box = QGroupBox('Directional Connectivity')
        self.direct1_box.setProperty('group', 'box_12')
        # functional
        self.coher_btn = QPushButton(self)
        self.coher_btn.setText('Coherence')
        self.coher_btn.setFixedSize(200, 28)
        self.coher_btn.clicked.connect(self.use_coherence)
        self.plv_btn = QPushButton(self)
        self.plv_btn.setText('Phase-Locking Value')
        self.plv_btn.setFixedSize(200, 28)
        self.plv_btn.clicked.connect(self.use_plv)
        self.pli_btn = QPushButton(self)
        self.pli_btn.setText('Phase-Lag Index')
        self.pli_btn.setFixedSize(200, 28)
        self.pli_btn.clicked.connect(self.use_pli)
        self.imag_coher_btn = QPushButton(self)
        self.imag_coher_btn.setText('Imaginary Coherence')
        self.imag_coher_btn.setFixedSize(240, 28)
        self.imag_coher_btn.clicked.connect(self.use_imaginary_coh)
        self.ciplv_btn = QPushButton(self)
        self.ciplv_btn.setText('Corrected Imaginary PLV')
        self.ciplv_btn.setFixedSize(240, 28)
        self.ciplv_btn.clicked.connect(self.use_ciplv)
        self.ppc_btn = QPushButton(self)
        self.ppc_btn.setText('Pairwise Phase Consistency')
        self.ppc_btn.setFixedSize(240, 28)
        self.ppc_btn.clicked.connect(self.use_ppc)
        self.wpli_btn = QPushButton(self)
        self.wpli_btn.setText('Weighted PLI')
        self.wpli_btn.setFixedSize(230, 28)
        self.wpli_btn.clicked.connect(self.use_wpli)
        self.uspli_btn = QPushButton(self)
        self.uspli_btn.setText('Unbiased Squared PLI')
        self.uspli_btn.setFixedSize(230, 28)
        self.uspli_btn.clicked.connect(self.use_unbiased_pli)
        self.dswpli_btn = QPushButton(self)
        self.dswpli_btn.setText('Unbiased Squared WPLI')
        self.dswpli_btn.setFixedSize(230, 28)
        self.dswpli_btn.clicked.connect(self.use_debiased_wpli)
        # directional
        self.psi_btn = QPushButton(self)
        self.psi_btn.setText('Phase Slope Index')
        self.psi_btn.setFixedSize(300, 28)
        self.para_granger_btn = QPushButton(self)
        self.para_granger_btn.setText('Parametric Granger Causality')
        self.para_granger_btn.setFixedSize(300, 28)
        self.non_para_granger_btn = QPushButton(self)
        self.non_para_granger_btn.setText('Non-parametric Granger Causality')
        self.non_para_granger_btn.setFixedSize(300, 28)


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

        time_layout_0 = QHBoxLayout()
        time_layout_0.addWidget(self.pearson_corre_btn, stretch=1)
        time_layout_0.addWidget(self.enve_coore_btn, stretch=1)
        time_layout_0.addWidget(self.mutual_info_btn, stretch=1)
        time_layout_0.addStretch(1000)
        self.func0_box.setLayout(time_layout_0)
        time_layout_1 = QHBoxLayout()
        time_layout_1.addWidget(self.cross_corre_btn, stretch=1)
        time_layout_1.addWidget(self.granger_causa0_btn, stretch=1)
        time_layout_1.addWidget(self.trans_entropy_btn)
        time_layout_1.addStretch(1000)
        self.direct0_box.setLayout(time_layout_1)
        layout_4 = QVBoxLayout()
        layout_4.addWidget(self.func0_box)
        layout_4.addWidget(self.direct0_box)


        freq_layout_0 = QVBoxLayout()
        freq_layout_0.addWidget(self.coher_btn)
        freq_layout_0.addWidget(self.pli_btn)
        freq_layout_0.addWidget(self.plv_btn)
        freq_layout_1 = QVBoxLayout()
        freq_layout_1.addWidget(self.imag_coher_btn)
        freq_layout_1.addWidget(self.ciplv_btn)
        freq_layout_1.addWidget(self.ppc_btn)
        freq_layout_2 = QVBoxLayout()
        freq_layout_2.addWidget(self.wpli_btn)
        freq_layout_2.addWidget(self.uspli_btn)
        freq_layout_2.addWidget(self.dswpli_btn)
        freq_layout_3 = QHBoxLayout()
        freq_layout_3.addLayout(freq_layout_0)
        freq_layout_3.addLayout(freq_layout_1)
        freq_layout_3.addLayout(freq_layout_2)
        self.func1_box.setLayout(freq_layout_3)
        freq_layout_4 = QVBoxLayout()
        freq_layout_4.addWidget(self.psi_btn)
        freq_layout_4.addWidget(self.para_granger_btn)
        freq_layout_4.addWidget(self.non_para_granger_btn)
        self.direct1_box.setLayout(freq_layout_4)
        layout_5 = QHBoxLayout()
        layout_5.addWidget(self.func1_box)
        layout_5.addWidget(self.direct1_box)

        layout_6 = QHBoxLayout()
        layout_6.addWidget(self.time_box)
        layout_6.addStretch(1000)
        layout_7 = QHBoxLayout()
        layout_7.addWidget(self.freq_box)
        layout_7.addStretch(1000)
        layout_8 = QVBoxLayout()
        layout_8.addLayout(layout_6)
        layout_8.addLayout(layout_4)
        layout_8.addLayout(layout_7)
        layout_8.addLayout(layout_5)

        self.connect_box.setLayout(layout_8)
        layout_9 = QVBoxLayout()
        layout_9.addLayout(info_layout)
        layout_9.addWidget(self.connect_box)
        self.center_widget.setLayout(layout_9)


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
            QWidget[group='center']{background-color: white}
        ''')

    # Connecivity analysis
    #
    # Time domain connecivity
    def show_pbar(self):
        self.pbar = My_Progress()
        self.pbar.show()

    def plot_con(self, para, result, title, ch_namex, ch_namey):
        self.pbar.step = 100
        import matplotlib.pyplot as plt
        if para['plot_mode'][1]:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            image = ax.matshow(result)
            fig.colorbar(image)
            plt.title(title)
            plt.show()
        elif para['plot_mode'][2]:
            pass
        else:
            if self.method == 'cross correlation':
                print('here I am')
                fig, ax = plt.subplots()
                for i in range(result.shape[0]):
                    ax.plot(result[i], label=ch_namey[i])
                ax.legend()
                ax.grid(axis='y', linestyle='-.')
                ax.set_title(title + ': ' + str(ch_namex))
                fig.show()
            else:
                fig, ax = plt.subplots()
                for i in range(len(result)):
                    if len(ch_namey) < 20:
                        ax.plot(result[i], label=ch_namex[i] + '————' + str(ch_namey),
                                marker='o', markerfacecolor='black', markersize=3)
                        ax.legend()
                    else:
                        ax.plot(result[i, :],marker='o', markerfacecolor='black',
                                markersize=3)
                ax.set_title(title)
                fig.show()


    def use_pearson(self):
        self.method = 'pearson'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()


    def use_enve(self):
        self.method = 'envelope'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()


    def use_mutul_info(self):
        self.method = 'mutul information'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()


    def use_cross_corre(self):
        self.method = 'cross correlation'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, multi=False, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()


    def use_gc(self):
        self.method = 'granger causality'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()

    def use_te(self):
        self.method = 'transfer entropy'
        event_id = list(self.data.event_id.keys())
        self.time_con_win = Time_Con_Win(event=event_id, data=self.data, con_method=self.method)
        self.time_con_win.para_signal.connect(self.get_para)
        self.time_con_win.show()

    def get_para(self, para):
        '''
        :param para: dict
                event: str  event
                chan: list  chanx, chany
                plot_mode: list  plot_all, plot_2d, plot_3d
        '''
        from matplotlib import pyplot as plt
        from mne.viz import plot_sensors_connectivity
        try:
            from gui.my_thread import Cal_Time_Con
        except:
            from my_thread import Cal_Time_Con
        self.show_pbar()
        self.para = para
        self.cal_con = Cal_Time_Con(data=self.data, method=self.method, para=para)
        self.cal_con.con_signal.connect(self.plot_time_con)
        self.cal_con.start()


    def plot_time_con(self, con, chanx, chany):
        self.pbar.step = 100
        if self.method == 'pearson':
            self.plot_con(para=self.para, result=con, title='Pearson', ch_namex=chanx, ch_namey=chany)
        elif self.method == 'envelope':
            self.plot_con(para=self.para, result=con, title='Envelope', ch_namex=chanx, ch_namey=chany)
        elif self.method == 'mutual information':
            self.plot_con(para=self.para, result=con, title='Mutual Information', ch_namex=chanx, ch_namey=chany)
        elif self.method == 'cross correlation':
            self.plot_con(para=self.para, result=con, title='Cross Correlation', ch_namex=chanx, ch_namey=chany)
        elif self.method == 'granger causality':
            self.plot_con(para=self.para, result=con, title='Granger Causality', ch_namex=chanx, ch_namey=chany)
        elif self.method == 'transfer entropy':
            self.plot_con(para=self.para, result=con, title='Transfer Entropy', ch_namex=chanx, ch_namey=chany)




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
                                           con_method=self.method)
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
                                           con_method=self.method)
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
                                           con_method=self.method)
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
                                           con_method=self.method)
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
                                           con_method=self.method)
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    # 'pli2_unbiased' : Unbiased estimator of squared PLI
    def use_unbiased_pli(self):
        self.method = 'pli2_unbiased'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method)
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    def use_wpli(self):
        self.method = 'wpli'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method)
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    def use_debiased_wpli(self):
        self.method = 'wpli2_debiased'
        event_id = list(self.data.event_id.keys())
        self.con_win = Freq_Con_Method_Win(event_id, chan=self.data.ch_names,
                                           con_method=self.method)
        self.con_win.con_signal.connect(self.calculate_con)
        self.con_win.show()

    def calculate_con(self, mode, event, freq):
        epoch = self.data[event]
        self.calcu_con = Cal_Spec_Con(epoch, method=self.method, mode=mode, freq=freq)
        self.calcu_con.con_signal.connect(self.plot_spec_con)
        self.calcu_con.start()

    def plot_spec_con(self, con):
        from matplotlib import pyplot as plt
        fig, ax = plt.subplots()
        image = ax.matshow(con[:, :])
        fig.colorbar(image)
        fig.tight_layout()
        plt.show()
        if self.method == 'coh':
            plt.title('Coherence')
        elif self.method == 'imcoh':
            plt.title('Imaginary Coherence')
        elif self.method == 'plv':
            plt.title('Phase-Locking Value (PLV)')
        elif self.method == 'ciplv':
            plt.title('corrected imaginary PLV')
        elif self.method == 'ppc':
            plt.title('Pairwise Phase Consistency (PPC)')
        elif self.method == 'pli':
            plt.title('Phase Lag Index (PLI)')
        elif self.method == 'pli2_unbiased':
            plt.title('Unbiased estimator of squared PLI')
        elif self.method == 'wpli':
            plt.title('Weighted Phase Lag Index (WPLI)')
        elif self.method == 'wpli2_debiased':
            plt.title('Debiased estimator of squared WPLI')













if __name__ == "__main__":
    app = QApplication(sys.argv)

    # GUI = Spec_Con_Win(['blue', 'red'], 'pli')
    # con = np.random.random((30, 40, 10))
    # times = np.arange(10).reshape(10, 1)

    import mne
    data = mne.read_epochs('D:\SEEG_Cognition\data\color_epoch.fif')
    GUI = Con_Win(data=data, subject='曹海娟')
    GUI.show()
    app.exec_()


