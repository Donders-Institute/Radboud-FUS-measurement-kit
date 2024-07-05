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
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 0.8),
https://github.com/Donders-Institute/Radboud-FUS-measurement-kit
"""

# Basic packages

# Miscellaneous packages
import configparser

from datetime import datetime

# Own packages
from fus_driving_systems import driving_system as ds
from fus_driving_systems import transducer as td

from fus_driving_systems.config.config import config_info as config


class InputParameters:
    """
    Class to manage input parameters that are applicable for the whole protocol/all sequences.

    Attributes:
        temp_dir_output (str): Temporary local output directory path.
        main_dir (str): Main protocol directory path.
        dir_output (str): Directory of output path on drive. (moving of results is done at the end
                                                              to minimize acquisition time)
        path_protocol_excel_file (str): Path to protocol Excel file.
        ds_list (list): List of available driving systems.
        driving_sys (ds.DrivingSystem): Selected driving system object.
        is_ds_com_port (bool): Flag indicating if driving system uses COM port.
        ds_names (list): Names of available driving systems.
        tran_list (list): List of available transducers.
        tran (td.Transducer): Selected transducer object.
        tran_names (list): Names of available transducers.
        oper_freq (int): Operating frequency in [kHz].
        pos_com_port (str): COM port of positioning system.
        acquisition_time (float): Hydrophone acquisition time in microseconds.
        sampl_freq_multi (float): Picoscope sampling frequency multiplication factor.
        temp (float): Temperature of water in Celsius.
        dis_oxy (float): Dissolved oxygen level of water in mg/L.
        coord_zero (list): List of x, y, z coordinates of relative zero point.
        perform_all_protocols (bool): Flag indicating if all protocols should be performed in
                                      sequence.
    """

    def __init__(self):
        """
        Initialize input parameters with default values and configurations.
        """

        self.temp_dir_output = config['Characterization']['Temporary output path']
        self.main_dir = config['Characterization']['Default protocol directory']
        self.dir_output = config['Characterization']['Default output directory']
        self.path_protocol_excel_file = self.main_dir

        # Get available driving systems and use the first one as default
        self.ds_list = ds.get_ds_list()
        self.driving_sys = self.ds_list[0]
        self.is_ds_com_port = 'COM' in self.driving_sys.connect_info
        self.ds_names = ds.get_ds_names()

        # Get available transducers and use the first one as default
        self.tran_list = td.get_tran_list()
        self.tran = self.tran_list[0]
        self.tran_names = td.get_tran_names()

        self.oper_freq = self.tran.fund_freq  # [kHz]

        self.pos_com_port = 'COM4'

        self.acquisition_time = 500  # microseconds
        self.sampl_freq_multi = 50

        self.temp = ''  # temperature in celsius
        self.dis_oxy = ''  # dissolved oxygen in mg/L

        self.coord_zero = [-50, -50, -150]
        self.perform_all_protocols = True

    def write_to_ini(self):
        """
        Write current input parameters to an INI file for caching.
        """

        cached_input = configparser.ConfigParser()

        now = datetime.now()
        cached_input['Input parameters'] = {}
        cached_input['Input parameters']['Date'] = str(now.strftime("%Y/%m/%d"))
        cached_input['Input parameters']['Path and filename of protocol excel file'] = str(self.path_protocol_excel_file)

        cached_input['Input parameters']['Driving system.serial_number'] = self.driving_sys.serial
        cached_input['Input parameters']['Driving system.name'] = self.driving_sys.name
        cached_input['Input parameters']['Driving system.manufact'] = self.driving_sys.manufact
        cached_input['Input parameters']['Driving system.available_ch'] = str(self.driving_sys.available_ch)
        cached_input['Input parameters']['Driving system.connect_info'] = self.driving_sys.connect_info
        cached_input['Input parameters']['Driving system.tran_comp'] = str(', '.join(self.driving_sys.tran_comp))
        cached_input['Input parameters']['Driving system.is_active'] = str(self.driving_sys.is_active)

        cached_input['Input parameters']['Transducer.serial_number'] = self.tran.serial
        cached_input['Input parameters']['Transducer.name'] = self.tran.name
        cached_input['Input parameters']['Transducer.manufact'] = self.tran.manufact
        cached_input['Input parameters']['Transducer.elements'] = str(self.tran.elements)
        cached_input['Input parameters']['Transducer.fund_freq'] = str(self.tran.fund_freq)
        cached_input['Input parameters']['Transducer.natural_foc'] = str(self.tran.natural_foc)
        cached_input['Input parameters']['Transducer.min_foc'] = str(self.tran.min_foc)
        cached_input['Input parameters']['Transducer.max_foc'] = str(self.tran.max_foc)
        cached_input['Input parameters']['Transducer.steer_info'] = self.tran.steer_info
        cached_input['Input parameters']['Transducer.is_active'] = str(self.tran.is_active)

        cached_input['Input parameters']['Operating frequency [kHz]'] = str(int(self.oper_freq))

        cached_input['Input parameters']['COM port of positioning system'] = str(self.pos_com_port)

        cached_input['Input parameters']['Hydrophone acquisition time [us]'] = str(self.acquisition_time)
        cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'] = str(self.sampl_freq_multi)

        cached_input['Input parameters']['Temperature of water [°C]'] = str(self.temp)
        cached_input['Input parameters']['Dissolved oxygen level of water [mg/L]'] = str(self.dis_oxy)

        cached_input['Input parameters']['Absolute G code x-coordinate of relative zero'] = str(self.coord_zero[0])
        cached_input['Input parameters']['Absolute G code y-coordinate of relative zero'] = str(self.coord_zero[1])
        cached_input['Input parameters']['Absolute G code z-coordinate of relative zero'] = str(self.coord_zero[2])

        cached_input['Input parameters']['Perform all protocols in sequence without waiting for user input?'] = str(self.perform_all_protocols)

        cached_path = config['Characterization']['Path of input parameters cache']
        with open(cached_path, 'w') as inputfile:
            cached_input.write(inputfile)

    def convert_ini_to_object(self, cached_input):
        """
        Convert input parameters from a cached INI file to object attributes.

        Args:
            cached_input (ConfigParser): ConfigParser object containing cached input parameters.
        """

        self.path_protocol_excel_file = cached_input['Input parameters']['Path and filename of protocol excel file']

        self.driving_sys.serial = cached_input['Input parameters']['Driving system.serial_number']
        self.driving_sys.name = cached_input['Input parameters']['Driving system.name']
        self.driving_sys.manufact = cached_input['Input parameters']['Driving system.manufact']
        self.driving_sys.available_ch = int(cached_input['Input parameters']['Driving system.available_ch'])
        self.driving_sys.connect_info = cached_input['Input parameters']['Driving system.connect_info']
        self.is_ds_com_port = 'COM' in self.driving_sys.connect_info

        self.driving_sys.tran_comp = cached_input['Input parameters']['Driving system.tran_comp'].split(', ')
        self.driving_sys.is_active = cached_input['Input parameters']['Driving system.is_active'] == 'True'

        self.tran.serial = cached_input['Input parameters']['Transducer.serial_number']
        self.tran.name = cached_input['Input parameters']['Transducer.name']
        self.tran.manufact = cached_input['Input parameters']['Transducer.manufact']
        self.tran.elements = int(cached_input['Input parameters']['Transducer.elements'])
        self.tran.fund_freq = int(cached_input['Input parameters']['Transducer.fund_freq'])
        self.tran.natural_foc = float(cached_input['Input parameters']['Transducer.natural_foc'])
        self.tran.min_foc = float(cached_input['Input parameters']['Transducer.min_foc'])
        self.tran.max_foc = float(cached_input['Input parameters']['Transducer.max_foc'])
        self.tran.steer_info = cached_input['Input parameters']['Transducer.steer_info']
        self.tran.is_active = cached_input['Input parameters']['Transducer.is_active'] == 'True'

        self.oper_freq = int(cached_input['Input parameters']['Operating frequency [kHz]'])

        self.pos_com_port = cached_input['Input parameters']['COM port of positioning system']

        self.acquisition_time = float(cached_input['Input parameters']['Hydrophone acquisition time [us]'])
        self.sampl_freq_multi = float(cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'])

        self.temp = float(cached_input['Input parameters']['Temperature of water [°C]'])
        self.dis_oxy = float(cached_input['Input parameters']['Dissolved oxygen level of water [mg/L]'])

        self.coord_zero[0] = float(cached_input['Input parameters']['Absolute G code x-coordinate of relative zero'])
        self.coord_zero[1] = float(cached_input['Input parameters']['Absolute G code y-coordinate of relative zero'])
        self.coord_zero[2] = float(cached_input['Input parameters']['Absolute G code z-coordinate of relative zero'])

        self.perform_all_protocols = cached_input['Input parameters']['Perform all protocols in sequence without waiting for user input?'] == 'True'

    def __str__(self):
        '''
        Returns a formatted string containing information about the input parameters.

        Returns:
            str: Formatted information about the input parameters.

        '''

        info = ''

        info += f"Path and filename of protocol excel file: {self.path_protocol_excel_file} \n "
        info += f"Temporary path of output: {self.temp_dir_output} \n "
        info += f"Path of output: {self.dir_output} \n "

        info = str(self.driving_sys)
        info = str(self.tran)

        info += f"Operating frequency [kHz]: {self.oper_freq} \n "

        info += f"COM port of positioning system: {self.pos_com_port} \n "
        info += f"Hydrophone acquisition time [us]: {self.acquisition_time} \n "
        info += f"Picoscope sampling frequency multiplication factor: {self.sampl_freq_multi} \n "

        info += f"Temperature of water [°C]: {self.temp} \n "
        info += f"Dissolved oxygen level of water [mg/L]: {self.dis_oxy} \n "

        info += f"Absolute G code xyz-coordinates of relative zero: [{self.coord_zero[0]}, {self.coord_zero[1]}, {self.coord_zero[2]}] \n "

        info += f"Perform all protocols in sequence without waiting for user input?: {self.perform_all_protocols} \n "

        return info
