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


def get_pearson(epoch):
    '''
    Calculate Pearson Coorelation for all channels
    :param epoch: instance of BaseRpochs
                  data needed to be calculated
    :return: numpy.array
             pearson
    '''
    from scipy.stats import pearsonr
    import numpy as np
    from mne.epochs import BaseEpochs

    if not isinstance(epoch, BaseEpochs):
        raise TypeError('This is not BaseEpochs class')

    chan = epoch.ch_names
    pearson = np.zeros((1, 148, 148))
    for j in range(len(epoch)):
        print('calculating epoch ' + str(j))
        pearson_tmp = np.zeros((1, len(chan))).astype(np.float32)
        data = epoch[j]._data[0, :, :]
        for k in range(len(chan)):
            result = np.array([])
            for i in range(len(chan)):
                result = np.append(result, pearsonr(data[k], data[i])[0])
            pearson_tmp = np.vstack((pearson_tmp, result.reshape(1, -1)))
        pearson_tmp = np.delete(pearson_tmp, 0, axis=0)
        pearson_tmp = np.expand_dims(pearson_tmp, 0).astype(np.float32)
        pearson = np.concatenate((pearson, pearson_tmp), axis=0)
    pearson = np.delete(pearson, 0, axis=0)

    return pearson


