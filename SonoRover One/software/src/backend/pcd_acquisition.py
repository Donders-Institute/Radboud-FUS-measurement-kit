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
If you use this kit in your research or project, please refer to the 'How to Cite' section in the
README.md file of https://github.com/Donders-Institute/Radboud-FUS-measurement-kit.
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
from backend.utils import get_config_value
from config.logging_config import logger

from fus_driving_systems import config as fds_config
from fus_driving_systems import utils as fds_utils
from backend import utils, sequence, picoscope as ps, acquisition as acq
import config as sr_config
from config.config import config_info, read_additional_config


def perform_pcd_acquisition(picoscope_serial, transducer_serial, driving_system_serial,
                            output_dir=None, sampl_freq_multi=None, acquisition_time=None,
                            pulse_dur=None, amplitude=None, all_elem_ampl=None):
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
        Path to save the acquired data. Default is read from config.
    sampl_freq_multi : int, optional
        Sampling frequency multiplier for the PicoScope. Default is read from config.
    acquisition_time : int, optional
        Time duration of the signal acquisition in microseconds. Default is read from config..
    pulse_dur : float, optional
        Pulse duration in milliseconds. Default is read from config.
    amplitude : int, optional
        Excitation amplitude in percentage. Default is read from config.
    all_elem_ampl : int, optional
        Default amplitude for all elements. Default is read from config.

    Returns
    -------
    None
    """

    _load_config_files()

    # Retrieve values from config only if they are None
    if output_dir is None:
        output_dir = get_config_value(logger, config_info, 'Default', 'output_dir',
                                      'C:\\Temp\\PCD_acquisition_output')

    if sampl_freq_multi is None:
        sampl_freq_multi = float(get_config_value(logger, config_info, 'Default',
                                                  'sampl_freq_multi', 50))

    if acquisition_time is None:
        acquisition_time = float(get_config_value(logger, config_info, 'Default',
                                                  'acquisition_time_us', 500))

    if pulse_dur is None:
        pulse_dur = float(get_config_value(logger, config_info, 'Default', 'pulse_dur_ms', 0.2))

    if amplitude is None:
        amplitude = float(get_config_value(logger, config_info, 'Default', 'per_elem_ampl', 5))

    if all_elem_ampl is None:
        all_elem_ampl = float(get_config_value(logger, config_info, 'Default', 'all_elems_ampl', 1))

    # Check amplitudes
    per_elem_limit = float(get_config_value(logger, config_info, 'Limit', 'per_elem_ampl', 10))
    all_elem_limit = float(get_config_value(logger, config_info, 'Limit', 'all_elems_ampl', 5))
    if amplitude > per_elem_limit:
        message = (f'Amplitude of {amplitude} [%] for firing all elements at once exceeds ' +
                   f'{per_elem_limit:.2f} [%] and might damage the PCD element. Stop measurement.')
        logger.critical(message)
        sys.exit(message)
    if all_elem_ampl > all_elem_limit:
        message = (f'Amplitude of {amplitude} [%] for firing one element at a time exceeds ' +
                   f'{all_elem_limit:.2f} [%] and might damage the PCD element. Stop measurement.')
        logger.critical(message)
        sys.exit(message)

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
        message = 'Initialize PicoScope connection...'
        logger.info(message)
        print(message, end='\n')
        pcd_acq.init_scope(sampl_freq_multi, acquisition_time, pico_object.pico_py_ident,
                           seq.transducer.fund_freq)

        time.sleep(5)

        # Connect with driving system
        message = 'Initialize driving system connection...'
        logger.info(message)
        print(message, end='\n')
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

    # Fix to bypass conversion equations checks TODO: permanent fix is on backlog
    seq.transducer.max_foc = 100

    seq.pulse_dur = pulse_dur

    seq.set_focus_wrt_mid_bowl(seq.transducer.natural_foc, False)
    seq.ampl = all_elem_ampl

    return pico_object, seq


def _acquire_and_save_data(pcd_acq, seq, pico_object, output_dir, acquisition_time, amplitude):
    """
    Handles the acquisition, processing, and saving of data.
    """

    baseline_path = get_config_value(logger, config_info, seq.transducer.serial, 'Baseline path',
                                     '')
    baseline_filenames = get_config_value(logger, config_info, seq.transducer.serial,
                                          'Baseline files', '').split('\n')

    n_elem = seq.transducer.elements
    for i_elem in range(n_elem + 1):
        if baseline_filenames == '':
            raw_baseline_filename = ''
        else:
            raw_baseline_filename = baseline_filenames[i_elem]

        raw_baseline_path = os.path.join(baseline_path, raw_baseline_filename)

        amplitudes = [0] * n_elem
        # Send sequence to driving system
        message = 'Send sequence to driving system...'
        logger.info(message)
        print(message, end='\n')
        pcd_acq.equipment["ds"].send_sequence(seq)

        volt_data = pcd_acq.acquire_data(attempt=0, sequence=seq)
        time_us = np.linspace(0, acquisition_time, pcd_acq.sample_count)

        date_time = datetime.now()
        timestamp_format = get_config_value(logger, config_info, 'Logging', 'Timestamp format',
                                            '%Y-%m-%d_%H-%M-%S')
        timestamp = date_time.strftime(timestamp_format)

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

    if raw_path != '':
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

    if raw_path != '':
        # Compute the absolute max of both y-values
        y_abs_max = max(abs(raw_baseline_data).max(), abs(volt_data).max())

    # Define symmetric y-axis limits
    y_min, y_max = -y_abs_max, y_abs_max

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    fig.suptitle(title)

    fig.text(0.5, 0.005, 'Time [us]', ha='center')
    fig.text(0.005, 0.5, 'Measured voltage [V]', va='center', rotation='vertical')

    if raw_path != '':
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
