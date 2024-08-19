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
import time

# Miscellaneous packages
import numpy as np

# Own packages
import fus_driving_systems as fds

import backend.acquisition as acq
from config.logging_config import logger
from backend.scan_iter import Scan_Iter

from backend.motor_GRBL import MotorsXYZ
from backend import pico

class TestAcquisition(acq.Acquisition):
    
    def __init__(self, input_param, init_motor, init_ds, init_pico):
        super().__init__(input_param, init_equip=False)
        
        # # Global acquisition parameters
        # Initialize equipment
        self.equipment = {
            "ds": None,
            "scope": None,
            "motors": None
            }
        
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
        
        if init_motor:
            # Connect with positioning system
            self.equipment["motors"] = MotorsXYZ()
            self._init_motor(self.input_param.pos_com_port)
        
        if init_ds:
            # Sync fus_driving_systems logging
            fds.config.logging_config.sync_logger(logger)
            
            # Connect with driving system
            self._init_ds()
            
        if init_pico:
            # Connect with PicoScope
            self.equipment["scope"] = pico.getScope(self.input_param.picoscope.pico_py_ident)
            self._init_scope(input_param.sampl_freq_multi, input_param.acquisition_time)
            
            # Initialize ACD processing parameters
            self.proces_param = self._init_processing(endus=input_param.acquisition_time)
    
    def init_scan(self, scan='Dir'):
        """
        init the scan in either direct mode: acquire all lines starting from the same position
        Dir: (0,0), (0,1), (0,2), (0,3), (1,0), (1,1), (1,2), (1,3)
        Alt: (0,0), (0,1), (0,2), (0,3), (1,3), (1,3), (1,1), (1,0)
        """
        logger.debug(f'scan: {scan}')
        self.grid = Scan_Iter(self.grid_param["nsl"], self.grid_param["nrow"], self.grid_param["ncol"], scan=scan)

    def init_scope_params(self, sampl_freq_multi):
        """
        Initialize picoscope parameters: sampling frequency
        """
        self.sampling_freq = sampl_freq_multi*self.protocol.oper_freq
        self.pico_sampling_freq = self.sampling_freq
        self.sampling_period = 1.0/self.pico_sampling_freq

    def scan_only(self, coord_zero, delay_s=0.0, scan='Dir'):
        """
        scan the predefined grid without any acquisition to verify grid positions
        """
        logger.debug(f'scan: {scan}')
        self.init_scan(scan=scan)
        t0 = time.time()

        counter = 0
        for s, r, c in self.grid:
            if self.sequence.use_coord_excel:
                destXYZ = [self.grid_param["coord_excel_data"].loc[counter, "X-coordinate [mm]"] + coord_zero[0],
                           self.grid_param["coord_excel_data"].loc[counter, "Y-coordinate [mm]"] + coord_zero[1],
                           self.grid_param["coord_excel_data"].loc[counter, "Z-coordinate [mm]"] + coord_zero[2]]
            else:
                destXYZ = self.starting_pos + s*self.vectSl + r*self.vectCol + c*self.vectRow

            logger.info(f'src: [{s}, {r}, {c}], destXYZ: {destXYZ[0]:.3f}, {destXYZ[1]:.3f}, {destXYZ[2]:.3f}')
            self.equipment["motors"].move(list(destXYZ), relative=False)
            counter = counter + 1

        # time.sleep(delay_s)
        t1 = time.time()
        delta_t = t1-t0
        print(f'duration: {delta_t}')
        return delta_t

    def pulse_only(self, performAllProtocols, repetitions=1, delay_s=1.0, log_dir='', is_sham = False):
        """
        execute the pulse sequence without having the pico connected and without motion
        use this with the picoscope software to acquire data with identical generator settings
        useful for setting up the picoscope parameters
        """
        try:
            self.init_generator(performAllProtocols, log_dir)
            self.init_pulse_sequence(is_sham)
            for i in range(repetitions):
                self.ds.execute_sequence()
                time.sleep(delay_s)
        finally:
            self.gen.close()

    def scan_noMotion(self, coord_zero):
        """
        scan without moving the motors (mostly for debugging)
        """
        self.cplx_data = np.zeros((2, self.grid_param["nsl"], self.grid_param["nrow"], self.grid_param["ncol"]), dtype='float32')

        counter = 0
        for i in range(self.grid_param["nsl"]):
            for j in range(self.grid_param["nrow"]):
                for k in range(self.grid_param["ncol"]):

                    if self.protocol.use_coord_excel:
                        measur_nr = self.grid_param["coord_excel_data"].loc[counter, "Measurement number"]
                        cluster_nr = self.grid_param["coord_excel_data"].loc[counter, "Cluster number"]
                        indices_nr = self.grid_param["coord_excel_data"].loc[counter, "Indices number"]
                        relatXYZ = [self.grid_param["coord_excel_data"].loc[counter, "X-coordinate [mm]"],
                                    self.grid_param["coord_excel_data"].loc[counter, "Y-coordinate [mm]"],
                                    self.grid_param["coord_excel_data"].loc[counter, "Z-coordinate [mm]"]]
                        destXYZ = [relatXYZ[0] + coord_zero[0], relatXYZ[1] + coord_zero[1],
                                   relatXYZ[2] + coord_zero[2]]
                        row_nr = self.grid_param["coord_excel_data"].loc[counter, "Row number"]
                        col_nr = self.grid_param["coord_excel_data"].loc[counter, "Column number"]
                        sl_nr = self.grid_param["coord_excel_data"].loc[counter, "Slice number"]

                    else:
                        measur_nr = counter + 1
                        cluster_nr = 1
                        indices_nr = measur_nr
                        destXYZ = (self.starting_pos + i*self.vectSl + j*self.vectCol
                                   + k*self.vectRow)
                        relatXYZ = [destXYZ[0] - coord_zero[0], destXYZ[1] - coord_zero[1],
                                    destXYZ[2] - coord_zero[2]]
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
            
    def check_scan(self, sequence, scan='Dir'):
        """
        perform a scan of the defined grid to check scanning path
        """
        
        # Save protocol, config, used driving system and used transducer
        self.sequence = sequence

        if sequence.use_coord_excel:
            self._init_grid_excel()
        else:
            self._init_grid()

        logger.info('Grid is initialized')

        duration = self.scan_only(self.input_param.coord_zero, delay_s=0.0, scan=scan)
        print(f'duration: {duration}: ns: {self.grid_param["nsl"]},  nr: {self.grid_param["nrow"]}, ' +
              f'nc: {self.grid_param["ncol"]},')
                
    def check_scan_ds_combo(self, sequence, scan='Dir'):
        """
        perform a scan of the defined grid to check scanning path
        """
        
        # Save protocol, config, used driving system and used transducer
        self.sequence = sequence

        if sequence.use_coord_excel:
            self._init_grid_excel()
        else:
            self._init_grid()

        logger.info('Grid is initialized')

        logger.debug(f'scan: {scan}')
        self.init_scan(scan=scan)
        t0 = time.time()

        counter = 0
        for s, r, c in self.grid:
            if self.sequence.use_coord_excel:
                destXYZ = [self.grid_param["coord_excel_data"].loc[counter, "X-coordinate [mm]"] + self.input_param.coord_zero[0],
                           self.grid_param["coord_excel_data"].loc[counter, "Y-coordinate [mm]"] + self.input_param.coord_zero[1],
                           self.grid_param["coord_excel_data"].loc[counter, "Z-coordinate [mm]"] + self.input_param.coord_zero[2]]
            else:
                destXYZ = self.starting_pos + s*self.vectSl + r*self.vectCol + c*self.vectRow

            logger.info(f'src: [{s}, {r}, {c}], destXYZ: {destXYZ[0]:.3f}, {destXYZ[1]:.3f}, {destXYZ[2]:.3f}')
            self.equipment["motors"].move(list(destXYZ), relative=False)
            
            # Send sequence to driving system
            self.equipment["ds"].send_sequence(self.sequence)
            logger.info('All driving system parameters are set')
            
            # Execute pulse sequence
            self.equipment["ds"].execute_sequence()
            
            counter = counter + 1

        # time.sleep(delay_s)
        t1 = time.time()
        delta_t = t1-t0
        print(f'duration: {delta_t}') 


###########################################################################################
# ######                              TEST FUNCTIONS                               ###### #
###########################################################################################

def simul_acquire(outfile, protocol, input_param):
    """
    simulate the entire acquisition process:
        check file output
        initialize the grid to be scanned
        initialize the pulse sequence
        prepare acquisition and processing
        save the acquisition parameters
    """
    my_acquisition = TestAcquisition(input_param)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = input_param.driving_system
    my_acquisition.transducer = input_param.transducer

    my_acquisition.check_file(outfile)

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    try:
        my_acquisition.init_generator(input_param.perform_all_protocols, input_param.main_dir)
        my_acquisition.init_pulse_sequence(protocol.is_sham)
        my_acquisition.init_scope_params(input_param.sampl_freq_multi)
        my_acquisition.init_aquisition(input_param.acquisition_time)
        my_acquisition.init_processing_parameters()
        my_acquisition.save_params_ini(input_param)
    finally:
        my_acquisition.close_all()





def check_generator(protocol, input_param, repetitions=1, delay_s=1.0):
    """
    initialize the generator and prepare the pulse sequence
    repeat the pulse sequence a number of time given by the repetitions parameter
    a delay iss added between sequences of delay_s
    This is use dtho check the picoscope settings with the chosen generator amplitude
    using the picoscope software
    """
    my_acquisition = TestAcquisition(input_param)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = input_param.driving_system
    my_acquisition.transducer = input_param.transducer

    my_acquisition.pulse_only(input_param.performAllProtocols, repetitions=repetitions,
                              delay_s=delay_s,
                              log_dir=input_param.main_dir, is_sham=protocol.is_sham)


def check_acquisition(outfile, protocol, input_param):
    """
    perform the entire acquisition process without any motion:
        check file output
        initialize the grid to be scanned
        initialize the generator and prepare the pulse sequence
        prepare acquisition and processing
        acquire the data ncol x nrow number of time
        this is usefull to check acquisition parameters (picoscope) and processing
    """
    my_acquisition = TestAcquisition(input_param)

    # Save protocol, config, used driving system and used transducer
    my_acquisition.protocol = protocol
    my_acquisition.driving_system = input_param.driving_system
    my_acquisition.transducer = input_param.transducer

    my_acquisition.check_file(outfile)

    if protocol.use_coord_excel:
        my_acquisition.init_grid_excel()
    else:
        my_acquisition.init_grid()

    try:
        my_acquisition.init_generator(input_param.performAllProtocols, input_param.main_dir)
        my_acquisition.init_pulse_sequence(protocol.is_sham)

        my_acquisition.init_scope(input_param.sampl_freq_multi)
        my_acquisition.init_aquisition(input_param.acquisition_time)
        my_acquisition.init_processing()
        my_acquisition.scan_noMotion(input_param.coord_zero)
    finally:
        my_acquisition.close_all()
