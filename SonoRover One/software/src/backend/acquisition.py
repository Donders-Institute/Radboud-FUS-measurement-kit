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

# -------------------------------------------------------------------------------
# Name:        Scan_acoustic_field
# Purpose:
#
# Author:      ED
#
# Created:     05/11/2022
# Copyright:   (c) Image Guided Therapy

# -------------------------------------------------------------------------------

# Basic packages
import os
import time

# Miscellaneous packages
import cmath
import configparser
import csv
from datetime import datetime

import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Own packages
from frontend import check_dialogs

from fus_driving_systems.igt import igt_ds as fds_igt
from fus_driving_systems.sonic_concepts import sonic_concepts_ds as fds_sc

from config.config import config_info
from config.logging_config import logger

from backend.motor_GRBL import MotorsXYZ
from backend import pico


class Acquisition:
    """
    Class to acquire acoustic signal on a pre-defined grid.
    """

    def __init__(self, input_param, init_equip=True):
        """
        Initialize Acquisition class with global acquisition parameters.

        Parameters:
        input_param (object): Given input parameters for acquisition including driving system,
        scope settings, and motor settings.
        """

        self.input_param = input_param

        # # Global acquisition parameters
        # Initialize equipment
        self.equipment = {
            "ds": None,
            "scope": None,
            "motors": None
            }

        if init_equip:
            # Connect with driving system
            self._init_ds()

            # Connect with PicoScope
            self.equipment["scope"] = pico.getScope(self.input_param.picoscope.pico_py_ident)
            self._init_scope(input_param.sampl_freq_multi, input_param.acquisition_time)

            # Initialize ACD processing parameters
            self.proces_param = self._init_processing(endus=input_param.acquisition_time)

            # Connect with positioning system
            self.equipment["motors"] = MotorsXYZ()
            self._init_motor(input_param.pos_com_port)

        # Initialize sequence specific parameters
        self.sequence = None
        self.grid_param = {
            "nrow": 0,
            "ncol": 0,
            "nsl": 0,
            "coord_excel_data": None
            }

        self.signal_a = None
        self.output = {
            "outputRAW": None,
            "outputACD": None,
            "outputJSON": None,
            "outputINI": None,
            "outputRAWCoord": None,
            "outputCoord": None
            }

    def _init_ds(self):
        """
        Initialize the driving system based on the manufacturer.

        This method initializes the driving system using the manufacturer information provided in
        input parameters.
        """

        ds_manufact = str(self.input_param.driving_sys.manufact)

        add_message = ''
        # Driving system of Sonic Concepts
        if ds_manufact == config_info['Equipment.Manufacturer.SC']['Name']:
            add_message = config_info['Equipment.Manufacturer.SC']['Additional charac. discon. message']
            self.equipment["ds"] = fds_sc.SonicConcepts()

            check_dialogs.check_disconnection_dialog(add_message)

            self.equipment["ds"].connect(self.input_param.driving_sys.connect_info)

        # Driving system of IGT
        elif ds_manufact == config_info['Equipment.Manufacturer.IGT']['Name']:
            add_message = config_info['Equipment.Manufacturer.IGT']['Additional charac. discon. message']
            self.equipment["ds"] = fds_igt.IGT()

            check_dialogs.check_disconnection_dialog(add_message)

            self.equipment["ds"].connect(self.input_param.driving_sys.connect_info)
        else:
            logger.error(f"Unknown driving system manufacturer: {ds_manufact}")

####################################################################
    def _init_scope(self, sampl_freq_multi, acquisition_dur_us):
        """
        Initialize and connect with the Picoscope.

        Parameters:
        sampl_freq_multi (float): Sampling frequency multiplier.
        acquisition_dur_us (float): Acquisition duration in microseconds.

        This method sets up the Picoscope with the appropriate channels, sampling frequency, and
            trigger settings.
        """

        self.equipment["scope"].openUnit(pico.Resolution.DR_14BIT)

        # #        self.equipment["scope"].closeChannels()
        # In an exploration phase using the picoscope with the same generator settings
        # Determine the max voltage to set the range (pico.Range.RANGE_10V)
        self.equipment["scope"].openChannel(pico.Channel.A, pico.Range.RANGE_500mV,
                                            pico.Coupling.DC, pico.Probe.x1)

        # Calculate and set sampling frequency
        self.sampling_freq = sampl_freq_multi*self.input_param.oper_freq*1e3  # convert kHz to Hz
        self.timebase = self.equipment["scope"].timeBase(self.sampling_freq)
        self.pico_sampling_freq = self.equipment["scope"].samplingRate(self.timebase)
        self.sampling_period = 1.0/self.pico_sampling_freq
        logger.debug(f'sampling freq: {self.sampling_freq}, timebase: {self.timebase}, ' +
                     f'actual sampling freq: {self.pico_sampling_freq}')

        # Determine the number of samples within the acquisition duration
        self.sample_count = int(acquisition_dur_us * self.pico_sampling_freq/1e6)
        self.sampling_duration_us = acquisition_dur_us
        logger.debug(f'duration_us: {acquisition_dur_us}, sample count: {self.sample_count}')

        # Set trigger threshold on EXT channel to 0.5V
        threshold = 0.5
        self.equipment["scope"].initEXTTrigger(pico.Probe.x1, threshold,
                                               direction=pico.Trigger.Direction.RISING,
                                               ignoredSamples=0, timeout=0)
        time.sleep(4)

    def _init_processing(self, begus=0.0, endus=0.0, adjust=0):
        """
        Prepare the processing of the data based on the sampling frequency and the signal frequency.

        Parameters:
        begus (float): Beginning time of processing window in microseconds.
        endus (float): End time of processing window in microseconds.
        adjust (int): Adjustment parameter for time of flight. It will adjust the windows [beg..end]
        with the time of flight when the row is along US propagation.
                adjust=-1 if top-left corner is far from transducer (decrease beg)
                adjust=+1 if top-left corner is close to the transducer (increase beg)
                adjust=0 : no adjustment

        This method sets up the necessary parameters for data processing, including time vectors and
        adjustment settings.
        """

        # self.t[n] is the sampling time for sample n
        t = self.sampling_period*np.arange(0, self.sample_count)
        eiwt = np.exp(1j * 2 * np.pi * self.input_param.oper_freq*1e3 * t)  # cos(wt) + j sin(wt)

        begn = int(begus*1e-6*self.pico_sampling_freq)  # begining of the processing window
        endn = int(endus*1e-6*self.pico_sampling_freq)  # end of the processing window
        npoints = endn - begn
        logger.debug(f'begus: {begus}, endus: {endus}, begn: {begn}, endn: {endn}')

        # Collect processing parameters
        proces_param = {
            "eiwt": eiwt,
            "adjust": adjust,
            "row_pixel_us": 0,
            "begus": begus,
            "endus": endus,
            "begn": begn,
            "endn": endn,
            "npoints": npoints
            }

        return proces_param

    def _init_motor(self, port):
        """
        Initialize and connect to the motors of the positioning system.

        Parameters:
        port (str): Port for connection.

        This method initializes the motor system and connects to it using the specified port.
        """

        self.equipment["motors"].connect(port=port)
        self.equipment["motors"].initialize()
        pos = self.equipment["motors"].readPosition()
        logger.debug(f'Motor positions: X={pos[0]:.3f}, Y={pos[1]:.3f}, Z={pos[2]:.3f}')

####################################################################
    def acquire_sequence(self, sequence):
        """
        Acquire data for a given sequence.

        Parameters:
        sequence (object): Sequence object containing sequence number, coordinates, and other
        relevant details.

        This method handles the data acquisition process for a given sequence, including grid
        initialization and data saving.
        """
        self.sequence = sequence

        # Check existance of directory
        outfile = os.path.join(self.input_param.temp_dir_output, 'sequence_' +
                               str(sequence.seq_number) + '_output_data.raw')
        self._check_file(outfile)

        if sequence.use_coord_excel:
            self._init_grid_excel()
        else:
            self._init_grid()

        logger.info('Grid is initialized')

        # Send sequence to driving system
        self.equipment["ds"].send_sequence(self.sequence)
        logger.info('All driving system parameters are set')

        self._save_params_ini()
        logger.info('Used parameters have been saved in a file.')

        self._scan_grid()
        logger.info('Pipeline for current sequence is finished.')

    def acoustical_alignment(self, sequence):
        """
        Perform acoustical alignment for the given sequence.

        This method acquires data and identifies the center of mass of the acoustical signal
        for a given sequence, which involves scanning the x and y coordinates around a
        given z-coordinate, iteratively narrowing down the search area.

        Parameters:
        -----------
        sequence : object
            Sequence object containing sequence number, coordinates, and other
            relevant details.
        """

        self.sequence = sequence

        # Validate and prepare output directory and files
        outfile = os.path.join(self.input_param.temp_dir_output,
                               f'sequence_{sequence.seq_number}_output_data.raw')
        self._check_file(outfile)

        self.equipment["ds"].send_sequence(self.sequence)
        logger.info('All driving system parameters are set')

        # Save parameters and prepare for alignment
        self._save_params_ini()
        logger.info('Used parameters have been saved in a file.')

        # Prepare and define coordinates for alignment
        distance_from_foc = self.sequence.ac_align["distance_from_foc"]
        z_coords = self._calculate_z_coords(distance_from_foc)

        # Initialize grid parameters for scanning
        self.grid_param["nsl"] = 1  # Number of slices
        self.grid_param["nrow"] = 1  # Number of rows
        self.sequence.vect_sl = np.array([0, 0, 1])  # Slice direction vector

        # Set up parameters for iterative alignment
        middle_points = self._perform_alignment(z_coords)

        # Calculate and save acoustical axis if needed
        self._calculate_acoustical_axis(middle_points)
        if self.sequence.ac_align["create_axis_file"]:
            self._save_acoustical_axis_to_excel(sequence)

    def _calculate_z_coords(self, distance_from_foc):
        """
        Calculate pre- and post-focus z-coordinates for alignment.

        Parameters:
        -----------
        distance_from_foc : float
            Distance from the focus point in millimeters.

        Returns:
        --------
        list of float
            Z-coordinates for pre-focus and post-focus alignment.
        """

        pre_foc = self.input_param.coord_zero[2] + self.sequence.focus - distance_from_foc
        post_foc = self.input_param.coord_zero[2] + self.sequence.focus + distance_from_foc
        return [pre_foc, post_foc]

    def _perform_alignment(self, z_coords):
        """
        Perform the acoustical alignment by iteratively scanning x and y coordinates.

        Parameters:
        -----------
        z_coords : list of float
            List of z-coordinates to perform the alignment.

        Returns:
        --------
        np.ndarray
            Array containing the middle points [x, y, z] for each z-coordinate.
        """

        initial_line_length = self.sequence.ac_align["init_line_len"]
        initial_line_step_size = self.sequence.ac_align["init_line_step"]
        line_n_points = round(initial_line_length / initial_line_step_size)
        self.grid_param["ncol"] = line_n_points
        self.sequence.nslices_nrow_ncol = [self.grid_param["nsl"], self.grid_param["nrow"], self.grid_param["ncol"]]
        
        reduction_factor = self.sequence.ac_align["reduction_factor"]
        threshold = self.sequence.ac_align["init_threshold"]

        middle_points = np.zeros((len(z_coords), 3))

        for idx, z_coord in enumerate(z_coords):
            logger.info(f"Finding acoustical axis coordinate for z = {round(z_coord, 2)} mm")
            self.sequence.coord_start[2] = z_coord

            # Perform iterative search for alignment
            found_x_coords, found_y_coords = self._search_alignment(threshold, initial_line_length,
                                                                    initial_line_step_size,
                                                                    reduction_factor)

            # Save the middle point of the scan
            middle_points[idx] = [found_x_coords[-1], found_y_coords[-1], z_coord]

        return middle_points

    def _search_alignment(self, threshold, line_length, line_step_size, reduction_factor):
        """
        Iteratively search and converge towards the acoustical center of mass.

        Parameters:
        -----------
        threshold : float
            Threshold for convergence in millimeters.
        line_length : float
            Initial line length for scanning in millimeters.
        line_step_size : float
            Initial step size for scanning in millimeters.
        reduction_factor : float
            Factor by which line length and step size are reduced in each iteration.

        Returns:
        --------
        list, list
            Final x and y coordinates found after iterative alignment.
        """

        found_x_coords = [0, self.input_param.coord_zero[0]]
        found_y_coords = [0, self.input_param.coord_zero[1]]

        while abs(found_x_coords[-2] - found_x_coords[-1]) > threshold or abs(found_y_coords[-2] - found_y_coords[-1]) > threshold:
            iteration = len(found_x_coords) - 2
            logger.info(f"Iteration {iteration}: X difference = " +
                        f"{abs(found_x_coords[-2] - found_x_coords[-1]):.4f} mm, " +
                        f"Y difference = {abs(found_y_coords[-2] - found_y_coords[-1]):.4f} mm")
            
            max_diff = max(abs(found_x_coords[-2] - found_x_coords[-1]), abs(found_y_coords[-2] - found_y_coords[-1]))            
            # Scan x and y directions
            found_x_coords.append(self._scan_and_find_center_of_mass(found_x_coords, found_y_coords,
                                                                     line_length,
                                                                     line_step_size,
                                                                     'x', 
                                                                     iteration, max_diff))

            max_diff = max(abs(found_x_coords[-2] - found_x_coords[-1]), abs(found_y_coords[-2] - found_y_coords[-1])) 
            found_y_coords.append(self._scan_and_find_center_of_mass(found_x_coords, found_y_coords,
                                                                     line_length,
                                                                     line_step_size,
                                                                     'y',
                                                                     iteration, max_diff))
            
            if iteration % (self.sequence.ac_align['max_red_iter'] - 1) == 0:
                # Reduce line length and step size
                line_length *= reduction_factor
                line_step_size *= reduction_factor
                
                line_n_points = round(line_length / line_step_size)
                self.grid_param["ncol"] = line_n_points
                self.sequence.nslices_nrow_ncol = [self.grid_param["nsl"], self.grid_param["nrow"], self.grid_param["ncol"]]
    
                logger.info(f"Reducing search area. New line_length: {line_length:.2f}mm, " +
                            f"new line_step_size: {line_step_size:.2f}mm")

        return found_x_coords, found_y_coords

    def _scan_and_find_center_of_mass(self, found_x_coords, found_y_coords, line_length, line_step_size, direction, iteration, max_diff):
        """
        Scan in the specified direction and find the center of mass of voltage data.

        Parameters:
        -----------
        found_x_coords : list of float
            Current x-coordinates found in the alignment process.
        found_y_coords : list of float
            Current y-coordinates found in the alignment process.
        line_length : float
            Current line length for the scan in millimeters.
        line_step_size : float
            Current step size for the scan in millimeters.
        direction : str
            'x' or 'y' indicating the direction to scan.

        Returns:
        --------
        float
            Center of mass coordinate in the specified direction.
        """

        if direction == 'x':
            self.sequence.vect_row = np.array([0, 1, 0])
            self.sequence.vect_col = np.array([line_step_size, 0, 0])
            self.sequence.coord_start[0] = found_x_coords[-1] - line_length / 2
            self.sequence.coord_start[1] = found_y_coords[-1]
        else:  # direction == 'y'
            self.sequence.vect_row = np.array([1, 0, 0])
            self.sequence.vect_col = np.array([0, line_step_size, 0])
            self.sequence.coord_start[0] = found_x_coords[-1]
            self.sequence.coord_start[1] = found_y_coords[-1] - line_length / 2

        logger.info(f"Scanning in {direction}-direction...")
        volt_data, dest_xyz_list = self._scan_grid()
        max_voltages = np.max(volt_data, axis=3).flatten()

        # Calculate center of mass
        cumsum = np.cumsum(max_voltages)
        total_sum = cumsum[-1]
        center_of_mass_index = np.argmin(np.abs(cumsum - total_sum / 2))

        center_of_mass = dest_xyz_list[center_of_mass_index][0 if direction == 'x' else 1]
        logger.info(f"Found center of mass in {direction}-direction: {center_of_mass:.3f} mm")

        if self.sequence.ac_align["create_graphs"]:
            z_coord = round(self.sequence.coord_start[2], 2)
            title = (f'Center of mass in {direction}-direction, {center_of_mass:.2f} [mm]' + 
                     f' Z-coord: {z_coord},  \n ' + 
                     f'Iter. {iteration}, Max diff. = {max_diff:.3f} mm, Line length:'  + 
                     f' {line_length:.1f}, stepsize: {line_step_size:.1f}')
            self._plot_center_of_mass_graph(direction, dest_xyz_list, max_voltages, center_of_mass, iteration, title)

        return center_of_mass

    def _plot_center_of_mass_graph(self, direction, dest_xyz_list, max_voltages, center_of_mass, iteration, title):
        """
        Plot the center of mass graph for the scanned data.

        Parameters:
        -----------
        direction : str
            'x' or 'y' indicating the direction of the scan.
        dest_xyz_list : list
            List of destination coordinates during the scan.
        max_voltages : np.ndarray
            Array of maximum voltages at each grid point.
        center_of_mass : float
            Calculated center of mass in the specified direction.
        """
        z_coord = round(self.sequence.coord_start[2], 2)
        
        coords = [coord[0 if direction == 'x' else 1] for coord in dest_xyz_list]
        plt.plot(coords, max_voltages, linestyle='-', marker='.')
        plt.axvline(x=center_of_mass, color='r', linestyle='--')
        
        if direction == 'x':
            x_upper_lim = self.input_param.coord_zero[0] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[0] - self.sequence.ac_align["init_line_len"]/2
        else: # direction == 'y'
            x_upper_lim = self.input_param.coord_zero[1] + self.sequence.ac_align["init_line_len"]/2
            x_lower_lim = self.input_param.coord_zero[1] - self.sequence.ac_align["init_line_len"]/2
        
        plt.xlim(x_lower_lim, x_upper_lim)
        plt.ylim(0, 0.1)
        plt.xlabel(f'{direction.upper()}-coordinates [mm]')
        plt.ylabel('Maximum voltage per grid point [V]')
        plt.title(title)
        
        if direction == 'x':
            filename = os.path.join(self.input_param.temp_dir_output, 
                                    f'acoustical_alignment_foc_{z_coord}_'  + 
                                    f'iter_{iteration}_x_coord.png')
        else:
            filename = os.path.join(self.input_param.temp_dir_output, 
                                    f'acoustical_alignment_foc_{z_coord}_'  + 
                                    f'iter_{iteration}_y_coord.png')

        plt.savefig(filename)
        plt.show()

    def _calculate_acoustical_axis(self, middle_points):
        """
        Calculate the acoustical axis based on the middle points.

        Parameters:
        middle_points (ndarray): Array of middle points [x, y, z] for the scanned z-coordinates.

        Returns:
        dict: Acoustical axis data containing the origin point and direction vector.
        """
        if len(middle_points) > 1:  # We need at least two points to determine a linear relationship
            point1 = middle_points[0]
            point2 = middle_points[1]

            # Calculate direction vector and unit vector for the acoustical axis
            direction_vector = point2 - point1
            unit_vector = direction_vector / np.linalg.norm(direction_vector)

            # Calculate the point where z-coordinate is equal to self.input_param.coord_zero[2]
            t = (self.input_param.coord_zero[2] - point1[2]) / direction_vector[2]
            transducer_z_point = point1 + t * direction_vector

            # Store the origin and direction of the acoustical axis
            self.acoustical_axis = {
                'origin': transducer_z_point,
                'direction': unit_vector
            }

            # Log the calculated axis details
            logger.info("Acoustical axis equation:")
            logger.info(f"Origin point: {self.acoustical_axis['origin']}")
            logger.info(f"Direction vector: {self.acoustical_axis['direction']}")
            logger.info("Equation: xyz_coordinate = origin + t * direction, where t is a scalar parameter")

    def _save_acoustical_axis_to_excel(self, sequence):
        """
        Save acoustical axis data to an Excel file if `create_axis_file` is enabled.

        Parameters:
        sequence (object): The sequence object containing alignment parameters and details.
        """
        axial_measurement_length = sequence.ac_align["axis_length"]  # [mm]
        axial_measurement_step_size = sequence.ac_align["axis_stepsize"]  # [mm]

        # Define the range of t values based on axis length and step size
        t_values = np.arange(0, axial_measurement_length + axial_measurement_step_size, axial_measurement_step_size)

        # Create rows to store data for Excel output
        rows = []
        cluster_nr = 1

        # Calculate coordinates for each t value
        for i, t in enumerate(t_values):
            point = self.acoustical_axis['origin'] + t * self.acoustical_axis['direction']

            measurement_nr = i + 1  # Measurement number
            # Store row data for each t value
            rows.append([measurement_nr, cluster_nr, measurement_nr, point[0],
                         point[1], point[2], 1, measurement_nr, 1,
                         point[0] - self.input_param.coord_zero[0],
                         point[1] - self.input_param.coord_zero[1],
                         point[2] - self.input_param.coord_zero[2]
                         ])

        # Define Excel filename
        excel_filename = os.path.splitext(self.output["outputRAW"])[0] + '_acoustical_axis.xlsx'

        # Save the data using the _save_acoustical_axis_data method
        self._save_acoustical_axis_data(rows, excel_filename)
        logger.info(f"Acoustical axis coordinates saved to: {excel_filename}")

    def _save_acoustical_axis_data(self, rows, filename):
        """
        Save acoustical axis data to an Excel file.

        Parameters:
        rows (list): List of rows containing acoustical axis data.
        filename (str): Name of the Excel file to save the data.
        """
        df = pd.DataFrame(rows, columns=['Measurement number', 'Cluster number',
                                         'Indices number', 'X-coordinate [mm]',
                                         'Y-coordinate [mm]', 'Z-coordinate [mm]',
                                         'Row number', 'Column number',
                                         'Slice number',
                                         'Absolute X-coordinate [mm]',
                                         'Absolute Y-coordinate [mm]',
                                         'Absolute Z-coordinate [mm]'])

        df.to_excel(filename, index=False)

        logger.info(f"Acoustical axis coordinates saved to: {filename}")

####################################################################

    def _check_file(self, outfile):
        """
        Check if the filename provided already exists and handle appropriately.

        Parameters:
        outfile (str): Output file path.

        This method checks if the specified output file already exists and handles naming conflicts
        by appending a number.
        """

        self.output["outputRAW"] = outfile
        head, tail = os.path.split(self.output["outputRAW"])
        if not os.path.isdir(head):  # if incorrect directory or no directory is given use CWD
            head = os.getcwd()
            raise OSError(f'directory does not exist: {head}')

        fileok = not os.path.isfile(self.output["outputRAW"])
        i = 0
        imax = int(config_info['General']['Maximum number of output filename'])
        filename = os.path.join(head, tail)

        while not fileok and i <= imax:
            name, ext = os.path.splitext(tail)
            fname = f'{name}_{i:02d}{ext}'
            filename = os.path.join(head, fname)
            fileok = not os.path.isfile(filename)
            logger.debug(f'try: {filename} : ok ?: {fileok}')
            i += 1

        if i > imax:
            raise OSError(f'no possible file name: {fname}')

        self._prepare_output_files(filename)

    def _prepare_output_files(self, filename):
        """
        Prepare output filenames for ACD, raw coordinate, and CSV files.

        Parameters:
        filename (str): Base filename to prepare related output files.

        This method generates related filenames for different output formats and prepares the
        initial CSV file structure.
        """

        self.output["outputRAW"] = filename
        self.output["outputACD"] = os.path.splitext(filename)[0]+'.acd'
        self.output["outputRAWCoord"] = os.path.splitext(filename)[0] + '_coord.raw'
        self.output["outputCoord"] = os.path.splitext(filename)[0]+'.csv'

        # Add header
        with open(self.output["outputCoord"], 'a', newline='') as outcoord:
            csv.writer(outcoord, delimiter=',').writerow(['Measurement number', 'Cluster number',
                                                          'Indices number', 'X-coordinate [mm]',
                                                          'Y-coordinate [mm]', 'Z-coordinate [mm]',
                                                          'Row number', 'Column number',
                                                          'Slice number',
                                                          'Absolute X-coordinate [mm]',
                                                          'Absolute Y-coordinate [mm]',
                                                          'Absolute Z-coordinate [mm]'])

        self.output["outputJSON"] = os.path.splitext(filename)[0]+'.json'
        self.output["outputINI"] = os.path.splitext(filename)[0]+'.ini'
        logger.debug(f'file name raw: {self.output["outputRAW"]}, file name acd: ' +
                     f'{self.output["outputACD"]}')

    def _init_grid(self):
        """
        Initialize grid with predefined grid parameters. Coordinate of the (i,j) grid point (with i
        = row, j = col) will be: starting_pos + i x vect_col + j x vect_row

        This method initializes the grid based on predefined coordinates for scanning.
        """

        # starting_pos is the initial position from which the scanning starts
        self.sequence.coord_start = np.array(self.sequence.coord_start)

        # Number of rows, columns and slices
        self.grid_param["nsl"] = self.sequence.nslices_nrow_ncol[0]
        self.grid_param["nrow"] = self.sequence.nslices_nrow_ncol[1]
        self.grid_param["ncol"] = self.sequence.nslices_nrow_ncol[2]

        # Vectors in row, column and slice direction, its length is the pixel spacing
        self.sequence.vect_row = np.array(self.sequence.vect_row)
        self.sequence.vect_col = np.array(self.sequence.vect_col)
        self.sequence.vect_sl = np.array(self.sequence.vect_sl)

        # Time in us for the US to propagate ever vect_row used for ACD processing
        self.proces_param["row_pixel_us"] = np.linalg.norm(self.sequence.vect_row)/1.5

    def _init_grid_excel(self):
        """
        Initialize grid by reading coordinates from an Excel file.

        This method initializes the grid by reading coordinate data from an Excel file specified in
        the input parameters.
        """

        # Import excel file containing coordinates
        excel_path = os.path.join(self.sequence.path_coord_excel)
        if os.path.exists(excel_path):
            logger.info('Extract coordinates from ' + excel_path)
            ext = os.path.splitext(excel_path)[1]
            if ext == '.xlsx':
                self.grid_param["coord_excel_data"] = pd.read_excel(excel_path, engine='openpyxl')
            elif ext == '.xls':
                self.grid_param["coord_excel_data"] = pd.read_excel(excel_path)
            elif ext == '.csv':
                self.grid_param["coord_excel_data"] = pd.read_csv(excel_path)
            else:
                logger.error(f'Extension {ext} of {excel_path} unknown.')

            # Determine amount of rows, columns and slices
            self.grid_param["nrow"] = self.grid_param["coord_excel_data"].loc[:, "Row number"].max()
            self.grid_param["ncol"] = (self.grid_param["coord_excel_data"].loc[:, "Column number"]
                                       .max())
            self.grid_param["nsl"] = (self.grid_param["coord_excel_data"].loc[:, "Slice number"]
                                      .max())

            self.sequence.nslices_nrow_ncol = np.array((self.grid_param["nsl"], self.grid_param["nrow"],
                                               self.grid_param["ncol"]))

        else:
            logger.error("Pipeline is cancelled. The following direction cannot be found: "
                         + excel_path)

    def _save_params_ini(self):
        """
        Save parameters to an INI file.

        This method saves the input parameters to an INI file for future reference like processing.
        """

        params = configparser.ConfigParser()
        self._save_gen_param(params)
        self._save_equip_param(params)
        self._save_seq_param(params)
        self._save_grid_param(params)
        self._save_acq_param(params)
        self._save_acd_proces_param(params)

        config_fold = config_info['General']['Configuration file folder']
        with open(os.path.join(config_fold, self.output["outputINI"]), 'w') as configfile:
            params.write(configfile)
        logger.info(f'Parameters saved to {self.output["outputINI"]}')

    def _save_gen_param(self, params):
        """
        Save general parameters to an INI file.
        """

        params['Versions'] = {}
        params['Versions']['Sonorover One software'] = (
            config_info['Versions']['sonorover one software']
            )

        # Get current date and time for logging
        date_time = datetime.now()
        timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')
        params['General'] = {}
        params['General']['Timestamp'] = str(timestamp)
        params['General']['Path and filename of protocol excel file'] = (
            self.input_param.path_protocol_excel_file
            )
        params['General']['Path of output'] = self.input_param.dir_output
        params['General']['Output filenames'] = ', '.join(key + ' - ' + str(val)
                                                          for key, val in self.output.items())
        params['General']['Perform all sequences in sequence without waiting for user input?'] = (
            str(self.input_param.perform_all_seqs)
            )
        params['General']['Temperature of water [°C]'] = str(self.input_param.temp)
        params['General']['Dissolved oxygen level of water [mg/L]'] = str(self.input_param.dis_oxy)

    def _save_equip_param(self, params):
        """
        Save equipment parameters to an INI file.
        """

        params['Equipment'] = {}
        params['Equipment']['Driving system.serial_number'] = self.input_param.driving_sys.serial
        params['Equipment']['Driving system.name'] = self.input_param.driving_sys.name
        params['Equipment']['Driving system.manufact'] = self.input_param.driving_sys.manufact
        params['Equipment']['Driving system.available_ch'] = (
            str(self.input_param.driving_sys.available_ch)
            )
        params['Equipment']['Driving system.connect_info'] = (
            self.input_param.driving_sys.connect_info
            )
        params['Equipment']['Driving system.tran_comp'] = (
            str(', '.join(self.input_param.driving_sys.tran_comp))
            )
        params['Equipment']['Driving system.is_active'] = (
            str(self.input_param.driving_sys.is_active)
            )

        params['Equipment']['Transducer.serial_number'] = self.input_param.tran.serial
        params['Equipment']['Transducer.name'] = self.input_param.tran.name
        params['Equipment']['Transducer.manufact'] = self.input_param.tran.manufact
        params['Equipment']['Transducer.elements'] = str(self.input_param.tran.elements)
        params['Equipment']['Transducer.fund_freq'] = str(self.input_param.tran.fund_freq)
        params['Equipment']['Transducer.natural_foc'] = str(self.input_param.tran.natural_foc)
        params['Equipment']['Transducer.min_foc'] = str(self.input_param.tran.min_foc)
        params['Equipment']['Transducer.max_foc'] = str(self.input_param.tran.max_foc)

        # Only log steer_info when IGT driving system is used
        ds_manufact = str(self.input_param.driving_sys.manufact)
        if ds_manufact == config_info['Equipment.Manufacturer.IGT']['Name']:
            params['Equipment']['Transducer.steer_info'] = self.input_param.tran.steer_info

        params['Equipment']['Transducer.is_active'] = str(self.input_param.tran.is_active)

        params['Equipment']['COM port of positioning system'] = self.input_param.pos_com_port

    def _save_seq_param(self, params):
        """
        Save sequence specific parameters to an INI file.
        """

        params['Sequence'] = {}
        params['Sequence']['Sequence number'] = str(self.sequence.seq_number)
        params['Sequence']['Tag'] = str(self.sequence.tag)
        params['Sequence']['Dephasing degree'] = str(self.sequence.dephasing_degree)

        params['Sequence']['Operating frequency [kHz]'] = str(self.input_param.oper_freq)
        params['Sequence']['Focus [um]'] = str(self.sequence.focus)

        ds_manufact = str(self.input_param.driving_sys.manufact)
        if ds_manufact == config_info['Equipment.Manufacturer.SC']['Name']:
            params['Sequence']['SC - Global power [W]'] = str(self.sequence.global_power)
        elif ds_manufact == config_info['Equipment.Manufacturer.IGT']['Name']:
            params['Sequence']['IGT - Maximum pressure in free water [MPa]'] = (
                str(self.sequence.press)
                )
            params['Sequence']['IGT - Voltage [V]'] = str(self.sequence.volt)
            params['Sequence']['IGT - Amplitude [%]'] = str(self.sequence.ampl)

            params['Sequence']['Normalized pressure [-] vs. focal depth [mm] equation (Pnorm = a0' +
                               '+ a1*f + a2*f^2 + a3*f^3 + a4*f^4 + a5*f^5)'] = (
                                   str(f"Pnorm = {self.sequence.a0} + "  + 
                                       f"{self.sequence.a1}*f + "  + 
                                       f"{self.sequence.a2}*f^2 + " +
                                       f"{self.sequence.a3}*f^3 + " + 
                                       f"{self.sequence.a4}*f^4 + " + 
                                       f"{self.sequence.a5}*f^5")
                                   )

            params['Sequence']["Normalized pressure [-] based on chosen focal depth of " +
                               f"{self.sequence.focus} [mm]"] = str(self.sequence.norm_press)

            params['Sequence']["Pressure [MPa] vs. voltage [V] equation (P = a*V + b)"] = (
                str(f"P = {self.sequence.V2P_a}*V + {self.sequence.V2P_b}")
                )

        else:
            params['Sequence']['Unknown power unit'] = str(self.sequence.power_value)

        params['Sequence']['Pulse duration [ms]'] = str(self.sequence.pulse_dur)
        params['Sequence']['Pulse repetition interval [ms]'] = str(self.sequence.pulse_rep_int)

        params['Sequence']['Pulse ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'] = (
            str(self.sequence.pulse_ramp_shape)
            )
        params['Sequence']['Pulse ramp duration [ms]'] = str(self.sequence.pulse_ramp_dur)

        params['Sequence']['Pulse train duration [ms]'] = str(self.sequence.pulse_train_dur)
        params['Sequence']['Pulse train repetition interval [ms]'] = (
            str(self.sequence.pulse_train_rep_int)
            )

        params['Sequence']['Pulse train repetition duration [ms]'] = (
            str(self.sequence.pulse_train_rep_dur)
            )

    def _save_grid_param(self, params):
        """
        Save grid parameters to an INI file.
        """

        params['Grid'] = {}
        params['Grid']['Absolute G code x-coordinate of relative zero [mm]'] = (
            str(self.input_param.coord_zero[0])
            )
        params['Grid']['Absolute G code y-coordinate of relative zero [mm]'] = (
            str(self.input_param.coord_zero[1])
            )
        params['Grid']['Absolute G code z-coordinate of relative zero [mm]'] = (
            str(self.input_param.coord_zero[2])
            )
        params['Grid']['Use coordinate excel as input?'] = str(self.sequence.use_coord_excel)
        params['Grid']['Path of coordinate excel'] = str(self.sequence.path_coord_excel)
        params['Grid']['Acoustical alignment'] = str(self.sequence.ac_align)
        
        if self.sequence.use_coord_excel:
            params['Grid']['Number of slices, rows, columns (z-dir, x-dir, y-dir)'] = (
                str(self.sequence.nslices_nrow_ncol)
                )
        elif not self.sequence.ac_align:
            params['Grid']['Begin coordinates [mm]'] = str(self.sequence.coord_start)

            sl_dir = np.nonzero(self.sequence.vect_sl)[0][0]
            row_dir = np.nonzero(self.sequence.vect_row)[0][0]
            col_dir = np.nonzero(self.sequence.vect_col)[0][0]

            dir_info = [[sl_dir, self.sequence.nslices_nrow_ncol[0]],
                        [row_dir, self.sequence.nslices_nrow_ncol[1]],
                        [col_dir, self.sequence.nslices_nrow_ncol[2]]]

            direction = '('
            for row in dir_info:
                if row[0] == 0:
                    add_dir = 'x'
                elif row[0] == 1:
                    add_dir = 'y'
                elif row[0] == 2:
                    add_dir = 'z'
                else:
                    add_dir = 'unknown'
                direction = direction + add_dir + '-dir '

            direction = direction + ')'

            params['Grid']['Number of slices, rows, columns ' + direction] = (
                str(self.sequence.nslices_nrow_ncol)
                )
            params['Grid']['Slice vector [mm]'] = str(self.sequence.vect_sl)
            params['Grid']['Row vector [mm]'] = str(self.sequence.vect_row)
            params['Grid']['Column vector [mm]'] = str(self.sequence.vect_col)
            

    def _save_acq_param(self, params):
        """
        Save PicoScope and hydrophone parameters to an INI file.
        """

        params['Acquisition'] = {}
        params['Acquisition']['PicoScope'] = str(self.input_param.picoscope.name)
        params['Acquisition']['PicoScope pico.py identification'] = (
            str(self.input_param.picoscope.pico_py_ident)
            )
        params['Acquisition']['Sampling frequency multiplication factor'] = (
            str(self.input_param.sampl_freq_multi)
            )
        params['Acquisition']['Sampling frequency [Hz]'] = str(self.pico_sampling_freq)
        params['Acquisition']['Hydrophone'] = str(self.input_param.hydrophone.name)

        # Extract corresponding sensitivity value
        datasheet_path = self.input_param.hydrophone.sens_v_pa
        sens_data = pd.read_excel(datasheet_path)
        freq_header = config_info['Characterization.Equipment']['Hydrophone datasheet freq. header']
        freq_mhz = round(self.input_param.oper_freq/1000, 2)
        match_row = sens_data.loc[sens_data[freq_header] == freq_mhz]

        if match_row.empty:
            logger.warning(f'No frequency in datasheet {datasheet_path}' +
                           f'corresponds with {freq_mhz}. Sensitivity value is not logged.')

        elif len(match_row) > 1:
            logger.warning(f'Duplicate frequency {freq_mhz} found in datasheet {datasheet_path}.' +
                           'Sensitivity value is not logged.')
        else:
            params['Acquisition']['Sensitivity (V/Pa) corresponding to used freq.'] = (
                str(match_row.iloc[0].iloc[1])
                )

        params['Acquisition']['Hydrophone acquisition time [us]'] = str(self.sampling_duration_us)
        params['Acquisition']['Amount of samples per acquisition'] = str(int(self.sample_count))

    def _save_acd_proces_param(self, params):
        """
        Save PicoScope parameters to an INI file.
        """

        params['ACD processing'] = {}
        params['ACD processing']['e^(iwt)'] = str(self.proces_param["eiwt"])
        params['ACD processing']['Adjustment parameter'] = str(self.proces_param["adjust"])
        params['ACD processing']['Time for the US to propagate every row [us]'] = (
            str(self.proces_param["row_pixel_us"])
            )
        params['ACD processing']['Beginning time of processing window [us]'] = (
            str(self.proces_param["begus"])
            )
        params['ACD processing']['End time of processing window [us]'] = (
            str(self.proces_param["endus"])
            )
        params['ACD processing']['Beginning sample point of processing window'] = (
            str(self.proces_param["begn"])
            )
        params['ACD processing']['End sample point of processing window'] = (
            str(self.proces_param["endn"])
            )
        params['ACD processing']['Amount of sample points in processing window'] = (
            str(self.proces_param["npoints"])
            )

    def _scan_grid(self):
        """
        Perform a scan over the grid.

        This method scans through the grid points and acquires data at each point. It saves the raw
        data and the complex acoustic data for each location.
        """

        cplx_data = np.zeros((2, self.grid_param["nsl"], self.grid_param["nrow"],
                             self.grid_param["ncol"]), dtype='float32')

        volt_data = np.zeros((self.grid_param["nsl"], self.grid_param["nrow"],
                             self.grid_param["ncol"], self.sample_count), dtype='float32')

        dest_xyz_list = []

        counter = 0
        for i in range(self.grid_param["nsl"]):
            for j in range(self.grid_param["nrow"]):
                for k in range(self.grid_param["ncol"]):
                    dest_xyz = self._calculate_new_coord_and_save(counter, i, j, k)

                    self.equipment["motors"].move(list(dest_xyz), relative=False)
                    self._acquire_data()

                    with open(self.output["outputRAW"], 'ab') as outraw:
                        self.signal_a.tofile(outraw)

                    volt_data[i, j, k] = self.signal_a

                    dest_xyz_list.append(dest_xyz)

                    # Process raw data as ACD
                    if self.proces_param["adjust"] != 0:
                        self.proces_param["begn"], self.proces_param["endn"] = self._adjust_beg(k)
                        logger.debug(f'k: {k}, begus: {self.proces_param["begus"]:.2f}, npoints ' +
                                     f'{self.proces_param["npoints"]}, beg: ' +
                                     f'{self.proces_param["begn"]}, end: ' +
                                     f'{self.proces_param["endn"]}')
                    a, p = self._process_data(beg=self.proces_param["begn"],
                                              end=self.proces_param["endn"])
                    cplx_data[0, i, j, k] = a
                    cplx_data[1, i, j, k] = p
                    time.sleep(0.025)

                    counter = counter + 1

        with open(self.output["outputACD"], 'wb') as outacd:
            cplx_data.tofile(outacd)

        return volt_data, dest_xyz_list

    def _calculate_new_coord_and_save(self, counter, i, j, k):
        """
        Calculate new coordinate based on the current position and save them.

        This method calculates the new coordinate for the scanning process, either by reading from
        an Excel file or by calculating based on the starting position and predefined vectors.
        It then logs the new position and saves the relevant data.

        Parameters:
        counter (int): The current counter for the grid scan process.
        i (int): The current slice index.
        j (int): The current row index.
        k (int): The current column index.

        Returns:
        list: The destination coordinates [destX, destY, destZ].
        """

        coord_zero = self.input_param.coord_zero
        if self.sequence.use_coord_excel:
            measur_nr = self.grid_param["coord_excel_data"].loc[counter, "Measurement number"]
            cluster_nr = self.grid_param["coord_excel_data"].loc[counter, "Cluster number"]
            indices_nr = self.grid_param["coord_excel_data"].loc[counter, "Indices number"]
            relat_xyz = [self.grid_param["coord_excel_data"].loc[counter, "X-coordinate [mm]"],
                         self.grid_param["coord_excel_data"].loc[counter, "Y-coordinate [mm]"],
                         self.grid_param["coord_excel_data"].loc[counter, "Z-coordinate [mm]"]]
            dest_xyz = [relat_xyz[0] + coord_zero[0], relat_xyz[1] + coord_zero[1],
                        relat_xyz[2] + coord_zero[2]]
            row_nr = self.grid_param["coord_excel_data"].loc[counter, "Row number"]
            col_nr = self.grid_param["coord_excel_data"].loc[counter, "Column number"]
            sl_nr = self.grid_param["coord_excel_data"].loc[counter, "Slice number"]

        else:
            measur_nr = counter + 1
            cluster_nr = 1
            indices_nr = measur_nr
            dest_xyz = (self.sequence.coord_start + i*self.sequence.vect_sl +
                        j*self.sequence.vect_row + k*self.sequence.vect_col)
            relat_xyz = [dest_xyz[0] - coord_zero[0], dest_xyz[1] - coord_zero[1],
                         dest_xyz[2] - coord_zero[2]]
            row_nr = j
            col_nr = k
            sl_nr = i

        logger.info(f'Moving to position: {dest_xyz[0]:.3f}, {dest_xyz[1]:.3f}, {dest_xyz[2]:.3f}')

        n = i*self.grid_param["nrow"]*self.grid_param["ncol"]+j*self.grid_param["ncol"]+k
        logger.info(f'i: {i}, j: {j}, k: {k}, n: {n}')

        # Save data in excel
        # [Measurement nr, Cluster nr, indices nr, relatXcor(mm), relatYcor(mm),
        # relatZcor(mm), rowNr, colNr, SliceNr, destXcor(mm), destYcor(mm),
        # destZcor(mm)]
        self._save_data([measur_nr, cluster_nr, indices_nr], relat_xyz, [row_nr, col_nr,
                        sl_nr], dest_xyz)

        return dest_xyz

    def _acquire_data(self, attempt=0):
        """
        Acquire data at the current motor position. It will start the acquisition on the PicoScope
        (wait for trigger), execute the pulse sequence (which will trigger the PicoScope), wait
        until the data has been acquired and read the data from the PicoScope into signal_a.
        """

        # Start picoscope acquisition on trigger
        self.equipment["scope"].startAcquisitionTB(self.sample_count, self.timebase)
        time.sleep(0.025)

        # Execute pulse sequence
        self.equipment["ds"].execute_sequence()

        # Wait for acquisition to complete
        ok = self.equipment["scope"].waitAcquisition()

        if not ok and attempt < 5:
            # Redo acquisition if waiting period is over and no data is acquired
            attempt += 1
            self._acquire_data(attempt)

        # Transfer data from picoscope
        self.signal_a = self.equipment["scope"].readVolts()[0]

        logger.debug(f'signal_a size: {self.signal_a.size}, ' +
                     f'dtype: {self.signal_a.dtype}')

    def _save_data(self, vol_orien, relat_xyz, plane_orien, dest_xyz):
        """
        Save the coordinates into the outputCoord file.

        Parameters:
        - vol_orien (list of int): Volume orientation consisting of -> measur_nr (int) - Measurement
            number, cluster_nr (int) - Cluster number, ind_nr (int) - Indices number.
        - relat_xyz (list of float): Relative X, Y, Z coordinates [mm].
        - plane_orien (list of int): Plane orientation consisting of -> row_nr (int) - Row number,
            col_nr (int) - Column number, sl_nr (int) - Slice number.
        - dest_xyz (list of float): Destination X, Y, Z coordinates [mm].
        """
        measur_nr, cluster_nr, ind_nr = vol_orien
        row_nr, col_nr, sl_nr = plane_orien

        with open(self.output["outputCoord"], 'a', newline='') as outcoord:
            # Round down floats to 3 decimals
            relat_xyz = [round(coord, 3) for coord in relat_xyz]
            dest_xyz = [round(coord, 3) for coord in dest_xyz]

            csv.writer(outcoord, delimiter=',').writerow([measur_nr, cluster_nr, ind_nr,
                                                          relat_xyz[0], relat_xyz[1], relat_xyz[2],
                                                          row_nr, col_nr, sl_nr,
                                                          dest_xyz[0], dest_xyz[1], dest_xyz[2]])

    def _adjust_beg(self, k):
        """
        Adjust the beginning of the processing window based on the row pixel and adjustment factor.

        This method calculates the new beginning and end points of the processing window
        by adjusting the initial beginning value with the specified row index.

        Parameters:
        - k (int): Row index used for adjustment.

        Returns:
        tuple: A tuple containing the new beginning (begn) and end (endn) points of the processin
        window
        """

        newbegus = (self.proces_param["begus"] +
                    self.proces_param["adjust"] * k * self.proces_param["row_pixel_us"])

        # Begining of the processing window
        begn = int(newbegus*1e-6*self.pico_sampling_freq)
        endn = begn + self.proces_param["npoints"]
        return (begn, endn)

    def _process_data(self, beg=0, end=None):
        """
        Process the signal data by calculating a phasor (amplitude and phase).

        This method processes the signal data within the specified range (beg to end)
        to compute the phasor, which includes the amplitude and phase of the signal.

        Parameters:
        - beg (int, optional): Beginning index for processing. Default is 0.
        - end (int, optional): Ending index for processing. Default is None, which uses the total
        sample count.

        Returns:
        tuple: A tuple containing:
            - ampl_a (float): Amplitude of the signal.
            - phase_a (float): Phase of the signal.
        """
        if not end:
            end = self.sample_count
        npoints = end-beg
        phasor = np.dot(self.signal_a[beg:end], self.proces_param["eiwt"][beg:end])
        phase_a = cmath.phase(phasor)
        ampl_a = abs(phasor)*2.0/npoints
        logger.debug(f'ampl_a: {ampl_a:.3f}, phase_a: {math.degrees(phase_a):.3f}')
        return (ampl_a, phase_a)

    def close_all(self):
        """
        Close all connected devices and release resources.
        """

        if self.equipment["motors"].connected:
            self.equipment["motors"].disconnect()

        if self.equipment["scope"] is not None:
            self.equipment["scope"].closeUnit()

        # When fus is none, probably NeuroFUS system used
        if self.equipment["ds"] is not None:
            self.equipment["ds"].disconnect()
