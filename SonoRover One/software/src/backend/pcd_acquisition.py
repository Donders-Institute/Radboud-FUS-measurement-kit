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
import sys
import time

# Miscellaneous packages
from datetime import datetime
from importlib import resources as impresources
import matplotlib.pyplot as plt
import numpy as np

# Own packages
from fus_driving_systems import config as fds_config
from fus_driving_systems import utils as fds_utils
from backend import utils, sequence, picoscope as ps, acquisition as acq
import config as sr_config
from config.config import config_info, read_additional_config


def perform_pcd_acquisition(picoscope_serial, transducer_serial, driving_system_serial,
                            output_dir='C:\\Temp\\PCD_acquisition_output', sampl_freq_multi=50,
                            acquisition_time=500, pulse_dur=0.2, amplitude=5, all_elem_ampl=1):
    """
    Performs a Passive Cavitation Detection (PCD) measurement.

    This function initializes the PicoScope and the driving system, then collects measurement
    data to assess the transducer's functionality. The acquired data is compared with a
    predefined baseline.

    Parameters
    ----------
    picoscope_serial : str
        Serial number of the PicoScope device.
    transducer_serial : str
        Serial number of the transducer used for acquisition.
    driving_system_serial : str
        Serial number of the driving system.
    output_dir : str, optional
        Path to save the acquired data. Default is "C:\\Temp\\PCD_acquisition_output".
    sampl_freq_multi : int, optional
        Sampling frequency multiplier for the PicoScope. Default is 50.
    acquisition_time : int, optional
        Time duration of the signal acquisition in microseconds. Default is 500 µs.
    pulse_dur : float, optional
        Pulse duration in milliseconds. Default is 0.2 ms.
    amplitude : int, optional
        Excitation amplitude in percentage. Default is 5%.
    all_elem_ampl : int, optional
        Default amplitude for all elements. Default is 1.

    Returns
    -------
    None
    """

    # Check amplitudes
    if amplitude > 10:
        sys.exit(f'Amplitude of {amplitude} [%] for firing all elements at once exceeds 10 [%] ' +
                 'and might damage the PCD element. Stop measurement.')
    if all_elem_ampl > 5:
        sys.exit(f'Amplitude of {amplitude} [%] for firing one element at a time exceeds 5 [%] ' +
                 'and might damage the PCD element. Stop measurement.')

    _load_config_files()

    # Initialize equipment
    pico_object, seq = _initialize_equipment(picoscope_serial, transducer_serial,
                                             driving_system_serial, pulse_dur, all_elem_ampl)

    is_exist = os.path.exists(output_dir)
    if not is_exist:
        # Create a new directory because it does not exist
        os.makedirs(output_dir)

    pcd_acq = acq.Acquisition(None, False)

    try:
        # Connect with PicoScope
        print('Initialize PicoScope connection...', end='\n')
        pcd_acq.init_scope(sampl_freq_multi, acquisition_time, pico_object.pico_py_ident,
                           seq.transducer.fund_freq)

        time.sleep(5)

        # Connect with driving system
        print('Initialize driving system connection...', end='\n')
        ds_manufact = seq.driving_sys.manufact
        ds_connect_info = seq.driving_sys.connect_info
        pcd_acq.init_ds(ds_manufact, ds_connect_info, is_ac_align=False,
                        protocol_name='PCD_acquisition', check_message=False, log_path=output_dir)

        # Acquire and process data
        _acquire_and_save_data(pcd_acq, seq, pico_object, output_dir, acquisition_time, amplitude)

    finally:
        pcd_acq.close_all()


def _load_config_files():
    """
    Loads additional configuration files for the fus_driving_systems and PCD acquisition.
    """

    # Read additional fus_driving_systems config file
    inp_file = impresources.files(fds_config) / fds_utils.get_config_file()
    read_additional_config(inp_file)

    # Read additional pcd config
    pcd_ini_file = impresources.files(sr_config) / utils.get_pcd_config_file()
    read_additional_config(pcd_ini_file)


def _initialize_equipment(picoscope_serial, transducer_serial, driving_system_serial, pulse_dur,
                          all_elem_ampl):
    """
    Initializes the PicoScope and driving system sequence.
    """

    # Set equipment
    pico_object = ps.PicoScope()
    pico_object.set_pico_info(picoscope_serial)

    seq = sequence.CharacSequence()
    seq.driving_sys = driving_system_serial
    seq.transducer = transducer_serial
    seq.pulse_dur = pulse_dur

    seq.set_focus_wrt_mid_bowl(seq.transducer.natural_foc, False)
    seq.ampl = all_elem_ampl

    return pico_object, seq


def _acquire_and_save_data(pcd_acq, seq, pico_object, output_dir, acquisition_time, amplitude):
    """
    Handles the acquisition, processing, and saving of data.
    """

    baseline_path = config_info[seq.transducer.serial]['Baseline path']
    baseline_filenames = config_info[seq.transducer.serial]['Baseline files'].split('\n')
    n_elem = seq.transducer.elements
    for i_elem in range(n_elem + 1):
        raw_baseline_filename = baseline_filenames[i_elem]
        raw_baseline_path = os.path.join(baseline_path, raw_baseline_filename)

        amplitudes = [0] * n_elem
        # Send sequence to driving system
        print('Send sequence to driving system...', end='\n')
        pcd_acq.equipment["ds"].send_sequence(seq)

        volt_data = pcd_acq.acquire_data(attempt=0, sequence=seq)
        time_us = np.linspace(0, acquisition_time, pcd_acq.sample_count)

        date_time = datetime.now()
        timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

        elem_name = f'elem_{i_elem}'
        elem_title = f'Element {i_elem}'
        if i_elem == 0:
            elem_name = 'all_elems'
            elem_title = 'All elements'

        filename = (f'PCD_acquisition_{timestamp}_{elem_name}_of_{seq.transducer.serial}_' +
                    f'{seq.driving_sys.serial}')
        output_path = os.path.join(output_dir, filename + '.png')

        raw_path = os.path.join(output_dir, filename + '.raw')
        with open(raw_path, 'ab') as outraw:
            volt_data.tofile(outraw)

        ampl_title = [f'{x:.1f}' for x in seq.ampl]
        fig_title = (f'{elem_title} - {seq.transducer.name} \n {seq.driving_sys.name} -' +
                     f' {pico_object.pico_py_ident}, ' +
                     f'pulse: {seq.pulse_dur:.3f} [ms], ampl.: {ampl_title} [%]')

        _plot_comparison_fig(time_us, raw_baseline_path, volt_data, fig_title, output_path)

        if i_elem < n_elem:
            amplitudes[i_elem] = amplitude
            seq.ampl = amplitudes

        # wait for reflections to go away
        time.sleep(2)


def _plot_comparison_fig(time_us, raw_path, volt_data, title, output_path):
    """
    Plots and saves a comparison figure between baseline and acquired voltage data.
    """

    with open(raw_path, 'rb') as inraw:
        raw_baseline_data = np.fromfile(inraw, dtype=np.float32)

    # Calculate RMS
    base_sqr_volt = np.square(raw_baseline_data)
    base_mean_volt = np.mean(base_sqr_volt)
    base_rms = np.sqrt(base_mean_volt)

    # Calculate RMS
    sqr_volt = np.square(volt_data)
    mean_volt = np.mean(sqr_volt)
    rms = np.sqrt(mean_volt)

    # Compute the absolute max of both y-values
    y_abs_max = max(abs(raw_baseline_data).max(), abs(volt_data).max())

    # Define symmetric y-axis limits
    y_min, y_max = -y_abs_max, y_abs_max

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.suptitle(title)

    fig.text(0.5, 0.005, 'Time [us]', ha='center')
    fig.text(0.005, 0.5, 'Measured voltage [V]', va='center', rotation='vertical')

    ax1.plot(time_us, raw_baseline_data, color='g')
    ax1.axhline(y=base_rms, color='g', linestyle='--', label=f'{base_rms:.2f} V')
    ax1.text(x=max(time_us) * 0.95, y=base_rms, s=f'RMS {base_rms:.2f} [V]', color='g',
             verticalalignment='bottom', horizontalalignment='right')
    ax1.set_title('Baseline')
    ax1.set_ylim(y_min, y_max)
    ax1.grid(True)

    ax2.plot(time_us, volt_data, color='r')
    ax2.axhline(y=rms, color='r', linestyle=':', label=f'{rms:.2f} V')
    ax2.text(x=max(time_us) * 0.95, y=rms, s=f'RMS {rms:.2f} [V]', color='r',
             verticalalignment='bottom', horizontalalignment='right')
    ax2.set_title('Acquired')
    ax2.set_ylim(y_min, y_max)
    ax2.grid(True)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path)
    plt.show()
