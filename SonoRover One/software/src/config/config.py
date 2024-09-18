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
import configparser
from importlib import resources as impresources

# Own packages
import config


# Initialize ConfigParser
config_info = configparser.ConfigParser(interpolation=None)


def read_config(file_path):
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Configuration file '{abs_path}' not found.")
    config_info.read(abs_path)


def read_additional_config(file_path):
    additional_config = configparser.ConfigParser(interpolation=None)
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Configuration file '{abs_path}' not found.")
    additional_config.read(abs_path)
    
    # Iterate through the sections and options
    for section in additional_config.sections():
        if not config_info.has_section(section):
            config_info.add_section(section)
        
        for option, value in additional_config.items(section):
            if not config_info.has_option(section, option):
                config_info.set(section, option, value)
            else:
                # Optionally, handle merging or appending here if needed
                existing_value = config_info.get(section, option)
                config_info.set(section, option, f"{existing_value}, {value}")

# Automatically read the main configuration file when the module is imported
inp_file = (impresources.files(config) / 'characterization_config.ini')
read_config(inp_file)
