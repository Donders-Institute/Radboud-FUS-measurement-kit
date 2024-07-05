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
import os

# Miscellaneous packages

# Own packages
from fus_driving_systems.config.config import config_info as config, read_additional_config
from fus_driving_systems.config.logging_config import initialize_logger, logger as global_logger

from frontend.input_dialog import InputDialog

from distutils.dir_util import copy_tree
import shutil

test_scanner_only = False
is_testing = test_scanner_only  # | other test examples


def main():
    """
    Main function to run the characterization pipeline.
    """
    # Read additional configuration file if needed
    read_additional_config('config//characterization_config.ini')

    # Create dialog to retrieve input values
    input_dialog = InputDialog()
    input_param = input_dialog.input_param

    if input_param is not None:
        # Initialize logger
        base_path = input_param.main_dir

        head, tail = os.path.split(input_param.path_protocol_excel_file)
        protocol_excel, ext = os.path.splitext(tail)
        global_logger = initialize_logger(base_path, protocol_excel)

        version = config['Versions']['SonoRover One software']
        global_logger.info(f'Characterization performed with the following software: {version}')
        global_logger.info(f'Characterization performed with the following parameters: \n {input_param}')

        # Import sequences of excel
        from backend import sequence
        sequence_list = sequence.generate_sequence_list(input_param)

        from backend import acquisition as aq
        try:
            # Initialize acquisition by initializing all equipment
            acquisition = aq.Acquisition(input_param)
            for seq in sequence_list:
                global_logger.info(f'Performing the following sequence: \n {seq}')

                if not is_testing:
                    acquisition.acquire_sequence(seq)
                else:
                    # Test functions
                    if test_scanner_only:
                        acquisition.check_scan(seq)

            # All sequences are finished, so move data
            move_output_data(global_logger, input_param.temp_dir_output, input_param.dir_output)
        finally:
            acquisition.close_all()

    else:
        print('No input parameters found.')


def move_output_data(logger, from_dir, to_dir):
    """
    Move output data to the final directory in case it is a internet drive to save acquisition time.

    Args:
        from_dir: Directory files are moved from.
        to_dir: Directory files are moved to.
    """

    try:
        copy_tree(from_dir, to_dir)
        shutil.rmtree(from_dir)
        global_logger.info(f'Output files have been moved to {to_dir}')
    except Exception as e:
        global_logger.info(f'Moving output files failed: {e}. Output files can be found in {from_dir}.')


if __name__ == '__main__':
    main()
