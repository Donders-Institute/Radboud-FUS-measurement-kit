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


CONFIG_FILE = 'pcd_config.ini'

pcd_config = configparser.ConfigParser(interpolation=None)

pcd_config['Default'] = {}
pcd_config['Default']['output_dir'] = 'C:\\Temp\\PCD_acquisition_output'
pcd_config['Default']['sampl_freq_multi'] = str(50)
pcd_config['Default']['acquisition_time_us'] = str(150)
pcd_config['Default']['pulse_dur_ms'] = str(0.025)
pcd_config['Default']['pulse_rep_int_ms'] = str(0.170)
pcd_config['Default']['per_elem_ampl'] = str(10)
pcd_config['Default']['all_elems_ampl'] = str(1)

pcd_config['Limit'] = {}
pcd_config['Limit']['all_elems_ampl'] = str(2.5)
pcd_config['Limit']['per_elem_ampl'] = str(15)

pcd_config['IS_PCD15287_01001'] = {}
pcd_config['IS_PCD15287_01001']['Baseline path'] = "D:\\Users\pcd_measurements\Baseline measurements\Imasonic_15287_1001_R75"
pcd_config['IS_PCD15287_01001']['acquisition_time_us'] = str(110)
pcd_config['IS_PCD15287_01001']['Baseline files'] = '\n'.join(
    ['PCD_acquisition_2026-03-04_10-48-26_all_elems_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-29_elem_1_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-31_elem_2_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-34_elem_3_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-36_elem_4_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-39_elem_5_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-42_elem_6_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-45_elem_7_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-47_elem_8_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-50_elem_9_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_10-48-53_elem_10_of_IS_PCD15287_01001_IGT-32-ch_comb_1x10-ch.raw'
     ])

pcd_config['IS_PCD15287_01002'] = {}
pcd_config['IS_PCD15287_01002']['Baseline path'] = "D:\\Users\pcd_measurements\Baseline measurements\Imasonic_15287_1002_R75"
pcd_config['IS_PCD15287_01002']['acquisition_time_us'] = str(110)
pcd_config['IS_PCD15287_01002']['Baseline files'] = '\n'.join(
    ['PCD_acquisition_2026-03-04_11-04-29_all_elems_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-32_elem_1_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-34_elem_2_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-37_elem_3_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-40_elem_4_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-42_elem_5_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-45_elem_6_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-48_elem_7_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-50_elem_8_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-53_elem_9_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-04-56_elem_10_of_IS_PCD15287_01002_IGT-32-ch_comb_1x10-ch.raw'
     ])

pcd_config['IS_PCD15473_01001'] = {}
pcd_config['IS_PCD15473_01001']['Baseline path'] = "D:\\Users\pcd_measurements\Baseline measurements\Imasonic_15473_1001_R100"
pcd_config['IS_PCD15473_01001']['acquisition_time_us'] = str(115)
pcd_config['IS_PCD15473_01001']['Baseline files'] = '\n'.join(
    ['PCD_acquisition_2026-03-04_11-38-16_all_elems_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-19_elem_1_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-22_elem_2_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-25_elem_3_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-27_elem_4_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-30_elem_5_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-33_elem_6_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-35_elem_7_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-38_elem_8_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-41_elem_9_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2026-03-04_11-38-43_elem_10_of_IS_PCD15473_01001_IGT-32-ch_comb_1x10-ch.raw'
     ])

pcd_config['IS_PCD15473_01003'] = {}
pcd_config['IS_PCD15473_01003']['Baseline path'] = "D:\\Users\pcd_measurements\Baseline measurements\Imasonic_15473_1003_R100"
pcd_config['IS_PCD15473_01003']['acquisition_time_us'] = str(115)
pcd_config['IS_PCD15473_01003']['Baseline files'] = '\n'.join(
    ['PCD_acquisition_2025-02-05_12-23-03_all_elems_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-06_elem_1_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-08_elem_2_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-11_elem_3_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-13_elem_4_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-16_elem_5_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-18_elem_6_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-21_elem_7_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-23_elem_8_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-26_elem_9_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw',
     'PCD_acquisition_2025-02-05_12-23-28_elem_10_of_IS_PCD15473_01003_IGT-32-ch_comb_1x10-ch.raw'
     ])

with open(CONFIG_FILE, 'w') as configfile:
    pcd_config.write(configfile)
