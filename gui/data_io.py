# -*- coding: utf-8 -*-
'''
@File : data_io.py
@Author : BarryLiu
@Time : 2020/12/1 16:00
@Desc :
'''
import scipy.io as sio

def write_raw_edf(fname, raw):
    """Export raw to EDF/BDF file (requires pyEDFlib)."""
    from pathlib import Path
    import pyedflib

    ext = "".join(Path(fname).suffixes)
    if ext == ".edf":
        filetype = pyedflib.FILETYPE_EDFPLUS
        dmin, dmax = -32768, 32767
    elif ext == ".bdf":
        filetype = pyedflib.FILETYPE_BDFPLUS
        dmin, dmax = -8388608, 8388607
    data = raw.get_data() * 1e6  # convert to microvolts
    fs = raw.info["sfreq"]
    nchan = raw.info["nchan"]
    ch_names = raw.info["ch_names"]
    if raw.info["meas_date"] is not None:
        meas_date = raw.info["meas_date"]
    else:
        meas_date = None
    prefilter = (f"{raw.info['highpass']}Hz - "
                 f"{raw.info['lowpass']}")
    pmin, pmax = data.min(axis=1), data.max(axis=1)
    f = pyedflib.EdfWriter(fname, nchan, filetype)
    channel_info = []
    data_list = []
    for i in range(nchan):
        channel_info.append(dict(label=ch_names[i],
                                 dimension="uV",
                                 sample_rate=fs,
                                 physical_min=pmin[i],
                                 physical_max=pmax[i],
                                 digital_min=dmin,
                                 digital_max=dmax,
                                 transducer="",
                                 prefilter=prefilter))
        data_list.append(data[i])
    f.setTechnician("Exported by MNELAB")
    f.setSignalHeaders(channel_info)
    if raw.info["meas_date"] is not None:
        f.setStartdatetime(meas_date)
    # note that currently, only blocks of whole seconds can be written
    f.writeSamples(data_list)
    for ann in raw.annotations:
        f.writeAnnotation(ann["onset"], ann["duration"], ann["description"])


def write_raw_set(fname, raw):
        """Export raw to EEGLAB .set file."""
        from numpy.core.records import fromarrays
        data = raw.get_data() * 1e6  # convert to microvolts
        fs = raw.info["sfreq"]
        times = raw.times
        ch_names = raw.info["ch_names"]
        chanlocs = fromarrays([ch_names], names=["labels"])
        events = fromarrays([raw.annotations.description,
                             raw.annotations.onset * fs + 1,
                             raw.annotations.duration * fs],
                            names=["type", "latency", "duration"])
        sio.savemat(fname + '.set', dict(EEG=dict(data=data,
                                     setname=fname,
                                     nbchan=data.shape[0],
                                     pnts=data.shape[1],
                                     trials=1,
                                     srate=fs,
                                     xmin=times[0],
                                     xmax=times[-1],
                                     chanlocs=chanlocs,
                                     event=events,
                                     icawinv=[],
                                     icasphere=[],
                                     icaweights=[])),
                                     appendmat=False)