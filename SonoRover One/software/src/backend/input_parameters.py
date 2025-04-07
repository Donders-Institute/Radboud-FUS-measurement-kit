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

# Miscellaneous packages
import configparser

from datetime import datetime

# Own packages
from fus_driving_systems import driving_system as ds
from fus_driving_systems import transducer as tran

import backend.hydrophone as hp
import backend.picoscope as ps
from backend import sequence

from backend.utils import get_config_value
from config.logging_config import logger

from config.config import config_info as config


class InputParameters:
    """
    Class to manage input parameters that are applicable for the whole protocol/all sequences.

    Attributes:
        temp_dir_output (str): Temporary local output directory path.
        dir_output (str): Directory of output path on drive (results moved at the end to minimize
                                                             acquisition time).
        path_protocol_excel_file (str): Path to protocol Excel file.
        driving_sys (ds.DrivingSystem): Selected driving system object.
        transducer (td.Transducer): Selected transducer object.
        oper_freq (int): Operating frequency in [kHz].
        pos_com_port (str): COM port of positioning system.
        hydrophone (hp.Hydrophone): Selected hydrophone object.
        acquisition_time (float): Hydrophone acquisition time in microseconds.
        picoscope (ps.PicoScope): Selected PicoScope object.
        sampl_freq_multi (float): Picoscope sampling frequency multiplication factor.
        temp (float): Temperature of water in Celsius.
        dis_oxy (float): Dissolved oxygen level of water in mg/L.
        coord_zero (list): x, y, z coordinates of relative zero point.
        perform_all_seqs (bool): Flag indicating if all sequences should be performed at once.
        acd_param (dict): Adjustment and processing window parameters.
            adjust (int): Adjustment parameter for time of flight. It will adjust the windows
            [beg..end] with the time of flight when the row is along US propagation.
                adjust=-1 if top-left corner is far from transducer (decrease beg)
                adjust=+1 if top-left corner is close to the transducer (increase beg)
                adjust=0 : no adjustment
            begus (float): Beginning time of processing window in microseconds.
            endus (float): End time of processing window in microseconds.
        protocol (str): name of chosen protocol
        is_ac_align (bool): Flag indicating if acoustic alignment is chosen.
        sequences (list): List of US sequences to perform.
    """

    def __init__(self):
        """
        Initialize input parameters with default values and configurations.
        """

        self._temp_dir_output = get_config_value(logger, config, 'Characterization',
                                                 'Temporary output path',
                                                 'C:\\Temp\\General output folder')
        self._dir_output = get_config_value(logger, config, 'Characterization',
                                            'Default output directory', 'C:\\Temp')
        self._path_protocol_excel_file = get_config_value(logger, config, 'Characterization',
                                                          'Default protocol directory', 'C:\\Temp')

        # Get available driving systems and use the first one as default
        self._driving_sys = ds.DrivingSystem()
        self.driving_sys = ds.get_ds_serials()[0]

        # Get available transducers and use the first one as default
        self._transducer = tran.Transducer()
        self.transducer = tran.get_tran_serials()[0]

        self._oper_freq = self._transducer.fund_freq  # [kHz]

        self._pos_com_port = get_config_value(logger, config, 'Characterization',
                                              'default.pos_com_port', 'COM3')

        # Get available hydrophones, for logging purposes only
        self._hydrophone = hp.Hydrophone()
        self.hydrophone = hp.get_hydro_serials()[0]

        self._acquisition_time = float(get_config_value(logger, config, 'Characterization',
                                                        'default.acq_time_us', 500))  # microseconds

        # Get available PicoScope list
        self._picoscope = ps.PicoScope()
        self.picoscope = ps.get_pico_serials()[0]

        self._sampl_freq_multi = int(get_config_value(logger, config, 'Characterization',
                                                      'default.sampl_freq_multi', 50))

        # temperature in celsius
        self._temp = get_config_value(logger, config, 'Characterization', 'default.temp', '')

        # dissolved oxygen in mg/L
        self._dis_oxy = get_config_value(logger, config, 'Characterization', 'default.dis_oxy', '')

        x_coord_zero = float(get_config_value(logger, config, 'Characterization',
                                              'default.x_coord_zero', -62.2))
        y_coord_zero = float(get_config_value(logger, config, 'Characterization',
                                              'default.y_coord_zero', -60.6))
        z_coord_zero = float(get_config_value(logger, config, 'Characterization',
                                              'default.z_coord_zero', -155.528))
        self._coord_zero = [x_coord_zero, y_coord_zero, z_coord_zero]

        self._perform_all_seqs = get_config_value(logger, config, 'Characterization',
                                                  'default.perform_all_seqs', 'True') == 'True'

        self._acd_param = {
            "adjust": 0,
            "begus": 0,
            "endus": self._acquisition_time,
            }

        self._protocol = ''
        self._is_ac_align = False
        self._sequences = []

    def __str__(self):
        '''
        Returns a formatted string containing information about the input parameters.

        Returns:
            str: Formatted information about the input parameters.

        '''

        info = ''

        info += f"Path and filename of protocol excel file: {self._path_protocol_excel_file} \n "
        info += f"Temporary path of output: {self._temp_dir_output} \n "
        info += f"Path of output: {self._dir_output} \n "

        info += str(self._driving_sys)
        info += str(self._transducer)

        info += f"Operating frequency [kHz]: {self._oper_freq} \n "

        info += f"COM port of positioning system: {self._pos_com_port} \n "

        info += str(self._hydrophone)
        info += f"Hydrophone acquisition time [us]: {self._acquisition_time} \n "

        info += str(self._picoscope)
        info += f"Picoscope sampling frequency multiplication factor: {self._sampl_freq_multi} \n "

        info += f"Temperature of water [°C]: {self._temp} \n "
        info += f"Dissolved oxygen level of water [mg/L]: {self._dis_oxy} \n "

        info += f"Absolute G code xyz-coordinates of relative zero [mm]: [{self._coord_zero[0]}, {self._coord_zero[1]}, {self._coord_zero[2]}] \n "

        info += f"Perform all sequences in sequence without waiting for user input?: {self._perform_all_seqs} \n "

        info += f"Beginning time of processing window [us]: {self._acd_param['begus']} \n "
        info += f"End time of processing window [us]: {self._acd_param['endus']} \n "
        info += f"Moving processing window along?: {self._acd_param['adjust']} \n "

        info += f"Protocol name: {self._protocol} \n "
        info += f"Acoustic alignment?: {self._is_ac_align} \n "

        for seq in self._sequences:
            info += str(seq)

        return info

    @property
    def temp_dir_output(self):
        """
        Get the temporary directory output path.

        Returns:
            str: Temporary directory output path.
        """
        return self._temp_dir_output

    @temp_dir_output.setter
    def temp_dir_output(self, path):
        """
        Set the temporary directory output path.

        Parameters:
            path (str): Path to the temporary directory.
        """
        self._temp_dir_output = path

    @property
    def dir_output(self):
        """
        Get the directory output path.

        Returns:
            str: Directory output path.
        """
        return self._dir_output

    @dir_output.setter
    def dir_output(self, path):
        """
        Set the directory output path.

        Parameters:
            path (str): Path to the directory.
        """
        self._dir_output = path

    @property
    def path_protocol_excel_file(self):
        """
        Get the protocol Excel file path.

        Returns:
            str: Protocol Excel file path.
        """
        return self._path_protocol_excel_file

    @path_protocol_excel_file.setter
    def path_protocol_excel_file(self, path):
        """
        Set the protocol Excel file path.

        Parameters:
            path (str): Path to the protocol Excel file.
        """
        self._path_protocol_excel_file = path

    @property
    def driving_sys(self):
        """
        Getter method for the driving system.

        Returns:
            DrivingSystem: The driving system associated with the sequence.
        """

        return self._driving_sys

    @driving_sys.setter
    def driving_sys(self, serial):
        """
        Sets the driving system based on the provided serial number.

        Parameters:
            serial (str): Serial number of the driving system.
        """

        self._driving_sys.set_ds_info(serial)

    @property
    def transducer(self):
        """
        Getter method for the transducer.

        Returns:
            Transducer: The transducer associated with the sequence.
        """

        return self._transducer

    @transducer.setter
    def transducer(self, serial):
        """
        Sets the transducer based on the provided serial number.

        Parameters:
            serial (str): Serial number of the transducer.
        """

        self._transducer.set_transducer_info(serial)

    @property
    def oper_freq(self):
        """
        Get the operating frequency.

        Returns:
            int: Operating frequency in kHz.
        """
        return self._oper_freq

    @oper_freq.setter
    def oper_freq(self, frequency):
        """
        Set the operating frequency.

        Parameters:
            frequency (int): Operating frequency in kHz.
        """
        self._oper_freq = frequency

    @property
    def pos_com_port(self):
        """
        Get the COM port of the positioning system.

        Returns:
            str: COM port of the positioning system.
        """
        return self._pos_com_port

    @pos_com_port.setter
    def pos_com_port(self, port):
        """
        Set the COM port of the positioning system.

        Parameters:
            port (str): COM port of the positioning system.
        """
        self._pos_com_port = port

    @property
    def hydrophone(self):
        """
        Getter method for the hydrophone.

        Returns:
            Hydrophone: The hydrophone associated with the sequence.
        """

        return self._hydrophone

    @hydrophone.setter
    def hydrophone(self, serial):
        """
        Sets the hydrophone based on the provided serial number.

        Parameters:
            serial (str): Serial number of the hydrophone.
        """

        self._hydrophone.set_hydro_info(serial)

    @property
    def acquisition_time(self):
        """
        Get the hydrophone acquisition time.

        Returns:
            float: Acquisition time in microseconds.
        """
        return self._acquisition_time

    @acquisition_time.setter
    def acquisition_time(self, time):
        """
        Set the hydrophone acquisition time.

        Parameters:
            time (float): Acquisition time in microseconds.
        """
        self._acquisition_time = time

    @property
    def picoscope(self):
        """
        Getter method for the picoscope.

        Returns:
            Transducer: The picoscope associated with the sequence.
        """

        return self._picoscope

    @picoscope.setter
    def picoscope(self, serial):
        """
        Sets the picoscope based on the provided serial number.

        Parameters:
            serial (str): Serial number of the picoscope.
        """

        self._picoscope.set_pico_info(serial)

    @property
    def sampl_freq_multi(self):
        """
        Get the sampling frequency multiplication factor.

        Returns:
            float: Sampling frequency multiplication factor.
        """
        return self._sampl_freq_multi

    @sampl_freq_multi.setter
    def sampl_freq_multi(self, factor):
        """
        Set the sampling frequency multiplication factor.

        Parameters:
            factor (float): Sampling frequency multiplication factor.
        """
        self._sampl_freq_multi = factor

    @property
    def temp(self):
        """
        Get the water temperature.

        Returns:
            float: Water temperature in Celsius.
        """
        return self._temp

    @temp.setter
    def temp(self, value):
        """
        Set the water temperature.

        Parameters:
            value (float): Water temperature in Celsius.
        """
        if value is not None and (value < 0 or value > 100):
            raise ValueError("Temperature must be between 0 and 100 Celsius.")
        self._temp = value

    @property
    def dis_oxy(self):
        """
        Get the dissolved oxygen level in water.

        Returns:
            float: Dissolved oxygen level in mg/L.
        """
        return self._dis_oxy

    @dis_oxy.setter
    def dis_oxy(self, value):
        """
        Set the dissolved oxygen level in water.

        Parameters:
            value (float): Dissolved oxygen level in mg/L.
        """
        if value is not None and value < 0:
            raise ValueError("Dissolved oxygen level must be positive.")
        self._dis_oxy = value

    @property
    def coord_zero(self):
        """
        Get the coordinates of the relative zero point.

        Returns:
            list: x, y, z coordinates.
        """
        return self._coord_zero

    @coord_zero.setter
    def coord_zero(self, value):
        """
        Set the coordinates of the relative zero point.

        Parameters:
            value (list): A list containing x, y, z coordinates.
        """
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError("coord_zero must be a list of three values (x, y, z).")
        self._coord_zero = value

    @property
    def perform_all_seqs(self):
        """
        Get the flag indicating if all sequences should be performed in order.

        Returns:
            bool: True if all sequences should be performed, False otherwise.
        """
        return self._perform_all_seqs

    @perform_all_seqs.setter
    def perform_all_seqs(self, value):
        """
        Set the flag indicating if all sequences should be performed in order.

        Parameters:
            value (bool): True to perform all sequences, False otherwise.
        """
        if not isinstance(value, bool):
            raise ValueError("perform_all_seqs must be a boolean value.")
        self._perform_all_seqs = value

    @property
    def adjust(self):
        """
        Get the "adjust" parameter from acd_param.

        Returns:
            int: Adjustment parameter.
        """
        return self.acd_param["adjust"]

    @adjust.setter
    def adjust(self, value):
        """
        Set the "adjust" parameter in acd_param.

        Parameters:
            value (int): Adjustment parameter.
        """
        if not isinstance(value, int):
            raise ValueError("adjust must be an integer.")
        self.acd_param["adjust"] = value

    @property
    def begus(self):
        """
        Get the "begus" parameter from acd_param.

        Returns:
            float: Beginning time of the processing window in microseconds.
        """
        return self.acd_param["begus"]

    @begus.setter
    def begus(self, value):
        """
        Set the "begus" parameter in acd_param.

        Parameters:
            value (float): Beginning time of the processing window in microseconds.
        """
        if not isinstance(value, (int, float)):
            raise ValueError("begus must be a number.")
        self.acd_param["begus"] = value

    @property
    def endus(self):
        """
        Get the "endus" parameter from acd_param.

        Returns:
            float: End time of the processing window in microseconds.
        """
        return self.acd_param["endus"]

    @endus.setter
    def endus(self, value):
        """
        Set the "endus" parameter in acd_param.

        Parameters:
            value (float): End time of the processing window in microseconds.
        """
        if not isinstance(value, (int, float)):
            raise ValueError("endus must be a number.")
        self.acd_param["endus"] = value

    @property
    def protocol(self):
        """
        Get the name of the chosen protocol.

        Returns:
            str: Name of the chosen protocol.
        """
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        """
        Set the name of the chosen protocol.

        Parameters:
            value (str): Name of the protocol.
        """
        if not isinstance(value, str):
            raise ValueError("protocol must be a string.")
        self._protocol = value

    @property
    def is_ac_align(self):
        """
        Get the flag indicating if acoustic alignment is chosen.

        Returns:
            bool: True if acoustic alignment is chosen, False otherwise.
        """
        return self._is_ac_align

    @is_ac_align.setter
    def is_ac_align(self, value):
        """
        Set the flag indicating if acoustic alignment is chosen.

        Parameters:
            value (bool): True for acoustic alignment, False otherwise.
        """
        if not isinstance(value, bool):
            raise ValueError("is_ac_align must be a boolean value.")
        self._is_ac_align = value

    @property
    def sequences(self):
        """
        Get the list of US sequences to perform.

        Returns:
            list: List of US sequences.
        """
        return self._sequences

    @sequences.setter
    def sequences(self, value):
        """
        Set the list of US sequences to perform.

        Parameters:
            value (list): List of US sequences.
        """
        if not isinstance(value, list):
            raise ValueError("sequences must be a list.")
        self._sequences = value

    def write_to_ini(self):
        """
        Write current input parameters to an INI file for caching.
        """

        cached_input = self._create_ini_object()

        cached_path = get_config_value(logger, config, 'Characterization',
                                       'Path of input parameters cache',
                                       'config//characterization_input_cache.ini')
        with open(cached_path, 'w') as inputfile:
            cached_input.write(inputfile)

    def _create_ini_object(self):
        """
        Helper function to create the INI object.
        """

        cached_input = configparser.ConfigParser(interpolation=None)
        now = datetime.now()

        cached_input['Input parameters'] = {}
        date_format = get_config_value(logger, config, 'Characterization', 'Cache date format',
                                       "%Y/%m/%d")
        cached_input['Input parameters']['Date'] = str(now.strftime(date_format))

        cached_input = self._write_common_parameters(cached_input)

        cached_input = self._write_equipment_parameters(cached_input)

        cached_input = self._write_protocol_parameters(cached_input)

        cached_input = self._write_condition_parameters(cached_input)

        cached_input = self._write_postprocessing_parameters(cached_input)

        return cached_input

    def _write_common_parameters(self, cached_input):
        """
        Write common parameters to the INI object.
        """

        cached_input['Input parameters']['Temporary output path'] = str(self._temp_dir_output)
        cached_input['Input parameters']['Output path'] = str(self._dir_output)

        return cached_input

    def _write_equipment_parameters(self, cached_input):
        """
        Write equipment parameters to the INI object.
        """

        cached_input['Input parameters']['Driving system.serial_number'] = self._driving_sys.serial
        cached_input['Input parameters']['Driving system.name'] = self._driving_sys.name
        cached_input['Input parameters']['Driving system.manufact'] = self._driving_sys.manufact
        cached_input['Input parameters']['Driving system.available_ch'] = str(self._driving_sys.available_ch)
        cached_input['Input parameters']['Driving system.connect_info'] = self._driving_sys.connect_info
        cached_input['Input parameters']['Driving system.tran_comp'] = str(', '.join(self._driving_sys.tran_comp))
        cached_input['Input parameters']['Driving system.is_active'] = str(self._driving_sys.is_active)

        cached_input['Input parameters']['Transducer.serial_number'] = self._transducer.serial
        cached_input['Input parameters']['Transducer.name'] = self._transducer.name
        cached_input['Input parameters']['Transducer.manufact'] = self._transducer.manufact
        cached_input['Input parameters']['Transducer.elements'] = str(self._transducer.elements)
        cached_input['Input parameters']['Transducer.fund_freq_khz'] = str(self._transducer.fund_freq)
        cached_input['Input parameters']['Transducer.natural_foc_mm'] = str(self._transducer.natural_foc)
        cached_input['Input parameters']['Transducer.min_foc_mm'] = str(self._transducer.min_foc)
        cached_input['Input parameters']['Transducer.max_foc_mm'] = str(self._transducer.max_foc)
        cached_input['Input parameters']['Transducer.steer_info'] = self._transducer.steer_info
        cached_input['Input parameters']['Transducer.is_active'] = str(self._transducer.is_active)
        cached_input['Input parameters']['Operating frequency [kHz]'] = str(int(self.oper_freq))

        cached_input['Input parameters']['COM port of positioning system'] = str(self.pos_com_port)
        cached_input['Input parameters']['Hydrophone serial number'] = str(self.hydrophone.serial)
        cached_input['Input parameters']['Hydrophone name'] = str(self.hydrophone.name)
        cached_input['Input parameters']['Hydrophone Sensitivity (V/Pa) datasheet'] = str(self.hydrophone.sens_v_pa)
        cached_input['Input parameters']['Hydrophone acquisition time [us]'] = str(self.acquisition_time)

        cached_input['Input parameters']['PicoScope serial number'] = str(self.picoscope.serial)
        cached_input['Input parameters']['Picoscope name'] = str(self.picoscope.name)
        cached_input['Input parameters']['PicoScope pico.py identification'] = str(self.picoscope.pico_py_ident)
        cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'] = str(self.sampl_freq_multi)

        return cached_input

    def _write_protocol_parameters(self, cached_input):
        """
        Write protocol-specific parameters to the INI object.
        """

        cached_input['Input parameters.Protocol'] = {}
        cached_input['Input parameters.Protocol']['Alignment.Acoustical'] = str(self._is_ac_align)

        # If no sequence is available, a protocol excel file should be selected.
        if self._is_ac_align:
            self._write_ac_alignment_parameters(cached_input)
        else:
            cached_input['Input parameters.Protocol']['Path and filename of protocol excel file'] = str(self.path_protocol_excel_file)

        return cached_input

    def _write_ac_alignment_parameters(self, cached_input):
        # Collect focus data from all sequences
        focus_wrt_exit_plane_array = []
        focus_wrt_mid_bowl_array = []
        for seq in self._sequences:
            focus_wrt_exit_plane_array.append(seq.focus_wrt_exit_plane)
            focus_wrt_mid_bowl_array.append(seq.focus_wrt_mid_bowl)

        # Save all parameters except for focus based on first sequence
        seq = self._sequences[0]

        cached_input['Input parameters.Protocol']['Alignment.pulse_dur_ms'] = str(seq.pulse_dur)
        cached_input['Input parameters.Protocol']['Alignment.pulse_rep_int_ms'] = str(seq.pulse_rep_int)

        cached_input['Input parameters.Protocol']['Alignment.power_option'] = seq.chosen_power

        gp_power = get_config_value(logger, config, 'Power', 'Option.glob_pow',
                                    'Global power [mW]')
        press_power = get_config_value(logger, config, 'Power', 'Option.press',
                                       'Max. pressure in free water [MPa]')
        volt_power = get_config_value(logger, config, 'Power', 'Option.volt', 'Voltage [V]')
        ampl_power = get_config_value(logger, config, 'Power', 'Option.ampl', 'Amplitude [%]')

        if seq.chosen_power == gp_power:
            cached_input['Input parameters.Protocol']['Alignment.power_value'] = str(seq.global_power)
        elif seq.chosen_power == press_power:
            cached_input['Input parameters.Protocol']['Alignment.power_value'] = str(seq.press)
        elif seq.chosen_power == volt_power:
            cached_input['Input parameters.Protocol']['Alignment.power_value'] = str(seq.volt)
        elif seq.chosen_power == ampl_power:
            cached_input['Input parameters.Protocol']['Alignment.power_value'] = str(seq.ampl)

        cached_input['Input parameters.Protocol']['Alignment.chosen_focus'] = str(seq.chosen_focus)
        cached_input['Input parameters.Protocol']['Alignment.focus_wrt_exit_plane_mm'] = str(focus_wrt_exit_plane_array)
        cached_input['Input parameters.Protocol']['Alignment.focus_wrt_mid_bowl_mm'] = str(focus_wrt_mid_bowl_array)

        cached_input['Input parameters.Protocol']['Alignment.distance_from_foc_mm'] = str(seq.ac_align['distance_from_foc'])
        cached_input['Input parameters.Protocol']['Alignment.init_line_len_mm'] = str(seq.ac_align['init_line_len'])
        cached_input['Input parameters.Protocol']['Alignment.init_line_step_mm'] = str(seq.ac_align['init_line_step'])
        cached_input['Input parameters.Protocol']['Alignment.init_threshold'] = str(seq.ac_align['init_threshold'])
        cached_input['Input parameters.Protocol']['Alignment.reduction_factor'] = str(seq.ac_align['reduction_factor'])
        cached_input['Input parameters.Protocol']['Alignment.max_red_iter'] = str(seq.ac_align['max_red_iter'])
        cached_input['Input parameters.Protocol']['Alignment.create_graphs'] = str(seq.ac_align['create_graphs'])
        cached_input['Input parameters.Protocol']['Alignment.y_lim_mv'] = str(seq.ac_align['y_lim'])
        cached_input['Input parameters.Protocol']['Alignment.create_axis_file'] = str(seq.ac_align['create_axis_file'])
        cached_input['Input parameters.Protocol']['Alignment.axis_length_mm'] = str(seq.ac_align['axis_length'])
        cached_input['Input parameters.Protocol']['Alignment.axis_stepsize_mm'] = str(seq.ac_align['axis_stepsize'])

        return cached_input

    def _write_condition_parameters(self, cached_input):
        """
        Write measurement condition parameters to the INI object.
        """

        cached_input['Input parameters']['Temperature of water [°C]'] = str(self._temp)
        cached_input['Input parameters']['Dissolved oxygen level of water [mg/L]'] = str(self._dis_oxy)

        cached_input['Input parameters']['Absolute G code x-coordinate of relative zero [mm]'] = str(self._coord_zero[0])
        cached_input['Input parameters']['Absolute G code y-coordinate of relative zero [mm]'] = str(self._coord_zero[1])
        cached_input['Input parameters']['Absolute G code z-coordinate of relative zero [mm]'] = str(self._coord_zero[2])

        cached_input['Input parameters']['Perform all sequences in sequence without waiting for user input?'] = str(self._perform_all_seqs)

        return cached_input

    def _write_postprocessing_parameters(self, cached_input):
        """
        Write postprocessing parameters to the INI object.
        """

        cached_input['Input parameters.ACD processing'] = {}
        cached_input['Input parameters.ACD processing']['Beginning time of processing window [us]'] = str(self._acd_param["begus"])
        cached_input['Input parameters.ACD processing']['End time of processing window [us]'] = (
            str(self._acd_param["endus"])
            )

        adjust_message = get_config_value(logger, config, 'Characterization', 'acd adjustment.zero',
                                          '0 - no adjustment')
        if self._acd_param["adjust"] == 1:
            adjust_message = get_config_value(logger, config, 'Characterization',
                                              'acd adjustment.plus',
                                              '+1 - axial measurement moving from transducer')
        elif self._acd_param["adjust"] == -1:
            adjust_message = get_config_value(logger, config, 'Characterization',
                                              'acd adjustment.min',
                                              '-1 - axial measurement moving towards transducer')

        cached_input['Input parameters.ACD processing']['Moving processing window along?'] = (
            adjust_message)

        return cached_input

    def convert_ini_to_object(self, cached_input):
        """
        Convert input parameters from a cached INI file to object attributes.

        Args:
            cached_input (ConfigParser): ConfigParser object containing cached input parameters.
        """

        self._driving_sys = self._convert_driving_system(cached_input)
        self._transducer, self._oper_freq = self._convert_transducer(cached_input)
        self._temp_dir_output, self._dir_output = self._convert_output_paths(cached_input)
        self._sequences, self._is_ac_align = self._convert_sequences(cached_input)

        self._pos_com_port = cached_input['Input parameters']['COM port of positioning system']
        self._hydrophone = self._convert_hydrophone(cached_input)
        self._picoscope, self._sampling_freq_multi, self._acquisition_time = self._convert_picoscope(cached_input)

        self._temp, self._dis_oxy, self._coord_zero, self._perform_all_seqs, self._acd_param = self._convert_conditions(cached_input)

    def _convert_driving_system(self, cached_input):
        """
        Convert driving system parameters from the INI file to object attributes.
        """
        driving_sys = ds.DrivingSystem()
        driving_sys.set_ds_info(cached_input['Input parameters']['Driving system.serial_number'])

        return driving_sys

    def _convert_transducer(self, cached_input):
        """
        Convert transducer parameters from the INI file to object attributes.
        """
        transducer = tran.Transducer()
        transducer.set_transducer_info(cached_input['Input parameters']['Transducer.serial_number'])

        oper_freq = int(cached_input['Input parameters']['Operating frequency [kHz]'])

        return transducer, oper_freq

    def _convert_output_paths(self, cached_input):
        """
        Convert temporary and output paths from the INI file to object attributes.
        """
        temp_dir_output = cached_input['Input parameters']['Temporary output path']
        dir_output = cached_input['Input parameters']['Output path']

        return temp_dir_output, dir_output

    def _convert_sequences(self, cached_input):
        """
        Convert sequence data from the INI file to a list of sequence objects.
        """
        
        is_ac_align = cached_input['Input parameters.Protocol']['Alignment.Acoustical'] == 'True'
        if is_ac_align:
            seq = sequence.CharacSequence()
            seq.is_ac_align = True
            seq.driving_sys = self._driving_sys.serial
            seq.transducer = self._transducer.serial
            seq.oper_freq = self._oper_freq
            seq.pulse_dur = float(cached_input['Input parameters.Protocol']['Alignment.pulse_dur_ms'])
            seq.pulse_rep_int = float(cached_input['Input parameters.Protocol']['Alignment.pulse_rep_int_ms'])

            # Add alignment-specific parameters
            seq = self._convert_alignment_parameters(seq, cached_input)

            # Convert focus and power parameters
            sequences = self._convert_focus_and_power_parameters(seq, cached_input)

        else:
            self._path_protocol_excel_file = cached_input['Input parameters.Protocol']['Path and filename of protocol excel file']

        return sequences, is_ac_align

    def _convert_alignment_parameters(self, seq, cached_input):
        """
        Convert alignment-specific parameters for sequences from the INI file to object attributes.
        """

        distance_str = cached_input['Input parameters.Protocol']['Alignment.distance_from_foc_mm']
        distance_array = [float(value) for value in distance_str.strip('][').split(',')]
        seq.ac_align['distance_from_foc'] = distance_array
        seq.ac_align['init_line_len'] = float(cached_input['Input parameters.Protocol']['Alignment.init_line_len_mm'])
        seq.ac_align['init_line_step'] = float(cached_input['Input parameters.Protocol']['Alignment.init_line_step_mm'])
        seq.ac_align['init_threshold'] = float(cached_input['Input parameters.Protocol']['Alignment.init_threshold'])
        seq.ac_align['reduction_factor'] = float(cached_input['Input parameters.Protocol']['Alignment.reduction_factor'])
        seq.ac_align['max_red_iter'] = int(cached_input['Input parameters.Protocol']['Alignment.max_red_iter'])
        seq.ac_align['create_graphs'] = cached_input['Input parameters.Protocol']['Alignment.create_graphs'] == 'True'
        seq.ac_align['y_lim'] = float(cached_input['Input parameters.Protocol']['Alignment.y_lim_mv'])
        seq.ac_align['create_axis_file'] = cached_input['Input parameters.Protocol']['Alignment.create_axis_file'] == 'True'
        seq.ac_align['axis_length'] = float(cached_input['Input parameters.Protocol']['Alignment.axis_length_mm'])
        seq.ac_align['axis_stepsize'] = float(cached_input['Input parameters.Protocol']['Alignment.axis_stepsize_mm'])

        return seq

    def _convert_focus_and_power_parameters(self, seq, cached_input):
        """
        Convert focus and power parameters for sequences from the INI file to object attributes.
        """

        exit_foc = get_config_value(logger, config, 'Focus', 'Option.exit',
                                    'Focus wrt exit plane [mm]')
        bowl_foc = get_config_value(logger, config, 'Focus', 'Option.bowl',
                                    'Focus wrt mid bowl [mm]')

        seq.chosen_focus = cached_input['Input parameters.Protocol']['Alignment.chosen_focus']
        if seq.chosen_focus == exit_foc:
            focus_str = cached_input['Input parameters.Protocol']['Alignment.focus_wrt_exit_plane_mm']
        elif seq.chosen_focus == bowl_foc:
            focus_str = cached_input['Input parameters.Protocol']['Alignment.focus_wrt_mid_bowl_mm']
        else:
            focus_str = ""

        focus_array = [float(value) for value in focus_str.strip('][').split(',')]

        # Retrieve and set power parameters based on the power option
        power_option = cached_input['Input parameters.Protocol']['Alignment.power_option']
        power_value_str = cached_input['Input parameters.Protocol']['Alignment.power_value']
        power_value = [float(value) for value in power_value_str.strip('][').split(',')]
        
        sequences = []
        for focus in focus_array:
            basic_seq = seq.clone()

            if basic_seq.chosen_focus == exit_foc:
                basic_seq.focus_wrt_exit_plane = focus
            elif basic_seq.chosen_focus == bowl_foc:
                basic_seq.focus_wrt_mid_bowl = focus

            gp_power = get_config_value(logger, config, 'Power', 'Option.glob_pow',
                                        'Global power [mW]')
            press_power = get_config_value(logger, config, 'Power', 'Option.press',
                                           'Max. pressure in free water [MPa]')
            volt_power = get_config_value(logger, config, 'Power', 'Option.volt', 'Voltage [V]')
            ampl_power = get_config_value(logger, config, 'Power', 'Option.ampl', 'Amplitude [%]')

            basic_seq.chosen_power = power_option
            if power_option == gp_power:
                basic_seq.global_power = power_value
            elif power_option == press_power:
                basic_seq.press = power_value
            elif power_option == volt_power:
                basic_seq.volt = power_value
            elif power_option == ampl_power:
                basic_seq.ampl = power_value
                
            sequences.append(basic_seq)

        return sequences

    def _convert_hydrophone(self, cached_input):
        """
        Convert hydrophone parameters from the INI file to object attributes.
        """
        hydrophone = hp.Hydrophone()
        hydrophone.serial = cached_input['Input parameters']['Hydrophone serial number']
        hydrophone.name = cached_input['Input parameters']['Hydrophone name']
        hydrophone.sens_v_pa = cached_input['Input parameters']['Hydrophone Sensitivity (V/Pa) datasheet']

        return hydrophone

    def _convert_picoscope(self, cached_input):
        """
        Convert picoscope parameters from the INI file to object attributes.
        """
        picoscope = ps.PicoScope()
        picoscope.serial = cached_input['Input parameters']['PicoScope serial number']
        picoscope.name = cached_input['Input parameters']['Picoscope name']
        picoscope.pico_py_ident = cached_input['Input parameters']['PicoScope pico.py identification']

        sampling_freq_multi = float(cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'])

        acquisition_time = float(cached_input['Input parameters']['Hydrophone acquisition time [us]'])

        return picoscope, sampling_freq_multi, acquisition_time

    def _convert_conditions(self, cached_input):
        """
        Convert environmental conditions (temperature, dissolved oxygen) from the INI file.
        """
        temp = float(cached_input['Input parameters']['Temperature of water [°C]'])
        dis_oxy = float(cached_input['Input parameters']['Dissolved oxygen level of water [mg/L]'])

        coord_zero = [float(cached_input['Input parameters']['Absolute G code x-coordinate of relative zero [mm]']),
                      float(cached_input['Input parameters']['Absolute G code y-coordinate of relative zero [mm]']),
                      float(cached_input['Input parameters']['Absolute G code z-coordinate of relative zero [mm]'])]

        perform_all_seqs = cached_input['Input parameters']['Perform all sequences in sequence without waiting for user input?'] == 'True'

        adjust_message = cached_input['Input parameters.ACD processing']['Moving processing window along?']

        adjust_value = 0
        if adjust_message == get_config_value(logger, config, 'Characterization',
                                              'acd adjustment.plus',
                                              '+1 - axial measurement moving from transducer'):
            adjust_value = 1
        elif adjust_message == get_config_value(logger, config, 'Characterization',
                                                'acd adjustment.min',
                                                '-1 - axial measurement moving towards transducer'):
            adjust_value = -1

        acd_param = {
            "begus": float(cached_input['Input parameters.ACD processing']['Beginning time of processing window [us]']),
            "endus": float(cached_input['Input parameters.ACD processing']['End time of processing window [us]']),
            "adjust": adjust_value
        }

        return temp, dis_oxy, coord_zero, perform_all_seqs, acd_param
