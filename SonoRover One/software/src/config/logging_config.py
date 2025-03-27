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
from datetime import datetime
import logging
from pathlib import Path

# Own packages
from config.config import config_info as config
from backend.utils import get_config_value

logger = None


def initialize_logger(log_dir, filename):
    global logger

    # create directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # reset logging
    logger_name = get_config_value(None, config, 'Logging', 'Logger name', 'SonoRover_One')
    logger = logging.getLogger(logger_name)
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()

    file_log_level = getattr(logging, get_config_value(None, config, 'Logging', 'Log level file',
                                                       'INFO').upper())
    console_log_level = getattr(logging, get_config_value(None, config, 'Logging',
                                                          'Log level console', 'WARNING').upper())

    # create logger
    logger = logging.getLogger(logger_name)

    # Get current date and time for logging
    date_time = datetime.now()
    timestamp_format = get_config_value(None, config, 'Logging', 'Timestamp format',
                                        '%Y-%m-%d_%H-%M-%S')
    timestamp = date_time.strftime(timestamp_format)

    # create file handler
    initial_part_log_filename = get_config_value(None, config, 'Logging',
                                                 'Initial part of log filename', 'log_')
    file_handler = logging.FileHandler(os.path.join(log_dir, initial_part_log_filename +
                                                    f'{timestamp}_' + filename + '.txt'), mode='w')

    # create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # create formatter and add it to the handlers
    formatterCompact = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - " +
                                         "%(funcName)s line %(lineno)d %(message)s")
    file_handler.setFormatter(formatterCompact)
    console_handler.setFormatter(formatterCompact)

    # add the handlers to the logger
    file_handler.setLevel(file_log_level)
    console_handler.setLevel(console_log_level)

    logger.setLevel(min(file_log_level, console_log_level))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def close_logger():
    """ Ensure the logger and its handlers are properly closed """
    global logger
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
