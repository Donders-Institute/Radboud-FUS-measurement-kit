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
import os

# Miscellaneous packages
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Own packages
from fus_driving_systems import driving_system as ds
from fus_driving_systems import transducer as td
import backend.picoscope as ps
from backend import sequence
import backend.acquisition as acq


def perform_pcd_acquisition(picoscope_serial, transducer_serial, driving_system_serial,
                            output_dir='C:\\Temp\\PCD_acquisition_output', sampl_freq_multi=50,
                            acquisition_time=500, pulse_dur=0.05, amplitude=20,
                            focus_wrt_exit_plane=50):
    """

    Parameters
    ----------
    picoscope_serial : TYPE
        DESCRIPTION.
    transducer_serial : TYPE
        DESCRIPTION.
    driving_system_serial : TYPE
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

    # Set equipment
    pico_object = ps.PicoScope()
    pico_object.set_pico_info(picoscope_serial)

    tran_object = td.Transducer()
    tran_object.set_transducer_info(transducer_serial)

    ds_object = ds.DrivingSystem()
    ds_object.set_ds_info(driving_system_serial)

    seq = sequence.CharacSequence()
    seq.pulse_dur = pulse_dur

    seq.focus_wrt_exit_plane = focus_wrt_exit_plane
    seq.ampl = amplitude

    is_exist = os.path.exists(output_dir)
    if not is_exist:
        # Create a new directory because it does not exist
        os.makedirs(output_dir)

    pcd_acq = acq.Acquisition(None, False)

    # Connect with PicoScope
    print('Initialize PicoScope connection...', end='\n')
    pcd_acq.init_scope(sampl_freq_multi, acquisition_time, pico_object.pico_py_ident,
                       tran_object.oper_freq)

    # Connect with driving system
    print('Initialize driving system connection...', end='\n')
    ds_manufact = ds_object.manufact
    ds_connect_info = ds_object.connect_info
    pcd_acq.init_ds(ds_manufact, ds_connect_info, is_ac_align=False,
                    protocol_name='PCD_acquisition')

    n_elem = len(tran_object.elements)
    for i_elem in range(n_elem + 1):
        amplitudes = [0] * n_elem
        # Send sequence to driving system
        print('Send sequence to driving system...', end='\n')
        pcd_acq.equipment["ds"].send_sequence(seq)

        volt_data = pcd_acq.acquire_data(attempt=0, sequence=seq)
        time_us = np.linspace(0, acquisition_time, pcd_acq.sample_count)

        date_time = datetime.now()
        timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

        elem_name = f'elem_{i_elem}'
        if i_elem == 0:
            elem_name = 'all_elem'

        filename = (f'PCD_acquisition_{timestamp}_{elem_name}_of_{tran_object.serial}_' +
                    f'{ds_object.serial}.png')
        output_path = os.path.join(output_dir, filename)

        plt.plot(time_us, volt_data)
        plt.xlabel('Time [us]')
        plt.ylabel('Measured voltage [mV]')
        plt.title(f'Measured ultrasound signal for {tran_object.name} - {ds_object.name} with ' +
                  f'{pico_object.name} \n sampl_freq_multi: {sampl_freq_multi:.0f}, ' +
                  f'acquisition_time: {acquisition_time:.1f} [us], pulse_dur: {pulse_dur:.3f} ' +
                  f'[ms], amplitude: {amplitude:.0f} [%], focus wrt exit plane: ' +
                  f'{focus_wrt_exit_plane:.1f} [mm]')

        plt.savefig(output_path)
        plt.show()

        if i_elem < n_elem:
            amplitudes[i_elem] = amplitude
            seq.ampl = amplitudes


if __name__ == '__main__':

    # location to store measurement data
    output_dir = "C:\\Temp\\PCD_acquisition_output"

    # to check available picoscopes: print(ps.get_pico_serials())
    # PicoScope 5442A - embedded in IGT driving system (128 ch.)
    # PicoScope 524? - embedded in IGT driving system (32 ch.)
    picoscope_serial = '5442A'

    # to check available transducers: print(transducer.get_tran_serials())
    transducer_serial = 'IS_PCD15278_01001'

    # to check available driving systems: print(driving_system.get_ds_serials())
    driving_system_serial = 'IGT-32-ch_comb_1x10-ch'

    sampl_freq_multi = 50  # Picoscope sampling frequency multiplication factor, at least 2.
    acquisition_time = 500  # [us], PCD acquisition time.
    pulse_dur = 0.5  # [ms], Pulse duration of the sequence.
    amplitude = 20  # [%], Power of the driving system.
    focus_wrt_exit_plane = 50  # [mm], Focal depth of the sequence w.r.t. exit plane respresenting the FWHM middle

    perform_pcd_acquisition(picoscope_serial, transducer_serial, driving_system_serial, output_dir,
                            sampl_freq_multi, acquisition_time, pulse_dur, amplitude,
                            focus_wrt_exit_plane)
