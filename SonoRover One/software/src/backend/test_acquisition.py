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

# Own packages
import acquisition as acq
from scan_iter import Scan_Iter


class TestAcquisition(acq.Acquisition):
    def init_scan(self, scan='Dir'):
        """
        init the scan in either direct mode: acquire all lines starting from the same position
        Dir: (0,0), (0,1), (0,2), (0,3), (1,0), (1,1), (1,2), (1,3)
        Alt: (0,0), (0,1), (0,2), (0,3), (1,3), (1,3), (1,1), (1,0)
        """
        self.logger.debug(f'scan: {scan}')
        self.grid = Scan_Iter(self.nsl,self.nrow,self.ncol,scan=scan)

    def init_scope_params(self, sampl_freq_multi):
        """
        Initialize picoscope parameters: sampling frequency
        """
        self.sampling_freq = sampl_freq_multi*self.protocol.oper_freq
        self.pico_sampling_freq = self.sampling_freq
        self.sampling_period = 1.0/self.pico_sampling_freq

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
        my_acquisition.init_pulse_sequence(protocol.is_sham)
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
                              log_dir=inputParam.main_dir, is_sham=protocol.is_sham)


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
        my_acquisition.init_pulse_sequence(protocol.is_sham)

        my_acquisition.init_scope(inputParam.sampl_freq_multi)
        my_acquisition.init_aquisition(inputParam.acquisition_time)
        my_acquisition.init_processing()
        my_acquisition.scan_noMotion(inputParam.coord_focus)
    finally:
        my_acquisition.close_all()