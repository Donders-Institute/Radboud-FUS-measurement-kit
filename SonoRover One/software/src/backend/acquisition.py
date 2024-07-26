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
import sys

# Miscellaneous packages
import cmath
import configparser
import csv
from datetime import datetime

from importlib import resources as impresources

import math
import numpy as np
import pandas as pd

import time

# Own packages
from frontend import check_dialogs

import fus_driving_systems as fds
from config.config import config_info as config, read_additional_config
from config.logging_config import logger

from backend.motor_GRBL import MotorsXYZ
from backend import pico


class Acquisition:
    def __init__(self, input_param):
        """
        Initialize Acquisition class with global acquisition parameters.

        Parameters:
        input_param (object): Given input parameters for acquisition including driving system,
        scope settings, and motor settings.
        """

        self.input_param = input_param

        # Read additional fus_driving_systems config file
        inp_file = (impresources.files(fds.config) / 'ds_config.ini')
        read_additional_config(inp_file)

        # Sync fus_driving_systems logging
        fds.config.logging_config.sync_logger(logger)

        # # Global acquisition parameters
        # Initialize equipment
        self.ds = None
        self.gen = None
        self.fus = None

        # Connect with driving system
        self._init_ds()

        # TODO: picoscope choice to front-end
        # Connect with PicoScope
        self.scope = pico.getScope("5244D")
        self.init_scope(input_param.sampl_freq_multi, input_param.acquisition_time)

        # Connect with positioning system
        self.motors = MotorsXYZ()
        self.init_motor(input_param.pos_com_port)

        # Initialize ACD processing parameters
        self.init_processing()

    def _init_ds(self):
        """
        Initialize the driving system based on the manufacturer.

        This method initializes the driving system using the manufacturer information provided in
        input parameters.
        """

        ds_manufact = str(self.input_param.driving_sys.manufact)

        add_message = ''
        # Driving system of Sonic Concepts
        if ds_manufact == config['Equipment.Manufacturer.SC']['Name']:
            add_message = config['Equipment.Manufacturer.SC']['Additional charac. discon. message']
            self.ds = fds.SC()

            check_dialogs.check_disconnection_dialog(add_message)

            self.ds.connect(self.input_param.driving_sys.connect_info)

        # Driving system of IGT
        elif ds_manufact == config['Equipment.Manufacturer.IGT']['Name']:
            add_message = config['Equipment.Manufacturer.IGT']['Additional charac. discon. message']
            self.ds = fds.IGT()

            check_dialogs.check_disconnection_dialog(add_message)

            self.ds.connect(self.input_param.driving_sys.connect_info, self.input_param.main_dir)
        else:
            logger.error(f"Unknown driving system manufacturer: {ds_manufact}")

####################################################################
    def init_scope(self, sampl_freq_multi, acquisition_dur_us):
        """
        Initialize and connect with the Picoscope.

        Parameters:
        sampl_freq_multi (float): Sampling frequency multiplier.
        acquisition_dur_us (float): Acquisition duration in microseconds.

        This method sets up the Picoscope with the appropriate channels, sampling frequency, and
            trigger settings.
        """

        self.scope.openUnit(pico.Resolution.DR_14BIT)

        # TODO: IGT - can this be removed?
        # #        self.scope.closeChannels()
        # In an exploration phase using the picoscope with the same generator settings
        # Determine the max voltage to set the range (pico.Range.RANGE_10V)
        self.scope.openChannel(pico.Channel.A, pico.Range.RANGE_500mV, pico.Coupling.DC,
                               pico.Probe.x1)

        # Calculate and set sampling frequency
        self.sampling_freq = sampl_freq_multi*self.sequence.oper_freq
        self.timebase = self.scope.timeBase(self.sampling_freq)
        self.pico_sampling_freq = self.scope.samplingRate(self.timebase)
        self.sampling_period = 1.0/self.pico_sampling_freq
        logger.debug(f'sampling freq: {self.sampling_freq}, timebase: {self.timebase}, ' +
                          f'actual sampling freq: {self.pico_sampling_freq}')

        # Determine the number of samples within the acquisition duration
        self.sample_count = int(acquisition_dur_us * self.pico_sampling_freq/1e6)
        self.sampling_duration_us = acquisition_dur_us
        logger.debug(f'duration_us: {acquisition_dur_us}, sample count: {self.sample_count}')

        # Set trigger threshold on EXT channel to 0.5V
        threshold = 0.5
        self.scope.initEXTTrigger(pico.Probe.x1, threshold, direction=pico.Trigger.Direction.RISING,
                                  ignoredSamples=0, timeout=0)
        time.sleep(4)

    def init_processing(self, begus=0.0, endus=0.0, adjust=0):
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
        self.t = self.sampling_period*np.arange(0, self.sample_count)
        self.eiwt = np.exp(1j * 2 * np.pi * self.sequence.oper_freq * self.t)  # cos(wt) + j sin(wt)

        self.adjust = adjust
        self.begus = begus
        self.begn = int(begus*1e-6*self.pico_sampling_freq)  # begining of the processing window
        self.endn = int(endus*1e-6*self.pico_sampling_freq)  # end of the processing window
        self.npoints = self.endn - self.begn
        logger.debug(f'begus: {begus}, endus: {endus}, begn: {self.begn}, endn: {self.endn}')

    def init_motor(self, port):
        """
        Initialize and connect to the motors of the positioning system.

        Parameters:
        port (str): Port for connection.

        This method initializes the motor system and connects to it using the specified port.
        """

        self.motors.connect(port=port)
        self.motors.initialize()
        pos = self.motors.readPosition()
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
        self.check_file(outfile)

        if sequence.use_coord_excel:
            self.init_grid_excel()
        else:
            self.init_grid()

        logger.info('Grid is initialized')

        # TODO: check connection with equipment
        # Send sequence to driving system
        self.ds.send_sequence(self.sequence)
        logger.info('All driving system parameters are set')

        self.save_params_ini()
        logger.info('Used parameters have been saved in a file.')

        self.scan_grid()
        logger.info('Pipeline for current sequence is finished.')

####################################################################

    def check_file(self, outfile):
        """
        Check if the filename provided already exists and handle appropriately.

        Parameters:
        outfile (str): Output file path.

        This method checks if the specified output file already exists and handles naming conflicts
        by appending a number.
        """

        self.outputRaw = outfile
        head, tail = os.path.split(self.outputRaw)
        if not os.path.isdir(head):  # if incorrect directory or no directory is given use CWD
            head = os.getcwd()
            raise OSError(f'directory does not exist: {head}')

        fileok = not os.path.isfile(self.outputRaw)
        i = 0
        imax = 99
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

        self.outputRaw = filename
        self.outputACD = os.path.splitext(filename)[0]+'.acd'
        self.outputRawCoord = os.path.splitext(filename)[0] + '_coord.raw'
        self.outputCoord = os.path.splitext(filename)[0]+'.csv'

        # Add header
        with open(self.outputCoord, 'a', newline='') as outcoord:
            csv.writer(outcoord, delimiter=',').writerow(['Measurement number', 'Cluster number',
                                                          'Indices number', 'X-coordinate [mm]',
                                                          'Y-coordinate [mm]', 'Z-coordinate [mm]',
                                                          'Row number', 'Column number',
                                                          'Slice number',
                                                          'Absolute X-coordinate [mm]',
                                                          'Absolute Y-coordinate [mm]',
                                                          'Absolute Z-coordinate [mm]'])

        self.outputJSON = os.path.splitext(filename)[0]+'.json'
        self.outputINI = os.path.splitext(filename)[0]+'.ini'
        logger.debug(f'file name raw: {self.outputRaw}, file name acd: {self.outputACD}')

    def init_grid(self):
        """
        Initialize grid with predefined grid parameters. Coordinate of the (i,j) grid point (with i
        = row, j = col) will be: starting_pos + i x vectCol + j x vectRow

        This method initializes the grid based on predefined coordinates for scanning.
        """

        # starting_pos is the initial position from which the scanning starts
        self.starting_pos = np.array(self.sequence.coord_begin)

        # Number of rows, columns and slices
        self.nsl = self.sequence.nslices_nrow_ncol[0]
        self.nrow = self.sequence.nslices_nrow_ncol[1]
        self.ncol = self.sequence.nslices_nrow_ncol[2]

        # Vectors in row, column and slice direction, its length is the pixel spacing
        self.vectRow = np.array(self.sequence.vectRow)
        self.vectCol = np.array(self.sequence.vectCol)
        self.vectSl = np.array(self.sequence.vectSl)

        # Time in us for the US to propagate ever vectRow used for ACD processing
        self.row_pixel_us = np.linalg.norm(self.vectRow)/1.5

    def init_grid_excel(self):
        """
        Initialize grid by reading coordinates from an Excel file.

        This method initializes the grid by reading coordinate data from an Excel file specified in
        the input parameters.
        """

        # Import excel file containing coordinates
        excel_path = os.path.join(self.sequence.path_coord_excel)
        if os.path.exists(excel_path):
            logger.info('Extract coordinates from ' + excel_path)
            path, ext = os.path.splitext(excel_path)
            if ext == '.xlsx':
                self.coord_excel_data = pd.read_excel(excel_path, engine='openpyxl')
            elif ext == '.xls':
                self.coord_excel_data = pd.read_excel(excel_path)
            elif ext == '.csv':
                self.coord_excel_data = pd.read_csv(excel_path)
            else:
                logger.error(f'Extension {ext} of {excel_path} unknown.')

            # Determine amount of rows, columns and slices
            self.nrow = self.coord_excel_data.loc[:, "Row number"].max()
            self.ncol = self.coord_excel_data.loc[:, "Column number"].max()
            self.nsl = self.coord_excel_data.loc[:, "Slice number"].max()

            self.sequence.nslices_nrow_ncol = [self.nsl, self.nrow, self.ncol]

        else:
            logger.error("Pipeline is cancelled. The following direction cannot be found: "
                         + excel_path)

    def save_params_ini(self):
        """
        Save parameters to an INI file.

        This method saves the input parameters to an INI file for future reference like processing.
        """

        params = configparser.ConfigParser()
        params['Versions'] = {}
        params['Versions']['Equipment characterization pipeline software'] = config['Versions']['Equipment characterization pipeline software']

        # Get current date and time for logging
        date_time = datetime.now()
        timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

        params['General'] = {}
        params['General']['Timestamp'] = str(timestamp)
        params['General']['Path and filename of protocol excel file'] = self.input_param.path_protocol_excel_file
        params['General']['Path of output'] = self.input_param.dir_output
        params['General']['Perform all sequences in sequence without waiting for user input?'] = str(self.input_param.perform_all_seqs)
        params['General']['Temperature of water [°C]'] = str(self.input_param.temp)
        params['General']['Dissolved oxygen level of water [mg/L]'] = str(self.input_param.dis_oxy)

        params['Equipment'] = {}
        params['Equipment']['Driving system.serial_number'] = self.driving_system.serial
        params['Equipment']['Driving system.name'] = self.driving_system.name
        params['Equipment']['Driving system.manufact'] = self.driving_system.manufact
        params['Equipment']['Driving system.available_ch'] = str(self.driving_system.available_ch)
        params['Equipment']['Driving system.connect_info'] = self.driving_system.connect_info
        params['Equipment']['Driving system.tran_comp'] = str(', '.join(self.driving_system.tran_comp))
        params['Equipment']['Driving system.is_active'] = str(self.driving_system.is_active)

        params['Equipment']['Transducer.serial_number'] = self.transducer.serial
        params['Equipment']['Transducer.name'] = self.transducer.name
        params['Equipment']['Transducer.manufact'] = self.transducer.manufact
        params['Equipment']['Transducer.elements'] = str(self.transducer.elements)
        params['Equipment']['Transducer.fund_freq'] = str(self.transducer.fund_freq)
        params['Equipment']['Transducer.natural_foc'] = str(self.transducer.natural_foc)
        params['Equipment']['Transducer.min_foc'] = str(self.transducer.min_foc)
        params['Equipment']['Transducer.max_foc'] = str(self.transducer.max_foc)
        params['Equipment']['Transducer.steer_info'] = self.transducer.steer_info
        params['Equipment']['Transducer.is_active'] = str(self.transducer.is_active)

        params['Equipment']['COM port of positioning system'] = self.input_param.pos_com_port

        params['Sequence'] = {}
        params['Sequence']['Sequence number'] = str(self.sequence.seq_number)
        params['Sequence']['Operating frequency [Hz]'] = str(self.sequence.oper_freq)
        params['Sequence']['Focus [um]'] = str(self.sequence.focus)

        params['Sequence']['Global power [mW] (NeuroFUS) or Amplitude [%] (IGT)'] = str(self.sequence.power_value)
        params['Sequence']['Path of Isppa to Global power conversion excel'] = str(self.sequence.path_conv_excel)

        params['Sequence']['Ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'] = str(self.sequence.ramp_mode)
        params['Sequence']['Ramp duration [us]'] = str(self.sequence.ramp_dur)
        params['Sequence']['Ramp duration step size [us]'] = str(self.sequence.ramp_dur_step)

        params['Sequence']['Pulse duration [us]'] = str(self.sequence.pulse_dur)
        params['Sequence']['Pulse repetition interval [us]'] = str(self.sequence.pulse_rep_int)
        params['Sequence']['Pulse train duration [us]'] = str(self.sequence.pulse_train_dur)

        self.save_grid_param(params)

        params['Picoscope'] = {}
        params['Picoscope']['Picoscope sampling frequency multiplication factor'] = str(self.input_param.sampl_freq_multi)
        params['Picoscope']['Sampling frequency [Hz]'] = str(self.pico_sampling_freq)
        params['Picoscope']['Hydrophone acquisition time [us]'] = str(self.sampling_duration_us)
        params['Picoscope']['Amount of samples per acquisition'] = str(int(self.sample_count))

        config_fold = config['General']['Configuration file folder']
        with open(os.path.join(config_fold, self.outputINI), 'w') as configfile:
            params.write(configfile)
        logger.info(f'Parameters saved to {self.outputINI}')

    def save_grid_param(self, params):
        params['Grid'] = {}
        params['Grid']['Absolute G code x-coordinate of relative zero [mm]'] = str(self.input_param.coord_zero[0])
        params['Grid']['Absolute G code y-coordinate of relative zero [mm]'] = str(self.input_param.coord_zero[1])
        params['Grid']['Absolute G code z-coordinate of relative zero [mm]'] = str(self.input_param.coord_zero[2])
        params['Grid']['Use coordinate excel as input?'] = str(self.sequence.use_coord_excel)
        params['Grid']['Path of coordinate excel'] = str(self.sequence.path_coord_excel)

        if self.sequence.use_coord_excel:
            params['Grid']['Number of slices, rows, columns (z-dir, x-dir, y-dir)'] = str(self.sequence.nslices_nrow_ncol)
        else:
            params['Grid']['Begin coordinates [mm]'] = str(self.sequence.coord_begin)

            sl_dir = np.nonzero(self.sequence.vectSl)[0][0]
            row_dir = np.nonzero(self.sequence.vectRow)[0][0]
            col_dir = np.nonzero(self.sequence.vectCol)[0][0]

            dirInfo = [[sl_dir, self.sequence.nslices_nrow_ncol[0]],
                       [row_dir, self.sequence.nslices_nrow_ncol[1]],
                       [col_dir, self.sequence.nslices_nrow_ncol[2]]]

            direction = '('
            for row in dirInfo:
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

            params['Grid']['Number of slices, rows, columns ' + direction] = str(self.sequence.nslices_nrow_ncol)

            params['Grid']['Slice vector [mm]'] = str(self.sequence.vectSl)
            params['Grid']['Row vector [mm]'] = str(self.sequence.vectRow)
            params['Grid']['Column vector [mm]'] = str(self.sequence.vectCol)

    def scan_grid(self):
        """
        Perform a scan over the grid.

        This method scans through the grid points and acquires data at each point. It saves the raw
        data and the complex acoustic data for each location.
        """

        self.cplx_data = np.zeros((2, self.nsl, self.nrow, self.ncol), dtype='float32')

        counter = 0
        for i in range(self.nsl):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    destXYZ = self._calculate_new_coord_and_save(counter, i, j, k)

                    self.motors.move(list(destXYZ), relative=False)
                    self.acquire_data()

                    # Process raw data as ACD
                    if self.adjust != 0:
                        self.begn, self.endn = self.adjust_beg(k)
                        logger.debug(f'k: {k}, begus: {self.begus:.2f}, npoints ' +
                                     f'{self.npoints}, beg: {self.begn}, end: {self.endn}')
                    a, p = self.process_data(beg=self.begn, end=self.endn)
                    self.cplx_data[0, i, j, k] = a
                    self.cplx_data[1, i, j, k] = p
                    time.sleep(0.025)

                    counter = counter + 1

        with open(self.outputACD, 'wb') as outacd:
            self.cplx_data.tofile(outacd)

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
            measur_nr = self.coord_excel_data.loc[counter, "Measurement number"]
            cluster_nr = self.coord_excel_data.loc[counter, "Cluster number"]
            indices_nr = self.coord_excel_data.loc[counter, "Indices number"]
            relatXYZ = [self.coord_excel_data.loc[counter, "X-coordinate [mm]"],
                        self.coord_excel_data.loc[counter, "Y-coordinate [mm]"],
                        self.coord_excel_data.loc[counter, "Z-coordinate [mm]"]]
            destXYZ = [relatXYZ[0] + coord_zero[0], relatXYZ[1] + coord_zero[1],
                       relatXYZ[2] + coord_zero[2]]
            row_nr = self.coord_excel_data.loc[counter, "Row number"]
            col_nr = self.coord_excel_data.loc[counter, "Column number"]
            sl_nr = self.coord_excel_data.loc[counter, "Slice number"]

        else:
            measur_nr = counter + 1
            cluster_nr = 1
            indices_nr = measur_nr
            destXYZ = (self.starting_pos + i*self.vectSl + j*self.vectCol +
                       k*self.vectRow)
            relatXYZ = [destXYZ[0] - coord_zero[0], destXYZ[1] - coord_zero[1],
                        destXYZ[2] - coord_zero[2]]
            row_nr = j
            col_nr = k
            sl_nr = i

        logger.info(f'Moving to position: {destXYZ[0]:.3f}, {destXYZ[1]:.3f}, {destXYZ[2]:.3f}')

        n = i*self.nrow*self.ncol+j*self.ncol+k
        logger.info(f'i: {i}, j: {j}, k: {k}, n: {n}')

        # Save data in excel
        # [Measurement nr, Cluster nr, indices nr, relatXcor(mm), relatYcor(mm),
        # relatZcor(mm), rowNr, colNr, SliceNr, destXcor(mm), destYcor(mm),
        # destZcor(mm)]
        self.save_data(measur_nr, cluster_nr, indices_nr, relatXYZ, row_nr, col_nr,
                       sl_nr, destXYZ)

        return destXYZ

    def acquire_data(self, attempt=0):
        """
        Acquire data at the current motor position. It will start the acquisition on the PicoScope
        (wait for trigger), execute the pulse sequence (which will trigger the PicoScope), wait
        until the data has been acquired and read the data from the PicoScope into signalA.
        """

        # Start picoscope acquisition on trigger
        self.scope.startAcquisitionTB(self.sample_count, self.timebase)
        time.sleep(0.025)

        # Execute pulse sequence
        self.ds.execute_sequence()

        # Wait for acquisition to complete
        ok = self.scope.waitAcquisition()

        if not ok and attempt < 5:
            # Redo acquisition if waiting period is over and no data is acquired
            attempt += 1
            self.acquire_data(attempt)

        # Transfer data from picoscope
        self.signalA = self.scope.readVolts()[0]
        logger.debug(f'signalA size: {self.signalA.size}, dtype: {self.signalA.dtype}')

    def save_data(self, measur_nr, cluster_nr, ind_nr, relatXYZ, row_nr, col_nr, sl_nr, destXYZ):
        """
        Save the acquired data in a float32 format into the outputRaw file and the corresponding
        coordinates into the outputCoord file.

        Parameters:
        - measur_nr (int): Measurement number.
        - cluster_nr (int): Cluster number.
        - ind_nr (int): Indices number.
        - relatXYZ (list of float): Relative X, Y, Z coordinates [mm].
        - row_nr (int): Row number.
        - col_nr (int): Column number.
        - sl_nr (int): Slice number.
        - destXYZ (list of float): Destination X, Y, Z coordinates [mm].
        """

        with open(self.outputRaw, 'ab') as outraw:
            self.signalA.tofile(outraw)

        with open(self.outputCoord, 'a', newline='') as outcoord:
            # Round down floats to 3 decimals
            relatXYZ = [round(coord, 3) for coord in relatXYZ]
            destXYZ = [round(coord, 3) for coord in destXYZ]

            csv.writer(outcoord, delimiter=',').writerow([measur_nr, cluster_nr, ind_nr,
                                                          relatXYZ[0], relatXYZ[1], relatXYZ[2],
                                                          row_nr, col_nr, sl_nr,
                                                          destXYZ[0], destXYZ[1], destXYZ[2]])

    def adjust_beg(self, k):
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

        newbegus = self.begus + self.adjust * k * self.row_pixel_us

        # Begining of the processing window
        begn = int(newbegus*1e-6*self.pico_sampling_freq)
        endn = begn + self.npoints
        return (begn, endn)

    def process_data(self, beg=0, end=None):
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
            - amplA (float): Amplitude of the signal.
            - phaseA (float): Phase of the signal.
        """
        if not end:
            end = self.sample_count
        npoints = end-beg
        phasor = np.dot(self.signalA[beg:end], self.eiwt[beg:end])
        phaseA = cmath.phase(phasor)
        amplA = abs(phasor)*2.0/npoints
        logger.debug(f'amplA: {amplA:.3f}, phaseA: {math.degrees(phaseA):.3f}')
        return (amplA, phaseA)

    def close_all(self):
        """
        Close all connected devices and release resources.
        """

        if self.motors.connected:
            self.motors.disconnect()
        self.scope.closeUnit()

        # When fus is none, probably NeuroFUS system used
        if self.fus is None:
            if self.gen is not None:
                self.gen.close()
        else:
            self.fus.clearListeners()
            self.fus.disconnect()
