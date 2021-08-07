import numpy as np
import traceback
import mne
import time
import os


def preprocess(seeg, path, name, sfreq=1000, low=0.5, high=200,
               rename=True, drop_chan=True):
    """
    Preprocess pipeline of SEEG time series data

    Parameters
    ----------
    path : str
        File path to save
    name : str
        File name to save
    sfreq : int | float
        Resampling frequency. The default is 1000Hz.
    low : int | float
        Low cut frequency. The default is 0.5.
    high : int | float
        DESCRIPTION. The default is 200.
    rename : bool
        Rename channels. The default is False.
    drop_chan :list of str | bool
        Drop useless channels. The default is True.

    Returns
    -------
    seeg: instance of BaseRaw
        SEEG time series.

    """
    if rename:
        print('============================')
        print('Start Renaming channels')
        start = time.time()
        seeg.rename_channels({chan: chan[4:]
                                   for chan in seeg.ch_names
                                   if 'POL' in chan})
        seeg.rename_channels({chan: chan[4:-4]
                                   for chan in seeg.ch_names
                                   if 'Ref' in chan})
        end = time.time()
        print('Finish Renaming channels')
        print('Using time {:.2f} seconds'.format(end - start))
        print('============================')
    if rename and (drop_chan == True):
        print('Start Dropping channels')
        start = time.time()
        drop_chan = ['DC16', 'DC01', 'DC02', 'DC03', 'DC04', 'DC05', 'DC06',
                     'DC07', 'DC08', 'BP1', 'BP2', 'BP3', 'BP4', 'EKG1',
                     'EKG2', 'EMG1', 'EMG2', 'EMG3', 'EMG4', 'E', 'DC09', 'DC10',
                     'DC11', 'DC12', 'DC13', 'DC14', 'DC15']
        for chan in drop_chan:
            try:
                seeg.drop_channels(chan)
            except:
                pass
        end = time.time()
        print('Finish Dropping channels')
        print('Using time {:.2f} seconds'.format(end - start))
        print('============================')
    print('Start Resampling channels')
    start = time.time()
    seeg = seeg.resample(sfreq)
    end = time.time()
    print('Finish Resampling channels')
    print('Using time {:.2f} seconds'.format(end - start))
    print('============================')
    print('Start Filtering channels')
    start = time.time()
    seeg.notch_filter(50)
    print('============================')
    seeg.notch_filter(100)
    print('============================')
    seeg.notch_filter(150)
    print('============================')
    seeg.filter(low, high)
    end = time.time()
    print('Finish Filtering channels')
    print('Using time {:.2f} seconds'.format(end - start))
    print('============================')
    print('Saving SEEG')
    seeg.save(os.path.join(path, name + '.fif'))

    return seeg



def get_chan_group_old(raw):
    '''
    :param raw: instance of Raw
                raw data
    :return: dict
             electrodes in the same shaft
    '''
    ch_names = raw.ch_names
    ch_group = []
    for ch_name in ch_names:
        ch_group.append(ch_name[:2])
    ch_group = list(set(ch_group))
    num = [str(i) for i in range(10)]
    for index in range(len(ch_group)):
        if len(ch_group[index]) == 2:
            if ch_group[index][1] in num:
                ch_group[index] = ch_group[index][0]
    ch_group = sorted(list(set(ch_group)))
    # 获取每个轴上的电极名称，但如A'1的仍在A中
    ch_group_cont = {group: [] for group in ch_group}
    for group in ch_group:
        for index in range(len(ch_names)):
            if group in ch_names[index]:
                ch_group_cont[group].append(ch_names[index])
    # 将错分的电极删掉 如 A'1 在轴A中
    length = [len(ch_group_cont[i]) for i in ch_group_cont]
    i = 0
    chan_del = {group: [] for group in ch_group_cont}
    for group in ch_group_cont:
        for index in range(length[i]):
            if (group != 'DC') and ('DC' in ch_group_cont[group][index]):
                chan_del[group].append(ch_group_cont[group][index])
            if ('\'' not in group) and ((group + '\'') in ch_group_cont[group][index]):
                chan_del[group].append(ch_group_cont[group][index])
        i += 1

    try:
        del ch_group_cont['DC']
    except Exception as error:
        if error.args[0] == "KeyError: 'E'":
            pass
    try:
        for group in ch_group_cont:
            [ch_group_cont[group].remove(chan) for chan in chan_del[group]]
            if '\'' in group:
                tip = None
                for index in range(len(ch_group_cont[group])):
                    if ch_group_cont[group][index] == group:
                        tip = [index, group]
                    break
                if tip:
                    ch_group_cont[group].remove(tip[1])
                    ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[2:])))
                    ch_group_cont[group].insert(0, tip[1])
                else:
                    ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[2:])))
            else:
                tip = None
                for index in range(len(ch_group_cont[group])):
                    if ch_group_cont[group][index] == group:
                        tip = [index, group]
                    break
                if tip:
                    ch_group_cont[group].remove(tip[1])
                    ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[1:])))
                    ch_group_cont[group].insert(0, tip[1])
                else:
                    ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[1:])))
    except:
        traceback.print_exc()

    return ch_group_cont

def get_chan_group(raw=None, chans=None):
    '''
    :param raw: instance of Raw
                raw data
           chans: list of channels' name
    :return: dict
             electrodes in the same shaft
    '''
    if raw is not None and chans is None:
        print(raw)
        chans = raw.ch_names
        try:
            raw.rename_channels({chan: chan[4:] for chan in raw.ch_names
                                 if 'POL' in chan})
            raw.rename_channels({chan: chan[4:6] for chan in raw.ch_names
                                 if 'Ref' in chan})
            useless_chan = [chan for chan in raw.ch_names if 'DC' in chan or 'BP' in chan
                            or 'EKG' in chan or 'EMG' in chan]
            raw.drop_channels(useless_chan)
        except:
            traceback.print_exc()
    else:
        pass
    
    if '-' not in chans[0]:
        key = list(set([ch[0] for ch in chans]))
        key += [k + '\'' for k in key]
        chan_group = {k: [] for k in key}
        for ch in chans:
            for k in key:
                if ch.startswith(k):
                    if not k.endswith('\'') and ('\'' in ch):
                        continue
                    else:
                        chan_group[k].append(ch)
    
        # delete no-element group(s)
        chan_del = []
        for group in chan_group:
            if not len(chan_group[group]):
                chan_del.append(group)
        [chan_group.pop(ch) for ch in chan_del]
    
        # sort the channels in its group for reference
        for group in chan_group:
            if group.endswith('\''):
                if group in chan_group[group]:
                    chan_group[group].remove(group)
                    chan_group[group].sort(key=lambda ch: (ch[0], int(ch[2:])))
                    chan_group[group].insert(0, group)
                else:
                    chan_group[group].sort(key=lambda ch: (ch[0], int(ch[2:])))
            else:
                if group in chan_group[group]:
                    chan_group[group].remove(group)
                    chan_group[group].sort(key=lambda ch: (ch[0], int(ch[1:])))
                    chan_group[group].insert(0, group)
                else:
                    chan_group[group].sort(key=lambda ch: (ch[0], int(ch[1:])))
    else:
        # 先假设所有电极都有A和A’两种形式 再删除没有电极的group
        key = list(set([ch[0] for ch in chans]))
        key += [k + '\'' for k in key]
        chan_group = {k: [] for k in key}
        for ch in chans:
            for k in key:
                if ch.startswith(k):
                    if not k.endswith('\'') and ('\'' in ch):
                        continue
                    else:
                        chan_group[k].append(ch)
    
        # delete no-element group(s)
        chan_del = []
        for group in chan_group:
            if not len(chan_group[group]):
                chan_del.append(group)
        [chan_group.pop(ch) for ch in chan_del]

    return chan_group


def car_ref(raw, data_class='raw'):
    '''
    Reference SEEG data using Common Average Reference(CAR)
    :param raw: instance of Raw
                raw data
    :return: instance of Raw
             re-referenced data
    '''
    new_raw = raw.copy()
    data = new_raw._data * 1e6
    if data_class == 'raw':
        data_mean = np.mean(data, axis=0)
    elif data_class == 'epoch':
        data_mean = np.mean(data, axis=1).reshape(data.shape[0], 1, data.shape[2])
    data_ref = (data - data_mean) * 1e-6
    new_raw._data = data_ref

    return new_raw


def gwr_ref(raw, data_class, coord_path):
    '''
    Reference SEEG data using Gray-white Matter Reference(GWR)
    :param raw: instance of Raw
                raw data
    :param gm: list
               channels in gray matter
    :param wm: list
               channels in white matter
    :return: instance of raw
             re-referenced data
    '''
    from gui.get_info import get_anat_loc, get_gchan_wchan
    print(coord_path)
    loca_data = get_anat_loc(coord_path, td_data_path='gui/TDDataBase.npy')
    chan_gm, chan_wm = get_gchan_wchan(loca_data)

    raw_gm = raw.copy().pick_channels(chan_gm)
    raw_wm = raw.copy().pick_channels(chan_wm)

    raw_gm.load_data()
    data_gm = raw_gm._data
    if data_class == 'raw':
        data_gm_mean = np.mean(data_gm, axis=0)
    elif data_class == 'epoch':
        data_gm_mean = np.mean(data_gm, axis=1).reshape(data_gm.shape[0], 1, data_gm.shape[2])
    raw_gm._data = data_gm - data_gm_mean

    raw_wm.load_data()
    data_wm = raw_wm._data
    if data_class == 'raw':
        data_wm_mean = np.mean(data_wm, axis=0)
    elif data_class == 'epoch':
        data_wm_mean = np.mean(data_wm, axis=1).reshape(data_wm.shape[0], 1, data_wm.shape[2])
    raw_wm._data = data_wm - data_wm_mean

    raw_ref = raw_gm.copy().add_channels([raw_wm])

    return raw_ref


def bipolar_ref(ieeg):
    '''
    Reference SEEG data using Bipolar Reference
    :param ieeg: instance of BaseRaw or BaseEpochs
                SEEG data

    :return: instance of raw
             data and raw data of the first contact in each shafts
    '''
    from mne.io import BaseRaw
    from mne import BaseEpochs
    group_chan = get_chan_group(ieeg)
    group_ieeg = {group: ieeg.copy().pick_channels(group_chan[group]).reorder_channels(group_chan[group])
                  for group in group_chan}
# =============================================================================
#     if data_class == 'raw':
#         group_ieeg_bipolar = {group: np.diff(group_ieeg[group]._data, axis=0) for group in group_chan}
#     elif data_class =='epoch':
#         group_ieeg_bipolar = {group: np.diff(group_ieeg[group]._data, axis=1) for group in group_chan}
# =============================================================================
    group_ieeg_bipolar = dict()
    if isinstance(ieeg, BaseRaw):
        group_ieeg_bipolar = {group: group_ieeg[group]._data[:-1, :] - 
                              group_ieeg[group]._data[1:, :]
                              for group in group_chan}
    elif isinstance(ieeg, BaseEpochs):
        group_ieeg_bipolar = {group: np.diff(group_ieeg[group]._data, axis=1) for group in group_chan}

    for group in group_ieeg:
        ch_name = group_ieeg[group].ch_names
        group_ieeg[group].drop_channels(group_chan[group][-1])._data = group_ieeg_bipolar[group]

    
    group_0 = list(group_chan.keys())[0]
    bipolar_ieeg = group_ieeg[group_0]
    group_ieeg.pop(group_0)
    for name in group_ieeg:
        if not (name == 'DC'):
            bipolar_ieeg.add_channels([group_ieeg[name]])
            
    bipolar_chan = bipolar_ieeg.ch_names
    bipolar_group = get_chan_group(chans=bipolar_chan)
    
    for key in bipolar_group:
            b_group = bipolar_group[key]
            for index in range(len(b_group)):
                chan = b_group[index]
                if index == len(b_group) - 1:
                    if '\'' not in chan:
                        bipolar_name = chan + '-' + chan[0:1] + str(int(chan[1:]) + 1)
                    else:
                        bipolar_name = chan + '-' + chan[0:2] + str(int(chan[2:]) + 1)
                    bipolar_ieeg.rename_channels({chan: bipolar_name})
                else:
                    latter_chan = b_group[index + 1]
                    bipolar_name = chan + '-' + latter_chan
                    bipolar_ieeg.rename_channels({chan: bipolar_name})
                print('Successfully convert {:} to {:}'.format(chan, bipolar_name))
    
    return bipolar_ieeg



def esr_ref(raw, data_class='raw'):
    '''
    Reference SEEG data using Electrode Shaft Reference(ESR)
    :param raw: instance of Raw
                raw data
    :return: instance of raw
             re-referenced data
    '''
    # 获取分组
    group_chan = get_chan_group(raw)

    ch_data = {group: raw.copy().pick_channels(group_chan[group]) for group in group_chan}
    for group in ch_data:
        data = ch_data[group]._data * 1e6
        if data_class == 'raw':
            data_mean = np.mean(data, axis=0)
        elif data_class == 'epoch':
            data_mean = np.mean(data, axis=1).reshape(data.shape[0], 1, data.shape[2])
        ch_data[group]._data = (data - data_mean) * 1e-6

    group_0 = list(group_chan.keys())[0]
    raw_new = ch_data[group_0]
    ch_data.pop(group_0)
    for name in ch_data:
        if not (name == 'DC'):
            raw_new.add_channels([ch_data[name]])

    return raw_new


def monopolar_ref(raw,ref_chan , data_class='raw'):
    '''
    :param raw: instance of Raw
                raw data
    :param ref_chan: list
                     the channels' name chosen as ref channel
    :return: instance of raw
             the re-ref raw data
    '''
    ref_raw = raw.copy().pick_channels(ref_chan)
    ref_data = ref_raw._data
    if data_class == 'raw':
        ref_mean = np.mean(ref_data, axis=0)
    elif data_class == 'epoch':
        ref_mean = np.mean(ref_data, axis=1).reshape(ref_data.shape[0],
                                                     1, ref_data.shape[2])

    new_raw = raw.copy()
    data = new_raw._data - ref_mean
    new_raw._data = data

    return new_raw


def laplacian_ref(raw, data_class='raw', mode='auto'):
    '''
    Reference SEEG data using Laplacian Reference
    :param raw: instance of Raw
                raw data
    :param mode: str
        if mode = 'auto' then don't show the first contact in each shafts
        if mode ='keep' then show
    :return: instance of raw
             data and raw data of the first contact in each shafts
    '''
    group_chan = get_chan_group(raw)
    group_len = {group: len(group_chan[group]) for group in group_chan}
    group_ieeg = {group: raw.copy().pick_channels(group_chan[group]) for group in group_chan}
    group_ieeg = {group: group_ieeg[group].reorder_channels(group_chan[group])
                  for group in group_chan}
    group_ieeg_only = {group: group_ieeg[group]._data * 1e6 for group in group_ieeg}
    group_ieeg_laplacian = {group: np.zeros(group_ieeg[group].copy()._data.shape) for group in group_ieeg}
    for group in group_ieeg_only:
        for index in range(1, group_len[group] - 1):
            if data_class == 'raw':
                group_ieeg_laplacian[group][index] = group_ieeg_only[group][index] - \
                                            np.divide(group_ieeg_only[group][index - 1] +
                                                      group_ieeg_only[group][index + 1], 2)
            elif data_class == 'epoch':
                group_ieeg_laplacian[group][:, index, :] = group_ieeg_only[group][:, index, :] - \
                                                      np.divide(group_ieeg_only[group][:, index - 1, :] +
                                                      group_ieeg_only[group][:, index + 1, :], 2)
        if data_class == 'raw':
            group_ieeg_laplacian[group] = np.delete(group_ieeg_laplacian[group], 0, axis=0)
            group_ieeg_laplacian[group] = np.delete(group_ieeg_laplacian[group], group_len[group] - 2, axis=0)
        elif data_class == 'epoch':
            group_ieeg_laplacian[group] = np.delete(group_ieeg_laplacian[group], 0, axis=1)
            group_ieeg_laplacian[group] = np.delete(group_ieeg_laplacian[group], group_len[group] - 2, axis=1)

    for group in group_chan:
        ch_name = group_ieeg[group].ch_names
        group_ieeg[group].drop_channels([ch_name[0], ch_name[-1]])
        group_ieeg[group]._data = group_ieeg_laplacian[group] * 1e-6

    group_0 = list(group_chan.keys())[0]
    laplacian_ieeg = group_ieeg[group_0]
    group_ieeg.pop(group_0)
    for name in group_ieeg:
        if not (name == 'DC'):
            laplacian_ieeg.add_channels([group_ieeg[name]])

    return laplacian_ieeg




