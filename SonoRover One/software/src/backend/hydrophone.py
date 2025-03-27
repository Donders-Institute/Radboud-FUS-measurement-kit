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
import copy

# Own packages
from config.config import config_info as config
from backend.utils import get_config_value
from config.logging_config import logger


class Hydrophone:
    """
    Class representing a hydrophone.

    Attributes:
        serial (str): Serial number of the hydrophone.
        name (str): Name of the hydrophone.
        sens_v_pa (float): Sensitivity (V/Pa) datasheet.
    """

    def _init__(self):
        """
        Initializes a hydrophone object with default values.
        """

        self.serial = None
        self.name = None
        self.sens_v_pa = None

    def set_hydro_info(self, serial):
        """
        Sets the hydrophone based on the provided serial number.

        Parameters:
            serial (str): Serial number of the hydrophone.
        """

        try:
            self.serial = serial
            section = 'Characterization.Equipment.' + serial
            get_config_value(logger, config, section, 'Name', 'Unknown hydrophone name')
            self.name = get_config_value(logger, config, section, 'Name', 'Unknown hydrophone name')
            self.sens_v_pa = get_config_value(logger, config, section,
                                              'Sensitivity (V/Pa) datasheet',
                                              'Unknown hydrophone datasheet')

        except KeyError:
            message = (f'No hydrophone with serial number {serial} found in' +
                       ' configuration file.')
            logger.critical(message)
            sys.exit(message)

    def __str__(self):
        """
        Returns a formatted string containing information about the hydrophone.

        Returns:
            str: Formatted information about the hydrophone.
        """

        info = ''
        info += f"Hydrophone serial number: {self.serial} \n "
        info += f"Hydrophone name: {self.name} \n "
        info += f"Hydrophone Sensitivity (V/Pa) datasheet: {self.sens_v_pa} \n "

        return info

    def clone(self):
        """
        Creates and returns a new instance of the Hydrophone class with the same attribute
        values.

        The new instance is a deep copy of the current instance, ensuring that changes to the cloned
        object do not affect the original object.

        Returns:
            CharacSequence: A new instance of the Hydrophone class with copied attribute values.
        """

        new_instance = Hydrophone()
        new_instance.__dict__ = copy.deepcopy(self.__dict__)  # Copy all attributes
        return new_instance


def get_hydro_serials():
    """
    Returns a list of serial numbers for available hydrophones.

    Returns:
        List[str]: Serial numbers for available hydrophones.
    """

    hydro_serial = get_config_value(logger, config, 'Characterization.Equipment', 'Hydrophones',
                                    '').split('\n')

    return hydro_serial


def get_hydro_names():
    """
    Returns a list of names for available hydrophones.

    Returns:
        List[str]: Names for available hydrophones.
    """

    names = []
    for serial in get_hydro_serials():
        try:
            section = 'Characterization.Equipment.' + serial
            hydro_name = get_config_value(logger, config, section, 'Name',
                                          'Unknown hydrophone name')
        except KeyError:
            message = (f'No hydrophone with serial number {serial} found in' +
                       ' configuration file.')
            logger.critical(message)
            sys.exit(message)

        names.append(hydro_name)

    if len(names) < 1:
        message = ('No hydrophones found in configuration file.')
        logger.critical(message)
        sys.exit(message)

    return names


def get_hydro_list():
    """
    Returns a list of available hydrophones.

    Returns:
        List[Obj]: Objects of available hydrophones.
    """

    hydro_list = []
    for serial in get_hydro_serials():
        try:
            hydro = Hydrophone()
            hydro.set_hydro_info(serial)
        except KeyError:
            message = (f'No hydrophone with serial number {serial} found in' +
                       ' configuration file.')
            logger.critical(message)
            sys.exit(message)

        hydro_list.append(hydro)

    if len(hydro_list) < 1:
        message = ('No hydrophones found in configuration file.')
        logger.critical(message)
        sys.exit(message)

    return hydro_list


def get_serial_from_name(name):
    """
    Returns the serial number matching the given name.

    Args:
        name (str): The name of the device.

    Returns:
        str: The serial number, or None if no match is found.
    """

    for hydro in get_hydro_list():
        if hydro.name == name:

            return hydro.serial
