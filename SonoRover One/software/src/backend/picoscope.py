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


class PicoScope:
    """
    Class representing a PicoScope.

    Attributes:
        serial (str): Serial number of the PicoScope.
        name (str): Name of the PicoScope.
        pico_py_ident (str): Pico.py identification name.
    """

    def _init__(self):
        """
        Initializes a PicoScope object with default values.
        """

        self.serial = None
        self.name = None
        self.pico_py_ident = None

    def set_pico_info(self, serial):
        """
        Sets the PicoScope based on the provided serial number.

        Parameters:
            serial (str): Serial number of the PicoScope.
        """

        try:
            self.serial = serial
            self.name = config['Characterization.Equipment.' + serial]['Name']
            self.pico_py_ident = (config['Characterization.Equipment.' + serial]
                                  ['Pico.py identification'])
        except KeyError:
            sys.exit(f'No PicoScope with serial number {serial} found in configuration file.')

    def __str__(self):
        """
        Returns a formatted string containing information about the PicoScope.

        Returns:
            str: Formatted information about the PicoScope.
        """

        info = ''
        info += f"PicoScope serial number: {self.serial} \n "
        info += f"PicoScope name: {self.name} \n "
        info += f"PicoScope pico.py identification: {self.pico_py_ident} \n "

        return info


def get_pico_serials():
    """
    Returns a list of serial numbers for available PicoScopes.

    Returns:
        List[str]: Serial numbers for available PicoScopes.
    """

    pico_serial = config['Characterization.Equipment']['PicoScopes'].split(', ')

    return pico_serial


def get_pico_names():
    """
    Returns a list of names for available PicoScopes.

    Returns:
        List[str]: Names for available PicoScopes.
    """

    names = []
    for serial in get_pico_serials():
        try:
            pico_name = config['Characterization.Equipment.' + serial]['Name']
        except KeyError:
            sys.exit(f'No PicoScope with serial number {serial} found in' +
                     ' configuration file.')
        names.append(pico_name)

    return names


def get_pico_list():
    """
    Returns a list of available PicoScopes.

    Returns:
        List[Obj]: Objects of available PicoScopes.
    """

    pico_list = []
    for serial in get_pico_serials():
        try:
            pico = PicoScope()
            pico.set_pico_info(serial)
        except KeyError:
            sys.exit(f'No PicoScope with serial number {serial} found in' +
                     ' configuration file.')
        pico_list.append(pico)

    if len(pico_list) < 1:
        sys.exit('No PicoScopes found in configuration file.')

    return pico_list