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

        self.protocol.seq_number = int(acqs_params['Sequence']['Sequence number'])
        self.protocol.oper_freq = int(acqs_params['Sequence']['Operating frequency [Hz]'])
        self.protocol.focus = int(acqs_params['Sequence']['Focus [um]'])

        self.protocol.power_value = float(acqs_params['Sequence']['Global power [mW] (NeuroFUS) or Amplitude [%] (IGT)'])
        self.protocol.path_conv_excel = str(acqs_params['Sequence']['Path of Isppa to Global power conversion excel'])

        self.protocol.ramp_mode = int(acqs_params['Sequence']['Ramp mode (0 - rectangular, 1 - linear, 2 - tukey)'])
        self.protocol.ramp_dur = float(acqs_params['Sequence']['Ramp duration [us]'])
        self.protocol.ramp_dur_step = float(acqs_params['Sequence']['Ramp duration step size [us]'])

        self.protocol.pulse_dur = float(acqs_params['Sequence']['Pulse duration [us]'])
        self.protocol.pulse_rep_int = float(acqs_params['Sequence']['Pulse repetition interval [us]'])
        self.protocol.pulse_train_dur = float(acqs_params['Sequence']['Pulse train duration [us]'])

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

    def init_processing_parameters(self, begus=0.0, endus=0.0, adjust=0):
        self.adjust=adjust
        self.begus=begus
        self.begn = int(begus*1e-6*self.pico_sampling_freq) # begining of the processing window
        self.endn = int(endus*1e-6*self.pico_sampling_freq) # end of the processing window
        self.npoints = self.endn - self.begn
        self.logger.debug(f'begus: {begus}, endus: {endus}, begn: {self.begn}, endn: {self.endn}')