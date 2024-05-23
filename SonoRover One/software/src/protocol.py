# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Margely Cornelissen (Radboud University) and Erik Dumont (Image Guided Therapy)

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
If you use this software in your project, please include the following attribution:
Margely Cornelissen (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided
Therapy, Pessac, France) (2024), Radboud FUS measurement kit, SonoRover One Software (Version 0.8),
https://github.com/MaCuinea/Radboud-FUS-measurement-kit
"""

import logging
import os
import sys
import pandas as pd
import re
import numpy


class ColumnIndices:
    # Object to save column index of excel corresponding to certain parameter
    def __init__(self):
        self.pulse_dur_ind = None
        self.pulse_rep_int_ind = None
        self.pulse_train_dur_ind = None

        self.power_ind = None
        self.power_value_ind = None
        self.isppa_to_gp_excel = None
        self.focus_ind = None
        self.ramp_mode_ind = None
        self.ramp_dur_ind = None
        self.ramp_dur_step = None

        self.excel_or_param = None
        self.coord_excel = None

        self.max_x_plus = None
        self.max_x_min = None
        self.max_y_plus = None
        self.max_y_min = None
        self.max_z_plus = None
        self.max_z_min = None
        
        self.dir_slices = None
        self.dir_rows = None
        self.dir_columns = None
        
        self.step_size_x = None
        self.step_size_y = None
        self.step_size_z = None

def setIndices(data):
    indices = ColumnIndices()
    indices.pulse_dur_ind = data.columns.get_loc('Pulse duration [us]')
    indices.pulse_rep_int_ind = data.columns.get_loc('Pulse Repetition Interval [ms]')
    indices.pulse_train_dur_ind = data.columns.get_loc('Pulse Train Duration [ms]')
    indices.power_ind = data.columns.get_loc('Isppa [W/cm2], Global power [mW] or Amplitude [%]')
    indices.power_value_ind = data.columns.get_loc('Corresponding value')
    indices.isppa_to_gp_excel = data.columns.get_loc('Path and filename of Isppa to Global power conversion excel')
    indices.focus_ind = data.columns.get_loc('Focus [mm]')
    indices.ramp_mode_ind = data.columns.get_loc('Modulation')
    indices.ramp_dur_ind = data.columns.get_loc('Ramp duration [us]')
    indices.ramp_dur_step_ind = data.columns.get_loc('Ramp duration step size [us]')

    indices.excel_or_param = data.columns.get_loc('Coordinates based on excel file or parameters on the right?')
    indices.coord_excel = data.columns.get_loc('Path and filename of coordinate excel')

    indices.max_x_plus = data.columns.get_loc('max. + x [mm] w.r.t. relative zero')
    indices.max_x_min = data.columns.get_loc('max. - x [mm] w.r.t. relative zero')
    indices.max_y_plus = data.columns.get_loc('max. + y [mm] w.r.t. relative zero')
    indices.max_y_min = data.columns.get_loc('max. - y [mm] w.r.t. relative zero')
    indices.max_z_plus = data.columns.get_loc('max. + z [mm] w.r.t. relative zero')
    indices.max_z_min = data.columns.get_loc('max. - z [mm] w.r.t. relative zero')
    
    indices.dir_slices = data.columns.get_loc('direction_slices')
    indices.dir_rows = data.columns.get_loc('direction_rows')
    indices.dir_columns = data.columns.get_loc('direction_columns')
    
    indices.step_size_x = data.columns.get_loc('step_size_x [mm]')
    indices.step_size_y = data.columns.get_loc('step_size_y [mm]')
    indices.step_size_z = data.columns.get_loc('step_size_z [mm]')
    
    return indices

class Protocol:
    
    def __init__(self, logger_name):
        '''
        '''
        self.logger = logging.getLogger(logger_name)

        self.seq_number = 0                    # sequence number of protocol in excel file
        self.oper_freq = 250000                # operating frequency in Hz
        self.pulse_dur = 50                    # pulse duration in micro seconds
        self.pulse_rep_int = 1000              # pulse repetition interval in micro seconds
        self.pulse_train_dur = 1000            # pulse train duration in micro seconds

        self.power_value = 0                   # global power in mili watt (NeuroFUS) or amplitude in percentage (IGT) linearly related to maximum pressure in free water
        self.path_conv_excel = None            # path of Isppa to Global power conversion excel
        self.focus = 40000                     # focus in micro meter
        self.ramp_mode = 0                     # Ramp modi: 0 = no ramping, 1 = linear, 2 = Tukey, 3 = Logarithmic, 4 = Exponential, 5 = Gaussian
        self.ramp_dur = 0                      # Ramp duration in micro seconds
        self.ramp_dur_step = 0                 # Ramp duration step size in micro seconds

        self.use_coord_excel = False           # boolean if coordinate excel file is used as input of grid
        self.path_coord_excel = None           # path of coordinate excel file

        self.coord_begin = [0, 0, 0]           # [x, y, z] coordinates of starting point in millimeters
        self.nslices_nrow_ncol = [0, 0, 0]     # [number of slices, number of rows, number of columns]

        self.vectSl = None                     # vector to define stepsize in step-direction in millimeters
        self.vectRow = None                    # vector to define stepsize in row-direction in millimeters
        self.vectCol = None                    # vector to define stepsize in column-direction in millimeters

    def info(self):
        '''
        '''

        info = ""
        info = info + f"Sequence number: {self.seq_number} \n "
        info = info + f"Operating frequency [Hz]: {self.oper_freq} \n "

        info = info + f"Global power [mW] (NeuroFUS) or Amplitude [%] (IGT): {self.power_value} \n "
        info = info + f"Path of Isppa to Global power conversion excel: {self.path_conv_excel} \n "
        info = info + f"Focus [um]: {self.focus} \n "

        info = info + f"Ramp mode: {self.ramp_mode} \n "
        info = info + f"Ramp duration [us]: {self.ramp_dur} \n "
        info = info + f"Ramp duration step size [us]: {self.ramp_dur_step} \n "

        info = info + f"Pulse duration [us]: {self.pulse_dur} \n "
        info = info + f"Pulse repetition interval [us]: {self.pulse_rep_int} \n "
        info = info + f"Pulse train duration [us]: {self.pulse_train_dur} \n "

        info = info + f"Use coordinate excel as input?: {self.use_coord_excel} \n "
        info = info + f"Path of coordinate excel: {self.path_coord_excel} \n "

        info = info + f"Begin coordinates [mm]: {self.coord_begin} \n "
        info = info + f"Number of slices, rows, columns: {self.nslices_nrow_ncol} \n "
        info = info + f"Slice vector [mm]: {self.vectSl} \n "
        info = info + f"Row vector [mm]: {self.vectRow} \n "
        info = info + f"Column vector [mm]: {self.vectCol} \n "
        
        return info

    def setPulseDur(self, pulse_dur):
        '''
        '''
        self.pulse_dur = pulse_dur

    def setPulseRepInt(self, pulse_rep_int):
        '''
        '''
        # convert pulse repetition interval in milliseconds to micro seconds
        self.pulse_rep_int = pulse_rep_int * 1e3
    
    def setPulseTrainDur(self, pulse_train_dur):
        '''
        '''
        # convert pulse train duration in seconds to micro seconds
        self.pulse_train_dur = pulse_train_dur * 1e3

    def setGlobalPower(self, isppa):
        '''
        '''
        # convert Isppa to corresponding Global power
        excel_path = os.path.join(self.path_conv_excel)
        if os.path.exists(excel_path):
            power_table = pd.read_excel(excel_path, engine='openpyxl')

            inten = power_table['intensity']
            index = min(range(len(inten)), key=lambda i: abs(inten[i]-isppa))
            if index < 0 or index == None:
                self.logger.error(f"Error: Power value not found for Isppa = {isppa}")
                sys.exit()
             
            self.power_value = power_table['globalPower'][index] # determine required global power based on Isppa
        else:
            self.logger.error(f"The following file doesn't exist: {excel_path}")
    
    def setFocus(self, focus):
        '''
        '''
        # convert focus in mm to micro meter
        self.focus = focus * 1e3
    
    def setRamping(self, ramp_mode, ramp_dur, ramp_dur_step):
        '''
        '''
        match ramp_mode:
                case 'Square':
                    self.ramp_mode = 0
                case 'Linear':
                    self.ramp_mode = 1
                case 'Tukey':
                    self.ramp_mode = 2

        if self.ramp_mode != 0:
            self.ramp_dur = ramp_dur
            self.ramp_dur_step = ramp_dur_step

    def setAllDirVectors(self, dir_slices, dir_rows, dir_columns, step_sizes):
        '''
        '''
        self.vectSl = setDirVector(dir_slices, step_sizes)
        self.vectRow = setDirVector(dir_rows, step_sizes)
        self.vectCol = setDirVector(dir_columns, step_sizes)

    def calculateNVector(self, dir_slices, dir_rows, dir_columns, max_values, step_sizes):
        '''
        '''
        nrow = calculateN(dir_columns, max_values, step_sizes)
        ncol = calculateN(dir_rows, max_values, step_sizes)
        nslices =calculateN(dir_slices, max_values, step_sizes)
        
        self.nslices_nrow_ncol = [nslices, nrow, ncol] 
  
    def setBeginCoordVector(self, coord_focus, directions, max_values):
        '''
        '''
        for direction in directions:
            # take opposite direction as starting positions
            match direction:
                case '+x':
                    self.coord_begin[0] = float("{:.3f}".format(coord_focus[0] - max_values[1])) # coord_focus_x - max_x_min = start_pos_x to measure in +x dir.
                case '-x':
                    self.coord_begin[0] = float("{:.3f}".format(coord_focus[0] + max_values[0])) # coord_focus_x + max_x_plus = start_pos_x to measure in -x dir.
                case '+y':
                    self.coord_begin[1] = float("{:.3f}".format(coord_focus[1] - max_values[3])) # coord_focus_y - max_y_min = start_pos_y to measure in +y dir.
                case '-y':
                    self.coord_begin[1] = float("{:.3f}".format(coord_focus[1] + max_values[2])) # coord_focus_y + max_y_plus = start_pos_y to measure in -y dir.
                case '+z':
                    self.coord_begin[2] = float("{:.3f}".format(coord_focus[2] - max_values[5])) # coord_focus_z - max_z_min = start_pos_z to measure in +z dir.
                case '-z':
                    self.coord_begin[2] = float("{:.3f}".format(coord_focus[2] + max_values[4])) # coord_focus_z + max_z_plus = start_pos_z to measure in -z dir.

def setDirVector(direction, step_sizes):
    '''
    '''
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

def calculateN(direction, max_values, step_sizes):
    '''
    '''
    # calculate number of rows/colums/slices in a specific direction
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
    
def newProtocol(inputParam, indices, seq, seq_number, logger_name):
    '''
    '''
    # create object to save parameters in
    prot = Protocol(logger_name)
    prot.seq_number = seq_number

    # get values from sequence and save in object
    prot.oper_freq = int(inputParam.oper_freq)

    pulse_dur = abs(float(seq[indices.pulse_dur_ind]))
    prot.setPulseDur(pulse_dur)

    pulse_rep_int = abs(float(seq[indices.pulse_rep_int_ind]))
    prot.setPulseRepInt(pulse_rep_int)

    pulse_train_dur = abs(float(seq[indices.pulse_train_dur_ind]))
    prot.setPulseTrainDur(pulse_train_dur)

    power_param = str(seq[indices.power_ind])

    match power_param:
        case 'Amplitude [%] (fill in \'Corresponding value\')':
            ampl = abs(int(seq[indices.power_value_ind]))
            prot.power_value = ampl
			
        case 'Isppa [W/cm2] (fill in \'Corresponding value\' and \'Excel path and filename of Isppa to Global power conversion table\')':
            prot.path_conv_excel = str(seq[indices.isppa_to_gp_excel])

            isppa = abs(float(seq[indices.power_value_ind]))
            prot.setGlobalPower(isppa)

        case 'Global power [mW] (fill in \'Corresponding value\')':
            global_power = abs(float(seq[indices.power_value_ind]))
            prot.power_value = global_power

    focus = abs(float(seq[indices.focus_ind]))
    prot.setFocus(focus)

    ramp_mode = str(seq[indices.ramp_mode_ind])
    ramp_dur = abs(float(seq[indices.ramp_dur_ind]))
    ramp_dur_step = abs(float(seq[indices.ramp_dur_step_ind]))
    prot.setRamping(ramp_mode, ramp_dur, ramp_dur_step)

    excel_or_param = str(seq[indices.excel_or_param])
    match excel_or_param:
        case 'Coordinate excel file':
            prot.use_coord_excel = True
            prot.path_coord_excel = str(seq[indices.coord_excel])

        case 'Parameters on the right':
            prot.use_coord_excel = False

            max_x_plus = abs(float(seq[indices.max_x_plus]))
            max_x_min = abs(float(seq[indices.max_x_min]))
            max_y_plus = abs(float(seq[indices.max_y_plus]))
            max_y_min = abs(float(seq[indices.max_y_min]))
            max_z_plus = abs(float(seq[indices.max_z_plus]))
            max_z_min = abs(float(seq[indices.max_z_min]))
                
            dir_slices = str(seq[indices.dir_slices])
            dir_rows = str(seq[indices.dir_rows])
            dir_columns = str(seq[indices.dir_columns])
                
            step_size_x = abs(float(seq[indices.step_size_x]))
            step_size_y = abs(float(seq[indices.step_size_y]))
            step_size_z = abs(float(seq[indices.step_size_z]))

            # set grid info
            prot.setBeginCoordVector(inputParam.coord_focus, [dir_slices, dir_rows, dir_columns], [max_x_plus, max_x_min, max_y_plus, max_y_min, max_z_plus, max_z_min])
            prot.setAllDirVectors(dir_slices, dir_rows, dir_columns, [step_size_x, step_size_y, step_size_z])
            prot.calculateNVector(dir_slices, dir_rows, dir_columns, [max_x_plus, max_x_min, max_y_plus, max_y_min, max_z_plus, max_z_min], [step_size_x, step_size_y, step_size_z])

    return prot