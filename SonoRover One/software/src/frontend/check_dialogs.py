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
import sys

# Miscellaneous packages
from CTkMessagebox import CTkMessagebox
import tkinter

# Own packages
from config.config import config_info as config
from config.logging_config import logger

from backend.utils import get_config_value


def continue_acquisition_dialog(sequence):
    message = get_config_value(logger, config, 'Characterization', 'Continue acquisition message',
                               'Continue acquisition with the following sequence:')
    message += '\n' + str(sequence)

    master = tkinter.Tk()
    master.withdraw()

    message_box = CTkMessagebox(title="Ready to continue acquisition?", message=message,
                                icon="question", option_1="Confirm")
    response = message_box.get()

    if response is None:
        message = 'Pipeline is cancelled by user.'
        logger.critical(message)
        sys.exit(message)

    logger.debug(f"Message box closed with response: {response}")


def check_disconnection_dialog(add_message):
    default_message = ('Ensure the following: \n - PicoScope software is not connected to the ' +
                       'PicoScope in use. \n - Universal Gcode Sender is not connected to the ' +
                       'positioning system.')
    message = get_config_value(logger, config, 'Characterization', 'Disconnection message',
                               default_message)
    message += add_message

    master = tkinter.Tk()
    master.withdraw()

    message_box = CTkMessagebox(title="Attention", message=message, icon="warning",
                                option_1="Confirm")
    response = message_box.get()

    if response is None:
        message = 'Pipeline is cancelled by user.'
        logger.critical(message)
        sys.exit(message)

    logger.debug(f"Message box closed with response: {response}")
