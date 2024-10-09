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
import tkinter as tk

# Miscellaneous packages
import customtkinter as ctk

import logging

# Own packages
from config.config import config_info as config
from config.logging_config import logger

from backend import sequence


class ProtocolDialog():
    """
    GUI dialog for setting additional ACD procesing parameters.

    Attributes:
        win (tk.Tk or None): The main tkinter window.
        not_exited_flag (bool): Flag indicating whether the dialog has not been exited.
        row_nr (int): Current row number for grid layout in the tkinter window.
        acd_param (dict): Dictionary storing ACD processing parameters.
    """

    def __init__(self, input_param, prot_entry):
        """
        Initializes the ProtocolDialog instance.
        """

        self.win = None
        self.main_prot_entry = prot_entry
        self.not_exited_flag = True
        self.row_nr = 0

        self.input_param = input_param

        if not self.input_param.sequences:
            self.ac_align_seq = sequence.CharacSequence()
        else:
            if len(self.input_param.sequences) > 1:
                logger.error('Handling a regular sequence collected by the GUI has not been implemented yet.')

            self.ac_align_seq = self.input_param.sequences[0]

        self.n_ac_align_rows = 14

        self._build_dialog()

    def _build_dialog(self, extra_button=False):
        """
        Initializes the GUI components of the dialog.
        """

        # Get input parameters from user
        try:
            self.win = ctk.CTk()
            ctk.set_appearance_mode("System")
            self.win.title('Choose protocol')

            self._create_us_equip_entries()

            self._create_buttons()

            #self._event_handling(None)  # perform initial event handling

            self._resize_window()

            self.win.mainloop()

        except AttributeError:
            print(logging.exception('AttributeError'))
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

    def _create_us_equip_entries(self):
        # Dropdown for selecting US Driving System
        self.ds_combo = self._create_combo("US Driving System", self.input_param.ds_names,
                                           self.input_param.driving_sys.name,
                                           self._ds_combo_action)

        # Entry field for COM port of US driving system if applicable
        com_us_num = self.input_param.driving_sys.connect_info.removeprefix('COM')
        self.com_us_label, self.com_us = self._create_entry(
            "COM port of US driving system", com_us_num, is_event=True,
            event_handling=self._event_handling, return_label=True)

        self.com_us_label.grid()
        self.com_us.grid()

        # Save location for the entry, but hide it when other equipment is chosen
        if not self.input_param.is_ds_com_port:
            self.com_us_label.grid_remove()
            self.com_us.grid_remove()

        # Dropdown for selecting transducer
        self.trans_combo = self._create_combo("Transducer", self.input_param.tran_names,
                                              self.input_param.tran.name,
                                              self._trans_combo_action)

        # Entry field for operating frequency
        self.oper_freq_entr = self._create_entry("Operating frequency [kHz]",
                                                 int(self.input_param.oper_freq),
                                                 is_event=True, event_handling=self._event_handling)

        # Protocol
        # TODO: add to config
        self.protocols = ['Select protocol excel file...', 'Acoustical alignment']
        if self.input_param.is_ac_align is False:
            self.chosen_prot = self.protocols[0]
        else:
            self.chosen_prot = self.protocols[1]

        self.prot_combo = self._create_combo("Protocol", self.protocols, self.chosen_prot,
                                             self._prot_combo_action)

        # Path and filename of protocol excel file
        self.path_prot = self._create_entry("Path and filename of protocol excel file",
                                            self.input_param.path_protocol_excel_file,
                                            is_event=True, event_handling=self._event_handling,
                                            width=350)

        # Browse button to select protocol excel file
        button = ctk.CTkButton(master=self.win, text="Browse", command=self._get_filename)
        button.grid(row=self.row_nr, column=1, padx=10, sticky="e")

        # Save row where to insert additional entries
        self.insert_row = self.row_nr

        self._prot_combo_action(None)

        # Error message label
        self._add_row()
        self.error_label = ctk.CTkLabel(master=self.win, text="")
        self.error_label.grid(row=self.row_nr, columnspan=2)

    def _create_ac_align_entries(self):
        """
        Creates entry fields for various ACD processing parameters.
        """

        start_row = self.row_nr

        # Define processing window
        self.pulse_dur = self._create_entry("Pulse duration [us]",
                                            self.ac_align_seq.pulse_dur*1000,
                                            is_event=True, event_handling=self._event_handling,
                                            width=500)

        self.pulse_rep_int = self._create_entry("Pulse repetition interval [ms]",
                                                self.ac_align_seq.pulse_rep_int,
                                                is_event=True, event_handling=self._event_handling,
                                                width=500)

        # TODO: add to config
        self.igt_power_options = ["Max. pressure in free water [MPa]", "Voltage [V]", "Amplitude [%]"]
        self.sc_power_options = ["Global power [mW]"]
        power_options = self.igt_power_options + self.sc_power_options

        # TODO: connect this part to ds_combo action
        # cur_ds_system = self.ds_combo.get()
        # for ds in self.input_param.ds_list:
        #     if ds.name == cur_ds_system:
        #         self.input_param.driving_sys = ds

        # # TODO: update this when ds is changed
        # ds_manufact = str(self.input_param.driving_sys.manufact)
        # if ds_manufact == config['Equipment.Manufacturer.SC']['Name']:
        #     power_options = self.sc_power_options

        # elif ds_manufact == config['Equipment.Manufacturer.IGT']['Name']:
        #     power_options = self.igt_power_options

        if not self.input_param.sequences:
            def_power = power_options[0]
            def_power_value = 0
        else:
            if len(self.input_param.sequences) > 1:
                logger.error('Handling a regular sequence collected by the GUI has not been implemented yet.')

            seq = self.input_param.sequences[0]

            def_power = seq.chosen_power
            if seq.chosen_power == "Global power [mW]":
                def_power = "Global power [mW]"
                def_power_value = seq.global_power
            elif seq.chosen_power == "Max. pressure in free water [MPa]":
                def_power_value = seq.press
            elif seq.chosen_power == "Voltage [V]":
                def_power_value = seq.volt
            elif seq.chosen_power == "Amplitude [%]":
                def_power_value = seq.ampl

        self.power_combo = self._create_combo("Power setting", power_options, def_power,
                                              self._event_handling, width=240)

        self.power_entry = ctk.CTkEntry(master=self.win, width=240)

        self.power_entry.bind('<Return>', self._event_handling)
        self.power_entry.bind('<1>', self._event_handling)

        # TODO: default power entry
        self.power_entry.insert(0, def_power_value)
        self.power_entry.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="e")

        self.focus = self._create_entry("Focus [mm]",
                                        self.ac_align_seq.focus,
                                        is_event=True, event_handling=self._event_handling,
                                        width=500)

        self.focus_dist = self._create_entry("Distance from focus [mm]",
                                             self.ac_align_seq.ac_align['distance_from_foc'],
                                             is_event=True, event_handling=self._event_handling,
                                             width=500)

        self.init_line_len = self._create_entry("Initial line length [mm]",
                                                self.ac_align_seq.ac_align['init_line_len'],
                                                is_event=True, event_handling=self._event_handling,
                                                width=500)

        self.init_line_step = self._create_entry("Initial line stepsize [mm]",
                                                 self.ac_align_seq.ac_align['init_line_step'],
                                                 is_event=True,
                                                 event_handling=self._event_handling,
                                                 width=500)

        self.init_threshold = self._create_entry("Initial threshold [mm]",
                                                 self.ac_align_seq.ac_align['init_threshold'],
                                                 is_event=True, event_handling=self._event_handling,
                                                 width=500)

        self.reduc_factor = self._create_entry("Reduction factor [-]",
                                               self.ac_align_seq.ac_align['reduction_factor'],
                                               is_event=True, event_handling=self._event_handling,
                                               width=500)

        self.max_red_iter = self._create_entry("Maximum amount of reduction iterations",
                                               self.ac_align_seq.ac_align['max_red_iter'],
                                               is_event=True, event_handling=self._event_handling,
                                               width=500)

        self.create_graphs = self._create_checkbox("Create graphs of every line measurement",
                                                   self.ac_align_seq.ac_align['create_graphs'],
                                                   True, self._event_handling)

        self.create_axis_file = self._create_checkbox("Create axial measurement coordinate file",
                                                      self.ac_align_seq.ac_align['create_axis_file'],
                                                      True, self._event_handling)

        # TODO: create self._create_axis_file_combo to enable/disable below entries

        self.axial_len_label, self.axial_len = self._create_entry("Length of axial measurement [mm]",
                                                                  self.ac_align_seq.ac_align['axis_length'],
                                                                  is_event=True, event_handling=self._event_handling,
                                                                  width=500, return_label=True)

        self.axial_step_label, self.axial_step = self._create_entry("Stepsize of axial measurement [mm]",
                                                                    self.ac_align_seq.ac_align['axis_stepsize'],
                                                                    is_event=True, event_handling=self._event_handling,
                                                                    width=500, return_label=True)

        end_row = self.row_nr

        self.n_ac_align_rows = end_row - start_row

        # TODO: enable/disable based on checkbox
        # Save location for the entry, but hide it when false
        # if not self.ac_align_seq.ac_align['create_axis_file']:
        #     self.axial_len_label.grid_remove()
        #     self.axial_len.grid_remove()

        #     self.axial_step_label.grid_remove()
        #     self.axial_step.grid_remove()

        #     self.n_ac_align_rows = self.n_ac_align_rows - 2

    def _create_buttons(self):
        """
        Creates Ok and Cancel buttons.
        """

        self._add_row()

        # Ok button
        self.ok_button = ctk.CTkButton(master=self.win, text="Ok", command=self._ok_action)
        self.ok_button.grid(row=self.row_nr, column=0, sticky='w', ipadx=53, padx=10, pady=10)
        # TODO: Change to DISABLED when validating values
        self.ok_button.configure(state=tk.NORMAL)

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

    def _create_combo(self, label_txt, value_list, def_value, combo_action, width=500):
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
        combo = ctk.CTkComboBox(master=self.win, width=width, values=value_list,
                                command=combo_action)

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

                    self.com_us.delete(0, tk.END)
                    com_us_num = ds.connect_info.removeprefix('COM')
                    self.com_us.insert(0, com_us_num)

                    self.com_us_label.grid()
                    self.com_us.grid()

                    self._resize_window()

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

    def _prot_combo_action(self, event):

        # First, remove any previously inserted widgets in the specific row range
        if self.row_nr >= self.insert_row + self.n_ac_align_rows - 1:
            for widget in self.win.grid_slaves():
                if self.insert_row <= widget.grid_info()['row'] < self.insert_row + self.n_ac_align_rows:
                    widget.destroy()

            # Shift widgets below insert_row up by self.n_ac_align_rows row
            for widget in self.win.grid_slaves():
                current_row = widget.grid_info()['row']
                if current_row > self.insert_row:
                    widget.grid(row=current_row - self.n_ac_align_rows, column=widget.grid_info()['column'])
        else:
            for widget in self.win.grid_slaves():
                if self.insert_row <= widget.grid_info()['row'] < self.insert_row + 1:
                    widget.destroy()

            # Shift widgets below insert_row up by one row
            for widget in self.win.grid_slaves():
                current_row = widget.grid_info()['row']
                if current_row > self.insert_row:
                    widget.grid(row=current_row - 1, column=widget.grid_info()['column'])

        # Define row_nr of previous widget
        self.row_nr = self.insert_row - 1

        cur_prot = self.prot_combo.get()

        # Protocols[0]: Select protocol excel file...
        if cur_prot == self.protocols[0]:
            self.input_param.is_ac_align = False

            # Shift widgets below this point down by updating their grid positions
            for widget in self.win.grid_slaves():
                if widget.grid_info()['row'] >= self.insert_row:
                    widget.grid(row=widget.grid_info()['row'] + 1, column=widget.grid_info()['column'])

            # Path and filename of protocol excel file
            self.path_prot = self._create_entry("Path and filename of protocol excel file",
                                                self.input_param.path_protocol_excel_file,
                                                is_event=True, event_handling=self._event_handling,
                                                width=350)

            # Browse button to select protocol excel file
            button = ctk.CTkButton(master=self.win, text="Browse", command=self._get_filename)
            button.grid(row=self.row_nr, column=1, padx=10, sticky="e")

        # Protocols[1]: acoustical alignment
        elif cur_prot == self.protocols[1]:
            self.input_param.is_ac_align = True

            # Shift widgets below this point down by updating their grid positions
            for widget in self.win.grid_slaves():
                if widget.grid_info()['row'] >= self.insert_row:
                    widget.grid(row=widget.grid_info()['row'] + self.n_ac_align_rows, column=widget.grid_info()['column'])

            self._create_ac_align_entries()

        self._resize_window()

    def _get_filename(self):
        """
        Opens a file dialog to select a filename and updates the corresponding entry field.
        """

        filename = tk.filedialog.askopenfilename(
            initialdir=self.input_param.path_protocol_excel_file,
            filetypes=[('Excel files', '*.xlsx')])

        self.path_prot.delete(0, tk.END)
        self.path_prot.insert(0, filename)

        # Lift window
        self._resize_window()

        #self._event_handling(None)

    def _event_handling(self, event):
        """
        Performs validation of input fields and updates UI elements accordingly.
        """

        def_color = 'black'
        if ctk.get_appearance_mode() == 'Dark':
            def_color = 'white'

        # error_message = self._validate_inputs()

        # if error_message == '':
        #     self.ok_button.configure(state=tk.NORMAL)
        #     self.error_label.configure(
        #             text=error_message,
        #             text_color=def_color)
        # else:
        #     self.ok_button.configure(state=tk.DISABLED)
        #     self.error_label.configure(
        #             text=error_message,
        #             text_color="red")

    def _validate_inputs(self):
        """
        Validates all input fields and returns error message if any field is invalid.

        Returns:
            str: Error message if validation fails, otherwise an empty string.
            str: Default text color based on appearance mode.
        """

        error_message = ''

        fields_to_validate = {
            'path_protocol_excel_file': (self.path_prot, False, False, '.xlsx or .xls extension',
                                         False),
            'driving system': (self.ds_combo, False, False, None, True),
            'transducer': (self.trans_combo, False, False, None, True),
            'operating frequency': (self.oper_freq_entr, True, True, None, False),
        }

        if self.input_param.is_ds_com_port:
            fields_to_validate.update({'COM port number of driving system':
                                       (self.com_us, True, True, None, False)})

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
                                  + ' Please select a file with {ext}. \n ')
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

    def _ok_action(self):
        """
        Action function triggered when Ok button is clicked. Saves valid input parameters.
        """

        if self.win:
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

            # Save numeric and boolean parameters
            self.input_param.oper_freq = int(self.oper_freq_entr.get())

            # Save COM port of US driving system if applicable
            if self.input_param.is_ds_com_port:
                self.input_param.driving_sys.connect_info = f'COM{self.com_us.get()}'

            # Global characterization parameters
            self.ac_align_seq.driving_sys = self.input_param.driving_sys.serial
            self.ac_align_seq.transducer = self.input_param.tran.serial
            self.ac_align_seq.oper_freq = self.input_param.oper_freq  # [kHz]

            chosen_prot = self.prot_combo.get()
            if chosen_prot == 'Select protocol excel file...':
                self.input_param.is_ac_align = False

                # Save protocol file path and main directory
                self.input_param.path_protocol_excel_file = self.path_prot.get()
                self.input_param.main_dir = os.path.dirname(self.input_param.path_protocol_excel_file)
                self.input_param.protocol = self.input_param.path_protocol_excel_file

                self.ac_align_seq.is_ac_align = False

            else:
                self.input_param.protocol = 'Acoustical alignment'
                self.input_param.is_ac_align = True
                self.ac_align_seq.is_ac_align = True

                self.ac_align_seq.pulse_dur = abs(float(self.pulse_dur.get()))/1e3  # [us] to [ms]
                self.ac_align_seq.pulse_rep_int = abs(float(self.pulse_rep_int.get()))  # [ms]
                self.ac_align_seq.pulse_train_dur = self.ac_align_seq.pulse_rep_int
                self.ac_align_seq.pulse_train_rep_int = self.ac_align_seq.pulse_rep_int
                self.ac_align_seq.pulse_train_rep_dur = self.ac_align_seq.pulse_rep_int/1000  # [s]

                chosen_power = self.power_combo.get()
                # TODO: add chosen powers to config
                if chosen_power == "Global power [mW]":
                    self.ac_align_seq.global_power = abs(float(self.power_entry.get()))/1000  # SC: gp [W]
                elif chosen_power == "Max. pressure in free water [MPa]":
                    self.ac_align_seq.press = abs(float(self.power_entry.get()))
                elif chosen_power == "Voltage [V]":
                    self.ac_align_seq.volt = abs(float(self.power_entry.get()))
                elif chosen_power == "Amplitude [%]":
                    self.ac_align_seq.ampl = abs(float(self.power_entry.get()))

                self.ac_align_seq.focus = abs(float(self.focus.get()))

                # Assign the values from the input fields to the ac_align parameters
                # Parse float entries from entry fields
                self.ac_align_seq.ac_align['distance_from_foc'] = abs(float(self.focus_dist.get()))
                self.ac_align_seq.ac_align['init_line_len'] = abs(float(self.init_line_len.get()))
                self.ac_align_seq.ac_align['init_line_step'] = abs(float(self.init_line_step.get()))
                self.ac_align_seq.ac_align['init_threshold'] = abs(float(self.init_threshold.get()))

                # Parse float entry for reduction factor
                self.ac_align_seq.ac_align['reduction_factor'] = abs(float(self.reduc_factor.get()))

                # Parse integer entry for maximum reduction iterations
                self.ac_align_seq.ac_align['max_red_iter'] = int(self.max_red_iter.get())

                # Parse boolean values from checkboxes
                self.ac_align_seq.ac_align['create_graphs'] = self.create_graphs.get() == 1
                self.ac_align_seq.ac_align['create_axis_file'] = self.create_axis_file.get() == 1

                # Parse float entries for axis length and stepsize
                self.ac_align_seq.ac_align['axis_length'] = abs(float(self.axial_len.get()))
                self.ac_align_seq.ac_align['axis_stepsize'] = abs(float(self.axial_step.get()))

                if self.input_param.is_ac_align is False:
                    # Extract protocol excel filename without extension
                    self.input_param.protocol = os.path.splitext(
                        os.path.basename(self.input_param.path_protocol_excel_file))[0]

            self.input_param.sequences = [self.ac_align_seq]

            self.main_prot_entry.delete(0, tk.END)
            self.main_prot_entry.insert(0, self.input_param.protocol)

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
