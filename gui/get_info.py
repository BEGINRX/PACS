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

def get_coord(filename, start_row = 1, end_row = 'auto'):

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


def mni2cor(mni, T='auto'):

    n = mni.shape[0]
    if T == 'auto':
        T = np.array([
            [-4, 0, 0, 84],
            [0, 4, 0, -116],
            [0, 0, 4, -56],
            [0, 0, 0, 1]])
    coord = np.array([
        [mni[:, 0], mni[:, 1], mni[:, 2], np.ones((n))]]).T
    coord = coord.reshape(coord.shape[0], coord.shape[1])
    coord = coord.dot(np.linalg.inv(T).T)
    coord = np.round(np.delete(coord, -1, axis=1))

    return coord


def get_mni_struct(coord, db = 'auto'):

    td_data_base = np.load('D:\SEEG_Cognition\datasets\TDDataBase.npy').item()
    db_default = td_data_base['DB']
    if db == 'auto':
        db = db_default
    n = coord.shape[0]
    loca_data = np.empty((n, len(db)), dtype=object)

    for i in range(n):
        for j in range(len(db)):
            try:
                # 注：python与matlab存储三维数组形式不一样，所以索引方式也不同
                gray_level = db[j]['mnilist'][coord[i, 2] - 1, coord[i, 1] - 1, coord[i, 0] - 1].astype(np.int64)
            except:
                gray_level = None
            finally:
                if gray_level == 0:
                    label = 'undefined'
                elif gray_level == None:
                    label = str('None')
                else:
                    if j == len(db) - 1:
                        tmp = ' (aal)'
                    else:
                        tmp = ''
                    label = db[j]['anatomy'][gray_level - 1] + tmp
            loca_data[i, j] = label

    return loca_data


def get_anat_loc(fpath, td_data_path = None):

    ch_name, ch_coord = get_coord(filename=fpath)
    if td_data_path == None:
        td_data_path = 'D:\\SEEG_Cognition\\dataset\\TDDataBase.npy'
    td_data_base = np.load(td_data_path).item()
    db = td_data_base['DB']

    mni = np.round(ch_coord / 2) * 2
    n = len(mni)
    T = np.array([
        [2, 0, 0, -92],
        [0, 2, 0, -128],
        [0, 0, 2, -74],
        [0, 0, 0, 1]])
    coord = mni2cor(mni, T=T)
    loca_data = get_mni_struct(coord)

    header = np.array(['Channel Name', 'MNI(X)', 'MNI(Y)', 'MNI(Z)', 'TD Hemispheres',
                       'TD Lobes', 'TD Labels', 'TD Type', 'TD brodmann areas+', 'AAL'], dtype=object)
    ch_name = np.array(ch_name, dtype=object).reshape(-1, 1)
    loca_data_new = np.hstack((ch_name, ch_coord, loca_data))
    loca_data = np.vstack((header, loca_data_new))

    return loca_data


def get_gchan_wchan(anatomy):
    '''
    :param anatomy: ndarray of anatomy
    :return: list chan list of gray matter and white matter
    '''
    chan_matter = anatomy[:, [0, 7]]
    chan_gm, chan_wm = [], []
    for index in range(len(chan_matter)):
        if chan_matter[index, 1] == 'Gray Matter':
            chan_gm.append(chan_matter[index, 0])
        elif chan_matter[index, 1] == 'White Matter':
            chan_wm.append(chan_matter[index, 0])

    return chan_gm, chan_wm


























