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
import os.path
from os import getcwd
import sys

# Miscellaneous packages
import cmath
import configparser
import csv
from datetime import datetime

import math
import numpy as np
import pandas as pd

import time

# Own packages
from frontend import check_disconnection_dialog as cdd

import fus_driving_systems as fds
from fus_driving_systems.config.config import config_info as config
from fus_driving_systems.config.logging_config import logger

from backend.motor_GRBL import MotorsXYZ
from backend import pico


class Acquisition:
    def __init__(self, input_param):
        # Global acquisition parameters
        self.input_param = input_param

        # Connect with equipment
        self.ds = None
        self.gen = None
        self.fus = None
        self._init_ds()

        # TODO: picoscope choice to front-end
        self.scope = pico.getScope("5244D")
        self.init_scope(input_param.sampl_freq_multi)
        self.init_aquisition(input_param.acquisition_time)
        self.init_processing()

        self.motors = MotorsXYZ()
        self.init_motor(input_param.pos_com_port)

        # TODO: rewrite parts of init_processing_parameters()

    def _init_ds(self):
        ds_manufact = str(self.input_param.driving_sys.manufact)

        add_message = ''
        # Driving system of Sonic Concepts
        if ds_manufact == config['Equipment.Manufacturer.SC']['Name']:
            add_message = config['Equipment.Manufacturer.SC']['Additional charac. discon. message']
            self.ds = fds.SC()

            cdd.CheckDisconnectionDialog(add_message)

            self.ds.connect(self.input_param.driving_sys.connect_info)

        # Driving system of IGT
        elif ds_manufact == config['Equipment.Manufacturer.IGT']['Name']:
            add_message = config['Equipment.Manufacturer.IGT']['Additional charac. discon. message']
            self.ds = fds.IGT()

            cdd.CheckDisconnectionDialog(add_message)

            self.ds.connect(self.input_param.driving_sys.connect_info, self.input_param.main_dir)

####################################################################
    def init_scope(self, sampl_freq_multi):
        """
        Initialize and connect with the picoscope
        by default the sampling frequency is set to 10 times the signal frequency (1.5MHz)
        It could be usefull to set it to 15 times the signal frequency for better precision
        """
        # do not hesitate to increase the multiplication factor to 15 (15 points per cycle)
        self.sampling_freq = sampl_freq_multi*self.protocol.oper_freq
        self.scope.openUnit(pico.Resolution.DR_14BIT)
        # #        self.scope.closeChannels()
        # in an exploration phase using the picoscope with the same generator settings
        # determine the max voltage to set the range (pico.Range.RANGE_10V)
        self.scope.openChannel(pico.Channel.A, pico.Range.RANGE_500mV, pico.Coupling.DC, pico.Probe.x1)
        self.timebase = self.scope.timeBase(self.sampling_freq)
        self.pico_sampling_freq = self.scope.samplingRate(self.timebase)
        self.sampling_period = 1.0/self.pico_sampling_freq
        self.logger.debug(f'sampling freq: {self.sampling_freq}, timebase: {self.timebase}, actual sampling freq: {self.pico_sampling_freq}')
        threshold = 0.5  # trigger threshold on EXT channel set to 0.5V
        self.scope.initEXTTrigger(pico.Probe.x1, threshold, direction=pico.Trigger.Direction.RISING, ignoredSamples=0, timeout=0)
        time.sleep(4)

    def init_aquisition(self, duration_us):
        """
        duration_us is the duration of the acquisition in us this will determine the number of samples (sample_count)
        """
        self.sample_count = int(duration_us * self.pico_sampling_freq/1e6)
        self.sampling_duration_us = duration_us
        self.logger.debug(f'duration_us: {duration_us}, sample count: {self.sample_count}')

    def init_processing(self, port=None):
        """
        prepare the processing of the data (based on the sampling frequency and the signal frequency
        """
        self.t = self.sampling_period*np.arange(0,self.sample_count) # self.t[n] is the sampling time for sample n
        self.eiwt = np.exp(1j * 2 * np.pi * self.protocol.oper_freq * self.t)  # cos(wt) + j sin(wt)

    def init_motor(self, port=None):
        """
        Initialize and connect to the motors
        it is preferable to enter the motor port number (look in device manager)
        it also performs the homing procedure
        motor system is ready
        """
        self.motors.connect(port=port)
        self.motors.initialize()
        pos = self.motors.readPosition()
        msg = f'pos: {pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}'
        self.logger.debug(msg)

####################################################################
    def acquire_sequence(self, sequence):
        # Check existance of directory
        outfile = os.path.join(self.input_param.temp_dir_output, 'sequence_' + str(sequence.seq_number)
                               + '_output_data.raw')

        self.check_file(outfile)

        if sequence.use_coord_excel:
            self.init_grid_excel()
        else:
            self.init_grid()

        logger.info('Grid is initialized')

        # TODO: check connection with equipment
        self.ds.send_sequence(sequence)
        logger.info('All driving system parameters are set')

        self.save_params_ini(self.input_param)
        logger.info('Used parameters have been saved in a file.')

        self.scan_grid(self.input_param.coord_focus)
        logger.info('Pipeline for current sequence is finished.')

####################################################################

    def check_file(self, outfile):
        """
        check if filename provided already exist and is it does add a number at the end of the name
        raise an exception if directory does not exist
        it also prepare the filename for the ACD (Acoustic Complex Data) file
        """
        self.outputRaw = outfile
        head, tail = os.path.split(self.outputRaw)
        if not os.path.isdir(head):  # if incorrect directory or no directory is given use CWD
            head = getcwd()
            raise OSError(f'directory does not exist: {head}')
        fileok = not os.path.isfile(self.outputRaw)
        imax = 99
        i = 0
        filename = os.path.join(head, tail)
        while not fileok:
            name, ext = os.path.splitext(tail)
            fname = f'{name}_{i:02d}{ext}'
            filename = os.path.join(head, fname)
            fileok = not os.path.isfile(filename)
            self.logger.debug(f'try: {filename} : ok ?: {fileok}')
            i += 1
            if i > imax:
                raise OSError(f'no possible file name: {fname}')
        self.outputRaw = filename
        self.outputACD = os.path.splitext(filename)[0]+'.acd'
        self.outputRawCoord = os.path.splitext(filename)[0] + '_coord' +'.raw'
        self.outputCoord = os.path.splitext(filename)[0]+'.csv'
        # add header
        with open(self.outputCoord, 'a', newline='') as outcoord:
            csv.writer(outcoord, delimiter=',').writerow(['Measurement number', 'Cluster number', 'Indices number', 'X-coordinate [mm]', 'Y-coordinate [mm]', 'Z-coordinate [mm]', 'Row number', 'Column number', 'Slice number', 'Absolute X-coordinate [mm]',     'Absolute Y-coordinate [mm]', 'Absolute Z-coordinate [mm]'])

        self.outputJSON = os.path.splitext(filename)[0]+'.json'
        self.outputINI = os.path.splitext(filename)[0]+'.ini'
        self.logger.debug(f'file name raw: {self.outputRaw}, file name acd: {self.outputACD}')

    def init_grid(self):
        """
        initialize the scanning grid
        starting_pos is the initial position from which the scanning starts
        nroncol is a tuple with the number of rows and the number of colums to scan
        vectRow is the vector in the row direction. Its length is the pixel spacing
        vectCol is the vector in the column direction. Its length is the pixel spacing
        coordinate of the (i,j) grid point (with i = row, j = col) will be:
            starting_pos + i x vectCol + j x vectRow
        """

        self.starting_pos = np.array(self.protocol.coord_begin)
        self.nsl = self.protocol.nslices_nrow_ncol[0]
        self.nrow = self.protocol.nslices_nrow_ncol[1]
        self.ncol = self.protocol.nslices_nrow_ncol[2]
        self.vectSl = np.array(self.protocol.vectSl)
        self.vectRow = np.array(self.protocol.vectRow)
        self.vectCol = np.array(self.protocol.vectCol)

        # time in us for the US to propagate ever vectRow
        self.row_pixel_us = np.linalg.norm(self.vectRow)/1.5

    def init_grid_excel(self):
        # Import excel file containing coordinates
        excel_path = os.path.join(self.protocol.path_coord_excel)

        self.logger.info('Extract coordinates from ' + excel_path)

        if os.path.exists(excel_path):
            # [Measurement nr, Cluster nr, indices nr, Xcor(mm), Ycor(mm), Zcor(mm), rowNr,
            # colNr, SliceNr]

            path, ext = os.path.splitext(excel_path)

            if ext == '.xlsx':
                self.coord_excel_data = pd.read_excel(excel_path, engine='openpyxl')
            elif ext == '.xls':
                self.coord_excel_data = pd.read_excel(excel_path)
            elif ext == '.csv':
                self.coord_excel_data = pd.read_csv(excel_path)

            self.nrow = self.coord_excel_data.loc[:, "Row number"].max()
            self.ncol = self.coord_excel_data.loc[:, "Column number"].max()
            self.nsl = self.coord_excel_data.loc[:, "Slice number"].max()

            self.protocol.nslices_nrow_ncol = [self.nsl, self.nrow, self.ncol]

        else:
            self.logger.error("Pipeline is cancelled. The following direction cannot be found: "
                              + excel_path)
            sys.exit()

    def save_params_ini(self, inputValues):
        params = configparser.ConfigParser()
        params['Versions'] = {}
        params['Versions']['Equipment characterization pipeline software'] = self.config['Versions']['Equipment characterization pipeline software']

        # Get current date and time for logging
        date_time = datetime.now()
        timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

        params['General'] = {}
        params['General']['Timestamp'] = str(timestamp)
        params['General']['Path and filename of protocol excel file'] = inputValues.path_protocol_excel_file
        params['General']['Path of output'] = inputValues.dir_output
        params['General']['Perform all protocols in sequence without waiting for user input?'] = str(inputValues.perform_all_protocols)
        params['General']['Temperature of water [°C]'] = str(inputValues.temp)
        params['General']['Dissolved oxygen level of water [mg/L]'] = str(inputValues.dis_oxy)

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

        params['Equipment']['COM port of positioning system'] = inputValues.pos_com_port

        params['Sequence'] = {}
        params['Sequence']['Sequence number'] = str(self.protocol.seq_number)
        params['Sequence']['Operating frequency [Hz]'] = str(self.protocol.oper_freq)
        params['Sequence']['Focus [um]'] = str(self.protocol.focus)

        params['Sequence']['Global power [mW] (NeuroFUS) or Amplitude [%] (IGT)'] = str(self.protocol.power_value)
        params['Sequence']['Path of Isppa to Global power conversion excel'] = str(self.protocol.path_conv_excel)

        params['Sequence']['Ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'] = str(self.protocol.ramp_mode)
        params['Sequence']['Ramp duration [us]'] = str(self.protocol.ramp_dur)
        params['Sequence']['Ramp duration step size [us]'] = str(self.protocol.ramp_dur_step)

        params['Sequence']['Pulse duration [us]'] = str(self.protocol.pulse_dur)
        params['Sequence']['Pulse repetition interval [us]'] = str(self.protocol.pulse_rep_int)
        params['Sequence']['Pulse train duration [us]'] = str(self.protocol.pulse_train_dur)

        params['Grid'] = {}
        params['Grid']['Absolute G code x-coordinate of relative zero [mm]'] = str(inputValues.coord_focus[0])
        params['Grid']['Absolute G code y-coordinate of relative zero [mm]'] = str(inputValues.coord_focus[1])
        params['Grid']['Absolute G code z-coordinate of relative zero [mm]'] = str(inputValues.coord_focus[2])
        params['Grid']['Use coordinate excel as input?'] = str(self.protocol.use_coord_excel)
        params['Grid']['Path of coordinate excel'] = str(self.protocol.path_coord_excel)

        if self.protocol.use_coord_excel:
            params['Grid']['Number of slices, rows, columns (z-dir, x-dir, y-dir)'] = str(self.protocol.nslices_nrow_ncol)
        else:
            params['Grid']['Begin coordinates [mm]'] = str(self.protocol.coord_begin)

            sl_dir = np.nonzero(self.protocol.vectSl)[0][0]
            row_dir = np.nonzero(self.protocol.vectRow)[0][0]
            col_dir = np.nonzero(self.protocol.vectCol)[0][0]

            dirInfo = [ [sl_dir, self.protocol.nslices_nrow_ncol[0]] , [row_dir, self.protocol.nslices_nrow_ncol[1]], [col_dir, self.protocol.nslices_nrow_ncol[2] ]]

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

            params['Grid']['Number of slices, rows, columns ' + direction] = str(self.protocol.nslices_nrow_ncol)

            params['Grid']['Slice vector [mm]'] = str(self.protocol.vectSl)
            params['Grid']['Row vector [mm]'] = str(self.protocol.vectRow)
            params['Grid']['Column vector [mm]'] = str(self.protocol.vectCol)

        params['Picoscope'] = {}
        params['Picoscope']['Picoscope sampling frequency multiplication factor'] = str(inputValues.sampl_freq_multi)
        params['Picoscope']['Sampling frequency [Hz]'] = str(self.pico_sampling_freq)
        params['Picoscope']['Hydrophone acquisition time [us]'] = str(self.sampling_duration_us)
        params['Picoscope']['Amount of samples per acquisition'] = str(int(self.sample_count))

        config_fold = self.config['General']['Configuration file folder']
        with open(os.path.join(config_fold, self.outputINI), 'w') as configfile:
            params.write(configfile)

    def scan_grid(self, coord_focus):
        """
        scan the predefined grid and save the raw data and the complex acoustic data for each
        location
        begus: start of the processing window in us
        endus: end of the processing window in us
        adjust will adjust the windows [beg..end] with the time of flight
        when the row is along US propagation.
        adjust=-1 if top-left corner is far from transducer (decrease beg)
        adjust=+1 if top-left corner is close to the transducer (increase beg)
        adjust=0 : no adjustment
        """

        self.cplx_data = np.zeros((2, self.nsl, self.nrow, self.ncol), dtype='float32')

        counter = 0
        for i in range(self.nsl):
            for j in range(self.nrow):
                for k in range(self.ncol):
                    if self.protocol.use_coord_excel:
                        measur_nr = self.coord_excel_data.loc[counter, "Measurement number"]
                        cluster_nr = self.coord_excel_data.loc[counter, "Cluster number"]
                        indices_nr = self.coord_excel_data.loc[counter, "Indices number"]
                        relatXYZ = [self.coord_excel_data.loc[counter, "X-coordinate [mm]"], self.coord_excel_data.loc[counter,"Y-coordinate [mm]"], self.coord_excel_data.loc[counter,"Z-coordinate [mm]"]]
                        destXYZ = [relatXYZ[0] + coord_focus[0], relatXYZ[1] + coord_focus[1], relatXYZ[2] + coord_focus[2] ]
                        row_nr = self.coord_excel_data.loc[counter, "Row number"]
                        col_nr = self.coord_excel_data.loc[counter, "Column number"]
                        sl_nr = self.coord_excel_data.loc[counter, "Slice number"]

                    else:
                        measur_nr = counter + 1
                        cluster_nr = 1
                        indices_nr = measur_nr
                        destXYZ = self.starting_pos + i*self.vectSl + j*self.vectCol + k*self.vectRow
                        relatXYZ = [destXYZ[0] - coord_focus[0], destXYZ[1] - coord_focus[1], destXYZ[2] - coord_focus[2]]
                        row_nr = j
                        col_nr = k
                        sl_nr = i

                    self.logger.info(f'destXYZ: pos: {destXYZ[0]:.3f}, {destXYZ[1]:.3f}, {destXYZ[2]:.3f}')
                    n = i*self.nrow*self.ncol+j*self.ncol+k
                    self.logger.info(f'i: {i}, j: {j}, k: {k}, n: {n}')
                    self.motors.move(list(destXYZ), relative=False)
                    self.acquire_data()

                    # [Measurement nr, Cluster nr, indices nr, Xcor(mm), Ycor(mm), Zcor(mm), rowNr, colNr, SliceNr]
                    self.save_data(measur_nr, cluster_nr, indices_nr, relatXYZ, row_nr, col_nr, sl_nr, destXYZ)

                    if self.adjust!=0:
                        self.begn, self.endn= self.adjust_beg(k)
                        self.logger.debug(f'k: {k}, begus: {self.begus:.2f}, npoints {self.npoints}, beg: {self.begn}, end: {self.endn}')
                    a,p = self.process_data(beg=self.begn,end=self.endn)
                    self.cplx_data[0,i,j,k]=a
                    self.cplx_data[1,i,j,k]=p
                    time.sleep(0.025)

                    counter = counter + 1

        with open(self.outputACD,'wb') as outacd:
            self.cplx_data.tofile(outacd)

    def acquire_data(self, attempt=0):
        """
        acquire data will:
            start acquisition on the picoscope (wait for trigger)
            execute the pulse sequence (which will trigger the picoscope
            wait until the data has been acquired
            read the data from the picoscope into signalA (because channel A is used)
        """
        self.scope.startAcquisitionTB (self.sample_count, self.timebase) # start picoscope acquisition on trigger
        time.sleep(0.025)
        self.ds.execute_sequence()                   # execute pulse sequence
        ok = self.scope.waitAcquisition()                # wait for acquisition to complete

        if not ok and attempt < 5:
            # redo acquisition
            attempt += 1
            self.acquire_data(attempt)

        self.signalA = self.scope.readVolts()[0]     # transfer data from picoscope
        msg = f'signalA size: {self.signalA.size}, dtype: {self.signalA.dtype}'
        self.logger.debug(msg)

    def save_data(self, measur_nr, cluster_nr, indices_nr, relatXYZ, row_nr, col_nr, sl_nr, destXYZ):
        """
        save the acquired data in a float32 format into outpuRaw
        """
        with open(self.outputRaw,'ab') as outraw:
            self.signalA.tofile(outraw)

        with open(self.outputCoord, 'a', newline='') as outcoord:
            # round down floats to 3 decimals
            relatXYZ = [round(coord,3) for coord in relatXYZ]
            destXYZ = [round(coord,3) for coord in destXYZ]

            csv.writer(outcoord, delimiter=',').writerow([measur_nr, cluster_nr, indices_nr, relatXYZ[0], relatXYZ[1], relatXYZ[2], row_nr, col_nr, sl_nr, destXYZ[0], destXYZ[1], destXYZ[2]])

    def adjust_beg(self, k):
        newbegus = self.begus + self.adjust * k * self.row_pixel_us

        # begining of the processing window
        begn = int(newbegus*1e-6*self.pico_sampling_freq)
        endn = begn + self.npoints
        return (begn, endn)

    def process_data(self, beg=0, end=None):
        """
        process the data by calculating a phasor (amplitude and phase)
        returns the phasor (amplitude and phase of the signal)
        """
        if not end:
            end = self.sample_count
        npoints = end-beg
        phasor = np.dot(self.signalA[beg:end], self.eiwt[beg:end])
        phaseA = cmath.phase(phasor)
        amplA = abs(phasor)*2.0/npoints
        self.logger.debug(f'amplA: {amplA:.3f}, phaseA: {math.degrees(phaseA):.3f}')
        return (amplA, phaseA)

    def close_all(self):
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
