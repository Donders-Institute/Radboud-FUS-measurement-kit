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

# Basic packages

# Miscellaneous packages

# Own packages
from config.logging_config import initialize_logger, close_logger
from fus_driving_systems.config import logging_config as fds_logging_config


if __name__ == '__main__':
    """
    Perform a Passive Cavitation Detection (PCD) measurement to assess the transducer's
    functionality. It is recommended to perform this before each experiment.

    This script helps researchers compare baseline and acquired results to ensure the transducer is
    operating correctly.

    Key details:
    - The PCD acquisition is performed using a PicoScope and a driving system.
    - You should always use:
      - **Channel A** on the PicoScope.
      - **The left/first slot** of the driving system.
      - **A driving system serial number containing "1x10"**.

    Values to Set:
    These values must be correctly configured to ensure the system functions as expected:

    - `output_dir`:
      Path where measurement data will be stored.
      **Default:** `"C:\\Temp\\PCD_acquisition_output"`
      Researchers can modify this if they prefer a different storage location.

    - `picoscope_serial`:
      Specifies which PicoScope model to use.
      **Default:** `'5242D'` (PicoScope 5242D, embedded in a 32-channel IGT driving system).
      To check available PicoScopes, use:
          import backend.picoscope as ps
          print(ps.get_pico_serials())

    - `transducer_serial`:
      The unique identifier for the transducer used in the PCD measurement.
      **Default:** `'IS_PCD15473_01002'`.
      Researchers should verify that this matches the transducer they are using.
      To check available transducers, use:
          from fus_driving_systems import transducer as td
          print(td.get_tran_serials())

    - `driving_system_serial`:
      Identifies the driving system controlling the transducer.
      **Default:** `'IGT-32-ch_comb_1x10-ch'` (a 32-channel IGT system using a 1x10 configuration).
      Ensure the correct serial number is used, as the experiment always requires a system
      containing `"1x10"`.
      To check available driving systems, use:
          from fus_driving_systems import driving_system as ds
          print(ds.get_ds_serials())

    """

    # Set location to store measurement data
    output_dir = "C:\\Temp\\PCD_acquisition_output"

    try:
        logger = initialize_logger(output_dir, 'PCD_acquisition')

        # Sync fus_driving_systems logging
        fds_logging_config.sync_logger(logger)

        # import other packages now to prevent logger is None
        from backend.pcd_acquisition import perform_pcd_acquisition

        # to check available picoscopes:
        # import backend.picoscope as ps
        # print(ps.get_pico_serials())
        # PicoScope 5242D - embedded in IGT driving system (32 ch.)
        # PicoScope 5442A - embedded in IGT driving system (128 ch.)
        picoscope_serial = '5242D'

        # to check available transducers:
        # from fus_driving_systems import transducer as td
        # print(td.get_tran_serials())
        transducer_serial = 'IS_PCD15473_01003'

        # to check available driving systems:
        # from fus_driving_systems import driving_system as ds
        # print(ds.get_ds_serials())
        driving_system_serial = 'IGT-32-ch_comb_1x10-ch'

        perform_pcd_acquisition(picoscope_serial, transducer_serial, driving_system_serial,
                                output_dir)
    finally:
        close_logger()
