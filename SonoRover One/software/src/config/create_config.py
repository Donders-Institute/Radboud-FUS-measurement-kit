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
import os

CONFIG_FOLDER = 'config'  # should be in the same directory as code
CONFIG_FILE = 'characterization_config.ini'

config = configparser.ConfigParser(interpolation=None)

config['Versions'] = {}
config['Versions']['Equipment characterization pipeline software'] = '0.8'

config['General'] = {}
config['General']['Logger name'] = 'equipment_characterization_pipeline'

config['General']['Configuration file folder'] = CONFIG_FOLDER
config['General']['Filename of input parameters cache'] = 'characterization_input_cache.ini'

config['General']['Temporary output path'] = 'C:\\Temp'

MAX_ALLOWED_PRESSURE = 1.2  # MPa
config['General']['Maximum pressure allowed in free water [MPa]'] = str(MAX_ALLOWED_PRESSURE)

# if ramp shapes are changed, don't forget to change values used in code as well
config['General']['Ramp shapes'] = ', '.join(['Rectangular - no ramping', 'Linear', 'Tukey'])

config['Headers'] = {}
config['Headers']['Software limit'] = (f'Amplitude limit %% based on {MAX_ALLOWED_PRESSURE} MPa'
                                       + ' in free water')
config['Headers']['a-coefficient'] = 'a-coefficient (pressure [Pa] = a*ampl %% + b)'
config['Headers']['b-coefficient'] = 'b-coefficent (pressure [Pa] = a*ampl %% + b)'
config['Headers']['100% pressure'] = 'Pressure [MPa] at 100% amplitude'

config['Equipment'] = {}


#######################################################################################
# Sonic Concepts
#######################################################################################

SONIC_CONCEPTS = 'Sonic Concepts'
CONFIG_FILE_FOLDER_SC_TRAN = CONFIG_FOLDER + '\\sonic_concepts_transducers'
config['Equipment.Manufacturer.SC'] = {}
config['Equipment.Manufacturer.SC']['Name'] = SONIC_CONCEPTS
config['Equipment.Manufacturer.SC']['Config. file folder transducers'] = CONFIG_FILE_FOLDER_SC_TRAN

SC_DS = ['203-035', '105-010']

config['Equipment.Manufacturer.SC']['Equipment - Driving systems'] = ', '.join(SC_DS)

SC_TRAN_2CH = ['CTX-250-009', 'CTX-250-014', 'CTX-500-006']
SC_TRAN_4CH = ['CTX-250-001', 'CTX-250-026', 'CTX-500-024', 'CTX-500-026']

SC_TRANS = SC_TRAN_2CH + SC_TRAN_4CH

config['Equipment.Manufacturer.SC']['Equipment - Transducers'] = ', '.join(SC_TRANS)


#######################################################################################
# IGT
#######################################################################################

IGT = 'IGT'
CONFIG_FILE_FOLDER_IGT_DS = CONFIG_FOLDER + '\\igt_ds'
config['Equipment.Manufacturer.IGT'] = {}
config['Equipment.Manufacturer.IGT']['Name'] = IGT
config['Equipment.Manufacturer.IGT']['Config. file folder driving sys.'] = CONFIG_FILE_FOLDER_IGT_DS

IGT_DS = ['IGT-128-ch', 'IGT-128-ch_comb_2x10-ch', 'IGT-128-ch_comb_1x10-ch',
          'IGT-128-ch_comb_1x8-ch', 'IGT-128-ch_comb_1x4-ch', 'IGT-128-ch_comb_1x2-ch',
          'IGT-32-ch', 'IGT-32-ch_comb_2x10-ch', 'IGT-32-ch_comb_1x10-ch',
          'IGT-8-ch_comb_2x4-ch', 'IGT-8-ch_comb_1x4-ch', 'IGT-8-ch_comb_2x2-ch',
          'IGT-8-ch_comb_1x2-ch']

config['Equipment.Manufacturer.IGT']['Equipment - Driving systems'] = ', '.join(IGT_DS)


#######################################################################################
# Imasonic
#######################################################################################

IMASONIC = 'Imasonic'
CONFIG_FILE_FOLDER_IS_TRAN = CONFIG_FOLDER + '\\imasonic_transducers'
config['Equipment.Manufacturer.IS'] = {}
config['Equipment.Manufacturer.IS']['Name'] = IMASONIC
config['Equipment.Manufacturer.IS']['Config. file folder transducers'] = CONFIG_FILE_FOLDER_IS_TRAN

IS_TRANS = ['IS PCD15287_01001', 'IS PCD15287_01002', 'IS PCD15473_01001', 'IS PCD15473_01002']


#######################################################################################
# Equipment collection
#######################################################################################

config['Equipment.Manufacturer.IS']['Equipment - Transducers'] = ', '.join(IS_TRANS)

# list of driving system 'serial numbers'
config['Equipment']['Driving systems'] = str(', '.join(SC_DS + IGT_DS))

DUMMY = 'Dummy'
DUMMIES = [DUMMY]
# list of transducer 'serial numbers'
config['Equipment']['Transducers'] = str(', '.join(SC_TRANS + IS_TRANS + DUMMIES))


#######################################################################################
# Sonic Concepts - Driving systems
#######################################################################################

config['Equipment.Driving system.' + SC_DS[0]] = {}
config['Equipment.Driving system.' + SC_DS[0]]['Name'] = ('NeuroFUS 1 x 4 ch. or 1 x 2 ch. TPO '
                                                          + 'junior ' + SC_DS[0])
config['Equipment.Driving system.' + SC_DS[0]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Driving system.' + SC_DS[0]]['Available channels'] = str(4)
config['Equipment.Driving system.' + SC_DS[0]]['Connection info'] = 'COM7'
config['Equipment.Driving system.' + SC_DS[0]]['Transducer compatibility'] = str(', '.join(
    SC_TRANS + DUMMIES))
config['Equipment.Driving system.' + SC_DS[0]]['Active?'] = str(True)

config['Equipment.Driving system.' + SC_DS[1]] = {}
config['Equipment.Driving system.' + SC_DS[1]]['Name'] = ('NeuroFUS 1 x 4 ch. or 1 x 2 ch. TPO '
                                                          + 'senior ' + SC_DS[1])
config['Equipment.Driving system.' + SC_DS[1]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Driving system.' + SC_DS[1]]['Available channels'] = str(4)
config['Equipment.Driving system.' + SC_DS[1]]['Connection info'] = 'COM8'
config['Equipment.Driving system.' + SC_DS[1]]['Transducer compatibility'] = str(', '.join(
    SC_TRANS + DUMMIES))
config['Equipment.Driving system.' + SC_DS[1]]['Active?'] = str(True)


#######################################################################################
# IGT - Driving systems
#######################################################################################

# # 128 ch. # #

config['Equipment.Driving system.' + IGT_DS[0]] = {}
config['Equipment.Driving system.' + IGT_DS[0]]['Name'] = IGT + ' 128 ch. all channels'
config['Equipment.Driving system.' + IGT_DS[0]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[0]]['Available channels'] = str(128)
config['Equipment.Driving system.' + IGT_DS[0]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_393F.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[0]]['Transducer compatibility'] = str(', '.join(
    DUMMIES))
config['Equipment.Driving system.' + IGT_DS[0]]['Active?'] = str(True)

config['Equipment.Driving system.' + IGT_DS[1]] = {}
config['Equipment.Driving system.' + IGT_DS[1]]['Name'] = IGT + ' 128 ch. combined into 2 x 10 ch.'
config['Equipment.Driving system.' + IGT_DS[1]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[1]]['Available channels'] = str(20)
config['Equipment.Driving system.' + IGT_DS[1]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_2x10_393F.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[1]]['Transducer compatibility'] = str(', '.join(
    IS_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[1]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[2]] = {}
config['Equipment.Driving system.' + IGT_DS[2]]['Name'] = IGT + ' 128 ch. combined into 1 x 10 ch.'
config['Equipment.Driving system.' + IGT_DS[2]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[2]]['Available channels'] = str(10)
config['Equipment.Driving system.' + IGT_DS[2]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_1x10_393F.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[2]]['Transducer compatibility'] = str(', '.join(
    IS_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[2]]['Active?'] = str(True)

config['Equipment.Driving system.' + IGT_DS[3]] = {}
config['Equipment.Driving system.' + IGT_DS[3]]['Name'] = IGT + ' 128 ch. combined into 1 x 8 ch.'
config['Equipment.Driving system.' + IGT_DS[3]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[3]]['Available channels'] = str(8)
config['Equipment.Driving system.' + IGT_DS[3]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_8c.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[3]]['Transducer compatibility'] = str(', '.join(
    SC_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[3]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[4]] = {}
config['Equipment.Driving system.' + IGT_DS[4]]['Name'] = IGT + ' 128 ch. combined into 4 ch.'
config['Equipment.Driving system.' + IGT_DS[4]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[4]]['Available channels'] = str(4)
config['Equipment.Driving system.' + IGT_DS[4]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_4ch.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[4]]['Transducer compatibility'] = str(', '.join(
    SC_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[4]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[5]] = {}
config['Equipment.Driving system.' + IGT_DS[5]]['Name'] = IGT + ' 128 ch. combined into 2 ch.'
config['Equipment.Driving system.' + IGT_DS[5]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[5]]['Available channels'] = str(2)
config['Equipment.Driving system.' + IGT_DS[5]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen128_2ch.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[5]]['Transducer compatibility'] = str(', '.join(
    SC_TRAN_2CH + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[5]]['Active?'] = str(False)


# # 32 ch. # #

config['Equipment.Driving system.' + IGT_DS[6]] = {}
config['Equipment.Driving system.' + IGT_DS[6]]['Name'] = IGT + ' 32 ch. all channels'
config['Equipment.Driving system.' + IGT_DS[6]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[6]]['Available channels'] = str(32)
config['Equipment.Driving system.' + IGT_DS[6]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen32_71D8.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[6]]['Transducer compatibility'] = str(', '.join(
    DUMMIES))
config['Equipment.Driving system.' + IGT_DS[6]]['Active?'] = str(True)

config['Equipment.Driving system.' + IGT_DS[7]] = {}
config['Equipment.Driving system.' + IGT_DS[7]]['Name'] = IGT + ' 32 ch. combined into 2 x 10 ch.'
config['Equipment.Driving system.' + IGT_DS[7]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[7]]['Available channels'] = str(20)
config['Equipment.Driving system.' + IGT_DS[7]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen32_2x10c_71D8.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[7]]['Transducer compatibility'] = str(', '.join(
    IS_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[7]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[8]] = {}
config['Equipment.Driving system.' + IGT_DS[8]]['Name'] = IGT + ' 32 ch. combined into 1 x 10 ch.'
config['Equipment.Driving system.' + IGT_DS[8]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[8]]['Available channels'] = str(10)
config['Equipment.Driving system.' + IGT_DS[8]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen32_10c_71D8.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[8]]['Transducer compatibility'] = str(', '.join(
    IS_TRANS + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[8]]['Active?'] = str(True)


# # 8 ch. # #

config['Equipment.Driving system.' + IGT_DS[9]] = {}
config['Equipment.Driving system.' + IGT_DS[9]]['Name'] = IGT + ' 8 ch. combined into 2 x 4 ch.'
config['Equipment.Driving system.' + IGT_DS[9]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[9]]['Available channels'] = str(8)
config['Equipment.Driving system.' + IGT_DS[9]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen_8_F720.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[9]]['Transducer compatibility'] = str(', '.join(
    SC_TRAN_4CH + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[9]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[10]] = {}
config['Equipment.Driving system.' + IGT_DS[10]]['Name'] = IGT + ' 8 ch. combined into 1 x 4 ch.'
config['Equipment.Driving system.' + IGT_DS[10]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[10]]['Available channels'] = str(4)
config['Equipment.Driving system.' + IGT_DS[10]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen_4_F720.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[10]]['Transducer compatibility'] = str(', '.join(
    SC_TRAN_4CH + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[10]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[11]] = {}
config['Equipment.Driving system.' + IGT_DS[11]]['Name'] = IGT + ' 8 ch. combined into 2 x 2 ch.'
config['Equipment.Driving system.' + IGT_DS[11]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[11]]['Available channels'] = str(4)
config['Equipment.Driving system.' + IGT_DS[11]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen_8c4_F720.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[11]]['Transducer compatibility'] = str(', '.join(
    SC_TRAN_2CH + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[11]]['Active?'] = str(False)

config['Equipment.Driving system.' + IGT_DS[12]] = {}
config['Equipment.Driving system.' + IGT_DS[12]]['Name'] = IGT + ' 8 ch. combined into 1 x 2 ch.'
config['Equipment.Driving system.' + IGT_DS[12]]['Manufacturer'] = IGT
config['Equipment.Driving system.' + IGT_DS[12]]['Available channels'] = str(2)
config['Equipment.Driving system.' + IGT_DS[12]]['Connection info'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IGT_DS,
    'gen_Nijmegen_4c2_F720.json'))  # should be in the same directory as code
config['Equipment.Driving system.' + IGT_DS[12]]['Transducer compatibility'] = str(', '.join(
    SC_TRAN_2CH + DUMMIES))
config['Equipment.Driving system.' + IGT_DS[12]]['Active?'] = str(False)


#######################################################################################
# Sonic Concepts - Tranducers
#######################################################################################

config['Equipment.Transducer.' + SC_TRANS[0]] = {}
config['Equipment.Transducer.' + SC_TRANS[0]]['Name'] = 'NeuroFUS 2 ch. CTX-250-009'
config['Equipment.Transducer.' + SC_TRANS[0]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[0]]['Elements'] = str(2)
config['Equipment.Transducer.' + SC_TRANS[0]]['Fund. freq.'] = str(250)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[0]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[0]]['Min. focus'] = str(15.9)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[0]]['Max. focus'] = str(46.0)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[0]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-250-009 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[0]]['Active?'] = str(True)

config['Equipment.Transducer.' + SC_TRANS[1]] = {}
config['Equipment.Transducer.' + SC_TRANS[1]]['Name'] = 'NeuroFUS 2 ch. CTX-250-014'
config['Equipment.Transducer.' + SC_TRANS[1]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[1]]['Elements'] = str(2)
config['Equipment.Transducer.' + SC_TRANS[1]]['Fund. freq.'] = str(250)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[1]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[1]]['Min. focus'] = str(12.6)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[1]]['Max. focus'] = str(44.1)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[1]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-250-014 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[1]]['Active?'] = str(True)


config['Equipment.Transducer.' + SC_TRANS[2]] = {}
config['Equipment.Transducer.' + SC_TRANS[2]]['Name'] = 'NeuroFUS 2 ch. CTX-500-006'
config['Equipment.Transducer.' + SC_TRANS[2]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[2]]['Elements'] = str(2)
config['Equipment.Transducer.' + SC_TRANS[2]]['Fund. freq.'] = str(500)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[2]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[2]]['Min. focus'] = str(33.2)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[2]]['Max. focus'] = str(79.4)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[2]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-500-006 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[2]]['Active?'] = str(True)

config['Equipment.Transducer.' + SC_TRANS[3]] = {}
config['Equipment.Transducer.' + SC_TRANS[3]]['Name'] = 'NeuroFUS 4 ch. CTX-250-001'
config['Equipment.Transducer.' + SC_TRANS[3]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[3]]['Elements'] = str(4)
config['Equipment.Transducer.' + SC_TRANS[3]]['Fund. freq.'] = str(250)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[3]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[3]]['Min. focus'] = str(14.2)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[3]]['Max. focus'] = str(60.9)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[3]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-250-001 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[3]]['Active?'] = str(True)

config['Equipment.Transducer.' + SC_TRANS[4]] = {}
config['Equipment.Transducer.' + SC_TRANS[4]]['Name'] = 'NeuroFUS 4 ch. CTX-250-026'
config['Equipment.Transducer.' + SC_TRANS[4]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[4]]['Elements'] = str(4)
config['Equipment.Transducer.' + SC_TRANS[4]]['Fund. freq.'] = str(250)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[4]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[4]]['Min. focus'] = str(22.2)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[4]]['Max. focus'] = str(61.5)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[4]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-250-026 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[4]]['Active?'] = str(True)

config['Equipment.Transducer.' + SC_TRANS[5]] = {}
config['Equipment.Transducer.' + SC_TRANS[5]]['Name'] = 'NeuroFUS 4 ch. CTX-500-024'
config['Equipment.Transducer.' + SC_TRANS[5]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[5]]['Elements'] = str(4)
config['Equipment.Transducer.' + SC_TRANS[5]]['Fund. freq.'] = str(500)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[5]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[5]]['Min. focus'] = str(31.7)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[5]]['Max. focus'] = str(77.0)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[5]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-500-024 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[5]]['Active?'] = str(False)

config['Equipment.Transducer.' + SC_TRANS[6]] = {}
config['Equipment.Transducer.' + SC_TRANS[6]]['Name'] = 'NeuroFUS 4 ch. CTX-500-026'
config['Equipment.Transducer.' + SC_TRANS[6]]['Manufacturer'] = SONIC_CONCEPTS
config['Equipment.Transducer.' + SC_TRANS[6]]['Elements'] = str(4)
config['Equipment.Transducer.' + SC_TRANS[6]]['Fund. freq.'] = str(500)  # [kHz]
config['Equipment.Transducer.' + SC_TRANS[6]]['Natural focus'] = str(0)  # [mm] only for Imasonic
config['Equipment.Transducer.' + SC_TRANS[6]]['Min. focus'] = str(39.6)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[6]]['Max. focus'] = str(79.6)  # [mm]
config['Equipment.Transducer.' + SC_TRANS[6]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_SC_TRAN,
    'CTX-500-026 - TPO-105-010 - Steer Table.xlsx'))  # should be in the same directory as code
config['Equipment.Transducer.' + SC_TRANS[6]]['Active?'] = str(True)


#######################################################################################
# Imasonic - Tranducers
#######################################################################################


config['Equipment.Transducer.' + IS_TRANS[0]] = {}
config['Equipment.Transducer.' + IS_TRANS[0]]['Name'] = IMASONIC + ' 10 ch. PCD15287_01001'
config['Equipment.Transducer.' + IS_TRANS[0]]['Manufacturer'] = IMASONIC
config['Equipment.Transducer.' + IS_TRANS[0]]['Elements'] = str(10)
config['Equipment.Transducer.' + IS_TRANS[0]]['Fund. freq.'] = str(300)  # [kHz]
config['Equipment.Transducer.' + IS_TRANS[0]]['Natural focus'] = str(75)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[0]]['Min. focus'] = str(10)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[0]]['Max. focus'] = str(150)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[0]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IS_TRAN,
    'transducer_15287_10_300kHz.ini'))  # should be in the same directory as code
config['Equipment.Transducer.' + IS_TRANS[0]]['Active?'] = str(True)

config['Equipment.Transducer.' + IS_TRANS[1]] = {}
config['Equipment.Transducer.' + IS_TRANS[1]]['Name'] = IMASONIC + ' 10 ch. PCD15287_01002'
config['Equipment.Transducer.' + IS_TRANS[1]]['Manufacturer'] = IMASONIC
config['Equipment.Transducer.' + IS_TRANS[1]]['Elements'] = str(10)
config['Equipment.Transducer.' + IS_TRANS[1]]['Fund. freq.'] = str(300)  # [kHz]
config['Equipment.Transducer.' + IS_TRANS[1]]['Natural focus'] = str(75)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[1]]['Min. focus'] = str(10)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[1]]['Max. focus'] = str(150)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[1]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IS_TRAN,
    'transducer_15287_10_300kHz.ini'))  # should be in the same directory as code
config['Equipment.Transducer.' + IS_TRANS[1]]['Active?'] = str(True)

config['Equipment.Transducer.' + IS_TRANS[2]] = {}
config['Equipment.Transducer.' + IS_TRANS[2]]['Name'] = IMASONIC + ' 10 ch. PCD15473_01001'
config['Equipment.Transducer.' + IS_TRANS[2]]['Manufacturer'] = IMASONIC
config['Equipment.Transducer.' + IS_TRANS[2]]['Elements'] = str(10)
config['Equipment.Transducer.' + IS_TRANS[2]]['Fund. freq.'] = str(300)  # [kHz]
config['Equipment.Transducer.' + IS_TRANS[2]]['Natural focus'] = str(100)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[2]]['Min. focus'] = str(10)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[2]]['Max. focus'] = str(150)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[2]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IS_TRAN,
    'transducer_15473_10_300kHz.ini'))  # should be in the same directory as code
config['Equipment.Transducer.' + IS_TRANS[2]]['Active?'] = str(True)

config['Equipment.Transducer.' + IS_TRANS[3]] = {}
config['Equipment.Transducer.' + IS_TRANS[3]]['Name'] = IMASONIC + ' 10 ch. PCD15473_01002'
config['Equipment.Transducer.' + IS_TRANS[3]]['Manufacturer'] = IMASONIC
config['Equipment.Transducer.' + IS_TRANS[3]]['Elements'] = str(10)
config['Equipment.Transducer.' + IS_TRANS[3]]['Fund. freq.'] = str(300)  # [kHz]
config['Equipment.Transducer.' + IS_TRANS[3]]['Natural focus'] = str(100)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[3]]['Min. focus'] = str(10)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[3]]['Max. focus'] = str(150)  # [mm]
config['Equipment.Transducer.' + IS_TRANS[3]]['Steer information'] = str(os.path.join(
    CONFIG_FILE_FOLDER_IS_TRAN,
    'transducer_15473_10_300kHz.ini'))  # should be in the same directory as code
config['Equipment.Transducer.' + IS_TRANS[3]]['Active?'] = str(True)

#######################################################################################
# Dummy tranducer
#######################################################################################

config['Equipment.Transducer.' + DUMMY] = {}
config['Equipment.Transducer.' + DUMMY]['Name'] = 'Dummy load'
config['Equipment.Transducer.' + DUMMY]['Manufacturer'] = ''
config['Equipment.Transducer.' + DUMMY]['Elements'] = str(0)
config['Equipment.Transducer.' + DUMMY]['Fund. freq.'] = str(0)  # [kHz]
config['Equipment.Transducer.' + DUMMY]['Natural focus'] = str(0)  # [mm]
config['Equipment.Transducer.' + DUMMY]['Min. focus'] = str(0)  # [mm]
config['Equipment.Transducer.' + DUMMY]['Max. focus'] = str(1000)  # [mm]
config['Equipment.Transducer.' + DUMMY]['Steer information'] = ''
config['Equipment.Transducer.' + DUMMY]['Active?'] = str(False)

# TODO: elaborate on other characterization equipment and print it in logging file (hydrophone etc.)
with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)
