# -*- coding: utf-8 -*-
'''
@File : extra_func.py
@Author : BarryLiu
@Time : 2020/12/8 22:09
@Desc :
'''
import mne
import numpy as np

def new_layout(chan):
    box = (0, 1, 0, 1)
    kind = 'SEEG'
    ch_len = len(chan)
    names = chan
    ids = np.arange(ch_len) + 1

    width = 0.05
    height = 0.05
    pos = np.zeros((ch_len, 4), dtype=np.float16)
    pos[:, 2:] = width, height

    pos_x = np.zeros((ch_len, 1), dtype=np.float16)
    for i in range(ch_len):
        if (i + 1) % 12 == 1:
            pos_x[i] = 0.03
        else:
            pos_x[i] = pos_x[i - 1] + 0.08

    pos_y = np.zeros((ch_len, 1), dtype=np.float16)
    for j in range(ch_len):
        if (j + 1) % 12 == 1:
            if j == 0:
                pos_y[j] = 0.9
            else:
                pos_y[j] = pos_y[j - 12] - 1 / (ch_len / 10)
        else:
            pos_y[j] = pos_y[j - 1]
    pos[:, 0], pos[:, 1] = pos_x.reshape(ch_len, ), pos_y.reshape(ch_len, )

    layout = mne.channels.Layout(box, ids=ids, kind=kind, names=names, pos=pos)

    return layout