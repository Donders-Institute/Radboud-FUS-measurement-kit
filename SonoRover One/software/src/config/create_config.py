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

import configparser

CONFIG_FOLDER = 'config'  # should be in the same directory as code
CONFIG_FILE = 'characterization_config.ini'

config = configparser.ConfigParser(interpolation=None)

config['General'] = {}
config['General']['Logger name'] = 'characterization'
config['General']['Maximum number of output filename'] = str(1000)

config['Versions'] = {}
config['Versions']['SonoRover One software'] = '1.0'

config['Characterization'] = {}
config['Characterization']['Path of input parameters cache'] = ('config//' +
                                                                'characterization_input_cache.ini')

config['Characterization']['Temporary output path'] = 'C:\\Temp\\General output folder'
config['Characterization']['Default protocol directory'] = ('//ru.nl//WrkGrp//FUS_Hub//' +
                                                            'Hydrophone measurements' +
                                                            '//Measurements//2024')
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

ACD_ADJUST = ['0 - no adjustment', '+1 - axial measurement moving from transducer',
              '-1 - axial measurement moving towards transducer']
config['Characterization']['ACD adjustment'] = ', '.join(ACD_ADJUST)

config['Characterization.Equipment'] = {}

HYDROPHONES = ['HGL 0200 SN2845', 'HNR 0500 SN2439']
config['Characterization.Equipment']['Hydrophones'] = ', '.join(HYDROPHONES)

config['Characterization.Equipment.' + HYDROPHONES[0]] = {}
config['Characterization.Equipment.' + HYDROPHONES[0]]['Name'] = 'Hydrophone ' + HYDROPHONES[0]
config['Characterization.Equipment.' + HYDROPHONES[0]]['Sensitivity (V/Pa) datasheet'] = (
    'config//hydrophones//HGL 0200 SN2845 Calibration datasheet.xlsx')

config['Characterization.Equipment.' + HYDROPHONES[1]] = {}
config['Characterization.Equipment.' + HYDROPHONES[1]]['Name'] = 'Hydrophone ' + HYDROPHONES[1]
config['Characterization.Equipment.' + HYDROPHONES[1]]['Sensitivity (V/Pa) datasheet'] = (
    'config//hydrophones//HNR 0500 SN2439 Calibration datasheet.xlsx')

config['Characterization.Equipment']['Hydrophone datasheet freq. header'] = 'Freq(MHz)'

PICO_SERIALS = ['5442D', '5242D', '5244D']
config['Characterization.Equipment']['PicoScopes'] = ', '.join(PICO_SERIALS)

config['Characterization.Equipment.' + PICO_SERIALS[0]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[0]]['Name'] = ('PicoScope ' + PICO_SERIALS[0] +
                                                                   ' - embedded in IGT driving ' +
                                                                   'system (128 ch.)')
config['Characterization.Equipment.' + PICO_SERIALS[0]]['Pico.py identification'] = PICO_SERIALS[0]

config['Characterization.Equipment.' + PICO_SERIALS[1]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[1]]['Name'] = ('PicoScope ' + PICO_SERIALS[1])
config['Characterization.Equipment.' + PICO_SERIALS[1]]['Pico.py identification'] = PICO_SERIALS[1]

config['Characterization.Equipment.' + PICO_SERIALS[2]] = {}
config['Characterization.Equipment.' + PICO_SERIALS[2]]['Name'] = ('PicoScope ' + PICO_SERIALS[2] +
                                                                   ' - embedded in ' +
                                                                   'characterization setup')
config['Characterization.Equipment.' + PICO_SERIALS[2]]['Pico.py identification'] = PICO_SERIALS[2]

with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)
