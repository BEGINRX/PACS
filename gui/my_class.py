# -*- coding: utf-8 -*-
'''
@File : my_class.py
@Author : BarryLiu
@Time : 2021/1/1 21:15
@Desc :
'''
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mne import BaseEpochs
from mne.io import BaseRaw


class SEEG(object):

    def __init__(self, name=None, data=None, events=None, mode=None):
        super(SEEG, self).__init__()
        self.name = name
        self.data = data
        self.mode = mode
        self.events = events
        self.data_para = dict()



    def get_para(self):
        if self.mode == 'raw':
            self.data_para['epoch_num'] = str(1)
            self.data_para['sfreq'] = str(self.data.info['sfreq'])
            self.data_para['chan_num'] = str(self.data.info['nchan'])
            self.data_para['epoch_start'] = str(self.data._first_time)
            self.data_para['epoch_end'] = str(round(self.data._last_time, 2))
            self.data_para['time_point'] = str(self.data.n_times)
            self.data_para['event_class'] = str(len(set(self.events[:, 2])))
            self.data_para['event_num'] = str(len(self.events))
            self.data_para['data_size'] = str(round(0.5 *(self.data._size /((2 ** 10) ** 2)), 2))
        else:
            self.data_para['epoch_num'] = str(self.events.shape[0])
            self.data_para['sfreq'] = str(self.data.info['sfreq'])
            self.data_para['chan_num'] = str(self.data.info['nchan'])
            self.data_para['epoch_start'] = str(self.data.tmin)
            self.data_para['epoch_end'] = str(self.data.tmax)
            self.data_para['time_point'] = str(len(self.data._raw_times))
            self.data_para['event_class'] = str(len(set(self.events[:, 2])))
            self.data_para['event_num'] = str(len(self.events))
            self.data_para['data_size'] = str(round(0.5 *(self.data._size /((2 ** 10) ** 2)), 2))



class Subject(object):

    def __init__(self, name=None, coord=None, mri=None,
                 b_obj=None, s_obj=None, c_obj=None):

        super(Subject, self).__init__()
        # key in seeg is the name of the data
        self.seeg = dict()
        self.name = name
        self.coord = coord
        self.image = dict()
        self.b_obj = b_obj
        self.s_obj = s_obj
        self.c_obj = c_obj





class Change_Figure(Figure):

    def __init__(self, data, title, *args, **kwargs):

        super(Change_Figure, self).__init__(*args, **kwargs)
        self.ax = self.add_subplot()
        self.data = data
        if isinstance(title, str):
            self.title = title
        else:
            raise TypeError('title needs to be a string')
        if len(self.data.shape) == 3:
            pass
        else:
            raise ValueError('It is not a 3-D data')
        self.num = 0
        self.data_plot = self.data[self.num, :, :]
        self.im = self.ax.matshow(self.data_plot)
        self.colorbar(self.im)
        self.ax.set_title(self.title +  str(self.num))
        self.canvas.mpl_connect('key_press_event', self.on_move)
        self.canvas.mpl_connect(
            "button_press_event", lambda *args, **kwargs: print(args, kwargs)
        )
        plt.ion()

    def on_move(self, event):
        print(f"activate this {event.key}, {self.num}")
        print('here')
        self.draw_idle()
        plt.cla()
        if event.key == "left":
            if self.num == 0:
                self.num = 0
            else:
                self.num -= 1
        elif event.key == "right":
            if self.num == self.data.shape[2] - 1:
                self.num = 0
            else:
                self.num += 1
        else:
            pass
        self.data_plot = self.data[self.num, :, :]
        self.ax.matshow(self.data_plot)
        self.ax.set_title(self.title + str(self.num))




"""Screenshot window and related functions."""


from visbrain.io import write_fig_pyqt, dialog_save
from visbrain.utils import ScreenshotPopup
class UiScreenshot(object):
    """Initialize the screenshot GUI and functions to apply it."""

    def __init__(self):
        """Init."""
        canvas_names = ['main']
        self._ssGui = ScreenshotPopup(self._fcn_run_screenshot,
                                      canvas_names=canvas_names)

    def show_gui_screenshot(self):
        """Display the GUI screenhot."""
        self._ssGui.show()

    def _fcn_run_screenshot(self):
        """Run the screenshot."""
        # Get filename :
        filename = dialog_save(self, 'Screenshot', 'screenshot', "PNG(*.PNG)"
                               ";;TIFF(*.tiff);;JPG(*.jpg);;"
                               "All files(*.*)")
        # Get screenshot arguments :
        kwargs = self._ssGui.to_kwargs()

        if kwargs['entire']:  # Screenshot of the entire window
            self._ssGui._ss.close()
            write_fig_pyqt(self, filename)
        else:  # Screenshot of selected canvas
            # Remove unsed entries :
            del kwargs['entire']
            self.screenshot(filename, **kwargs)

from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDesktopWidget, QPushButton, QStackedWidget, QVBoxLayout, \
    QHBoxLayout, QComboBox, QCheckBox, QSlider, QGroupBox, QLabel, QFormLayout, QSpinBox, QTableView, \
    QFrame, QTabWidget, QTableWidget, QSplitter, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np
from visbrain.objects.scene_obj import VisbrainCanvas
from visbrain.objects import BrainObj, CombineSources, RoiObj, SourceObj
import pandas as pd
from vispy import scene
import vispy.visuals.transforms as vist
from visbrain.utils.guitools import fill_pyqt_table
from gui.re_ref import get_chan_group
from gui.my_func import u_color

class Brain_Ui(object):

    source_signal = pyqtSignal(CombineSources)

    def __init__(self):
        super(Brain_Ui, self).__init__()
        self.cdict = {'bgcolor': '#dcdcdc', 'cargs': {'size':(900, 600), 'dpi': 600,
                      'fullscreen': True, 'resizable': True}}
        self._gl_scale = 100
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
        

    def create_source(self, elec_df=None):
        self.elec_df = elec_df
        if self.elec_df is not None:
            self.ch_names = self.elec_df[0].tolist()
            self.ch_group = get_chan_group(chans=self.ch_names)
            self.elec_df.set_index([0], inplace=True)
            self.ch_pos = self.elec_df[[1, 2, 3]].to_numpy(dtype=float)
            ch_coords = []
            [ch_coords.append(self.ch_group[group]) for group in self.ch_group]
            self.s_obj = [SourceObj(str(group), xyz=self.elec_df.loc[self.ch_group[group]].to_numpy(dtype=float),
                                text=self.ch_group[group], color=u_color[index % 15], **self.s_kwargs)
                          for index, group in enumerate(self.ch_group)]
            self.source_signal.connect(self._fcn_create_source)
            self.source_signal.emit(self.s_obj)


    def _brain_ui(self):
        self.widget = QWidget()

        # root node
        self._vbNode = scene.Node(name='Brain')
        self._vbNode.transform = vist.STTransform(scale=[self._gl_scale] * 3)

        object_lst = ['Brain', 'Sources', 'Region of Interest(ROI)']
        self._obj_type_lst = QComboBox()
        self._obj_type_lst.addItems(object_lst)
        self._obj_type_lst.currentTextChanged.connect(self.change_group)
        self._obj_type_lst.model().item(1).setEnabled(False)


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
        self.layout = QHBoxLayout()
        self.layout.addLayout(left_layout)
        self.layout.addWidget(self.view.canvas.native)
        self.widget.setLayout(self.layout)

        self.view.wc.camera = self._camera
        self._vbNode.parent = self.view.wc.scene
        self.atlas.camera = self._camera
        self.atlas._csize = self.view.canvas.size
        self.atlas.rotate ('left')
        self.atlas.camera.set_default_state()


    def _fcn_create_source(self):
        self._source_widget()


    
    def _brain_widget(self):

        self._brain_group = QGroupBox('Display Brain')
        # self.brain_group.setFixedWidth(300)
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
        self._brain_group.setChecked(True)
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
        self._source_tab1.setStyleSheet("background-color: '#fafafa'")
        self._obj_name_lst = QComboBox()
        self._obj_name_lst.addItems(sorted(self.group))
        self._select_label = QLabel('Select')
        self._s_select = QComboBox()
        self._s_select.addItems(['All', 'Inside the brain', 'Outside the brain', 
                                 'Left hemisphere', 'Right hemisphere', 'None'])
        self._symbol_label = QLabel('Symbol')
        self._s_symbol = QComboBox()
        symbol = ['hbar', 'vbar', 'disc', 'arrow', 'ring', 'clobber', 
                  'square', 'diamond', 'cross']
        self._s_symbol.addItems(symbol)

        self._project_label = QLabel('Cortical projection')
        self._projection = QComboBox()
        self._projection.addItems(['Modulation', 'Repartition'])
        self.project_btn = QPushButton('Run')

        s_layout_0 = QVBoxLayout()
        s_layout_1 = QFormLayout()
        s_layout_1.addRow(self._select_label, self._s_select)
        s_layout_1.addRow(self._symbol_label, self._s_symbol)
        s_layout_2 = QHBoxLayout()
        s_layout_2.addWidget(self._projection)
        s_layout_2.addWidget(self.project_btn)
        s_layout_0.addWidget(self._obj_name_lst)
        s_layout_0.addLayout(s_layout_1)
        s_layout_0.addWidget(self._project_label)
        s_layout_0.addLayout(s_layout_2)
        s_layout_0.addStretch(1000)
        self._source_tab1.setLayout(s_layout_0)

        self._source_tab2 = QWidget()
        self._s_table = QTableWidget()
        self._s_table.setFixedHeight(500)
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
            self._obj_type_lst.model().item(4).setEnabled(False)
        self.sources.parent = self._vbNode
        name = self._obj_name_lst.currentText()
        self._source_group.setChecked(self.sources[name].visible_obj)
        self._source_group.clicked.connect(self._fcn_source_visible)
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
        self._roi_group.setFixedWidth(400)
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
        r_layout_2.addWidget(self._roi_group)
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
        self._roi_vis.setChecked(self.roi.visible_obj)
        self._roi_vis.clicked.connect(self._fcn_roi_visible)
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
            self.group_stack.removeWidget (self.roi_group)
            self.group_stack.addWidget(self.brain_group)
        elif self._obj_type_lst.currentText() == 'Sources':
            self.group_stack.removeWidget(self.brain_group)
            self.group_stack.removeWidget (self.roi_group)
            self.group_stack.addWidget(self._source_group)
        elif self._obj_type_lst.currentText() == 'Region of Interest (ROI)':
            self.group_stack.removeWidget(self.brain_group)
            self.group_stack.removeWidget(self._source_group)
            self.group_stack.addWidget (self.roi_group)


    # ========================== Brain Slot ========================

    def _fcn_brain_visible(self):
        """Display / hide the brain."""
        viz = self._brain_group.isChecked()
        self.atlas.visible_obj = viz


    def _fcn_brain_template(self):
        template = str (self._brain_template.currentText())
        hemisphere = str(self._brain_hemi.currentText())
        if self.atlas.name != template:
            self.atlas.set_data(name=template, hemisphere=hemisphere)

        self.atlas.mesh.xmin = float (-self.x)
        self.atlas.mesh.xmax = float (self.x)
        self.atlas.mesh.ymin = float (-self.y)
        self.atlas.mesh.ymax = float (self.y)
        self.atlas.mesh.zmin = float (-self.z)
        self.atlas.mesh.zmax = float (self.z)
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
        if viz:
            self.sources.set_visible_sources('all', self.atlas.vertices)
            for name in self.group:
                self.sources[name]._sources_text.visible = True
        else:
            for name in self.group:
                self.sources[name]._sources_text.visible = False
        self._fcn_brain_alpha()


    def _fcn_brain_alpha(self):
        """Update brain transparency."""
        alpha = self._brain_alpha.value() / 100.
        self.atlas.alpha = alpha
        self.atlas.mesh.update ()


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
        viz = self._source_group.isChecked()
        name = self._obj_name_lst.currentText ()
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
        self._source_group.setChecked(viz)
        self._select_label.setEnabled(viz)
        self._s_select.setEnabled(viz)
        self._symbol_label.setEnabled(viz)
        self._s_symbol.setEnabled(viz)
        self._project_label.setEnabled(viz)
        self._projection.setEnabled(viz)
        self.project_btn.setEnabled (viz)


    def _fcn_source_proj(self, _, **kwargs):
        """Apply source projection."""
        b_obj = self.atlas
        radius = 10.0
        mask_color = 'gray'
        project = str(self.projection.currentText()).lower()
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


