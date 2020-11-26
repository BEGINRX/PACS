# -*- coding: utf-8 -*-
'''
@File : get_info.py
@Author : BarryLiu
@Time : 2020/11/10 16:28
@Desc : get some specific information from the subject's data
'''

# To get GWR re-reference, we need to know the anatomical information
# of each electrode, here are the functions we need.

#
import pandas as pd
import numpy  as np

def get_mni_struct(filename, start_row = 1, end_row = 'auto'):

    delimiter = '\t'
    file_pd = pd.read_csv(filename, delimiter=delimiter, header=None)
    # file_tab = pd.read_table(filename, delimiter=delimiter, header=None)
    if end_row == 'auto':
        file = file_pd[start_row - 1:]
    else:
        file = file_pd[start_row - 1 : end_row]

    ch_name = file[0].tolist()
    ch_coord = file[[1, 2, 3]].to_numpy(dtype=np.float64)
    ch_x = ch_coord[:, 0]
    ch_y = ch_coord[:, 1]
    ch_z = ch_coord[:, 2]

    return ch_name, ch_coord


def load_seeg_loc():

    pass



def get_anat_loc():

    pass


def get_brain_coord():

    pass


def stat_struct():

    pass

























