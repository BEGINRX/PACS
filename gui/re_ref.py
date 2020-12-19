import numpy as np
import traceback


def get_group_chan(raw):
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
        del ch_group_cont['E']
        del ch_group_cont['DC']
    except Exception as error:
        if error.args[0] == "KeyError: 'E'":
            pass
    try:
        for group in ch_group_cont:
            [ch_group_cont[group].remove(chan) for chan in chan_del[group]]
            if '\'' in group:
                ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[2:])))
            else:
                ch_group_cont[group].sort(key=lambda chan: (chan[0], int(chan[1:])))
    except:
        traceback.print_exc()

    return ch_group_cont


def car_ref(raw):
    '''
    Reference sEEG data using Common Average Reference(CAR)
    :param raw: instance of Raw
                raw data
    :return: instance of Raw
             re-referenced data
    '''
    new_raw = raw.copy()
    data = new_raw._data * 1e6
    data_mean = np.mean(data, axis=0)
    data_ref = (data - data_mean) * 1e-6
    new_raw._data = data_ref

    return new_raw


def gwr_ref(raw, coord_path):
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
    loca_data = get_anat_loc(coord_path)
    chan_gm, chan_wm = get_gchan_wchan(loca_data)

    raw_gm = raw.copy().pick_channels(chan_gm)
    raw_wm = raw.copy().pick_channels(chan_wm)

    data_gm = raw_gm._data
    data_gm_mean = np.mean(data_gm, axis=0)
    raw_gm._data = data_gm - data_gm_mean

    data_wm = raw_wm._data
    data_wm_mean = np.mean(data_wm, axis=0)
    raw_wm._data = data_wm - data_wm_mean

    raw_ref = raw_gm.copy().add_channels([raw_wm])

    return raw_ref


def esr_ref(raw):
    '''
    Reference sEEG data using Electrode Shaft Reference(ESR)
    :param raw: instance of Raw
                raw data
    :return: instance of raw
             re-referenced data
    '''
    # 获取分组
    group_chan = get_group_chan(raw)

    ch_data = {group: raw.copy().pick_channels(group_chan[group]) for group in group_chan}
    for group in ch_data:
        data = ch_data[group]._data * 1e3
        data_mean = np.mean(data, axis=0)
        ch_data[group]._data = (data - data_mean) * 1e-3

    group_0 = list(group_chan.keys())[0]
    raw_new = ch_data[group_0]
    ch_data.pop(group_0)
    for name in ch_data:
        if not (name == 'DC') or not (name == 'E'):
            raw_new.add_channels([ch_data[name]])

    return raw_new


def bipolar_ref(raw, mode='auto'):
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
    group_chan = get_group_chan(raw)
    group_data = {group: raw.copy().pick_channels(group_chan[group]).reorder_channels(group_chan[group])
                  for group in group_chan}

    group_data_new = {group: np.diff(group_data[group]._data, axis=0) for group in group_chan}

    # 保留最后一个没东西减的通道，但是不显示
    miss_data = dict()
    for group in group_data:
        print(group_chan[group][0])
        miss_data[group] = group_data[group].copy().pick_channels([group_chan[group][0]])
        group_data[group].drop_channels(group_chan[group][0])._data = group_data_new[group]
        if mode == 'keep':
            group_data[group].add_channels([miss_data[group]])

    group_0 = list(group_chan.keys())[0]
    raw_new = group_data[group_0]
    group_data.pop(group_0)
    for name in group_data:
        if not (name == 'DC') or not (name == 'E'):
            raw_new.add_channels([group_data[name]])

    return raw_new, miss_data


def monopolar_ref(raw, ref_chan):
    '''
    :param raw: instance of Raw
                raw data
    :param ref_chan: list
                     the channels' name chosen as ref channel
    :return: instance of raw
             the re-ref raw data
    '''
    chan = raw.ch_names

    ref_raw = raw.copy().pick_channels(ref_chan)
    ref_data = ref_raw._data
    ref_mean = np.mean(ref_data, axis=0)

    new_raw = raw.copy()
    data = new_raw._data - ref_mean
    new_raw._data = data

    return new_raw


def laplacian_ref(raw, mode='auto'):
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
    group_chan = get_group_chan(raw)
    group_len = {group: len(group_chan[group]) for group in group_chan}
    group_data = {group: raw.copy().pick_channels(group_chan[group]) for group in group_chan}
    group_data = {group: group_data[group].reorder_channels(group_chan[group])
                  for group in group_chan}
    group_data_only = {group: group_data[group]._data * 1e3 for group in group_data}

    for group in group_data_only:
        for index in range(1, group_len[group] - 1):
            group_data_only[group][index] = group_data_only[group][index] - \
                                            np.divide(group_data_only[group][index - 1] +
                                                      group_data_only[group][index + 1], 2)
        group_data_only[group] = np.delete(group_data_only[group], 0, axis=0)
        group_data_only[group] = np.delete(group_data_only[group], group_len[group] - 2, axis=0)

    miss_data = dict()
    for group in group_chan:
        ch_name = group_data[group].ch_names
        miss_data[group] = group_data[group].copy().pick_channels([ch_name[0], ch_name[-1]])
        group_data[group].drop_channels([ch_name[0], ch_name[-1]])
        group_data[group]._data = group_data_only[group] * 1e-3
        if mode == 'keep':
            group_data[group].add_channels([miss_data[group]]).reorder_channels(group_chan[group])

    group_0 = list(group_chan.keys())[0]
    raw_new = group_data[group_0]
    group_data.pop(group_0)
    for name in group_data:
        if not (name == 'DC') or not (name == 'E'):
            raw_new.add_channels([group_data[name]])

    return raw_new, miss_data




