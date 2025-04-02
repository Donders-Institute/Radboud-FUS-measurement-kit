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

import configparser

CONFIG_FOLDER = 'config'  # should be in the same directory as code
CONFIG_FILE = 'characterization_config.ini'

config = configparser.ConfigParser(interpolation=None)

config['General'] = {}
config['General']['Maximum number of output filename'] = str(1000)

config['Logging'] = {}
config['Logging']['Logger name'] = 'SonoRover_One'
config['Logging']['Timestamp format'] = '%Y-%m-%d_%H-%M-%S'
config['Logging']['Log level console'] = 'WARNING'
config['Logging']['Log level file'] = 'DEBUG'
config['Logging']['Initial part of log filename'] = 'log_'

config['Versions'] = {}
config['Versions']['SonoRover One software'] = '1.2.0'

config['Characterization'] = {}
config['Characterization']['Path of input parameters cache'] = ('config//' +
                                                                'characterization_input_cache.ini')
config['Characterization']['Cache date format'] = "%Y/%m/%d"

config['Characterization']['Temporary output path'] = 'C:\\Temp\\General output folder'
config['Characterization']['Temporary logging path'] = config['Characterization']['Temporary output path']  + '\\logs'
config['Characterization']['Default protocol directory'] = ('//ru.nl//WrkGrp//FUS_Hub//' +
                                                            'Hydrophone measurements' +
                                                            '//Measurements')
config['Characterization']['Default output directory'] = ('//ru.nl//WrkGrp//FUS_Hub//' +
                                                          'Hydrophone measurements//Measurements' +
                                                          '//2024//General output folder')

config['Characterization']['Disconnection message'] = ('Ensure the following: \n - PicoScope ' +
                                                       'software is not connected to the ' +
                                                       'PicoScope in use. \n - Universal Gcode ' +
                                                       'Sender is not connected to the ' +
                                                       'positioning system.')

config['Characterization']['Continue acquisition message'] = ('Continue acquisition with the ' +
                                                              'following sequence: ')

ACD_ZERO = '0 - no adjustment'
ACD_PLUS = '+1 - axial measurement moving from transducer'
ACD_MIN = '-1 - axial measurement moving towards transducer'
config['Characterization']['ACD adjustment.zero'] = ACD_ZERO
config['Characterization']['ACD adjustment.plus'] = ACD_PLUS
config['Characterization']['ACD adjustment.min'] = ACD_MIN
config['Characterization']['ACD adjustment'] = '\n'.join([ACD_ZERO, ACD_PLUS, 
                                                          ACD_MIN])

PROT_EXCEL = 'Select protocol excel file...'
PROT_AC_ALIGN = 'Acoustical alignment'
config['Characterization']['Protocols'] = '\n'.join([PROT_EXCEL, PROT_AC_ALIGN])
config['Characterization']['Protocol.excel'] = PROT_EXCEL
config['Characterization']['Protocol.ac_align'] = PROT_AC_ALIGN

config['Characterization']['output_name_suffix'] = 'output_data'

config['Characterization']['Ac_align.output_name_suffix'] = 'output_data'
config['Characterization']['Ac_align.axis_suffix'] = 'acoustical_axis'
config['Characterization']['Ac_align.additional_x_lim'] = str(15)  # [mm]

config['Characterization']['protocol_dialog.n_ac_align_rows'] = str(14)
config['Characterization']['protocol_dialog.stay_topmost_in_ms'] = str(5000)

config['Characterization']['input_dialog.stay_topmost_in_ms'] = str(5000)

config['Characterization']['acd_dialog.stay_topmost_in_ms'] = str(5000)

MEAS_NUM = 'Measurement number'
CLUSTER_NUM = 'Cluster number'
INDICES_NUM = 'Indices number'
X_COORD = 'X-coordinate [mm]'
Y_COORD = 'Y-coordinate [mm]'
Z_COORD = 'Z-coordinate [mm]'
ROW_COL = 'Row number'
COL_COL = 'Column number'
SL_COL = 'Slice number'
ABS_X_COORD = 'Absolute X-coordinate [mm]'
ABS_Y_COORD = 'Absolute Y-coordinate [mm]'
ABS_Z_COORD = 'Absolute Z-coordinate [mm]'

config['Characterization']['coord_excel_columns.meas_num'] = MEAS_NUM
config['Characterization']['coord_excel_columns.clus_num'] = CLUSTER_NUM
config['Characterization']['coord_excel_columns.ind_num'] = INDICES_NUM
config['Characterization']['coord_excel_columns.x_coord'] = X_COORD
config['Characterization']['coord_excel_columns.y_coord'] = Y_COORD
config['Characterization']['coord_excel_columns.z_coord'] = Z_COORD
config['Characterization']['coord_excel_columns.row'] = ROW_COL
config['Characterization']['coord_excel_columns.col'] = COL_COL
config['Characterization']['coord_excel_columns.sl'] = SL_COL
config['Characterization']['coord_excel_columns.abs_x_coord'] = ABS_X_COORD
config['Characterization']['coord_excel_columns.abs_y_coord'] = ABS_Y_COORD
config['Characterization']['coord_excel_columns.abs_z_coord'] = ABS_Z_COORD


config['Characterization']['coord_excel_columns'] = '\n'.join([MEAS_NUM,
                                                               CLUSTER_NUM,
                                                               INDICES_NUM,
                                                               X_COORD,
                                                               Y_COORD,
                                                               Z_COORD,
                                                               ROW_COL,
                                                               COL_COL,
                                                               SL_COL,
                                                               ABS_X_COORD,
                                                               ABS_Y_COORD,
                                                               ABS_Z_COORD])

config['Characterization']['prot_excel_columns.seq_num'] = 'Sequence number'
config['Characterization']['prot_excel_columns.tag'] = 'Tag'
config['Characterization']['prot_excel_columns.dephasing'] = "(De)phase array [degree] (None = no (de)phasing) ONLY FOR IGT DS"
config['Characterization']['prot_excel_columns.pulse_dur'] = 'Pulse duration [us]'
config['Characterization']['prot_excel_columns.pulse_rep_int'] = 'Pulse Repetition Interval [ms]'

config['Characterization']['prot_excel_columns.power'] = 'SC - Global power [mW] or IGT - Max. pressure in free water [Mpa], Voltage [V] or Amplitude [%]'
config['Characterization']['prot_excel_columns.power_value'] = 'Corresponding value'
config['Characterization']['prot_excel_columns.focus_def'] = 'Focus definition'
config['Characterization']['prot_excel_columns.focus_value'] = 'Focus value [mm]'
config['Characterization']['prot_excel_columns.ramp_mode'] = 'Modulation'
config['Characterization']['prot_excel_columns.ramp_dur'] = 'Ramp duration [us]'

config['Characterization']['prot_excel_columns.excel_or_param'] = 'Coordinates based on excel file or parameters on the right?'
config['Characterization']['prot_excel_columns.coord_excel'] = 'Path and filename of coordinate excel'

config['Characterization']['prot_excel_columns.max_x_plus'] = 'max. + x [mm] w.r.t. relative zero'
config['Characterization']['prot_excel_columns.max_x_min'] = 'max. - x [mm] w.r.t. relative zero'
config['Characterization']['prot_excel_columns.max_y_plus'] = 'max. + y [mm] w.r.t. relative zero'
config['Characterization']['prot_excel_columns.max_y_min'] = 'max. - y [mm] w.r.t. relative zero'
config['Characterization']['prot_excel_columns.max_z_plus'] = 'max. + z [mm] w.r.t. relative zero'
config['Characterization']['prot_excel_columns.max_z_min'] = 'max. - z [mm] w.r.t. relative zero'

config['Characterization']['prot_excel_columns.dir_slices'] = 'direction_slices'
config['Characterization']['prot_excel_columns.dir_rows'] = 'direction_rows'
config['Characterization']['prot_excel_columns.dir_columns'] = 'direction_columns'

config['Characterization']['prot_excel_columns.step_size_x'] = 'step_size_x [mm]'
config['Characterization']['prot_excel_columns.step_size_y'] = 'step_size_y [mm]'
config['Characterization']['prot_excel_columns.step_size_z'] = 'step_size_z [mm]'

config['Characterization']['prot_excel.glob_pow'] = 'SC - Global power [mW] (fill in \'Corresponding value\')'
config['Characterization']['prot_excel.press'] = 'IGT - Max. pressure in free water [MPa] (fill in \'Corresponding value\')'
config['Characterization']['prot_excel.volt'] = 'IGT - Voltage [V] (fill in \'Corresponding value\')'
config['Characterization']['prot_excel.ampl'] = 'IGT - Amplitude [%] (fill in \'Corresponding value\')'

config['Characterization']['prot_excel.coord_excel'] = 'Coordinate excel file'
config['Characterization']['prot_excel.grid_param'] = 'Parameters on the right'

config['Characterization']['default.acq_time_us'] = str(500)
config['Characterization']['default.sampl_freq_multi'] = str(50)
config['Characterization']['default.pos_com_port'] = 'COM3'

config['Characterization']['default.temp'] = ''
config['Characterization']['default.dis_oxy'] = ''

config['Characterization']['default.x_coord_zero'] = str(-63)
config['Characterization']['default.y_coord_zero'] = str(-62.5)
config['Characterization']['default.z_coord_zero'] = str(-154)

config['Characterization']['default.perform_all_seqs'] = str(True)

config['Characterization']['default.distance_from_foc'] = '\n'.join([str(-10), str(10)])
config['Characterization']['default.init_line_len'] = str(40)
config['Characterization']['default.init_line_step'] = str(0.5)
config['Characterization']['default.init_threshold'] = str(0.01)
config['Characterization']['default.reduction_factor'] = str(0.5)
config['Characterization']['default.max_red_iter'] = str(5)
config['Characterization']['default.create_graphs'] = str(True)
config['Characterization']['default.y_lim'] = str(200)
config['Characterization']['default.create_axis_file'] = str(True)
config['Characterization']['default.axis_length'] = str(140)
config['Characterization']['default.axis_stepsize'] = str(0.5)

config['Characterization']['picoscope.reacquire_attempts'] = str(5)
config['Characterization']['picoscope.resolution'] = 'DR_14BIT'
config['Characterization']['picoscope.channel'] = 'A'
config['Characterization']['picoscope.range'] = 'RANGE_500mV'
config['Characterization']['picoscope.coupling'] = 'DC'
config['Characterization']['picoscope.probe_multi'] = 'x1'
config['Characterization']['picoscope.trigger_threshold_v'] = str(0.5)

config['Characterization']['pos_sys.reacquire_attempts'] = str(5)

config['Characterization.Equipment'] = {}

HYDROPHONES = ['HGL 0200 SN2845', 'HGL 0200 SN3030', 'HNR 0500 SN2439']
config['Characterization.Equipment']['Hydrophones'] = '\n'.join(HYDROPHONES)

config['Characterization.Equipment.' + HYDROPHONES[0]] = {}
config['Characterization.Equipment.' + HYDROPHONES[0]]['Name'] = 'Hydrophone ' + HYDROPHONES[0]
config['Characterization.Equipment.' + HYDROPHONES[0]]['Sensitivity (V/Pa) datasheet'] = (
    'config//hydrophones//HGL 0200 SN2845 Calibration datasheet.xlsx')

config['Characterization.Equipment.' + HYDROPHONES[1]] = {}
config['Characterization.Equipment.' + HYDROPHONES[1]]['Name'] = 'Hydrophone ' + HYDROPHONES[1]
config['Characterization.Equipment.' + HYDROPHONES[1]]['Sensitivity (V/Pa) datasheet'] = (
    'config//hydrophones//HGL 0200 SN3030 Calibration datasheet.xlsx')

config['Characterization.Equipment.' + HYDROPHONES[2]] = {}
config['Characterization.Equipment.' + HYDROPHONES[2]]['Name'] = 'Hydrophone ' + HYDROPHONES[2]
config['Characterization.Equipment.' + HYDROPHONES[2]]['Sensitivity (V/Pa) datasheet'] = (
    'config//hydrophones//HNR 0500 SN2439 Calibration datasheet.xlsx')

config['Characterization.Equipment']['Hydrophone datasheet freq. header'] = 'Freq(MHz)'

PICO_SERIALS = ['5442D', '5242D', '5442A', '5244D']
config['Characterization.Equipment']['PicoScopes'] = '\n'.join(PICO_SERIALS)

config['Characterization.Equipment.' + PICO_SERIALS[0]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[0]]['Name'] = ('PicoScope ' + PICO_SERIALS[0] +
                                                                   ' - embedded in ' +
                                                                   'characterization setup')
config['Characterization.Equipment.' + PICO_SERIALS[0]]['Pico.py identification'] = PICO_SERIALS[0]

config['Characterization.Equipment.' + PICO_SERIALS[1]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[1]]['Name'] = ('PicoScope ' + PICO_SERIALS[1])
config['Characterization.Equipment.' + PICO_SERIALS[1]]['Pico.py identification'] = PICO_SERIALS[1]

config['Characterization.Equipment.' + PICO_SERIALS[2]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[2]]['Name'] = ('PicoScope ' + PICO_SERIALS[2] +
                                                                   ' - embedded in IGT driving ' +
                                                                   'system (128 ch.)')
config['Characterization.Equipment.' + PICO_SERIALS[2]]['Pico.py identification'] = PICO_SERIALS[2]

config['Characterization.Equipment.' + PICO_SERIALS[3]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[3]]['Name'] = ('PicoScope ' + PICO_SERIALS[3] +
                                                                   ' - test setup')
config['Characterization.Equipment.' + PICO_SERIALS[3]]['Pico.py identification'] = PICO_SERIALS[3]

with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)
