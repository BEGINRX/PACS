import numpy as np
import traceback
import mne


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


def get_chan_group(raw):
    '''
    :param raw: instance of Raw
                raw data
    :return: dict
             electrodes in the same shaft
    '''
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
    return chan_group


def car_ref(raw, data_class):
    '''
    Reference sEEG data using Common Average Reference(CAR)
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
    Reference sEEG data using Gray-white Matter Reference(GWR)
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


def esr_ref(raw, data_class):
    '''
    Reference sEEG data using Electrode Shaft Reference(ESR)
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


def bipolar_ref(raw, data_class, mode='auto'):
    '''
    Reference sEEG data using Bipolar Reference
    :param raw: instance of Raw
                raw data
    :param mode: str
        if mode = 'auto' then don't show the first contact in each shafts
        if mode ='keep' then show
    :return: instance of raw
             data and raw data of the first contact in each shafts
    '''
    group_chan = get_chan_group(raw)
    group_data = {group: raw.copy().pick_channels(group_chan[group]).reorder_channels(group_chan[group])
                  for group in group_chan}
    if data_class == 'raw':
        group_data_new = {group: np.diff(group_data[group]._data, axis=0) for group in group_chan}
    elif data_class =='epoch':
        group_data_new = {group: np.diff(group_data[group]._data, axis=1) for group in group_chan}

    # 保留最后一个没东西减的通道，但是不显示
    miss_data = dict()
    for group in group_data:
        ch_name = group_data[group].ch_names
        miss_data[group] = group_data[group].copy().pick_channels([group_chan[group][0]])
        group_data[group].drop_channels(group_chan[group][0])._data = group_data_new[group]
        if mode == 'keep':
            if data_class == 'raw':
                group_data[group].add_channels([miss_data[group]]).reorder_channels(group_chan[group])
            elif data_class == 'epoch':
                group_data[group] = mne.epochs.add_channels_epochs([group_data[group], miss_data[group]])
                group_data[group].reorder_channels(ch_name)

    group_0 = list(group_chan.keys())[0]
    raw_new = group_data[group_0]
    group_data.pop(group_0)
    for name in group_data:
        if not (name == 'DC'):
            raw_new.add_channels([group_data[name]])

    return raw_new, miss_data


def monopolar_ref(raw, data_class, ref_chan):
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


def laplacian_ref(raw, data_class, mode='auto'):
    '''
    Reference sEEG data using Laplacian Reference
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
    group_data = {group: raw.copy().pick_channels(group_chan[group]) for group in group_chan}
    group_data = {group: group_data[group].reorder_channels(group_chan[group])
                  for group in group_chan}
    group_data_only = {group: group_data[group]._data * 1e6 for group in group_data}
    group_data_new = {group: np.zeros(group_data[group].copy()._data.shape) for group in group_data}
    for group in group_data_only:
        for index in range(1, group_len[group] - 1):
            if data_class == 'raw':
                group_data_new[group][index] = group_data_only[group][index] - \
                                            np.divide(group_data_only[group][index - 1] +
                                                      group_data_only[group][index + 1], 2)
            elif data_class == 'epoch':
                group_data_new[group][:, index, :] = group_data_only[group][:, index, :] - \
                                                      np.divide(group_data_only[group][:, index - 1, :] +
                                                      group_data_only[group][:, index + 1, :], 2)
        if data_class == 'raw':
            group_data_new[group] = np.delete(group_data_new[group], 0, axis=0)
            group_data_new[group] = np.delete(group_data_new[group], group_len[group] - 2, axis=0)
        elif data_class == 'epoch':
            group_data_new[group] = np.delete(group_data_new[group], 0, axis=1)
            group_data_new[group] = np.delete(group_data_new[group], group_len[group] - 2, axis=1)

    miss_data = dict()
    for group in group_chan:
        ch_name = group_data[group].ch_names
        miss_data[group] = group_data[group].copy().pick_channels([ch_name[0], ch_name[-1]])
        group_data[group].drop_channels([ch_name[0], ch_name[-1]])
        group_data[group]._data = group_data_new[group] * 1e-6
        if mode == 'keep':
            if data_class == 'raw':
                group_data[group].add_channels([miss_data[group]]).reorder_channels(group_chan[group])
            elif data_class == 'epoch':
                group_data[group] = mne.epochs.add_channels_epochs([group_data[group], miss_data[group]])
                group_data[group].reorder_channels(ch_name)

    group_0 = list(group_chan.keys())[0]
    raw_new = group_data[group_0]
    group_data.pop(group_0)
    for name in group_data:
        if not (name == 'DC'):
            raw_new.add_channels([group_data[name]])

    return raw_new, miss_data




