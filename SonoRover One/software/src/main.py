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
(Image Guided Therapy, Pessac, France) (2024), Radboud FUS measurement kit (version 1.0),
https://github.com/Donders-Institute/Radboud-FUS-measurement-kit
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

from fus_driving_systems import config as fds_config
from fus_driving_systems.config import logging_config as fds_logging_config

from distutils.dir_util import copy_tree
from pathlib import Path
import shutil

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
    move_to_archive(config_info['Characterization']['Temporary output path'])

    # Initialize logger
    log_path = config_info['Characterization']['Temporary logging path']
    try:
        logger = initialize_logger(log_path, config_info['General']['Logger name'])

        version = config_info['Versions']['SonoRover One software']
        logger.info(f'Characterization performed with the following software: {version}')

        # Sync fus_driving_systems logging
        fds_logging_config.sync_logger(logger)

        # Read additional fus_driving_systems config file
        inp_file = impresources.files(fds_config) / 'ds_config.ini'
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
            logger.info(f'Characterization performed with the following parameters: \n {input_param}')

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

                    logger.info(f'Performing the following sequence: \n {seq}')

                    if is_testing:
                        # Test functions
                        if test_scanner_only:
                            # acquisition.check_scan(seq)
                            acquisition.check_scan_ds_combo(seq)
                    else:
                        if seq.is_ac_align:
                            found_middle_points = acquisition.acoustical_alignment(seq)
                            if n_dist == 1:
                                middle_points[n_dist*i:n_dist*(i+1), :] = found_middle_points
                            else:
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
            sys.exit('No input parameters found.')
    finally:
        close_logger()
        
    # Move logging data
    move_output_data(logger, log_path, input_param.temp_dir_output)

    # All sequences are finished, so move data and remove second folder
    move_output_data(logger, input_param.temp_dir_output, input_param.dir_output)

    print('Pipeline finished.', end='\n')


def move_to_archive(folder_path):
    folder = Path(folder_path)
    archive_folder = folder / "archive"

    # Check if the folder exists
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
        return

    # Create the archive folder if it doesn't exist
    if not archive_folder.exists():
        archive_folder.mkdir(parents=True, exist_ok=True)

    # Check if the folder is empty
    if any(folder.iterdir()):  # Check if folder is empty

        # Move all files and subfolders to the archive folder
        for item in folder.iterdir():
            if item.name == "archive":  # Skip the archive folder itself
                continue
            destination = archive_folder / item.name

            # Handle conflict if the destination already exists
            if destination.exists():
                counter = 1
                new_destination = destination.with_name(f"{item.stem}_{counter}{item.suffix}")
                while new_destination.exists():
                    counter += 1
                    new_destination = destination.with_name(f"{item.stem}_{counter}{item.suffix}")
                destination = new_destination  # Use the new unique name
            try:
                shutil.move(str(item), destination)
                print(f"Moved '{item}' to '{destination}'.", end='\n')
            except PermissionError:
                print('The process cannot access the file because it is being used by another pro' +
                      f'cess or you do not have permission to move this file. Skip {item} for now.',
                      end='\n')
    else:
        print(f"The folder '{folder}' is empty; nothing to move.", end='\n')

    print(f"All content moved to archive folder: {archive_folder}", end='\n')


def move_output_data(logger, from_dir, to_dir):
    """
    Move output data to the final directory in case it is a internet drive to save acquisition time.

    Args:
        from_dir: Directory files are moved from.
        to_dir: Directory files are moved to.
    """

    try:
        copy_tree(from_dir, to_dir)

        logger.info(f'Output files have been moved to {to_dir}')
        print(f'Output files have been moved to {to_dir}', end='\n')
    except Exception as e:
        logger.error(f'Moving output files failed: {e}. Output files can be found in {from_dir}.')
        print(f'WARNING Moving output files failed: {e}. Output files can be found in {from_dir}.')


if __name__ == '__main__':
    main()
