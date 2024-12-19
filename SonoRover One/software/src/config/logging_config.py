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

# Miscellaneous packages
from datetime import datetime
import logging

# Own packages
from config.config import config_info as config

logger = None


def initialize_logger(log_dir, filename):
    global logger

    # reset logging
    logger = logging.getLogger(config['General']['Logger name'])
    handlers = logger.handlers[:]
    for handler in handlers:
        logger.removeHandler(handler)
        handler.close()

    # create logger
    logger = logging.getLogger(config['General']['Logger name'])
    logger.setLevel(logging.INFO)

    # Get current date and time for logging
    date_time = datetime.now()
    timestamp = date_time.strftime('%Y-%m-%d_%H-%M-%S')

    # Create directory if it doesn't exist and create file handler
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_dir, f'log_{timestamp}_' + filename
                                                    + '.txt'), mode='w')

    # create formatter and add it to the handlers
    formatterCompact = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - " +
                                         "%(funcName)s line %(lineno)d %(message)s")
    file_handler.setFormatter(formatterCompact)

    # add the handlers to the logger
    logger.addHandler(file_handler)

    return logger


def close_logger():
    """ Ensure the logger and its handlers are properly closed """
    global logger
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
