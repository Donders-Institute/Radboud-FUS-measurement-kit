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

import pandas as pd
import os
import sys
import protocol
import acquisition
import logging
from datetime import datetime
import input_parameters
import configparser

from distutils.dir_util import copy_tree
import shutil

config_file = 'config\\characterization_config.ini'
config = configparser.ConfigParser()
config.read(config_file)


def initializeLogging(base_path, protocol_excel):
    # reset logging
    logger = logging.getLogger(config['General']['Logger name'])
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()

    logging.basicConfig(level=logging.INFO)

    # create logger
    logger = logging.getLogger(config['General']['Logger name'])
    logger.setLevel(logging.INFO)

    # Get current date and time for logging
    date_time = datetime.now()
    timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

    # create file handler
    file_handler = logging.FileHandler(os.path.join(base_path, f'log_{timestamp}_' + protocol_excel
                                                    + '.txt'), mode='w')

    # create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # create formatter and add it to the handlers
    formatterCompact = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(funcName)s "
                                         + "line %(lineno)d %(message)s")
    file_handler.setFormatter(formatterCompact)
    console_handler.setFormatter(formatterCompact)

    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def importExcel(logger, inputValues):
    # Import excel file containing us protocol parameters
    excel_path = os.path.join(inputValues.path_protocol_excel_file)

    logger.info('Extract protocol parameters from ' + excel_path)

    if os.path.exists(excel_path):
        data = pd.read_excel(excel_path, engine='openpyxl')

        logger.info('Find index of each column')
        indices = protocol.setIndices(data)

        protocol_list = []
        seq_number = 1
        for seq in data.values:
            protocol_list.append(protocol.newProtocol(inputValues, indices, seq, seq_number,
                                                      config['General']['Logger name']))
            seq_number = seq_number + 1
        logger.info(str(len(protocol_list)) + " different sequences found in "
                    + inputValues.path_protocol_excel_file)

        return protocol_list

    else:
        logger.error("Pipeline is cancelled. The following direction cannot be found: "
                     + excel_path)
        sys.exit()


def main():
    # Create dialog to retrieve input values
    inputValues = input_parameters.InputDialog(config).updated_inputParam

    version = config['Versions']['Equipment characterization pipeline software']

    if inputValues is not None:
        # Acquire values
        head, tail = os.path.split(inputValues.path_protocol_excel_file)
        protocol_excel, ext = os.path.splitext(tail)

        logger = initializeLogging(inputValues.main_dir, protocol_excel)
        logger.info(f'Characterization performed with the following software: {version}')
        logger.info('Characterization pipeline started with the following parameters: \n'
                    + inputValues.info())

        # Import protocols of excel
        protocol_list = importExcel(logger, inputValues)

        for prot in protocol_list:
            logger.info('Performing the following protocol: \n' + prot.info())

            # Check existance of directory
            outfile = os.path.join(inputValues.temp_dir_output, 'sequence_' + str(prot.seq_number)
                                   + '_output_data.raw')

            acquisition.acquire(outfile, prot, config, inputValues)

            # Test functions
            # acquisition.check_scan(prot, config, inputValues)

        # all protocols are finished, so move data
        try:
            # copy all data over to internet drive
            from_dir = inputValues.temp_dir_output
            to_dir = inputValues.dir_output

            copy_tree(from_dir, to_dir)

            shutil.rmtree(from_dir)

            logger.info(f'Output files have been moved to {to_dir}')
        except:
            logger.info(f'Moving output files has failed. Output files can be found in {from_dir}.')
    else:
        print('No input parameters found.')


if __name__ == '__main__':
    main()
