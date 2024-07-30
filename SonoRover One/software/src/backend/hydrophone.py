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
import sys

# Miscellaneous packages

# Own packages
from config.config import config_info as config


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
            self.name = config['Characterization.Equipment.' + serial]['Name']
            self.sens_v_pa = (config['Characterization.Equipment.' + serial]
                                    ['Sensitivity (V/Pa) datasheet'])
        except KeyError:
            sys.exit(f'No hydrophone with serial number {serial} found in configuration file.')

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


def get_hydro_serials():
    """
    Returns a list of serial numbers for available hydrophones.

    Returns:
        List[str]: Serial numbers for available hydrophones.
    """

    hydro_serial = config['Characterization.Equipment']['Hydrophones'].split(', ')

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
            hydro_name = config['Characterization.Equipment.' + serial]['Name']
        except KeyError:
            sys.exit(f'No hydrophone with serial number {serial} found in' +
                     ' configuration file.')
        names.append(hydro_name)

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
            sys.exit(f'No hydrophone with serial number {serial} found in' +
                     ' configuration file.')
        hydro_list.append(hydro)

    if len(hydro_list) < 1:
        sys.exit('No hydrophones found in configuration file.')

    return hydro_list
