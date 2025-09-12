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

import sys
import inspect
from distutils.dir_util import copy_tree
from pathlib import Path
import shutil


def get_config_value(logger, config, section, key, default, isSysExit=False):
    """
    Retrieve a configuration value from a given section and key.

    If the section or key is missing, logs a warning and returns the default value.

    Parameters:
    - logger (logging.Logger): The logger instance to log warnings.
    - config (configparser.ConfigParser): The configuration parser object.
    - section (str): The section in the configuration file.
    - key (str): The key within the section to retrieve.
    - default (any): The default value to return if the section or key is missing.

    Returns:
    - any: The retrieved value or the default if missing.
    """

    # Function to log the warning message with additional context (caller function details)
    def log_warning(message):
        # Get the stack and retrieve information about the caller (the function that called get_config_value)
        stack = inspect.stack()
        caller_frame = stack[2]  # The function that called get_config_value is two levels up
        file_name = caller_frame.filename  # File name of the caller
        line_number = caller_frame.lineno  # Line number of the caller
        function_name = caller_frame.function  # Function name of the caller

        # Add file, line, and function information to the message
        message = (f"{message}, using default: {default} "
                   f"(called from {file_name}, {function_name} at line {line_number})")

        # Log the warning
        if logger is None:
            print(message)
        else:
            logger.warning(message)

    # Check if the config is None
    if config is None:
        message = "Config not found"
        if isSysExit:
            sys.exit(message)

        log_warning(message)
        return default

    # Check if the section exists in the config
    if section not in config:
        message = f"Config section '{section}' not found"
        if isSysExit:
            sys.exit(message)

        log_warning(message)
        return default

    # Check if the key exists in the section
    if key not in config[section]:
        message = f"Config key '{key}' not found in section '{section}'"
        if isSysExit:
            sys.exit(message)

        log_warning(message)
        return default

    # Return the config value if found
    return config[section][key]


def get_config_folder():
    """
    Returns the configuration folder name.
    """

    return "config"


def get_charac_config_file():
    """
    Returns the configuration file name.
    """

    return "characterization_config.ini"


def get_pcd_config_file():
    """
    Returns the configuration file name.
    """

    return "pcd_config.ini"


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
        logger.error(f'\n WARNING! \n \n Moving output files failed: {e}. Output files can be found in {from_dir}.')
        print(f'\n WARNING! \n \n Moving output files failed: {e}. Output files can be found in {from_dir}.')


def check_attribute(logger, obj, attr):
    """
    Check whether an object has a given attribute and log a warning if it does not.

    Args:
        logger (logging.Logger): Logger instance used to issue warnings.
        obj (object): The object to inspect.
        attr (str): The attribute name to check for.
    """

    if hasattr(obj, attr):
        return True
    else:
        logger.warning(f'Object {obj.__class__.__name__} has no attribute called {attr}. ' +
                       'Parameter is not logged.')
        return False
