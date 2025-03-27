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
import re
import sys

# Miscellaneous packages
import copy
import numpy

import pandas as pd

# Own packages
from fus_driving_systems import sequence
from config.logging_config import logger
from config.config import config_info as config
from backend.utils import get_config_value


class CharacSequence(sequence.Sequence):
    """
    Class to represent a characterization sequence, inheriting from Sequence.

    Attributes:
        seq_number (int): Sequence number of the protocol in the Excel file.
        tag (str): User-defined description of the sequence.
        is_ac_align (bool): Flag indicating if acoustical alignment is performed. If True, no grid
                            input is required.
        ac_align (dict): Configuration for acoustical alignment including:
            - distance_from_foc (list): [mm] Distance from the focus point in millimeters.
            - init_line_len (float): [mm] Initial line length used for alignment.
            - init_line_step (float): [mm] Step size for alignment in millimeters.
            - init_threshold (float): [mm] Threshold for initial alignment error in millimeters.
            - DEPRECATED reduction_factor (float): [-] Reduction factor for iterative alignment
                                                       steps.
            - DEPRECATED max_red_iter (int): [-] Maximum number of reduction iterations allowed.
            - create_graphs (bool): Boolean to indicate if graphs should be created for
                                    visualization.
            - y_lim (float): [mV] Y-axis limit used for plotting.
            - create_axis_file (bool): Boolean to indicate if an axis file should be generated.
            - axis_length (float): [mm] Total length of the axis in millimeters.
            - axis_stepsize (float): [mm] Step size for each point along the axis in millimeters.
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
        self.is_ac_align = False
        dist_from_foc_str = get_config_value(logger, config, 
                                             "Characterization", 
                                             "default.distance_from_foc",
                                             '-10\n10').split('\n')
        dist_from_foc_float = [float(i) for i in dist_from_foc_str]

        self.ac_align = {
            "distance_from_foc": dist_from_foc_float,
            'init_line_len': float(get_config_value(logger, config, 
                                                    "Characterization", 
                                                    "default.init_line_len",
                                                    40)),
            'init_line_step': float(get_config_value(logger, config, 
                                                     "Characterization",
                                                     "default.init_line_step",
                                                     0.5)),
            'init_threshold': float(get_config_value(logger, config, 
                                                     "Characterization",
                                                     "default.init_threshold",
                                                     0.01)),
            'reduction_factor': float(get_config_value(
                logger, config,"Characterization", "default.reduction_factor",
                0.5)),
            'max_red_iter': int(get_config_value(logger, config, 
                                                 "Characterization",
                                                 "default.max_red_iter", 5)),
            'create_graphs': get_config_value(logger, config, 
                                              "Characterization", 
                                              "default.create_graphs", 'True')
            == 'True',
            'y_lim': float(get_config_value(logger, config, "Characterization",
                                            "default.y_lim", 200)),
            'create_axis_file': get_config_value(logger, config, 
                                                 "Characterization", 
                                                 "default.create_axis_file",
                                                 'True') == 'True',
            'axis_length': float(get_config_value(logger, config, 
                                                  "Characterization",
                                                  "default.axis_length", 140)),
            'axis_stepsize': float(get_config_value(logger, config, 
                                                    "Characterization", 
                                                    "default.axis_stepsize",
                                                    0.5))
            }

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

        info += f"Acoustical alignment performed?: {self.is_ac_align} \n "
        info += "Acoustical alignment parameters: \n"
        info += ("  - Distance from focus wrt exit plane [mm]:" +
                 f" {self.ac_align['distance_from_foc']} \n")
        info += f"  - Initial line length [mm]: {self.ac_align['init_line_len']} \n"
        info += f"  - Initial line stepsize [mm]: {self.ac_align['init_line_step']} \n"
        info += f"  - Initial threshold [mm]: {self.ac_align['init_threshold']} \n"
        # info += f"  - Reduction factor: {self.ac_align['reduction_factor']} \n"
        # info += f"  - Maximum reduction iterations: {self.ac_align['max_red_iter']} \n"
        info += f"  - Create graphs?: {self.ac_align['create_graphs']} \n"
        info += f"  - Y axis limit [mV]: {self.ac_align['y_lim']} \n"
        info += f"  - Create axis file?: {self.ac_align['create_axis_file']} \n"
        info += f"  - Axis length [mm]: {self.ac_align['axis_length']} \n"
        info += f"  - Axis step size [mm]: {self.ac_align['axis_stepsize']} \n"

        info += f"Use coordinate excel as input?: {self.use_coord_excel} \n "
        info += f"Path of coordinate excel: {self.path_coord_excel} \n "

        info += f"Begin coordinates [mm]: {self.coord_start} \n "
        info += f"Number of slices, rows, columns: {self.nslices_nrow_ncol} \n "
        info += f"Slice vector [mm]: {self.vect_sl} \n "
        info += f"Row vector [mm]: {self.vect_row} \n "
        info += f"Column vector [mm]: {self.vect_col} \n "

        return info

    def clone(self):
        """
        Creates and returns a new instance of the CharacSequence class with the same attribute
        values.

        The new instance is a deep copy of the current instance, ensuring that changes to the cloned
        object do not affect the original object.

        Returns:
            CharacSequence: A new instance of the CharacSequence class with copied attribute values.
        """

        new_instance = CharacSequence()
        new_instance.__dict__ = copy.deepcopy(self.__dict__)  # Copy all attributes
        return new_instance

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
        self.transducer = input_param.transducer.serial
        self.oper_freq = input_param.oper_freq  # [kHz]

        # Sequence specific characterization parameters
        self.seq_number = int(seq_row[excel_ind["seq_num"]])
        self.tag = str(seq_row[excel_ind["tag"]])

        dephasing_values = str(seq_row[excel_ind["dephasing"]])
        if dephasing_values == 'nan':
            self.dephasing_degree = None
        else:
            # Remove the brackets and normalize the separators (replace commas with spaces)
            normalized_str = re.sub(r"[,\[\]\s]+", " ", dephasing_values).strip()

            # Convert the string to a list of floats
            try:
                self.dephasing_degree = [float(num) for num in normalized_str.split()]
            except ValueError:
                self.dephasing_degree = None
                logger.warning('WARNING (De)phase array cannot be converted to a ' +
                               'float array. Disable dephasing.')
                print('WARNING (De)phase array cannot be converted to a ' +
                      'float array. Disable dephasing.')

        focus_definition = str(seq_row[excel_ind["focus_def"]])
        focus_exit = get_config_value(logger, config, 'Focus', 'Option.exit',
                                      'Focus wrt exit plane [mm]')
        focus_bowl = get_config_value(logger, config, 'Focus', 'Option.bowl',
                                      'Focus wrt mid bowl [mm]')
        if focus_definition == focus_exit:
            self.focus_wrt_exit_plane = abs(float(seq_row[excel_ind["focus_value"]]))  # [mm]

        elif focus_definition == focus_bowl:
            self.focus_wrt_mid_bowl = abs(float(seq_row[excel_ind["focus_value"]]))  # [mm]

        # Extract general excel information from config
        glob_pow_input = get_config_value(logger, config, "Characterization", "prot_excel.glob_pow",
                                          "SC - Global power [mW] (fill in 'Corresponding value')")
        press_input = get_config_value(logger, config, "Characterization", "prot_excel.press",
                                       "IGT - Max. pressure in free water [MPa] (fill in 'Corresponding value')")
        volt_input = get_config_value(logger, config, "Characterization", "prot_excel.volt",
                                      "IGT - Voltage [V] (fill in 'Corresponding value')")
        ampl_input = get_config_value(logger, config, "Characterization", "prot_excel.ampl",
                                      "IGT - Amplitude [%] (fill in 'Corresponding value')")

        power_param = str(seq_row[excel_ind["power"]])
        if power_param == glob_pow_input:
            # Order is important, because the code will check if other value is
            # set: first set new parameter and then set power value of other
            # driving system to None

            self.global_power = abs(float(seq_row[excel_ind["power_value"]]))/1000  # SC: gp [W]

        elif power_param == press_input:
            self.press = abs(float(seq_row[excel_ind["power_value"]]))

        elif power_param == volt_input:
            voltages = str(seq_row[excel_ind["power_value"]])
            volt_str = re.sub(r"[,\[\]\s]+", " ", voltages).strip()

            try:
                self.volt = [float(num) for num in volt_str.split()]
            except ValueError:
                message = 'Voltage array cannot be converted to a float array.'
                logger.critical(message)
                sys.exit(message)

        elif power_param == ampl_input:
            amplitudes = str(seq_row[excel_ind["power_value"]])
            ampl_str = re.sub(r"[,\[\]\s]+", " ", amplitudes).strip()

            try:
                self.ampl = [float(num) for num in ampl_str.split()]
            except ValueError:
                message = 'Amplitude array cannot be converted to a float array.'
                logger.critical(message)
                sys.exit(message)
        else:
            message = f'No power value found in sequence {self.seq_number}.'
            logger.critical(message)
            sys.exit(message)

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
        self.pulse_train_dur = self.pulse_rep_int  # [ms]
        self.pulse_train_rep_int = self.pulse_train_dur  # [ms]

        # ## pulse train repetition ## #
        # convert pulse_train_rep_int to s
        self.pulse_train_rep_dur = self.pulse_train_rep_int/1000  # [s]

        # Extract general excel information from config
        coord_excel_input = get_config_value(logger, config, "Characterization",
                                             "prot_excel.coord_excel", "Coordinate excel file")
        grid_param_input = get_config_value(logger, config, "Characterization",
                                            "prot_excel.grid_param", "Parameters on the right")

        # Grid
        excel_or_param = str(seq_row[excel_ind["excel_or_param"]])
        if excel_or_param == coord_excel_input:
            self.use_coord_excel = True
            self.path_coord_excel = str(seq_row[excel_ind["coord_excel"]])

        elif excel_or_param == grid_param_input:
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


def _define_excel_indices(data):
    """
    Define column indices from the Excel sheet for sequence parameters.

    Args:
        data (pandas.DataFrame): Excel data read into a DataFrame.

    Returns:
        dict: Dictionary mapping column names to their respective indices.
    """

    excel_indices = {}
    for key in [
        "seq_num", "tag", "dephasing", "pulse_dur", "pulse_rep_int",
        "power", "power_value", "focus_def", "focus_value", "ramp_mode", "ramp_dur",
        "excel_or_param", "coord_excel",
        "max_x_plus", "max_x_min", "max_y_plus", "max_y_min", "max_z_plus", "max_z_min",
        "dir_slices", "dir_rows", "dir_columns",
        "step_size_x", "step_size_y", "step_size_z"
    ]:
        column_name = get_config_value(logger, config, 'Characterization', "prot_excel_columns." +
                                       key, default=None)
        if column_name is not None:
            try:
                excel_indices[key] = data.columns.get_loc(column_name)
            except KeyError:
                logger.warning(f"Column '{column_name}' not found in dataset.")
        else:
            logger.warning(f"Missing config entry for 'prot_excel_columns.{key}'")

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

        logger.debug(f'{len(sequence_list)} different sequences found in {excel_path}')

        return sequence_list
    else:
        message = ('Pipeline is cancelled. The following direction cannot be found:' +
                   f' {excel_path}')
        logger.critical(message)
        sys.exit(message)
