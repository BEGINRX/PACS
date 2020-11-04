import numpy as np


def car_ref(raw):
    '''Reference sEEG data using Common Average Reference(CAR)'''
    data = raw._data * 1e6
    data_mean = np.mean(data, axis=0)
    data_ref = (data - data_mean) * 1e-6
    raw._data = data_ref

    return raw


def gwr_reref(raw):
    '''Reference sEEG data using Gray-white Matter Reference(GWR)'''

    return raw


def esr_reref(raw):
    '''Reference sEEG data using Electrode Shaft Reference(ESR)'''
    # 获取所有轴的名称
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
    for group in ch_group_cont:
        for index in range(length[i]):
            if ('\'' not in group) and ((group + '\'') in ch_group_cont[group][-1]):
                ch_group_cont[group].remove(ch_group_cont[group][-1])
            if ('DC' in ch_group_cont[group][-1]) and group != 'DC':
                ch_group_cont[group].remove(ch_group_cont[group][-1])
        i += 1

    ch_data = {group: raw.copy().pick_channels(ch_group_cont[group]) for group in ch_group_cont}
    for group in ch_data:
        data = ch_data[group]._data * 1e6
        data_mean = np.mean(data, axis=0)
        ch_data[group]._data = data - data_mean

    raw_new = ch_data['A']
    ch_data.pop('A')
    for name in ch_data:
        if not name == 'DC':
            # try:
            raw_new.add_channels([ch_data[name]])

    return raw_new


def bipolar_reref(raw):
    '''Reference sEEG data using Bipolar Reference'''

    return raw


def monopolar_reref(raw):
    '''Reference sEEG data using Monopolar Reference'''

    return raw


def laplacian_reref(raw):
    '''Reference sEEG data using Laplacian Reference'''

    return raw


