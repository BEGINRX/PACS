"""
@File: sub_window.py
@Author: BarryLiu
@Time: 2020/9/21 22:58
@Desc: sub windows
"""

from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QPushButton,\
    QLabel, QGroupBox, QVBoxLayout, QHBoxLayout, QFormLayout, \
    QInputDialog, QLineEdit, QApplication, QCheckBox, QScrollArea, QWidget, \
    QMessageBox, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QDoubleValidator
import sys


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

        self.setFixedWidth(400)
        self.setMinimumHeight(100)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.create_center_widget()
        self.set_font()
        self.create_labels()
        self.create_line_edit()
        self.create_button()
        self.create_layout()
        self.set_style()


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
            self.line_edit_layout.addRow(self.event_name_edit_group[i],
                                         self.event_id_edit_group[i])

        self.layout_0 = QVBoxLayout()
        self.layout_0.addLayout(self.label_layout)
        self.layout_0.addLayout(self.line_edit_layout)
        self.widget = QWidget()
        self.widget.setLayout(self.layout_0)
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidget(self.widget)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea_layout = QVBoxLayout()
        self.scrollarea_layout.addWidget(self.scrollarea)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.scrollarea_layout)
        self.main_layout.addLayout(self.button_layout)

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


class Choose_Time(QMainWindow):

    time_signal= pyqtSignal(list)

    def __init__(self, end_time=None):

        super(Choose_Time, self).__init__()
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



class Choose_Channel(QMainWindow):

    chan_signal = pyqtSignal(list)

    def __init__(self, channel_name=None):

        super(Choose_Channel, self).__init__()
        self.channel_number = len(channel_name)
        self.channel_name = channel_name
        self.channel_check_box = []
        self.channel_new = []
        self.init_ui()



    def init_ui(self):
        self.setFixedSize(1650, 350)
        # self.setFixedHeight(350)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_button()
        self.create_check_box()
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
        self.center_widget.setFont(self.font)


    def create_button(self):

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def ok_func(self):

        self.chan_signal.emit(self.channel_new)


    def create_check_box(self):

        channel_check_box = {}
        for i in range(self.channel_number):
            channel_check_box[i] = QCheckBox(self.channel_name[i])
            channel_check_box[i].setChecked(True)
            channel_check_box[i].stateChanged.connect(lambda _, chan=channel_check_box[i]: self.change_channel(channel_check_box = chan))
            self.channel_check_box.append(channel_check_box[i])


    def change_channel(self, channel_check_box):

        if not channel_check_box.isChecked():
            self.channel_new.append(channel_check_box.text())
            self.channel_new = list(set(self.channel_new))
            print(self.channel_new)
        elif channel_check_box.isChecked():
            self.channel_new.remove(channel_check_box.text())
            print(self.channel_new)



    def create_layout(self):

        layout = []
        layout_num = int(self.channel_number/ 8)
        layout_num_2 = self.channel_number % 8
        flag = 0
        for i in range(layout_num):
            checkbox_layout = QHBoxLayout()
            for j in range(8):
                checkbox_layout.addWidget(self.channel_check_box[j + flag])
            layout.append(checkbox_layout)
            flag += 8
        checkbox_layout_2 = QHBoxLayout()
        for i in range(self.channel_number - layout_num_2, self.channel_number):
            checkbox_layout_2.addWidget(self.channel_check_box[i], stretch=1)
        checkbox_layout_2.addSpacing(198.5 * (8 - layout_num_2))
        layout.append(checkbox_layout_2)

        channel_layout = QVBoxLayout()
        for i in range(len(layout)):
            channel_layout.addLayout(layout[i])

        self.channel_group_box = QGroupBox()
        self.channel_group_box.setLayout(channel_layout)
        self.scrollbar = QScrollArea()
        self.scrollbar.setWidget(self.channel_group_box)
        self.scrollbar.setWidgetResizable(True)
        scrollbar_layout = QVBoxLayout()
        scrollbar_layout.addWidget(self.scrollbar)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(scrollbar_layout)
        main_layout.addLayout(button_layout)

        self.center_widget.setLayout(main_layout)


    def set_style(self):
        pass



class Choose_Event(QMainWindow):
    
    event_signal = pyqtSignal(list)

    def __init__(self, event=None):
        
        super(Choose_Event, self).__init__()



class Select_Data(QMainWindow):

    time_signal = pyqtSignal(list)
    chan_signal = pyqtSignal(list)
    event_signal = pyqtSignal(list)

    def __init__(self, data_mode=None, end_time=None, channel_name=None, event_id=None):
        super(Select_Data, self).__init__()
        self.end_time = end_time
        self.channel_name = channel_name
        self.event_id = event_id
        self.chan = []
        self.time = []
        self.event = []
        self.data_mode = data_mode

        self.init_ui()

    def init_ui(self):
        self.setFixedSize(300,200)
        self.setWindowModality(Qt.ApplicationModal)
        self.center()
        self.set_font()
        self.create_center_widget()
        self.create_button()
        self.create_layout()
        self.set_style()


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


    def create_button(self):

        self.time_button = QPushButton(self)
        self.time_button.setText('Time Range')
        self.time_button.clicked.connect(self.choose_time)
        if self.data_mode == 'epoch':
            self.time_button.setEnabled(False)
        self.channel_button = QPushButton(self)
        self.channel_button.setText('Channel Range')
        self.channel_button.clicked.connect(self.choose_channel)
        self.event_button = QPushButton(self)
        self.event_button.setText('Event Range')
        self.event_button.clicked.connect(self.choose_event)

        self.ok_button = QPushButton(self)
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.ok_func)
        self.ok_button.clicked.connect(self.close)
        self.cancel_button = QPushButton(self)
        self.cancel_button.setText('Cancel')
        self.cancel_button.clicked.connect(self.close)


    def create_layout(self):

        button_layout_0 = QVBoxLayout()
        button_layout_0.addWidget(self.time_button)
        button_layout_0.addWidget(self.channel_button)
        button_layout_0.addWidget(self.event_button)

        button_layout_1 = QHBoxLayout()
        button_layout_1.addStretch(1)
        button_layout_1.addStretch(1)
        button_layout_1.addWidget(self.ok_button)
        button_layout_1.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout_0)
        main_layout.addLayout(button_layout_1)

        self.center_widget.setLayout(main_layout)


    def choose_time(self):
        '''choose time window'''
        self.choose_time_window = Choose_Time(self.end_time)
        self.choose_time_window.time_signal.connect(self.get_time)
        self.choose_time_window.show()


    def get_time(self, time):
        '''get time points chose'''
        self.time = time
        print('select data window', self.time)


    def choose_channel(self):
        '''choose channel window'''
        self.choose_channel_window = Choose_Channel(self.channel_name)
        self.choose_channel_window.chan_signal.connect(self.get_del_channel)
        self.choose_channel_window.show()


    def get_del_channel(self, channel):
        '''get delete channel'''
        self.chan = channel


    def choose_event(self):
        '''choose event window'''
        self.choose_event_window = Choose_Event(self.event_id)
        self.choose_event_window.show()


    def get_event(self, event):
        '''get event chose'''
        self.event = event


    def ok_func(self):
        '''emit the signal'''
        if self.time:
            self.time_signal.emit(self.time)
        elif self.chan:
            self.chan_signal.emit(self.chan)
        elif self.event:
            self.event_signal.emit(self.event)


    def set_style(self):
        pass



class Epoch_Time(QMainWindow):

    time_signal = pyqtSignal(float, float)

    def __init__(self):

        super(Epoch_Time, self).__init__()
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

        self.tmin_label = QLabel('tmin (sec)')
        self.tmax_label = QLabel('tmax(sec)')


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

        self.setStyleSheet('''QLabel{color:black; font: bold 20px Arial}''')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chan = sorted(['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4',
            'P3', 'P4', 'O1', 'O2', 'F7', 'F8',
            'T7', 'T8', 'P7', 'P8', 'Fz', 'Cz',
            'Pz', 'IO', 'FC1', 'FC2', 'CP1', 'CP2',
            'FC5', 'FC6', 'CP5', 'CP6', 'FT9', 'FT10',
            'TP9', 'TP10', 'F1', 'F2', 'C1', 'C2', 'P1',
            'P2', 'AF3', 'AF4', 'FC3', 'FC4', 'CP3', 'CP4',
            'PO3', 'PO4', 'F5', 'F6', 'C5', 'C6', 'P5', 'P6',
            'AF7', 'AF8', 'FT7', 'FT8', 'TP7', 'TP8', 'PO7',
            'PO8', 'Fpz', 'CPz'])
    # GUI = Select_Data(end_time=9000)
    # GUI = Event_Window()
    GUI = Epoch_Time()
    GUI.show()
    app.exec_()





