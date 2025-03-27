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
import os
import sys

# Miscellaneous packages
from importlib import resources as impresources
import numpy as np

# Own packages
from config.config import config_info, read_additional_config
from config.logging_config import initialize_logger, close_logger
from backend.utils import get_config_value, move_to_archive, move_output_data

from fus_driving_systems import config as fds_config
from fus_driving_systems.config import logging_config as fds_logging_config
from fus_driving_systems.utils import get_config_file

test_scanner_only = False
init_motor = True
init_ds = True
init_pico = False
is_testing = test_scanner_only  # | other test examples


def main():
    """
    Main function to run the characterization pipeline.
    """

    # Check if temporary output folder exists and is empty, otherwise archive contents
    temp_output_path = get_config_value(None, config_info, 'Characterization',
                                        'Temporary output path', 'C:\\Temp\\General output folder')
    move_to_archive(temp_output_path)

    # Initialize logger
    log_path = get_config_value(None, config_info, 'Characterization', 'Temporary logging path',
                                'C:\\Temp\\General output folder\\logs')
    try:
        logger_name = get_config_value(None, config_info, 'Logging', 'Logger name', 'SonoRover_One')
        logger = initialize_logger(log_path, logger_name)

        version = get_config_value(logger, config_info, 'Versions', 'SonoRover One software',
                                   'Unknown')
        logger.debug(f'Characterization performed with the following software: {version}')

        # Sync fus_driving_systems logging
        fds_logging_config.sync_logger(logger)

        # Read additional fus_driving_systems config file
        inp_file = impresources.files(fds_config) / get_config_file()
        read_additional_config(inp_file)

        # Delay import due to initialization of logger
        from frontend.input_dialog import InputDialog
        from backend import sequence
        from backend import test_acquisition as test_aq
        from backend import acoustical_alignment as ac_align
        from backend import acquisition as aq
        from frontend import check_dialogs

        # Create dialog to retrieve input values
        input_dialog = InputDialog()
        input_param = input_dialog.input_param

        if input_param is not None:
            logger.debug('Characterization performed with the following parameters: ' +
                         f'\n {input_param}')

            # No sequence chosen using GUI, so read excel file
            if not input_param.sequences:
                # Import sequences of excel, delay import due to initialization of logger
                input_param.sequences = sequence.generate_sequence_list(input_param)

            # Initialize acquisition by initializing all equipment
            if is_testing:
                acquisition = test_aq.TestAcquisition(input_param, init_motor, init_ds, init_pico)
            elif input_param.is_ac_align:
                acquisition = ac_align.AcousticalAlignment(input_param)
                n_dist = len(input_param.sequences[0].ac_align['distance_from_foc'])
                n_foci = len(input_param.sequences)
                middle_points = np.zeros([n_dist*n_foci, 3])
            else:
                acquisition = aq.Acquisition(input_param)

            try:
                for i in range(len(input_param.sequences)):
                    print(f'Perform sequence {i+1} of {len(input_param.sequences)}...', end='\n')
                    seq = input_param.sequences[i]
                    if not input_param.perform_all_seqs:
                        # Wait for user input before continuing
                        check_dialogs.continue_acquisition_dialog(seq)

                    logger.debug(f'Performing the following sequence: \n {seq}')

                    if is_testing:
                        # Test functions
                        if test_scanner_only:
                            # acquisition.check_scan(seq)
                            acquisition.check_scan_ds_combo(seq)
                    else:
                        if seq.is_ac_align:
                            found_middle_points = acquisition.acoustical_alignment(seq)
                            middle_points[n_dist*i:n_dist*(i+1), :] = found_middle_points
                        else:
                            acquisition.acquire_sequence(seq)

                if input_param.is_ac_align:
                    output_name = os.path.splitext(acquisition.output["outputRAW"])[0]
                    ac_align.process_acoustical_alignment(input_param.sequences[0],
                                                          input_param.coord_zero, middle_points,
                                                          output_name, input_param.temp_dir_output)

            finally:
                acquisition.close_all()
        else:
            message = 'No input parameters found.'
            logger.critical(message)
            sys.exit(message)
    finally:
        close_logger()

    # Move logging data
    move_output_data(logger, log_path, input_param.temp_dir_output)

    # All sequences are finished, so move data and remove second folder
    move_output_data(logger, input_param.temp_dir_output, input_param.dir_output)

    message = 'Pipeline finished.'
    logger.info(message)
    print(message, end='\n')


if __name__ == '__main__':
    main()
