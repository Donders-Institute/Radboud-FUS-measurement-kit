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
from config import config
from logging_config import initialize_logger, logger

import sequence

from input_dialog import InputDialog

from distutils.dir_util import copy_tree
import shutil

test_scanner_only = False
is_testing = test_scanner_only  # | other test examples


def main():
    """
    Main function to run the characterization pipeline.
    """

    # Create dialog to retrieve input values
    input_dialog = InputDialog()
    input_param = input_dialog.input_param

    if input_param is not None:
        # Initialize the logger
        logger = initialize_logger(input_param)

        version = config['Versions']['Equipment characterization pipeline software']
        logger.info(f'Characterization performed with the following software: {version}')
        logger.info(f'Characterization performed with the following parameters: \n {input_param}')

        # Import sequences of excel
        sequence_list = sequence.generate_sequence_list(input_param)

        for seq in sequence_list:
            logger.info(f'Performing the following sequence: \n {seq}')

            # Check existance of directory
            outfile = os.path.join(input_param.temp_dir_output, 'sequence_' + str(seq.seq_number)
                                   + '_output_data.raw')

            if not is_testing:
                acquisition.acquire(outfile, seq, input_param)
            else:
                # Test functions
                if test_scanner_only:
                    acquisition.check_scan(seq, input_param)

        # All sequences are finished, so move data
        move_output_data(input_param.temp_dir_output, input_param.dir_output)

    else:
        print('No input parameters found.')


def move_output_data(from_dir, to_dir):
    """
    Move output data to the final directory in case it is a internet drive to save acquisition time.

    Args:
        from_dir: Directory files are moved from.
        to_dir: Directory files are moved to.
    """

    try:
        copy_tree(from_dir, to_dir)
        shutil.rmtree(from_dir)
        logger.info(f'Output files have been moved to {to_dir}')
    except Exception as e:
        logger.info(f'Moving output files failed: {e}. Output files can be found in {from_dir}.')


if __name__ == '__main__':
    main()
