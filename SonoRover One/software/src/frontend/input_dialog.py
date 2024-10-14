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
from datetime import datetime
import os
import tkinter as tk

# Miscellaneous packages
import configparser
import customtkinter as ctk

import logging

# Own packages
from config.config import config_info as config
from config.logging_config import logger

from backend.input_parameters import InputParameters
import frontend.acd_param_dialog as apd
import frontend.protocol_dialog as pd


class InputDialog():
    """
    GUI dialog for setting input parameters related to protocol execution.

    Attributes:
        win (tk.Tk or None): The main tkinter window.
        not_exited_flag (bool): Flag indicating whether the dialog has not been exited.
        row_nr (int): Current row number for grid layout in the tkinter window.
        input_param (InputParameters or None): Object storing input parameters.
    """

    def __init__(self):
        """
        Initializes the InputDialog instance.
        """

        self.win = None
        self.not_exited_flag = True
        self.row_nr = 0

        self.input_param = None

        self._build_dialog()

    def _build_dialog(self):
        """
        Builds the dialog window by initializing parameters and creating GUI elements.
        """

        self._init_param()
        self._init_body()

    def _init_param(self):
        """
        Initializes input parameters, checks for cached data, and loads if available.
        """

        self.input_param = InputParameters()

        # Check if cached data exists and load if valid
        config_path = config['Characterization']['Path of input parameters cache']
        if os.path.exists(config_path):
            cached_input = configparser.ConfigParser(interpolation=None)
            cached_input.read(config_path)

            # Check if cached data exists and load if valid
            now = datetime.now()
            if cached_input['Input parameters']['Date'] == str(now.strftime("%Y/%m/%d")):
                try:
                    self.input_param.convert_ini_to_object(cached_input)
                except KeyError:
                    print('Cached data cannot be read. Use default parameters')

    def _init_body(self):
        """
        Initializes the GUI components of the dialog.
        """

        # Get input parameters from user
        try:
            self.win = ctk.CTk()
            ctk.set_appearance_mode("System")
            self.win.title('Set input parameters')

            self._create_entries()
            self._create_buttons()

            self._event_handling(None)  # perform initial event handling

            self._resize_window()

            self.win.mainloop()

        except AttributeError:
            logger.error(logging.exception('AttributeError'))
            if self.not_exited_flag:
                self.win.destroy()

    def _resize_window(self):
        """
        Resizes window according to content and displays the window on top of all windows.
        """
        # Update window to calculate required size
        self.win.update_idletasks()

        # Automatic resizing
        self.win.geometry(f"{self.win.winfo_reqwidth()}x{self.win.winfo_reqheight()}")

        # Display this window on top of all windows
        self.win.lift()
        self.win.attributes('-topmost', True)
        self.win.after(5000, lambda: self.win.attributes('-topmost', False))  # stay for 5s

    def _create_entries(self):
        """
        Creates entry fields for various input parameters.
        """

        # Path and filename of protocol excel file
        if self.input_param.is_ac_align is True:
            self.input_param.protocol = 'Acoustical alignment'
        else:
            self.input_param.protocol = self.input_param.path_protocol_excel_file

        self.path_prot = self._create_entry("Protocol",
                                            self.input_param.protocol,
                                            is_event=True, event_handling=self._event_handling,
                                            width=350)

        # Browse button to select protocol excel file
        button = ctk.CTkButton(master=self.win, text="Select", command=self._select_prot_action)
        button.grid(row=self.row_nr, column=1, padx=10, sticky="e")

        # Entry field for COM port of positioning system
        com_pos_num = self.input_param.pos_com_port.removeprefix('COM')
        self.com_pos = self._create_entry("COM port of positioning system", com_pos_num,
                                          is_event=True, event_handling=self._event_handling)
        # Dropdown for selecting hydrophone
        self.hydro_combo = self._create_combo("Hydrophone", self.input_param.hydro_names,
                                              self.input_param.hydrophone.name,
                                              self._event_handling)

        # Entry field for hydrophone acquisition time
        self.acq_time = self._create_entry("Hydrophone acquisition time [us]",
                                           self.input_param.acquisition_time,
                                           is_event=True, event_handling=self._event_handling)

        # Dropdown for selecting picoscope
        self.pico_combo = self._create_combo("PicoScope", self.input_param.pico_names,
                                             self.input_param.picoscope.name,
                                             self._event_handling)

        # Entry field for Picoscope sampling frequency multiplication factor
        self.sampl_freq = self._create_entry("Picoscope sampling frequency multiplication factor",
                                             self.input_param.sampl_freq_multi,
                                             is_event=True, event_handling=self._event_handling)

        # Entry field for temperature of water
        self.temp_ent = self._create_entry("Temperature of water [°C]", self.input_param.temp,
                                           is_event=True, event_handling=self._event_handling)

        # Entry field for dissolved oxygen level of water
        self.oxy_entry = self._create_entry("Dissolved oxygen level of water [mg/L]",
                                            self.input_param.dis_oxy,
                                            is_event=True, event_handling=self._event_handling)

        # Entry fields for coordinates
        self._create_coord_entries()

        # Checkbox for performing all protocols in sequence without waiting for user input
        self.perform_check = self._create_checkbox(
            "Perform all sequences in sequence without waiting for user input?",
            self.input_param.perform_all_seqs, is_event=True,
            event_handling=self._event_handling)

        # Error message label
        self._add_row()
        self.error_label = ctk.CTkLabel(master=self.win, text="")
        self.error_label.grid(row=self.row_nr, columnspan=2)

    def _create_coord_entries(self):
        """
        Creates one coordinate label and three entries for each x, y and z-coordinate.
        """

        self._add_row()

        label = ctk.CTkLabel(master=self.win, text="Absolute G code coordinates of relative zero" +
                             " [x, y, z]")
        label.grid(row=self.row_nr, column=0, padx=20, sticky='w')

        # Create three entries
        self.coord_entries = [None, None, None]
        orientation = ['w', '', 'e']
        for i in range(len(self.coord_entries)):
            entry = ctk.CTkEntry(master=self.win, width=150)

            entry.bind('<Return>', self._event_handling)
            entry.bind('<1>', self._event_handling)

            def_value = self.input_param.coord_zero[i]
            entry.insert(0, def_value)
            entry.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky=orientation[i])

            self.coord_entries[i] = entry

    def _create_buttons(self):
        """
        Creates Ok and Cancel buttons.
        """

        self._add_row()

        # Additional ACD processing parameters
        self.acd_button = ctk.CTkButton(master=self.win,
                                        text="Additional ACD processing parameters",
                                        command=self._acd_action)
        self.acd_button.grid(row=self.row_nr, column=0, sticky='w', ipadx=53, padx=10, pady=10)

        # Ok button
        self.ok_button = ctk.CTkButton(master=self.win, text="Ok", command=self._ok_action)
        self.ok_button.grid(row=self.row_nr, column=1, sticky='w', ipadx=53, padx=10, pady=10)
        self.ok_button.configure(state=tk.DISABLED)

        # Cancel button
        button = ctk.CTkButton(master=self.win, text="Cancel", command=self._cancel_action)
        button.grid(row=self.row_nr, column=1, sticky='e', ipadx=53, padx=10, pady=10)

    def _add_row(self):
        """
        Increments the row number for grid layout.
        """

        self.row_nr += 1

    def _create_entry(self, label_txt, def_value='', is_event=False, event_handling=None,
                      width=500, return_label=False):
        """
        Creates an entry field with a label.

        Args:
            label_txt (str): Text to display as the label.
            def_value (str or int or float): Default value to display in the entry field.
            is_event (bool): Flag indicating whether to bind events to the entry field.
            event_handling (function): Event handler function for the entry field.
            width (int): Width of the entry field.
            return_label (bool): Flag indicating whether to return the label widget.

        Returns:
            tk.Entry or (tk.Label, tk.Entry): Created entry field or label and entry field pair.
        """

        self._add_row()

        label = ctk.CTkLabel(master=self.win, text=label_txt)
        label.grid(row=self.row_nr, column=0, padx=20, sticky='w')
        entry = ctk.CTkEntry(master=self.win, width=width)

        if is_event:
            entry.bind('<Return>', event_handling)
            entry.bind('<1>', event_handling)

        entry.insert(0, def_value)
        entry.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="w")

        if return_label:
            return label, entry

        return entry

    def _create_combo(self, label_txt, value_list, def_value, combo_action):
        """
        Creates a dropdown (combobox) with a label.

        Args:
            label_txt (str): Text to display as the label.
            value_list (list): List of values for the dropdown.
            def_value (str): Default value to display in the dropdown.
            combo_action (function): Action function to call when an item in the dropdown is
                                     selected.

        Returns:
            ctk.CTkComboBox: Created combobox widget.
        """

        self._add_row()

        label = ctk.CTkLabel(master=self.win, text=label_txt)
        label.grid(row=self.row_nr, column=0, padx=20, sticky='w')
        combo = ctk.CTkComboBox(master=self.win, width=500, values=value_list, command=combo_action)

        combo.set(def_value)
        combo.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="w")

        return combo

    def _create_checkbox(self, label_txt, def_bool=True, is_event=False, event_handling=None):
        """
        Creates a checkbox with a label.

        Args:
            label_txt (str): Text to display as the label.
            def_bool (bool): Default state of the checkbox.
            is_event (bool): Flag indicating whether to bind events to the checkbox.
            event_handling (function): Event handler function for the checkbox.

        Returns:
            ctk.CTkCheckBox: Created checkbox widget.
        """

        self._add_row()

        label = ctk.CTkLabel(master=self.win, text=label_txt)
        label.grid(row=self.row_nr, column=0, padx=20, sticky='w')
        bool_int = 1 if def_bool else 0
        bool_var = tk.IntVar(value=bool_int)

        checkbox = ctk.CTkCheckBox(master=self.win, text='', variable=bool_var)

        if is_event:
            checkbox.bind('<Return>', event_handling)
            checkbox.bind('<1>', event_handling)

        checkbox.grid(row=self.row_nr, column=1, padx=100)

        return checkbox

    def _event_handling(self, event):
        """
        Performs validation of input fields and updates UI elements accordingly.
        """

        def_color = 'black'
        if ctk.get_appearance_mode() == 'Dark':
            def_color = 'white'

        error_message = self._validate_inputs()

        if error_message == '':
            self.ok_button.configure(state=tk.NORMAL)
            self.error_label.configure(
                    text=error_message,
                    text_color=def_color)
        else:
            self.ok_button.configure(state=tk.DISABLED)
            self.error_label.configure(
                    text=error_message,
                    text_color="red")

    def _validate_inputs(self):
        """
        Validates all input fields and returns error message if any field is invalid.

        Returns:
            str: Error message if validation fails, otherwise an empty string.
            str: Default text color based on appearance mode.
        """

        error_message = ''

        fields_to_validate = {
            'COM port number of positioning system': (self.com_pos, True, True, None, False),
            'hydrophone': (self.hydro_combo, False, False, None, True),
            'acquisition time': (self.acq_time, True, True, None, False),
            'picoscope': (self.pico_combo, False, False, None, True),
            'sampling frequency multiplication factor': (self.sampl_freq, True, True, None, False),
            'temperature of water': (self.temp_ent, True, True, None, False),
            'dissolved oxygen level of water': (self.oxy_entry, True, True, None, False),
            'x-coordinate': (self.coord_entries[0], True, False, None, False),
            'y-coordinate': (self.coord_entries[1], True, False, None, False),
            'z-coordinate': (self.coord_entries[2], True, False, None, False),
        }

        for field_name, (widget, is_float, check_positive, ext,
                         selected_combo) in fields_to_validate.items():
            error_message = self._check_field(error_message, widget, is_float,
                                              check_positive, field_name, ext, selected_combo)

        return error_message

    def _check_field(self, error_message, widget, is_float, check_positive, field_name, ext,
                     selected_combo):
        """
        Checks validity of a specific input field.

        Args:
            error_message (str): Current error message.
            widget (tk.Widget): Widget to validate.
            is_float (bool): Flag indicating if the field value should be float.
            check_positive (bool): Flag indicating if the field value should be positive.
            field_name (str): Name of the field being validated.
            ext (str or None): Expected file extension if the field represents a file.
            selected_combo (bool): Flag indicating if the field is a combobox. If so, it is checked
            if a value is selected.

        Returns:
            str: Updated error message.
            str: Default text color based on appearance mode.
        """

        def_color = 'black'
        if ctk.get_appearance_mode() == 'Dark':
            def_color = 'white'

        widget.configure(text_color=def_color)
        value = widget.get()

        if ext:
            path, file_ext = os.path.splitext(value)
            if file_ext not in ['.xlsx', '.xls', '.csv']:
                widget.configure(text_color="red")
                error_message += (f'Error: No {ext} file is selected.'
                                  + f' Please select a file with {ext}. \n ')
                return error_message
            if not os.path.exists(value):
                widget.configure(text_color="red")
                error_message += 'Error: File doesn\'t exist. Please change value. \n '
                return error_message
        elif selected_combo:
            if value == '':
                widget.configure(text_color="red")
                error_message += f'Error: A {field_name} must be selected. Please change value. \n '
                return error_message
        else:
            try:
                if is_float:
                    value = float(value)
                else:
                    value = int(value)
                if check_positive and value < 0:
                    widget.configure(text_color="red")
                    error_message += (f'Error: {field_name} cannot be a negative value.' +
                                      ' Please change value. \n ')
                    return error_message
                if field_name == 'sampling frequency multiplication factor' and value < 2:
                    widget.configure(text_color="red")
                    error_message += ('Error: Picoscope sampling frequency multiplication' +
                                      'factor needs to be at least 2. Please change value. \n ')
                    return error_message
            except ValueError:
                widget.configure(text_color="red")
                error_message += (f'Error: value of {field_name} is not a number or contains a ' +
                                  'comma as a decimal separator. Please change value or decimal' +
                                  ' separator. \n ')
                return error_message

        return error_message

    def _select_prot_action(self):
        prot_dialog = pd.ProtocolDialog(self.input_param, self.path_prot)
        self.input_param = prot_dialog.input_param
        
        # Define temporary and main output directories based on selected parameters
        folder_struct = f'Output of T [{self.input_param.tran.name}] - DS [{self.input_param.driving_sys.name}]'
        self.input_param.temp_dir_output = os.path.join(
            config['Characterization']['Temporary output path'], folder_struct,
            f'P [{self.input_param.protocol}]')
        self.input_param.dir_output = self.input_param.temp_dir_output

        # Create directories if they don't exist
        os.makedirs(self.input_param.temp_dir_output, exist_ok=True)
        # os.makedirs(self.input_param.dir_output, exist_ok=True)

    def _acd_action(self):
        acd_dialog = apd.ACDParamDialog(self.input_param.acd_param, self.input_param.adjust_param)
        self.input_param.acd_param = acd_dialog.acd_param

    def _ok_action(self):
        """
        Action function triggered when Ok button is clicked. Saves valid input parameters.
        """

        if self.win:
            self.input_param.pos_com_port = f'COM{self.com_pos.get()}'

            # Save selected hydrophone object
            hydro_name = self.hydro_combo.get()
            for hydro in self.input_param.hydro_list:
                if hydro.name == hydro_name:
                    self.input_param.hydrophone = hydro

            self.input_param.acquisition_time = float(self.acq_time.get())

            # Save selected PicoScope object
            pico_name = self.pico_combo.get()
            for pico in self.input_param.pico_list:
                if pico.name == pico_name:
                    self.input_param.picoscope = pico

            self.input_param.sampl_freq_multi = float(self.sampl_freq.get())

            self.input_param.temp = float(self.temp_ent.get())
            self.input_param.dis_oxy = float(self.oxy_entry.get())
            self.input_param.coord_zero = [float(self.coord_entries[0].get()),
                                           float(self.coord_entries[1].get()),
                                           float(self.coord_entries[2].get())]
            self.input_param.perform_all_seqs = self.perform_check.get() == 1

            # Cache data by writing to ini file
            self.input_param.write_to_ini()

            # Close the dialog
            self._cancel_action()

    def _cancel_action(self):
        """
        Action function triggered when Cancel button is clicked.
        Closes the input dialog.
        """

        if self.not_exited_flag:
            self.not_exited_flag = False
            self.win.destroy()
