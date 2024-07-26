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

# Own packages
from config.config import config_info as config

from backend.input_parameters import InputParameters


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
            cached_input = configparser.ConfigParser()
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
            self.win.geometry("920x645")
            self.win.title('Set input parameters')

            self._create_entries()
            self._create_buttons()

            self._event_handling(None)  # perform initial event handling

            self.win.lift()
            self.win.mainloop()

        finally:
            if self.not_exited_flag:
                self.win.destroy()

    def _create_entries(self):
        """
        Creates entry fields for various input parameters.
        """

        # Path and filename of protocol excel file
        self.path_prot = self._create_entry("Path and filename of protocol excel file",
                                            self.input_param.path_protocol_excel_file,
                                            is_event=True, event_handling=self._event_handling,
                                            width=350)

        # Browse button to select protocol excel file
        button = ctk.CTkButton(master=self.win, text="Browse", command=self._get_filename)
        button.grid(row=self.row_nr, column=1, sticky="e")

        # Dropdown for selecting US Driving System
        self.ds_combo = self._create_combo("US Driving System", self.input_param.ds_names,
                                           self.input_param.driving_sys.name,
                                           self._ds_combo_action)

        # Dropdown for selecting transducer
        self.trans_combo = self._create_combo("Transducer", self.input_param.tran_names,
                                              self.input_param.tran.name,
                                              self._trans_combo_action)

        # Entry field for operating frequency
        self.oper_freq_entr = self._create_entry("Operating frequency [kHz]",
                                                 int(self.input_param.oper_freq),
                                                 is_event=True, event_handling=self._event_handling)

        # Entry field for COM port of US driving system if applicable
        if self.input_param.is_ds_com_port:
            com_us_num = self.input_param.driving_sys.connect_info.removeprefix('COM')
            self.com_us_label, self.com_us = self._create_entry(
                "COM port of US driving system", com_us_num, is_event=True,
                event_handling=self._event_handling, return_label=True)

            self.com_us_label.grid()
            self.com_us.grid()

        # Entry field for COM port of positioning system
        com_pos_num = self.input_param.pos_com_port.removeprefix('COM')
        self.com_pos = self._create_entry("COM port of positioning system", com_pos_num,
                                          is_event=True, event_handling=self._event_handling)

        # Entry field for hydrophone acquisition time
        self.acq_time = self._create_entry("Hydrophone acquisition time [us]",
                                           self.input_param.acquisition_time,
                                           is_event=True, event_handling=self._event_handling)

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
        self.x_coord = self._create_entry("Absolute G code x-coordinate of relative zero",
                                          self.input_param.coord_zero[0],
                                          is_event=True, event_handling=self._event_handling)

        self.y_coord = self._create_entry("Absolute G code y-coordinate of relative zero",
                                          self.input_param.coord_zero[1],
                                          is_event=True, event_handling=self._event_handling)

        self.z_coord = self._create_entry("Absolute G code z-coordinate of relative zero",
                                          self.input_param.coord_zero[2],
                                          is_event=True, event_handling=self._event_handling)

        # Checkbox for performing all protocols in sequence without waiting for user input
        self.perform_check = self._create_checkbox(
            "Perform all sequences in sequence without waiting for user input?",
            self.input_param.perform_all_seqs, is_event=True,
            event_handling=self._event_handling)

        # Error message label
        self._add_row()
        self.error_label = ctk.CTkLabel(master=self.win, text="")
        self.error_label.grid(row=self.row_nr, columnspan=2)

    def _create_buttons(self):
        """
        Creates Ok and Cancel buttons.
        """

        self._add_row()

        # Ok button
        self.ok_button = ctk.CTkButton(master=self.win, text="Ok", command=self._ok_action)
        self.ok_button.grid(row=self.row_nr, column=1, sticky='w', ipadx=53)
        self.ok_button.configure(state=tk.DISABLED)

        # Cancel button
        button = ctk.CTkButton(master=self.win, text="Cancel", command=self._cancel_action)
        button.grid(row=self.row_nr, column=1, sticky='e', ipadx=53)

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
        entry.grid(row=self.row_nr, column=1, pady=5, sticky="w")

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
        combo.grid(row=self.row_nr, column=1, pady=5, sticky="w")

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

    def _get_filename(self):
        """
        Opens a file dialog to select a filename and updates the corresponding entry field.
        """

        filename = tk.filedialog.askopenfilename(
            initialdir=self.input_param.path_protocol_excel_file,
            filetypes=[('Excel files', '*.xlsx')])

        self.path_prot.delete(0, tk.END)
        self.path_prot.insert(0, filename)

        self._event_handling(None)

    def _ds_combo_action(self, event):
        """
        Action function triggered when a new driving system is selected from the dropdown.
        Updates related fields and performs event handling.
        """

        cur_ds = self.ds_combo.get()

        for ds in self.input_param.ds_list:
            if ds.name == cur_ds:
                if 'COM' in ds.connect_info:
                    self.input_param.is_ds_com_port = True

                    self.com_us_label.grid()
                    self.com_us.grid()
                else:
                    self.input_param.is_ds_com_port = False

                    if hasattr(self, 'com_us'):
                        self.com_us_label.grid_remove()
                        self.com_us.grid_remove()

        self._event_handling(event)

    def _trans_combo_action(self, event):
        """
        Action function triggered when a new transducer is selected from the dropdown.
        Updates related fields and performs event handling.
        """

        new_tran_name = self.trans_combo.get()

        for tran in self.input_param.tran_list:
            if tran.name == new_tran_name:
                self.oper_freq_entr.delete(0, tk.END)
                self.oper_freq_entr.insert(0, int(tran.fund_freq))

        self._event_handling(event)

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
            'path_protocol_excel_file': (self.path_prot, False, False, '.xlsx or .xls extension'),
            'driving system': (self.ds_combo, False, False, None),
            'transducer': (self.trans_combo, False, False, None),
            'operating frequency': (self.oper_freq_entr, True, True, None),
            'COM port number of positioning system': (self.com_pos, True, True, None),
            'acquisition time': (self.acq_time, True, True, None),
            'sampling frequency multiplication factor': (self.sampl_freq, True, True, None),
            'temperature of water': (self.temp_ent, True, True, None),
            'dissolved oxygen level of water': (self.oxy_entry, True, True, None),
            'x-coordinate': (self.x_coord, True, False, None),
            'y-coordinate': (self.y_coord, True, False, None),
            'z-coordinate': (self.z_coord, True, False, None),
        }

        if self.input_param.is_ds_com_port:
            fields_to_validate.update({'COM port number of driving system':
                                       (self.com_us, True, True, None)})

        for field_name, (widget, is_float, check_positive, ext) in fields_to_validate.items():
            error_message = self._check_field(error_message, widget, is_float,
                                              check_positive, field_name, ext)

        return error_message

    def _check_field(self, error_message, widget, is_float, check_positive, field_name, ext):
        """
        Checks validity of a specific input field.

        Args:
            error_message (str): Current error message.
            widget (tk.Widget): Widget to validate.
            is_float (bool): Flag indicating if the field value should be float.
            check_positive (bool): Flag indicating if the field value should be positive.
            field_name (str): Name of the field being validated.
            ext (str or None): Expected file extension if the field represents a file.

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
                                  + ' Please select a file with {ext}. \n ')
                return error_message
            if not os.path.exists(value):
                widget.configure(text_color="red")
                error_message += 'Error: File doesn\'t exist. Please change value. \n '
                return error_message
        elif field_name in ['driving system', 'transducer']:
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

    def _ok_action(self):
        """
        Action function triggered when Ok button is clicked. Saves valid input parameters.
        """

        if self.win:
            # Save protocol file path and main directory
            self.input_param.path_protocol_excel_file = self.path_prot.get()
            self.input_param.main_dir = os.path.dirname(self.input_param.path_protocol_excel_file)

            # Save selected driving system object
            ds_name = self.ds_combo.get()
            for ds in self.input_param.ds_list:
                if ds.name == ds_name:
                    self.input_param.driving_sys = ds

            # Save selected transducer object
            td_name = self.trans_combo.get()
            for tran in self.input_param.tran_list:
                if tran.name == td_name:
                    self.input_param.tran = tran

            # Extract protocol excel filename without extension
            protocol_excel_filename = os.path.splitext(
                os.path.basename(self.input_param.path_protocol_excel_file))[0]

            # Define temporary and main output directories based on selected parameters
            folder_struct = f'Output of T [{td_name}] - DS [{ds_name}]'
            self.input_param.temp_dir_output = os.path.join(
                config['Characterization']['Temporary output path'], folder_struct,
                f'P [{protocol_excel_filename}]')
            self.input_param.dir_output = os.path.join(self.input_param.main_dir, folder_struct,
                                                       f'P [{protocol_excel_filename}]')

            # Create directories if they don't exist
            os.makedirs(self.input_param.temp_dir_output, exist_ok=True)
            os.makedirs(self.input_param.dir_output, exist_ok=True)

            # Save numeric and boolean parameters
            self.input_param.oper_freq = int(self.oper_freq_entr.get())

            # Save COM port of US driving system if applicable
            if self.input_param.is_ds_com_port:
                self.input_param.driving_sys.connect_info = f'COM{self.com_us.get()}'

            self.input_param.pos_com_port = f'COM{self.com_pos.get()}'
            self.input_param.acquisition_time = float(self.acq_time.get())
            self.input_param.sampl_freq_multi = float(self.sampl_freq.get())
            self.input_param.temp = float(self.temp_ent.get())
            self.input_param.dis_oxy = float(self.oxy_entry.get())
            self.input_param.coord_zero = [float(self.x_coord.get()), float(self.y_coord.get()),
                                           float(self.z_coord.get())]
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
            self.win.quit()
