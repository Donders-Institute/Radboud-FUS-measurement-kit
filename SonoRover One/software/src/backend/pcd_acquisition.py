# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Margely Cornelissen, Stein Fekkes (Radboud University) and Erik Dumont (Image
Guided Therapy)

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

**Attribution Notice**:
If you use this kit in your research or project, please include the following attribution:
Margely Cornelissen, Stein Fekkes (Radboud University, Nijmegen, The Netherlands) & Erik Dumont
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 1.0),
https://github.com/Donders-Institute/Radboud-FUS-measurement-kit
"""

# Basic packages

# Miscellaneous packages
import matplotlib.pyplot as plt
import numpy as np

# Own packages
from fus_driving_systems.igt import igt_ds as fds_igt
from fus_driving_systems.sonic_concepts import sonic_concepts_ds as fds_sc

from config.config import config_info
from backend.input_parameters import InputParameters

from fus_driving_systems import driving_system as ds
from fus_driving_systems import transducer as td
from backend import pico
import backend.picoscope as ps
from backend import sequence
import backend.acquisition as acq


class PCDAcquisition(acq.Acquisition):

    def __init__(self, input_param, init_equip=True):
        super().__init__(input_param, init_equip=False)


def perform_pcd_acquisition(picoscope_name, transducer, driving_system, sampl_freq_multi=50,
                            acquisition_time=500, pulse_dur=0.05, amplitude=20,
                            focus_wrt_exit_plane=50):
    """

    Parameters
    ----------
    picoscope : TYPE
        DESCRIPTION.
    transducer : TYPE
        DESCRIPTION.
    ds : TYPE
        DESCRIPTION.
    sampl_freq_multi : TYPE, optional
        DESCRIPTION. The default is 50 [-].
    acquisition_time : TYPE, optional
        DESCRIPTION. The default is 500 [us].
    pulse_dur : TYPE, optional
        DESCRIPTION. The default is 0.05 [ms].
    amplitude : TYPE, optional
        DESCRIPTION. The default is 20 [%].
    focus_wrt_exit_plane : TYPE, optional
        DESCRIPTION. The default is 50 [mm].

    Returns
    -------
    None.

    """

    input_param = InputParameters()

    # Set equipment
    input_param.picoscope = picoscope_name
    input_param.transducer = transducer
    input_param.driving_sys = driving_system

    # Set sampling frequency multiplication
    input_param.sampl_freq_multi = sampl_freq_multi
    input_param.acquisition_time = acquisition_time

    # TODO: when setting pulse duration set other timing parameters to pulse duration
    seq = sequence.CharacSequence()
    seq.pulse_dur = pulse_dur
    seq.pulse_rep_int = pulse_dur
    seq.pulse_train_dur = pulse_dur
    seq.pulse_train_rep_int = pulse_dur
    seq.pulse_train_rep_dur = pulse_dur/1000  # convert ms to s

    seq.focus_wrt_exit_plane = focus_wrt_exit_plane
    seq.ampl = amplitude

    pcd_acq = acq.Acquisition(input_param, False)
    pcd_acq.sequence = seq

    # Connect with PicoScope
    print('Initialize PicoScope connection...', end='\n')
    pcd_acq.equipment["scope"] = pico.getScope(input_param.picoscope.pico_py_ident)
    pcd_acq._init_scope(sampl_freq_multi, acquisition_time)

    # Connect with driving system
    print('Initialize driving system connection...', end='\n')
    pcd_acq._init_ds()

    # Send sequence to driving system
    print('Send sequence to driving system...', end='\n')
    pcd_acq.equipment["ds"].send_sequence(seq)

    # TODO: enable shooting an element a time - for loop and end with shooting all elements

    volt_data = pcd_acq.acquire_data()
    time_us = np.linspace(0, acquisition_time, pcd_acq.sample_count)

    plt.plot(time_us, volt_data)
    plt.xlabel('Time [us]')
    plt.ylabel('Measured voltage [mV]')
    plt.title('Measured ultrasound signal')
    plt.show()
