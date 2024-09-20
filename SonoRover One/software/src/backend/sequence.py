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
import os
import re
import sys

# Miscellaneous packages
import numpy

import pandas as pd

# Own packages
from fus_driving_systems import sequence
from config.logging_config import logger


class CharacSequence(sequence.Sequence):
    """
    Class to represent a characterization sequence, inheriting from Sequence.

    Attributes:
        seq_number (int): Sequence number of the protocol in the Excel file.
        use_coord_excel (bool): Flag indicating if coordinate Excel file is used as input for grid.
        path_coord_excel (str): Path of the coordinate Excel file.
        coord_start (list): Coordinates [x, y, z] of the starting point in millimeters.
        nslices_nrow_ncol (list): Number of slices, rows, and columns in the grid.
        vect_sl (numpy.ndarray): Step vector for slice direction in millimeters.
        vect_row (numpy.ndarray): Step vector for row direction in millimeters.
        vect_col (numpy.ndarray): Step vector for column direction in millimeters.
    """

    def __init__(self):
        """
        Initialize a characterization sequence with default values.
        """

        super().__init__()

        self.seq_number = 0   # sequence number of protocol in excel file
        self.tag = ''  # user can add a description to the sequence

        # boolean if acoustical alignment is performed, if so, no grid input required.
        self.ac_align = False
        self.use_coord_excel = False  # boolean if coordinate excel file is used as input of grid
        self.path_coord_excel = None  # path of coordinate excel file

        self.coord_start = [0, 0, 0]  # [x, y, z] coordinates of starting point in millimeters
        self.nslices_nrow_ncol = [0, 0, 0]  # [number of slices, number of rows, number of columns]

        self.vect_sl = None  # vector to define stepsize in step-direction in millimeters
        self.vect_row = None  # vector to define stepsize in row-direction in millimeters
        self.vect_col = None  # vector to define stepsize in column-direction in millimeters

    def __str__(self):
        """
        Returns a formatted string containing information about the sequence.

        Returns:
            str: Formatted information about the sequence.
        """

        info = ''

        info += super().__str__()

        info += f"Sequence number: {self.seq_number} \n "
        info += f"Tag: {self.tag} \n "

        info += f"Acoustical alignment performed?: {self.ac_align} \n "
        info += f"Use coordinate excel as input?: {self.use_coord_excel} \n "
        info += f"Path of coordinate excel: {self.path_coord_excel} \n "

        info += f"Begin coordinates [mm]: {self.coord_start} \n "
        info += f"Number of slices, rows, columns: {self.nslices_nrow_ncol} \n "
        info += f"Slice vector [mm]: {self.vect_sl} \n "
        info += f"Row vector [mm]: {self.vect_row} \n "
        info += f"Column vector [mm]: {self.vect_col} \n "

        return info

    def _set_start_coord_vector(self, coord_zero, directions, dimensions):
        """
        Calculate and set starting coordinates based on relative zero and dimensions in different
        directions.

        Args:
            coord_zero (list): Coordinates [x, y, z] of the relative zero.
            directions (list): List of directions ('+x', '-x', '+y', '-y', '+z', '-z').
            dimensions (list): List of dimensions [max_x_plus, max_x_min, max_y_plus, max_y_min,
                                                   max_z_plus, max_z_min].
        """

        for direction in directions:
            # take opposite direction as starting positions
            match direction:
                case '+x':
                    # coord_zero_x - max_x_min = start_pos_x to measure in +x dir.
                    coord_start = coord_zero[0] - dimensions[1]
                    self.coord_start[0] = float(f'{coord_start:.3f}')
                case '-x':
                    # coord_zero_x + max_x_plus = start_pos_x to measure in -x dir.
                    coord_start = coord_zero[0] + dimensions[0]
                    self.coord_start[0] = float(f'{coord_start:.3f}')
                case '+y':
                    # coord_zero_y - max_y_min = start_pos_y to measure in +y dir.
                    coord_start = coord_zero[1] - dimensions[3]
                    self.coord_start[1] = float(f'{coord_start:.3f}')
                case '-y':
                    # coord_zero_y + max_y_plus = start_pos_y to measure in -y dir.
                    coord_start = coord_zero[1] + dimensions[2]
                    self.coord_start[1] = float(f'{coord_start:.3f}')
                case '+z':
                    # coord_zero_z - max_z_min = start_pos_z to measure in +z dir.
                    coord_start = coord_zero[2] - dimensions[5]
                    self.coord_start[2] = float(f'{coord_start:.3f}')
                case '-z':
                    # coord_zero_z + max_z_plus = start_pos_z to measure in -z dir.
                    coord_start = coord_zero[2] + dimensions[4]
                    self.coord_start[2] = float(f'{coord_start:.3f}')

    def _set_all_dir_vectors(self, directions, step_sizes):
        """
        Set step vectors for slice, row, and column directions.

        Args:
            directions (list): List of directions ('+x', '-x', '+y', '-y', '+z', '-z').
            step_sizes (list): List of step sizes [step_size_x, step_size_y, step_size_z].
        """

        self.vect_sl = _set_dir_vector(directions[0], step_sizes)
        self.vect_row = _set_dir_vector(directions[1], step_sizes)
        self.vect_col = _set_dir_vector(directions[2], step_sizes)

    def _calculate_n_vector(self, directions, dimensions, step_sizes):
        """
        Calculate number of slices, rows, and columns based on directions, dimensions, and step
        sizes.

        Args:
            directions (list): List of directions ('+x', '-x', '+y', '-y', '+z', '-z').
            dimensions (list): List of dimensions [max_x_plus, max_x_min, max_y_plus, max_y_min
                                                   max_z_plus, max_z_min].
            step_sizes (list): List of step sizes [step_size_x, step_size_y, step_size_z].
        """

        nrow = _calculate_n(directions[2], dimensions, step_sizes)
        ncol = _calculate_n(directions[1], dimensions, step_sizes)
        nslices = _calculate_n(directions[0], dimensions, step_sizes)

        self.nslices_nrow_ncol = [nslices, nrow, ncol]

    def set_sequence(self, excel_ind, seq_row, input_param):
        """
        Set the sequence parameters based on Excel indices, row data, and input parameters.

        Args:
            excel_ind (dict): Dictionary containing Excel column indices.
            seq_row (pandas.Series): Row data from the Excel sheet.
            input_param (InputParameters): Input parameters object containing driving system,
            transducer, and other parameters.
        """

        # Global characterization parameters
        self.driving_sys = input_param.driving_sys.serial
        self.transducer = input_param.tran.serial
        self.oper_freq = input_param.oper_freq  # [kHz]

        # Sequence specific characterization parameters
        self.seq_number = int(seq_row[excel_ind["seq_num"]])
        self.tag = str(seq_row[excel_ind["tag"]])

        self.dephasing_degree = float(seq_row[excel_ind["dephasing"]])

        self.focus = abs(float(seq_row[excel_ind["focus"]]))  # [mm]

        power_param = str(seq_row[excel_ind["power"]])
        match power_param:
            # Order is important, because the code will check if other value is
            # set: first set new parameter and then set power value of other
            # driving system to None

            case 'SC - Global power [mW] (fill in \'Corresponding value\')':
                self.global_power = abs(float(seq_row[excel_ind["power_value"]]))/1000  # SC: gp [W]
                self.ampl = None  # IGT: amplitude [%]

            case 'IGT - Max. pressure in free water [MPa] (fill in \'Corresponding value\')':
                self.press = abs(float(seq_row[excel_ind["power_value"]]))
                self.global_power = None  # SC: global power [W]

            case 'IGT - Voltage [V] (fill in \'Corresponding value\')':
                self.volt = abs(float(seq_row[excel_ind["power_value"]]))
                self.global_power = None  # SC: global power [W]

            case 'IGT - Amplitude [%] (fill in \'Corresponding value\')':
                self.ampl = abs(float(seq_row[excel_ind["power_value"]]))  # IGT: amplitude [%]
                self.global_power = None  # SC: global power [W]

        # Timing parameters
        # ## pulse ## #
        self.pulse_dur = abs(float(seq_row[excel_ind["pulse_dur"]]))/1e3  # [us] to [ms]
        self.pulse_rep_int = abs(float(seq_row[excel_ind["pulse_rep_int"]]))  # [ms]

        # pulse ramping
        self.pulse_ramp_shape = str(seq_row[excel_ind["ramp_mode"]])

        # ramping up and ramping down duration are equal and are equal to ramp duration
        # at least 70 us between ramping up and down, convert [us] to [ms]
        self.pulse_ramp_dur = abs(float(seq_row[excel_ind["ramp_dur"]])) / 1e3

        # ## pulse train ## #
        self.pulse_train_dur = abs(float(seq_row[excel_ind["pulse_train_dur"]]))  # [ms]
        self.pulse_train_rep_int = self.pulse_train_dur  # [ms]

        # ## pulse train repetition ## #
        # convert pulse_train_rep_int to s
        self.pulse_train_rep_dur = self.pulse_train_rep_int/1000  # [s]

        # Grid
        excel_or_param = str(seq_row[excel_ind["excel_or_param"]])
        match excel_or_param:
            case 'Coordinate excel file':
                self.use_coord_excel = True
                self.path_coord_excel = str(seq_row[excel_ind["coord_excel"]])

            case 'Parameters on the right':
                self.use_coord_excel = False
                self.path_coord_excel = None

                max_x_plus = abs(float(seq_row[excel_ind["max_x_plus"]]))
                max_x_min = abs(float(seq_row[excel_ind["max_x_min"]]))
                max_y_plus = abs(float(seq_row[excel_ind["max_y_plus"]]))
                max_y_min = abs(float(seq_row[excel_ind["max_y_min"]]))
                max_z_plus = abs(float(seq_row[excel_ind["max_z_plus"]]))
                max_z_min = abs(float(seq_row[excel_ind["max_z_min"]]))

                dimensions = [max_x_plus, max_x_min, max_y_plus, max_y_min, max_z_plus, max_z_min]

                dir_slices = str(seq_row[excel_ind["dir_slices"]])
                dir_rows = str(seq_row[excel_ind["dir_rows"]])
                dir_columns = str(seq_row[excel_ind["dir_columns"]])

                directions = [dir_slices, dir_rows, dir_columns]

                step_size_x = abs(float(seq_row[excel_ind["step_size_x"]]))
                step_size_y = abs(float(seq_row[excel_ind["step_size_y"]]))
                step_size_z = abs(float(seq_row[excel_ind["step_size_z"]]))

                step_sizes = [step_size_x, step_size_y, step_size_z]

                self._set_start_coord_vector(input_param.coord_zero, directions, dimensions)

                self._set_all_dir_vectors(directions, step_sizes)

                self._calculate_n_vector(directions, dimensions, step_sizes)

            case 'Acoustical alignment':
                self.use_coord_excel = False
                self.path_coord_excel = None
                self.ac_align = True


def _define_excel_indices(data):
    """
    Define column indices from the Excel sheet for sequence parameters.

    Args:
        data (pandas.DataFrame): Excel data read into a DataFrame.

    Returns:
        dict: Dictionary mapping column names to their respective indices.
    """

    excel_indices = {
        "seq_num": data.columns.get_loc('Sequence number'),
        "tag": data.columns.get_loc('Tag'),
        "dephasing": data.columns.get_loc('Dephasing degree (0 = no dephasing) ' +
                                          'CURRENLTY ONLY APPLICABLE FOR IGT DS'),
        "pulse_dur": data.columns.get_loc('Pulse duration [us]'),
        "pulse_rep_int": data.columns.get_loc('Pulse Repetition Interval [ms]'),
        "pulse_train_dur": data.columns.get_loc('Pulse Train Duration [ms]'),

        "power": data.columns.get_loc('SC - Global power [mW] or IGT - Max. pressure in free ' +
                                      'water [Mpa], Voltage [V] or Amplitude [%]'),
        "power_value": data.columns.get_loc('Corresponding value'),
        "focus": data.columns.get_loc('Focus [mm]'),
        "ramp_mode": data.columns.get_loc('Modulation'),
        "ramp_dur": data.columns.get_loc('Ramp duration [us]'),

        "excel_or_param": data.columns.get_loc('Coordinates based on excel file or parameters on ' +
                                               'the right?'),
        "coord_excel": data.columns.get_loc('Path and filename of coordinate excel'),

        "max_x_plus": data.columns.get_loc('max. + x [mm] w.r.t. relative zero'),
        "max_x_min": data.columns.get_loc('max. - x [mm] w.r.t. relative zero'),
        "max_y_plus": data.columns.get_loc('max. + y [mm] w.r.t. relative zero'),
        "max_y_min": data.columns.get_loc('max. - y [mm] w.r.t. relative zero'),
        "max_z_plus": data.columns.get_loc('max. + z [mm] w.r.t. relative zero'),
        "max_z_min": data.columns.get_loc('max. - z [mm] w.r.t. relative zero'),

        "dir_slices": data.columns.get_loc('direction_slices'),
        "dir_rows": data.columns.get_loc('direction_rows'),
        "dir_columns": data.columns.get_loc('direction_columns'),

        "step_size_x": data.columns.get_loc('step_size_x [mm]'),
        "step_size_y": data.columns.get_loc('step_size_y [mm]'),
        "step_size_z": data.columns.get_loc('step_size_z [mm]')
        }

    return excel_indices


def _set_dir_vector(direction, step_sizes):
    """
    Determine the direction vector based on the specified direction and step sizes.

    Args:
        direction (str): Direction identifier ('+x', '-x', '+y', '-y', '+z', '-z').
        step_sizes (list): List of step sizes [step_size_x, step_size_y, step_size_z].

    Returns:
        numpy.ndarray: Direction vector in millimeters.
    """

    # create step size vector
    match direction:
        case '+x':
            vect = numpy.array((1.0, 0.0, 0.0), float) * step_sizes[0]
        case '-x':
            vect = numpy.array((-1.0, 0.0, 0.0), float) * step_sizes[0]
        case '+y':
            vect = numpy.array((0.0, 1.0, 0.0), float) * step_sizes[1]
        case '-y':
            vect = numpy.array((0.0, -1.0, 0.0), float) * step_sizes[1]
        case '+z':
            vect = numpy.array((0.0, 0.0, 1.0), float) * step_sizes[2]
        case '-z':
            vect = numpy.array((0.0, 0.0, -1.0), float) * step_sizes[2]

    return vect


def _calculate_n(direction, max_values, step_sizes):
    """
    Calculate the number of slices, rows, or columns in a specific direction.

    Args:
        direction (str): Direction identifier ('x', 'y', 'z').
        max_values (list): List of maximum values [max_x_plus, max_x_min, max_y_plus, max_y_min,\
                                                   max_z_plus, max_z_min].
        step_sizes (list): List of step sizes [step_size_x, step_size_y, step_size_z].

    Returns:
        int: Number of slices, rows, or columns.
    """

    num = 0
    if re.search('x', direction):
        if step_sizes[0] != 0:
            num = int(((max_values[0] + max_values[1]) / step_sizes[0]) + 1)
    elif re.search('y', direction):
        if step_sizes[1] != 0:
            num = int(((max_values[2] + max_values[3]) / step_sizes[1]) + 1)
    elif re.search('z', direction):
        if step_sizes[2] != 0:
            num = int(((max_values[4] + max_values[5]) / step_sizes[2]) + 1)
    return num


def generate_sequence_list(input_param):
    """
    Generate a list of characterization sequences based on input parameters.

    Args:
        input_param (InputParameters): Input parameters object containing file paths, coordinates,
        etc.

    Returns:
        list: List of CharacSequence objects representing different characterization sequences.
    """

    excel_path = input_param.path_protocol_excel_file
    if os.path.exists(excel_path):
        data = pd.read_excel(excel_path, engine='openpyxl')

        excel_ind = _define_excel_indices(data)

        sequence_list = []
        for seq_row in data.values:
            charac_seq = CharacSequence()
            charac_seq.set_sequence(excel_ind, seq_row, input_param)
            sequence_list.append(charac_seq)

        logger.info(f'{len(sequence_list)} different sequences found in {excel_path}')

        return sequence_list
    else:
        logger.error('Pipeline is cancelled. The following direction cannot be found:' +
                     f' {excel_path}')
        sys.exit()
