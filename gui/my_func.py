# -*- coding: utf-8 -*-
'''
@File : extra_func.py
@Author : BarryLiu
@Time : 2020/12/8 22:09
@Desc :
'''
import mne
import numpy as np
from mne import BaseEpochs, Evoked
from mne.io import BaseRaw

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


def plot_sensors_connectivity(con, dir=False):
    if not dir:
        pass
    else:
        pass


def standardize_epoch(epoch, baseline, normal=False):
    '''
    standardize epochs
    :param epoch: instance of BaseEpochs
    :param baseline: tuple
                     use baseline's mean and std to calculate connectivity
    :return: instance of BaseEpochs
             standardized epoch
    '''
    if not isinstance(epoch, BaseEpochs):
        raise TypeError('This is not Epoch')
    epoch_new = epoch.copy().crop(baseline[1])
    data = epoch_new.get_data()
    base = epoch.copy().crop(baseline[0], baseline[1]).get_data()
    if not normal:
        base_mean = np.expand_dims(base.mean(axis=2), 2)
        base_std = np.expand_dims(base.std(axis=2), 2)
        stand_data = (data - base_mean) / base_std
        epoch_new._data = stand_data
    else:
        max = np.expand_dims(np.max(data, axis=2), 2)
        min = np.expand_dims(np.min(data, axis=2), 2)
        normal_data = (data - min) / (max - min)
        epoch_new._data = normal_data

    return epoch_new


def standardize_evoke(evoke, baseline):
    '''
    standardize evokes
    :param evoke: instance of Evoked
    :param baseline: tuple
                     use baseline's mean and std to calculate connectivity
    :return: instance of Evoked
             standardized evoke
    '''
    if not isinstance(evoke, Evoked):
        raise TypeError('This is not Evoke')
    evoke_new = evoke.copy().crop(baseline[1])
    data = evoke_new.get_data()
    base = evoke.copy().crop(baseline[0], baseline[1]).get_data()
    base_mean = np.expand_dims(base.mean(axis=2), 2)
    base_std = np.expand_dims(base.std(axis=2), 2)
    stand_data = (data - base_mean) / base_std
    evoke_new._data = stand_data

    return evoke_new


def get_pearson(epoch):
    '''
    Calculate Pearson Correlation for all channels
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
    pearson = np.zeros((1, len(chan), len(chan)))
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
    pearson = np.mean(pearson, axis=0)

    return pearson


def get_spec_pearson(epochx, epochy):
    '''
    Calculate Pearson Coorelation for sub channels
    :param epochx: instance of BaseEpochs
    :param epochy: instance of BaseEpochs
    :return: pearson for sub channels
    '''
    from scipy.stats import pearsonr
    import numpy as np
    from mne.epochs import BaseEpochs

    if not isinstance(epochx, BaseEpochs):
        raise TypeError('This is not BaseEpochs class')
    if not isinstance(epochy, BaseEpochs):
        raise TypeError('This is not BaseEpochs class')
    if not len(epochx) == len(epochy):
        raise TypeError('This is not the same epoch')

    chanx = epochx.ch_names
    chany = epochy.ch_names
    pearson = np.zeros((1, len(chanx), len(chany)))
    for i in range(len(epochx)):
        print('calculating epoch ' + str(i))
        pearson_tmp = np.zeros((1, len(chany))).astype(np.float32)
        datax = epochx[i]._data[0, :, :]
        datay = epochy[i]._data[0, :, :]
        for j in range(len(chanx)):
            result = np.array([])
            for k in range(len(chany)):
                result = np.append(result, pearsonr(datax[j, :], datay[k, :])[0])
            pearson_tmp = np.vstack((pearson_tmp, result.reshape(1, -1)))
        pearson_tmp = np.delete(pearson_tmp, 0, axis=0)
        pearson_tmp = np.expand_dims(pearson_tmp, 0).astype(np.float32)
        pearson = np.concatenate((pearson, pearson_tmp), axis=0)
    pearson = np.delete(pearson, 0, axis=0)
    pearson = np.mean(pearson, axis=0)
    return pearson


def get_corr(epoch1, epoch2, baseline, normal=False, mode='valid', norm=True):
    from scipy.signal import correlate

    sta_epoch1 = standardize_epoch(epoch1, baseline, normal=normal)
    sta_epoch2 = standardize_epoch(epoch2, baseline, normal=normal)
    try:
        data1 = sta_epoch1.copy().crop(0.)._data
        data2 = sta_epoch2.copy().crop(0.)._data
    except:
        data1 = sta_epoch1._data
        data2 = sta_epoch2._data
    if mode == 'valid':
        corr = np.zeros((1, data1.shape[1], data2.shape[1]))
        for i in range(len(epoch1)):
            print('calculating epoch ' + str(i))
            datax = data1[i, :, :]
            datay = data2[i, :, :]
            corr_tmp = np.zeros((1, datay.shape[0])).astype(np.float32)
            for j in range(len(datax)):
                result = np.array([])
                for k in range(len(datay)):
                    result = np.append(result, correlate(datax[j, :], datay[k, :], mode=mode))
                corr_tmp = np.vstack((corr_tmp, np.expand_dims(result, 0)))
            corr_tmp = np.delete(corr_tmp, 0, axis=0).astype(np.float32)
            corr = np.concatenate((corr, np.expand_dims(corr_tmp, 0)), axis=0)
        corr = np.delete(corr, 0, axis=0)
        corr = np.mean(corr, axis=0)
    elif mode == 'same':
        pass
    elif mode == 'full':
        corr = np.zeros((1, epoch2._data.shape[1], 2 * epoch2._data.shape[2] - 1))
        for i in range(len(epoch1)):
            corr_tmp = correlate(epoch1._data[i], epoch2._data[i], mode='full')
            corr = np.vstack((corr, np.expand_dims(corr_tmp, 0)))
        corr = np.delete(corr, 0, axis=0).astype(np.float64)
        if norm:
            print('calculate normalized cross-correlation')
            trans = np.zeros((1, len(epoch2.ch_names), 1))
            for i in range(data2.shape[0]):
                trans_tmp = np.array([])
                for j in range(data2.shape[1]):
                    n = np.sqrt(np.dot(data1[i, 0, :], data1[i, 0, :].T) *
                                np.dot(data2[i, j, :], data2[i, j, :].T))
                    trans_tmp = np.expand_dims(np.append(trans_tmp, np.array([n])), axis=1)
                trans = np.vstack((trans, np.expand_dims(trans_tmp, axis=0)))
            trans = np.delete(trans, 0, axis=0)
            corr = np.true_divide(corr, trans)
        corr = np.mean(corr, axis=0)
    return corr


def get_mutual_info():
    pass





if __name__ == '__main__':

    import mne
    fpath = 'D:\SEEG_Cognition\data\color_epoch.fif'
    evoke = mne.read_epochs(fpath)[0:2]
    epochx = evoke.copy().pick_channels(['A1', 'A2', 'A3', 'A4'])
    epochy = evoke.copy().pick_channels(['B1', 'B2', 'B3'])
    epochx_data = epochx._data
    epochy_data = epochy._data
    result = get_spec_pearson(epochx, epochy)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    image = ax.matshow(result)
    fig.colorbar(image)
    plt.title('Pearson')
    plt.show()

    fig, ax = plt.subplots()
    for i in range(len(result)):
        ax.plot(result[i, :], label= epochx.ch_names[i] + '————' + str(epochy.ch_names),
        marker = 'o', markerfacecolor = 'black', markersize = 3)
    ax.legend()
    ax.set_title('Pearson')
    plt.show()


