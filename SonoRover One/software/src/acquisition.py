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

import sys
import os.path
from os import getcwd
import time
import logging
import numpy as np
import cmath
import math
import serial

import json
import tpoCommunication as tpoCom
from psychopy import gui
import csv
from datetime import datetime

from scan_iter import Scan_Iter
from motor_GRBL import MotorsXYZ
import pico
import pandas as pd

import utils
import unifus

import configparser
import transducerXYZ


class Acquisition:
    """
    class to acquire acoustic signal on a scanned grid
    outfile is the path+filename of the output file with the raw data
    starting_pos is the starting position of the scan [X0, Y0, Z0]
    nrowncol is the number of points in the row and col directions respectively
    vectRow, vectCol are the direction vectors for rows and columns.
    Ex: vectRow = [0.5,0.0,0.0] and vectCol = [0.0,0.5,0.0] will have a grid os
    points in the XY plane coordinate of the (i,j) grid point (with i = row,
    j = col) will be: starting_pos + i x vectCol + j x vectRow
    """

    def __init__(self, config):
        self.logger = logging.getLogger(config['General']['Logger name'])
        self.logger.setLevel(logging.INFO)

        self.outputRaw = None
        self.outputACD = None
        self.outputRawCoord = None
        self.outputCoord = None
        self.outputJSON = None
        self.outputINI = None

        self.nrowncol = None
        self.vectRow = None
        self.vectCol = None

        self.motors = MotorsXYZ(config['General']['Logger name'])
        self.gen = None
        self.fus = None
        self.scope = pico.getScope("5244D")
        self.sampling_freq = 0
        self.sampling_period = 0
        self.sampling_duration_us = 0
        self.sample_count = 0
        self.pico_sampling_freq = 15625000
        self.sequence = []
        self.signalA = None

        self.begn = 0  # begining of the processing window
        self.endn = 1  # end of the processing window
        self.adjust = 0  # adjust for time of flight
        self.begus = 40
        self.protocol = None
        self.npoints = 2500

        self.coord_excel_data = None
        self.config = config

        self.driving_system = None
        self.transducer = None

        self.listener = None  # listener for IGT driving system
        self.totalSequenceDuration_ms = 0

        self.channels = 0

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

    def adjust_beg(self, k):
        newbegus = self.begus + self.adjust * k * self.row_pixel_us

        # begining of the processing window
        begn = int(newbegus*1e-6*self.pico_sampling_freq)
        endn = begn + self.npoints
        return (begn, endn)

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

    def init_generator(self, performAllProtocols=False, log_dir=''):
        """
        initialize the generator
        """

        # If it is the first protocol, then show message independent of performAllProtocols value
        if self.protocol.seq_number == 1 or not performAllProtocols:
            # check if correct transducer is selected on driving system
            confirmation_dialog = gui.Dlg(title="WARNING")

            if self.config['Equipment.Manufacturer.SC']['Name'] == self.driving_system.manufact:
                confirmation_dialog.addText('Ensure the following: \n - the correct TRANSDUCER is selected on the driving system. \n - PicoScope software is not connected to the PicoScope in use. \n - Universal Gcode Sender is not connected to the positioning system.')

            elif self.config['Equipment.Manufacturer.IGT']['Name'] == self.driving_system.manufact:
                confirmation_dialog.addText('Ensure the following: \n - PicoScope software is not connected to the PicoScope in use. \n - Universal Gcode Sender is not connected to the positioning system.')

            confirmation_dialog.show()
            if confirmation_dialog.OK:
                self.logger.info("Correct transducer selection, and disconnection of PicoScope software and Universal Gcode Sender are confirmed.")
            else:
                self.logger.error("Pipeline is cancelled by user.")
                sys.exit()

        if self.config['Equipment.Manufacturer.SC']['Name'] == self.driving_system.manufact:

            # Establish connection with driving system
            self.gen = serial.Serial(self.driving_system.connect_info, 115200, timeout=1)
            startup_message = self.gen.readline().decode("ascii").strip()
            self.logger.info(f"Driving system: {startup_message}")

            if startup_message == 'E2':
                self.logger.error("Error E2; connection cannot be made with driving system")
                sys.exit()
            else:
                self.logger.info(f"Connection with driving system {startup_message} is established")

        elif self.config['Equipment.Manufacturer.IGT']['Name'] == self.driving_system.manufact:

            # Establish connection with driving system
            self.fus = unifus.FUSSystem()

            unifus.setLogPath(log_dir, "log")
            unifus.setLogLevel(unifus.LogLevel.Debug)

            # Update the name of your configuration file
            igt_config = os.path.join(os.getcwd(), self.driving_system.connect_info)
            if igt_config != '':
                self.fus.loadConfig(igt_config)
            else:
                self.logger.error(f"Configuration file {igt_config} doesn't exist.")
                sys.exit()

            # Create and register an event listener
            self.listener = utils.ExecListener()
            self.fus.registerListener(self.listener)

            self.fus.connect()
            self.listener.waitConnection()
            if not self.fus.isConnected():
                self.logger.error("Error: connection failed.")
                sys.exit()

            self.gen = self.fus.gen()

    def init_pulse_sequence(self):
        """
        initialize the pulse sequence
        duration = duration of the pulse in us. Usually 120us is a good duration
        delay = pulse delay (should be set to at least 2000us)
        frequency = chose your transducer frequence (1.5MHz)
        self.frequency
        """

        if self.config['Equipment.Manufacturer.SC']['Name'] == self.driving_system.manufact:
            com_bridge = tpoCom.tpoCommunication(self.config['General']['Logger name'], self.gen)
            com_bridge.resetParameters()

            com_bridge.setOperatingFreq(self.protocol.oper_freq)
            com_bridge.setFocus(self.protocol.focus)
            com_bridge.setGlobalPower(self.protocol.power_value)
            com_bridge.setBurstAndPeriod(self.protocol.pulse_dur, self.protocol.pulse_rep_int)
            com_bridge.setTimer(self.protocol.pulse_train_dur)
            com_bridge.setRamping(self.protocol.ramp_mode, self.protocol.ramp_dur,
                                  self.protocol.seq_number)

        elif self.config['Equipment.Manufacturer.IGT']['Name'] == self.driving_system.manufact:
            self.channels = self.gen.getParam(unifus.GenParam.ChannelCount)
            self.logger.info("Generator: %d channels" % self.channels)

            # Define pulse
            pulse = unifus.Pulse(self.channels, 1, 1)  # n phases, n frequencies, n amplitudes

            pulse_dur_ms = self.protocol.pulse_dur/1000  # convert from us to ms
            pulse_rep_int_ms = self.protocol.pulse_rep_int/1000  # convert from us to ms

            # duration: 25us, delay: 500ms
            pulse.setDuration(pulse_dur_ms, round(pulse_rep_int_ms - pulse_dur_ms, 1))

            # set same frequency for all channels = 250KHz, in Hz
            pulse.setFrequencies([self.protocol.oper_freq])

            # set same amplitude for all channels in percent (of max amplitude)
            pulse.setAmplitudes([self.protocol.power_value])

            if self.config['Equipment.Manufacturer.IS']['Name'] == self.transducer.manufact:
                ini_path = os.path.join(os.getcwd(), self.transducer.steer_info)

                trans = transducerXYZ.Transducer(self.logger)
                if not trans.load(ini_path):
                    self.logger.error(f'Error: can not load the transducer definition from {ini_path}')
                    sys.exit()

                focus_mm = round(self.protocol.focus/1000, 1)  # convert from um to mm
                # Calculate target focus with respect to natural focus: + is before natural focus,
                # - is after natural focus
                aim_wrt_natural_focus = self.transducer.natural_foc - focus_mm

                # Aim n mm away from the natural focal spot, on main axis (Z)
                trans.computePhases(pulse, (0, 0, aim_wrt_natural_focus), focus_mm)

            # Assume NeuroFUS transducers are used
            else:
                phases = self.getPhases()
                pulse.setPhases(phases)  # set same phase offset for all channels (angle in [0,360] degrees)

            # Define pulse train
            pulse_train_dur_ms = self.protocol.pulse_train_dur/1000 # convert from us to ms

            nPulseTrain = math.floor(pulse_train_dur_ms / pulse_rep_int_ms)      # number of executions of one pulse train

            # Not used right now during characterization
            self.nPulseTrainRep = 1
            self.pulseTrainDelay = 0
            # =============================================================================
            #             pulseTrainDelay = pulse_rep_int_ms - pulse_train_dur_ms  # milliseconds between pulse trains
            #             #execFlags = unifus.ExecFlag.MeasureBoards
            #                 # Use unifus.ExecFlag.NONE if nothing special, or simply don't pass the execFlags argument.
            #                 # Use '|' to combine multiple flags: flag1 | flag2 | flag3
            #                 # To use trigger, add one of unifus::ExecFlag::Trigger*
            #                 # execFlags = unifus.ExecFlag.MeasureTimings | unifus.ExecFlag.TriggerAllSequences
            # 
            #             # Define pulse train repetition
            #             nPulseTrainRep = math.floor(self.protocol.pulse_train_rep_dur / self.protocol.pulse_train_rep_int)     # number of executions of one pulse train
            # =============================================================================

            # # | unifus.ExecFlag.MeasureBoards
            self.execFlags = unifus.ExecFlag.MeasureTimings | unifus.ExecFlag.DisableMonitoringChannelCombiner | unifus.ExecFlag.DisableMonitoringChannelCurrentOut
            # flags to disable checking the current limit

            # Define a complete sequence
            self.seqBuffer = 0
            self.seq = []
            self.seq += nPulseTrain * [pulse]

            # Apply ramping

            # Execution with pulse modulation (automatically disable ramps if any)
            # Values are attenuation in percent of the full Pulse amplitude.
            # 0 = no attenuation = full amplitude, 100 = full attenuation = 0 amplitude.
            # Check gen.getTiming (unifus.GenTiming.Min/MaxModulationStep) for valid range.
            myStepDurationMs = self.protocol.ramp_dur_step/1000  # convert from us to ms, for example, 1ms / step
            if myStepDurationMs < self.gen.getTiming(unifus.GenTiming.MinModulationStep):
                myStepDurationMs = self.gen.getTiming(unifus.GenTiming.MinModulationStep)
            elif myStepDurationMs > self.gen.getTiming(unifus.GenTiming.MaxModulationStep):
                myStepDurationMs = self.gen.getTiming(unifus.GenTiming.MaxModulationStep)

            pulse_ramp_dur_ms = self.protocol.ramp_dur/1000  # convert from us to ms
            if self.protocol.ramp_mode != 0:
                aRamp = getRampingAmplitude(self.protocol.ramp_mode,
                                            pulse_ramp_dur_ms, myStepDurationMs)
                maxAmpl = 100  # %

                # Note: ramp up and ramp down order are the other way around
                # ramp up descends, ramp down ascends
                rampDown = aRamp * maxAmpl
                rampDown = [int(pUp) for pUp in rampDown]

                rampUp = np.flip(aRamp) * maxAmpl
                rampUp = [int(pDown) for pDown in rampUp]

                self.gen.setPulseModulation(
                    rampUp, myStepDurationMs,   # beginning
                    rampDown, myStepDurationMs)   # end

            # (optional) restore disabled channels
            self.gen.enableAllChannels()

            # (optional) disable HeartBeat security
            self.gen.setParam(unifus.GenParam.HeartBeatTimeout, 0)

            # (optional) only for generator with a transducer multiplexer
            # gen.setParam (unifus.GenParam.MultiplexerValue, 3);

            return

    def getPhases(self):
        focus_mm = round(self.protocol.focus/1000, 1)  # convert from um to mm

        # Import excel file containing phases per focal depth
        excel_path = os.path.join(os.getcwd(), self.transducer.steer_info)

        self.logger.info('Extract phase information from ' + excel_path)

        if os.path.exists(excel_path):
            data = pd.read_excel(excel_path, engine='openpyxl')

            # Make sure both values have the same amount of decimals
            focus = round(focus_mm, 1)
            match_row = data.loc[data['Distance'] == focus]

            if match_row.empty:
                self.logger.error(f'No focus in transducer phases file {excel_path} corresponds with {focus_mm}')
                sys.exit()
            elif len(match_row) > 1:
                self.logger.error(f'Duplicate foci {focus_mm} found in transducer phases file {excel_path}')
                sys.exit()

            # Retrieve phases dependent of number of channels
            phases = [match_row.iloc[0][1:int(self.channels)+1]].to_list()

        else:
            self.logger.error("Pipeline is cancelled. The following direction cannot be found: " + excel_path)
            sys.exit()

        return phases

    def exec_pulse_sequence(self, repetitions=1, exec_delay_us=0, exec_flags = 0):
        """
        execute the pulse sequence
        """

        if self.config['Equipment.Manufacturer.SC']['Name'] == self.driving_system.manufact:
            cmd = 'START\r'
            nb = self.gen.write(cmd.encode('ascii'))
            time.sleep(0.05)
            line = self.gen.readline().decode('ascii')
            print(f'START: {line}')

        elif self.config['Equipment.Manufacturer.IGT']['Name'] == self.driving_system.manufact:
            try:
                # Upload and execute the sequence
                self.gen.sendSequence(self.seqBuffer, self.seq)

                self.gen.prepareSequence(self.seqBuffer, self.nPulseTrainRep, self.pulseTrainDelay, self.execFlags)

                self.totalSequenceDuration_ms = (100 + unifus.sequenceDurationMs (self.seq, self.nPulseTrainRep, self.pulseTrainDelay))

                self.gen.startSequence()
                self.listener.waitSequence(self.totalSequenceDuration_ms / 1000.0)

            except Exception as why:
                self.logger.error("Exception: " + str(why))

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

    def init_scope_params(self, sampl_freq_multi):
        """
        Initialize picoscope parameters: sampling frequency
        """
        self.sampling_freq = sampl_freq_multi*self.protocol.oper_freq
        self.pico_sampling_freq = self.sampling_freq
        self.sampling_period = 1.0/self.pico_sampling_freq

    def init_aquisition(self, duration_us):
        """
        duration_us is the duration of the acquisition in us this will determine the number of samples (sample_count)
        """
        self.sample_count = int(duration_us * self.pico_sampling_freq/1e6)
        self.sampling_duration_us = duration_us
        self.logger.debug(f'duration_us: {duration_us}, sample count: {self.sample_count}')

    def init_scan(self, scan='Dir'):
        """
        init the scan in either direct mode: acquire all lines starting from the same position
        Dir: (0,0), (0,1), (0,2), (0,3), (1,0), (1,1), (1,2), (1,3)
        Alt: (0,0), (0,1), (0,2), (0,3), (1,3), (1,3), (1,1), (1,0)
        """
        self.logger.debug(f'scan: {scan}')
        self.grid = Scan_Iter(self.nsl,self.nrow,self.ncol,scan=scan)

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
        self.exec_pulse_sequence()                    # execute pulse sequence
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
    
    def init_motor(self, port=None):
        """
        Initialize and connect to the motors
        it is preferable to enter the motor port number (look in device manager)
        it also performs the homing procedure
        motor system is ready
        """
        self.motors.connect(port=port)
        self.motors.initialize()
        pos=self.motors.readPosition()
        msg = f'pos: {pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}'
        self.logger.debug(msg)

    def init_processing(self, port=None):
        """
        prepare the processing of the data (based on the sampling frequency and the signal frequency
        """
        self.t = self.sampling_period*np.arange(0,self.sample_count) # self.t[n] is the sampling time for sample n
        self.eiwt = np.exp(1j * 2 * np.pi * self.protocol.oper_freq * self.t)  # cos(wt) + j sin(wt)

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

    def init_processing_parameters(self, begus=0.0, endus=0.0, adjust=0):
        self.adjust=adjust
        self.begus=begus
        self.begn = int(begus*1e-6*self.pico_sampling_freq) # begining of the processing window
        self.endn = int(endus*1e-6*self.pico_sampling_freq) # end of the processing window
        self.npoints = self.endn - self.begn
        self.logger.debug(f'begus: {begus}, endus: {endus}, begn: {self.begn}, endn: {self.endn}')

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

        params['Protocol'] = {}
        params['Protocol']['Sequence number'] = str(self.protocol.seq_number)
        params['Protocol']['Operating frequency [Hz]'] = str(self.protocol.oper_freq)
        params['Protocol']['Focus [um]'] = str(self.protocol.focus)

        params['Protocol']['Global power [mW] (NeuroFUS) or Amplitude [%] (IGT)'] = str(self.protocol.power_value)
        params['Protocol']['Path of Isppa to Global power conversion excel'] = str(self.protocol.path_conv_excel)

        params['Protocol']['Ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'] = str(self.protocol.ramp_mode)
        params['Protocol']['Ramp duration [us]'] = str(self.protocol.ramp_dur)
        params['Protocol']['Ramp duration step size [us]'] = str(self.protocol.ramp_dur_step)

        params['Protocol']['Pulse duration [us]'] = str(self.protocol.pulse_dur)
        params['Protocol']['Pulse repetition interval [us]'] = str(self.protocol.pulse_rep_int)
        params['Protocol']['Pulse train duration [us]'] = str(self.protocol.pulse_train_dur)

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

    def save_params_json(self):
        """
        save the acquisition params into outputJSON
        """
        acq_params = {
            'processing':
            {
                'begin': self.begn,
                'end': self.endn,
                'adjust': self.adjust
            },
            'protocol':
            {
                'Driving system': self.protocol.driving_system.name,
                'Transducer': self.protocol.transducer.name,
                'Sequence number': self.protocol.seq_number,
                'Operating frequency [Hz]': self.protocol.oper_freq,
                'Pulse duration [us]': self.protocol.pulse_dur,
                'Pulse repetition interval [us]': self.protocol.pulse_rep_int,
                'Pulse train duration [us]': self.protocol.pulse_train_dur,
                'Global power [mW]': int(self.protocol.power_value),
                'Focus [um]': self.protocol.focus,
                'Ramp mode': self.protocol.ramp_mode,
                'Ramp duration [us]': self.protocol.ramp_dur,
                'Begin coordinates [mm]': self.protocol.coord_begin,
                'Number of slices, rows, columns': self.protocol.nslices_nrow_ncol
            },
            'scope':
            {
                'sampling_freq [Hz]': self.pico_sampling_freq,
                'acquisition_duration [us]': self.sampling_duration_us,
                'samples': self.sample_count
            },
            'grid':
            {
                'starting_pos [mm]': self.starting_pos.tolist(),
                'n_slices': self.nsl,
                'n_row': self.nrow,
                'n_col': self.ncol,
                'vect_slice [mm]': self.vectSl.tolist(),
                'vect_row [mm]': self.vectRow.tolist(),
                'vect_col [mm]': self.vectCol.tolist()
            }
        }
        json_string = json.dumps(acq_params, indent=4)
        with open(self.outputJSON, 'w') as outfile:
            outfile.write(json_string)

    def scan_noMotion(self, coord_focus):
        """
        scan without moving the motors (mostly for debugging)
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
                        relatXYZ = [self.coord_excel_data.loc[counter, "X-coordinate [mm]"],
                                    self.coord_excel_data.loc[counter, "Y-coordinate [mm]"],
                                    self.coord_excel_data.loc[counter, "Z-coordinate [mm]"]]
                        destXYZ = [relatXYZ[0] + coord_focus[0], relatXYZ[1] + coord_focus[1],
                                   relatXYZ[2] + coord_focus[2]]
                        row_nr = self.coord_excel_data.loc[counter, "Row number"]
                        col_nr = self.coord_excel_data.loc[counter, "Column number"]
                        sl_nr = self.coord_excel_data.loc[counter, "Slice number"]

                    else:
                        measur_nr = counter + 1
                        cluster_nr = 1
                        indices_nr = measur_nr
                        destXYZ = (self.starting_pos + i*self.vectSl + j*self.vectCol
                                   + k*self.vectRow)
                        relatXYZ = [destXYZ[0] - coord_focus[0], destXYZ[1] - coord_focus[1],
                                    destXYZ[2] - coord_focus[2]]
                        row_nr = j
                        col_nr = k
                        sl_nr = i

                    self.acquire_data()

                    # [Measurement nr, Cluster nr, indices nr, Xcor(mm), Ycor(mm), Zcor(mm), rowNr,
                    # colNr, SliceNr, destXYZ]
                    self.save_data(measur_nr, cluster_nr, indices_nr, relatXYZ, row_nr,
                                   col_nr, sl_nr, destXYZ)

                    a, p = self.process_data(beg=0, end=int(self.sample_count//2))
                    self.cplx_data[0, i, j, k] = a
                    self.cplx_data[1, i, j, k] = p
                    time.sleep(0.05)

                    counter = counter + 1

        with open(self.outputACD, 'wb') as outacd:
            self.cplx_data.tofile(outacd)

    def pulse_only(self, performAllProtocols, repetitions=1, delay_s=1.0, log_dir=''):
        """
        execute the pulse sequence without having the pico connected and without motion
        use this with the picoscope software to acquire data with identical generator settings
        useful for setting up the picoscope parameters
        """
        try:
            self.init_generator(performAllProtocols, log_dir)
            self.init_pulse_sequence()
            for i in range(repetitions):
                self.exec_pulse_sequence()
                time.sleep(delay_s)
        finally:
            self.gen.close()

    def scan_only(self, coord_focus, delay_s=0.0, scan='Dir'):
        """
        scan the predefined grid without any acquisition to verify grid positions
        """
        self.logger.debug(f'scan: {scan}')
        self.init_scan(scan=scan)
        t0 = time.time()

        counter = 0
        for s, r, c in self.grid:
            if self.protocol.use_coord_excel:
                destXYZ = [self.coord_excel_data.loc[counter, "X-coordinate [mm]"] + coord_focus[0],
                           self.coord_excel_data.loc[counter, "Y-coordinate [mm]"] + coord_focus[1],
                           self.coord_excel_data.loc[counter, "Z-coordinate [mm]"] + coord_focus[2]]
            else:
                destXYZ = self.starting_pos + s*self.vectSl + r*self.vectCol + c*self.vectRow

            self.logger.info(f'src: [{s}, {r}, {c}], destXYZ: {destXYZ[0]:.3f}, {destXYZ[1]:.3f}, {destXYZ[2]:.3f}')
            self.motors.move(list(destXYZ), relative=False)
            counter = counter + 1

        # time.sleep(delay_s)
        t1 = time.time()
        delta_t = t1-t0
        print(f'duration: {delta_t}')
        return delta_t

    def read_params_ini(self, filepath):
        """
        save the acquisition params into outputJSON
        """

        acqs_params = configparser.ConfigParser()
        acqs_params.read(filepath)

        self.driving_system.serial = acqs_params['Equipment']['Driving system.serial_number']
        self.driving_system.name = acqs_params['Equipment']['Driving system.name']
        self.driving_system.manufact = acqs_params['Equipment']['Driving system.manufact']
        self.driving_system.available_ch = int(acqs_params['Equipment']['Driving system.available_ch'])
        self.driving_system.connect_info = acqs_params['Equipment']['Driving system.connect_info']
        self.driving_system.tran_comp = acqs_params['Equipment']['Driving system.tran_comp'].split(', ')
        self.driving_system.is_active = (acqs_params['Equipment']['Driving system.is_active'] == 'True')

        self.transducer.serial = acqs_params['Equipment']['Transducer.serial_number']
        self.transducer.name = acqs_params['Equipment']['Transducer.name']
        self.transducer.manufact = acqs_params['Equipment']['Transducer.manufact']
        self.transducer.elements = int(acqs_params['Equipment']['Transducer.elements'])
        self.transducer.fund_freq = int(acqs_params['Equipment']['Transducer.fund_freq'])
        self.transducer.natural_foc = float(acqs_params['Equipment']['Transducer.natural_foc'])
        self.transducer.min_foc = float(acqs_params['Equipment']['Transducer.min_foc'])
        self.transducer.max_foc = float(acqs_params['Equipment']['Transducer.max_foc'])
        self.transducer.steer_info = acqs_params['Equipment']['Transducer.steer_info']
        self.transducer.is_active = (acqs_params['Equipment']['Transducer.is_active'] == 'True')

        self.protocol.seq_number = int(acqs_params['Protocol']['Sequence number'])
        self.protocol.oper_freq = int(acqs_params['Protocol']['Operating frequency [Hz]'])
        self.protocol.focus = int(acqs_params['Protocol']['Focus [um]'])

        self.protocol.power_value = float(acqs_params['Protocol']['Global power [mW] (NeuroFUS) or Amplitude [%] (IGT)'])
        self.protocol.path_conv_excel = str(acqs_params['Protocol']['Path of Isppa to Global power conversion excel'])

        self.protocol.ramp_mode = int(acqs_params['Protocol']['Ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'])
        self.protocol.ramp_dur = float(acqs_params['Protocol']['Ramp duration [us]'])
        self.protocol.ramp_dur_step = float(acqs_params['Protocol']['Ramp duration step size [us]'])

        self.protocol.pulse_dur = float(acqs_params['Protocol']['Pulse duration [us]'])
        self.protocol.pulse_rep_int = float(acqs_params['Protocol']['Pulse repetition interval [us]'])
        self.protocol.pulse_train_dur = float(acqs_params['Protocol']['Pulse train duration [us]'])

        self.protocol.use_coord_excel = (acqs_params['Grid']['Use coordinate excel as input?'] == 'True')
        self.protocol.path_coord_excel = str(acqs_params['Grid']['Path of coordinate excel'])

        if self.protocol.use_coord_excel:

            array_str = acqs_params['Grid']['Number of slices, rows, columns (z-dir, x-dir, y-dir)']
            strip_split_array = array_str.replace('[', '').replace(']', '').strip().split(',')

            self.protocol.nslices_nrow_ncol = [int(num) for num in strip_split_array]

            self.nsl = self.protocol.nslices_nrow_ncol[0]
            self.nrow = self.protocol.nslices_nrow_ncol[1]
            self.ncol = self.protocol.nslices_nrow_ncol[2]

        else:
            self.protocol.coord_begin = np.array(acqs_params['Grid']['Begin coordinates [mm]'])

            self.protocol.vectSl = np.array(acqs_params['Grid']['Slice vector [mm]'])
            self.protocol.vectRow = np.array(acqs_params['Grid']['Row vector [mm]'])
            self.protocol.vectCol = np.array(acqs_params['Grid']['Column vector [mm]'])

            sl_dir = np.nonzero(self.protocol.vectSl)[0][0]
            row_dir = np.nonzero(self.protocol.vectRow)[0][0]
            col_dir = np.nonzero(self.protocol.vectCol)[0][0]

            direction = '('
            for num_dir in [sl_dir, row_dir, col_dir]:
                if num_dir == 0:
                    add_dir = 'x'
                elif num_dir == 1:
                    add_dir = 'y'
                elif num_dir == 2:
                    add_dir = 'z'
                else:
                    add_dir = 'unknown'
                direction = direction + add_dir + '-dir '

            direction = direction + ')'

            array_str = acqs_params['Grid']['Number of slices, rows, columns ' + direction]
            strip_split_array = array_str.replace('[', '').replace(']', '').strip().split(',')

            self.protocol.nslices_nrow_ncol = [int(num) for num in strip_split_array]

            self.nsl = self.protocol.nslices_nrow_ncol[0]
            self.nrow = self.protocol.nslices_nrow_ncol[1]
            self.ncol = self.protocol.nslices_nrow_ncol[2]

        self.pico_sampling_freq = float(acqs_params['Picoscope']['Sampling frequency [Hz]'])
        self.sampling_period = 1.0/self.pico_sampling_freq

        self.sampling_duration_us = float(acqs_params['Picoscope']['Hydrophone acquisition time [us]'])
        self.sample_count = int(acqs_params['Picoscope']['Amount of samples per acquisition'])


def getRampingAmplitude(ramp_mode, ramp_dur, myStepDurationMs):
    match ramp_mode:
        case 1:  # Linear ramping
            # amount of points where ramping is applied
            nPoints = math.floor(ramp_dur/myStepDurationMs)
            aRamp = np.linspace(0, 1, nPoints)
        case 2:  # Tukey ramping
            # amount of points where ramping is applied
            nPoints = math.floor(ramp_dur/myStepDurationMs)
            alpha = 1
            x = np.linspace(0, alpha/2, nPoints)
            aRamp = np.zeros(nPoints)
            for i in range(nPoints):
                aRamp[i] = 0.5 * (1 + math.cos((2*math.pi/alpha) * (x[i] - alpha/2)))

    return aRamp


def acquire(outfile, protocol, config, inputParam):
    """
    perform the entire acquisition process:
        check file output
        initialize the grid to be scanned
        initialize the generator and prepare the pulse sequence
        initialize the motor system
        prepare acquisition and processing
        scan and acquire the data
    """
    my_acquisition = Acquisition(config)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = inputParam.driving_system
    my_acquisition.transducer = inputParam.transducer

    my_acquisition.check_file(outfile)

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    my_acquisition.logger.info('Grid is initialized')

    try:
        my_acquisition.init_generator(inputParam.perform_all_protocols, inputParam.main_dir)
        my_acquisition.init_pulse_sequence()
        my_acquisition.logger.info('All driving system parameters are set')

        my_acquisition.init_scope(inputParam.sampl_freq_multi)
        my_acquisition.init_aquisition(inputParam.acquisition_time)
        my_acquisition.init_processing()
        my_acquisition.init_processing_parameters()
        # determine the COM port used by the motors using the Device manager
        my_acquisition.init_motor(inputParam.pos_com_port)

        my_acquisition.save_params_ini(inputParam)
        my_acquisition.logger.info('Used parameters have been saved in a file.')

        my_acquisition.scan_grid(inputParam.coord_focus)

    finally:
        my_acquisition.close_all()

    my_acquisition.logger.info('Pipeline for current protocol is finished.')


###########################################################################################
# ######                              TEST FUNCTIONS                               ###### #
###########################################################################################

def simul_acquire(outfile, protocol, config, inputParam):
    """
    simulate the entire acquisition process:
        check file output
        initialize the grid to be scanned
        initialize the pulse sequence
        prepare acquisition and processing
        save the acquisition parameters
    """
    my_acquisition = Acquisition(config)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = inputParam.driving_system
    my_acquisition.transducer = inputParam.transducer

    my_acquisition.check_file(outfile)

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    try:
        my_acquisition.init_generator(inputParam.perform_all_protocols, inputParam.main_dir)
        my_acquisition.init_pulse_sequence()
        my_acquisition.init_scope_params(inputParam.sampl_freq_multi)
        my_acquisition.init_aquisition(inputParam.acquisition_time)
        my_acquisition.init_processing_parameters()
        my_acquisition.save_params_ini(inputParam)
    finally:
        my_acquisition.close_all()


def check_scan(protocol, config, inputParam, scan='Dir'):
    """
    perform a scan of the defined grid to check scanning path
    """
    my_acquisition = Acquisition(config)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = inputParam.driving_system
    my_acquisition.transducer = inputParam.transducer

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    try:
        # determine the COM port used by the motors using the Device manager
        my_acquisition.init_motor(inputParam.pos_com_port)
        duration = my_acquisition.scan_only(inputParam.coord_focus, delay_s=0.0, scan=scan)
        print(f'duration: {duration}: ns: {my_acquisition.nsl},  nr: {my_acquisition.nrow}, nc: {my_acquisition.ncol},')
    finally:
        if my_acquisition.motors.connected:
            my_acquisition.motors.disconnect()


def check_generator(protocol, config, inputParam, repetitions=1, delay_s=1.0):
    """
    initialize the generator and prepare the pulse sequence
    repeat the pulse sequence a number of time given by the repetitions parameter
    a delay iss added between sequences of delay_s
    This is use dtho check the picoscope settings with the chosen generator amplitude
    using the picoscope software
    """
    my_acquisition = Acquisition(config)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = inputParam.driving_system
    my_acquisition.transducer = inputParam.transducer

    my_acquisition.pulse_only(inputParam.performAllProtocols, repetitions=repetitions,
                              delay_s=delay_s,
                              log_dir=inputParam.main_dir)


def check_acquisition(outfile, protocol, config, inputParam):
    """
    perform the entire acquisition process without any motion:
        check file output
        initialize the grid to be scanned
        initialize the generator and prepare the pulse sequence
        prepare acquisition and processing
        acquire the data ncol x nrow number of time
        this is usefull to check acquisition parameters (picoscope) and processing
    """
    my_acquisition = Acquisition(config)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = inputParam.driving_system
    my_acquisition.transducer = inputParam.transducer

    my_acquisition.check_file(outfile)

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    try:
        my_acquisition.init_generator(inputParam.performAllProtocols, inputParam.main_dir)
        my_acquisition.init_pulse_sequence()

        my_acquisition.init_scope(inputParam.sampl_freq_multi)
        my_acquisition.init_aquisition(inputParam.acquisition_time)
        my_acquisition.init_processing()
        my_acquisition.scan_noMotion(inputParam.coord_focus)
    finally:
        my_acquisition.close_all()


def determineCoordDir(dir_num):
    coord_dir = 'unknown'
    if dir_num == 0:
        coord_dir = 'x'
    elif dir_num == 1:
        coord_dir = 'y'
    elif dir_num == 2:
        coord_dir = 'z'

    return coord_dir
