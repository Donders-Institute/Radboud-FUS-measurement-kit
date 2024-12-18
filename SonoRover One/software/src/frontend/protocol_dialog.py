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

    def __init__(self, root_win, input_param, prot_entry):
        """
        Initializes the ProtocolDialog instance.
        """

        self.root_win = root_win
        self.win = None
        self.main_prot_entry = prot_entry
        self.row_nr = 0

        self.input_param = input_param

        self._equip_combos = config['Equipment']['Combinations'].split('\n')
        self._ds_tran_combo = '~'.join([self.input_param.driving_sys.serial,
                                        self.input_param.tran.serial])

        self.focus_wrt_exit_plane_array = []
        self.focus_wrt_mid_bowl_array = []
        if not self.input_param.sequences:
            self.ac_align_seq = sequence.CharacSequence()
            self.focus_wrt_exit_plane_array.append(self.ac_align_seq.focus_wrt_exit_plane)
            self.focus_wrt_mid_bowl_array.append(self.ac_align_seq.focus_wrt_mid_bowl)
        else:
            # Use first sequence to set all parameters
            self.ac_align_seq = self.input_param.sequences[0]

            # Use all sequences to extract the focus array

            for seq in self.input_param.sequences:
                self.focus_wrt_exit_plane_array.append(seq.focus_wrt_exit_plane)
                self.focus_wrt_mid_bowl_array.append(seq.focus_wrt_mid_bowl)

        self.n_ac_align_rows = 14

        self._build_dialog()

    def _build_dialog(self, extra_button=False):
        """
        Initializes the GUI components of the dialog.
        """

        # Get input parameters from user
        try:
            # Block main window until action within subdialog is finished
            self.win = ctk.CTkToplevel(self.root_win)
            self.win.grab_set()

            ctk.set_appearance_mode("System")
            self.win.title('Choose protocol')

            self._create_us_equip_entries()

            self._create_buttons()

            self._event_handling(None)  # perform initial event handling

            self._resize_window()

            self.win.mainloop()

        except AttributeError:
            print(logging.exception('AttributeError'))
            self._cancel_action()

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

        # Update conversion coefficients according to chosen equipment
        self._ds_tran_combo = '~'.join([self.input_param.driving_sys.serial,
                                        self.input_param.tran.serial])

        if self._ds_tran_combo in self._equip_combos:
            # TODO: fix private func
            self.ac_align_seq._ds_tran_combo = self._ds_tran_combo
            self.ac_align_seq._update_conv_param()

        # Entry field for operating frequency
        self.oper_freq_entr = self._create_entry("Operating frequency [kHz]",
                                                 int(self.input_param.oper_freq),
                                                 is_event=True, event_handling=self._event_handling)

        # Choose protocol extraction method
        protocols = config['Characterization']['Protocols'].split('\n')
        if self.input_param.is_ac_align:
            chosen_prot = config['Characterization']['Protocol.ac_align']
        else:
            chosen_prot = config['Characterization']['Protocol.excel']

        self.prot_combo = self._create_combo("Protocol", protocols, chosen_prot,
                                             self._prot_combo_action)

        # Save row where to insert additional entries
        self.insert_row = self.row_nr + 1

        if self.input_param.is_ac_align:
            self._create_ac_align_entries()
        else:
            # Path and filename of protocol excel file
            self.path_prot = self._create_entry("Path and filename of protocol excel file",
                                                self.input_param.path_protocol_excel_file,
                                                is_event=True, event_handling=self._event_handling,
                                                width=350)

            # Browse button to select protocol excel file
            button = ctk.CTkButton(master=self.win, text="Browse", command=self._get_filename)
            button.grid(row=self.row_nr, column=1, padx=10, sticky="e")

        # Error message label
        self._add_row()
        self.error_label = ctk.CTkLabel(master=self.win, text="")
        self.error_label.grid(row=self.row_nr, columnspan=2)

    def _create_ac_align_entries(self):
        """
        Creates entry fields for various ACD processing parameters.
        """

        start_row = self.row_nr

        # Output path
        self.output_path = self._create_entry("Path of output directory",
                                              self.input_param.dir_output, is_event=True,
                                              event_handling=self._event_handling, width=350)

        # Browse button to select output directory
        button = ctk.CTkButton(master=self.win, text="Browse", command=self._get_directory)
        button.grid(row=self.row_nr, column=1, padx=10, sticky="e")

        self.pulse_dur = self._create_entry("Pulse duration [us]",
                                            self.ac_align_seq.pulse_dur*1000,
                                            is_event=True, event_handling=self._event_handling,
                                            width=500)

        self.pulse_rep_int = self._create_entry("Pulse repetition interval [ms]",
                                                self.ac_align_seq.pulse_rep_int,
                                                is_event=True, event_handling=self._event_handling,
                                                width=500)

        power_options = config['General']['Power options'].split('\n')

        def_power = self.ac_align_seq.chosen_power
        if def_power is not None:
            if self.ac_align_seq.chosen_power == config['General']['Power option.glob_pow']:
                def_power_value = self.ac_align_seq.global_power*1000  # [W] to [mW]
            elif self.ac_align_seq.chosen_power == config['General']['Power option.press']:
                def_power_value = self.ac_align_seq.press
            elif self.ac_align_seq.chosen_power == config['General']['Power option.volt']:
                def_power_value = self.ac_align_seq.volt
            elif self.ac_align_seq.chosen_power == config['General']['Power option.ampl']:
                def_power_value = self.ac_align_seq.ampl
        else:
            def_power = power_options[0]
            def_power_value = 0

        self.power_combo = self._create_combo("Power setting", power_options, def_power,
                                              self._event_handling, width=240)

        self.power_entry = ctk.CTkEntry(master=self.win, width=240)
        self.power_entry.bind('<Return>', self._event_handling)
        self.power_entry.bind('<1>', self._event_handling)
        self.power_entry.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="e")

        cur_ds_system = self.ds_combo.get()
        for ds in self.input_param.ds_list:
            if ds.name == cur_ds_system:
                self._update_power_options(ds, def_power_value, self.ac_align_seq.chosen_power)
                break

        focus_settings = config['General']['Focus options'].split('\n')
        def_focus_setting = focus_settings[0]
        self.focus_combo = self._create_combo("Focus", focus_settings, def_focus_setting,
                                              self._event_handling, width=240)

        self.focus_entry = ctk.CTkEntry(master=self.win, width=240)
        self.focus_entry.bind('<Return>', self._event_handling)
        self.focus_entry.bind('<1>', self._event_handling)
        self.focus_entry.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="e")

        self._update_focus_entry(self.ac_align_seq.chosen_focus)

        self.focus_dist = self._create_entry("Distance from focus wrt exit plane [mm] array",
                                             str(self.ac_align_seq.ac_align['distance_from_foc']),
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

        # TODO: reduction is disabled from the frontend
        # self.reduc_factor = self._create_entry("Reduction factor [-]",
        #                                        self.ac_align_seq.ac_align['reduction_factor'],
        #                                        is_event=True, event_handling=self._event_handling,
        #                                        width=500)

        # self.max_red_iter = self._create_entry("Maximum amount of reduction iterations",
        #                                        self.ac_align_seq.ac_align['max_red_iter'],
        #                                        is_event=True, event_handling=self._event_handling,
        #                                        width=500)

        self.create_graphs = self._create_checkbox("Create graphs of every line measurement",
                                                   self.ac_align_seq.ac_align['create_graphs'],
                                                   True, self._graph_check_action)

        self.y_lim_label, self.y_lim = self._create_entry("Y axis limit [mV]",
                                                          self.ac_align_seq.ac_align['y_lim'],
                                                          is_event=True,
                                                          event_handling=self._event_handling,
                                                          width=500, return_label=True)

        if not self.ac_align_seq.ac_align['create_graphs']:
            # Save location for the entry, but hide it when false
            self.y_lim_label.grid_remove()
            self.y_lim.grid_remove()

        self.create_axis_file = self._create_checkbox("Create axial measurement coordinate file",
                                                      self.ac_align_seq.ac_align['create_axis_file'],
                                                      True, self._axis_file_check_action)

        self.axial_len_label, self.axial_len = self._create_entry("Length of axial measurement [mm]",
                                                                  self.ac_align_seq.ac_align['axis_length'],
                                                                  is_event=True, event_handling=self._event_handling,
                                                                  width=500, return_label=True)

        self.axial_step_label, self.axial_step = self._create_entry("Stepsize of axial measurement [mm]",
                                                                    self.ac_align_seq.ac_align['axis_stepsize'],
                                                                    is_event=True, event_handling=self._event_handling,
                                                                    width=500, return_label=True)

        # Save location for the entry, but hide it when false
        if not self.ac_align_seq.ac_align['create_axis_file']:
            self.axial_len_label.grid_remove()
            self.axial_len.grid_remove()

            self.axial_step_label.grid_remove()
            self.axial_step.grid_remove()

        self._resize_window()

        end_row = self.row_nr

        self.n_ac_align_rows = end_row - start_row

    def _update_power_options(self, cur_ds, def_power_value=0, def_power=None):

        ds_manufact = str(cur_ds.manufact)
        if ds_manufact == config['Equipment.Manufacturer.SC']['Name']:
            power_options = config['Equipment.Manufacturer.SC']['Power options'].split('\n')

        elif ds_manufact == config['Equipment.Manufacturer.IGT']['Name']:

            if self._ds_tran_combo in self._equip_combos:
                power_options = config['Equipment.Manufacturer.IGT']['Power options'].split('\n')
            else:
                power_options = [config['General']['Power option.ampl']]

        else:
            power_options = config['General']['Power options'] .split('\n')

        if def_power is None:
            def_power = power_options[0]

        self.power_combo.configure(values=power_options)
        self.power_combo.set(def_power)

        self.power_entry.delete(0, tk.END)
        self.power_entry.insert(0, def_power_value)

    def _update_focus_entry(self, focus_option):

        shown_focus = 0
        if focus_option == config['General']['Focus option.exit']:
            shown_focus = self.focus_wrt_exit_plane_array
        elif focus_option == config['General']['Focus option.bowl']:
            shown_focus = self.focus_wrt_mid_bowl_array

        self.focus_combo.set(focus_option)

        self.focus_entry.delete(0, tk.END)
        self.focus_entry.insert(0, str(shown_focus))

    def _create_buttons(self):
        """
        Creates Ok and Cancel buttons.
        """

        self._add_row()

        # Ok button
        self.ok_button = ctk.CTkButton(master=self.win, text="Ok", command=self._ok_action)
        self.ok_button.grid(row=self.row_nr, column=0, sticky='w', ipadx=53, padx=10, pady=10)
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
                self.input_param.driving_sys = ds
                self.ac_align_seq.driving_sys = ds.serial
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

                # Update equipment combo name
                self._ds_tran_combo = '~'.join([ds.serial,
                                                self.input_param.tran.serial])

                # Update power options if acoustical alignment is chosen
                if self.prot_combo.get() == config['Characterization']['Protocol.ac_align']:
                    self._update_power_options(ds)
                break

        self._event_handling(event)

    def _trans_combo_action(self, event):
        """
        Action function triggered when a new transducer is selected from the dropdown.
        Updates related fields and performs event handling.
        """

        new_tran_name = self.trans_combo.get()

        for tran in self.input_param.tran_list:
            if tran.name == new_tran_name:
                self.input_param.tran = tran
                self.ac_align_seq.transducer = tran.serial
                self.oper_freq_entr.delete(0, tk.END)
                self.oper_freq_entr.insert(0, int(tran.fund_freq))

                # Update equipment combo name
                self._ds_tran_combo = '~'.join([self.input_param.driving_sys.serial,
                                                tran.serial])

                self._event_handling(event)
                break

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
        if cur_prot == config['Characterization']['Protocol.excel']:
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

        elif cur_prot == config['Characterization']['Protocol.ac_align']:
            self.input_param.is_ac_align = True

            # Shift widgets below this point down by updating their grid positions
            for widget in self.win.grid_slaves():
                if widget.grid_info()['row'] >= self.insert_row:
                    widget.grid(row=widget.grid_info()['row'] + self.n_ac_align_rows, column=widget.grid_info()['column'])

            self._create_ac_align_entries()

        self._event_handling(event)

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

        self.input_param.is_ac_align = False

        # Lift window
        self._resize_window()

        self._event_handling(None)

    def _get_directory(self):
        """
        Opens a file dialog to select a folder and updates the corresponding entry field.
        """

        directory = tk.filedialog.askdirectory(initialdir=self.input_param.dir_output)

        self.output_path.delete(0, tk.END)
        self.output_path.insert(0, directory)

        # Lift window
        self._resize_window()

        self._event_handling(None)

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

        self._resize_window()

    def _graph_check_action(self, event):
        check_value = self.create_graphs.get() == 1

        if check_value:
            self.y_lim_label.grid()
            self.y_lim.grid()

        else:
            self.y_lim_label.grid_remove()
            self.y_lim.grid_remove()

        self._event_handling(event)
        self._resize_window()

    def _axis_file_check_action(self, event):
        check_value = self.create_axis_file.get() == 1

        if check_value:
            self.axial_len_label.grid()
            self.axial_len.grid()

            self.axial_step_label.grid()
            self.axial_step.grid()

        else:
            self.axial_len_label.grid_remove()
            self.axial_len.grid_remove()

            self.axial_step_label.grid_remove()
            self.axial_step.grid_remove()

        self._event_handling(event)
        self._resize_window()

    def _validate_inputs(self):
        """
        Validates all input fields and returns error message if any field is invalid.

        Returns:
            str: Error message if validation fails, otherwise an empty string.
            str: Default text color based on appearance mode.
        """

        error_message = ''

        # widget, is_float, check_positive, check_nonzero, selected_combo, is_dir, excel,
        # check_array, check_focus

        fields_to_validate = {
            'driving system': (self.ds_combo, False, False, False, True, False, False, False,
                               False),
            'transducer': (self.trans_combo, False, False, False, True, False, False, False, False),
            'operating frequency': (self.oper_freq_entr, True, True, True, False, False, False,
                                    False, False),
            'protocol': (self.prot_combo, False, False, False, True, False, False, False, False)

        }

        if self.input_param.is_ds_com_port:
            fields_to_validate.update({'COM port number of driving system':
                                       (self.com_us, True, True, True, False, False, False, False,
                                        False)})

        if self.input_param.is_ac_align:
            fields_to_validate.update({
                'output path': (self.output_path, False, False, False, False, True, False, False,
                                False),
                'pulse duration': (self.pulse_dur, True, True, True, False, False, False, False,
                                   False),
                'pulse rep. interval': (self.pulse_rep_int, True, True, True, False, False, False,
                                        False, False),
                'power setting': (self.power_combo, False, False, False, True, False, False, False,
                                  False),
                'power value': (self.power_entry, True, True, True, False, False, False, False,
                                False),
                'focus setting': (self.focus_combo, False, False, False, True, False, False, False,
                                  False),
                'focus value': (self.focus_entry, True, True, True, False, False, False, True,
                                True),
                'distance from focus wrt exit plane': (self.focus_dist, True, False, False, False,
                                                       False, False, True, False),
                'initial line length': (self.init_line_len, True, True, True, False, False, False,
                                        False, False),
                'initial line stepsize': (self.init_line_step, True, True, True, False, False,
                                          False, False, False),
                'initial threshold': (self.init_threshold, True, True, True, False, False, False,
                                      False, False)
                # TODO: reduction is disabled from the frontend
                # 'reduction fact.': (self.reduc_factor, True, True, True, False, False, False,
                #                     False, False)
                # 'n reduction iterations': (self.max_red_iter, True, True, False, False, False,
                #                           False, False, False)
                })

            if self.create_graphs.get():
                fields_to_validate.update({'y axis limit':
                                           (self.y_lim, True, True, True, False, False, False,
                                            False, False)})
            if self.create_axis_file.get():
                fields_to_validate.update({'length of axial meas.':
                                           (self.axial_len, True, True, True, False, False, False,
                                            False, False),
                                          'stepsize of axial meas.':
                                           (self.axial_step, True, True, True, False, False, False,
                                            False, False)})
        else:
            fields_to_validate.update({'path_protocol_excel_file': (self.path_prot, False, False,
                                                                    False, False, True, True, False,
                                                                    False)})

        for field_name, (widget, is_float, check_positive, check_nonzero, selected_combo, is_dir,
                         excel, check_array, check_focus) in fields_to_validate.items():
            error_message = self._check_field(error_message, widget, field_name, is_float,
                                              check_positive, check_nonzero, selected_combo,
                                              is_dir, excel, check_array, check_focus)

        return error_message

    def _check_field(self, error_message, widget, field_name, is_float, check_positive,
                     check_nonzero, selected_combo, is_dir, excel, check_array, check_focus):
        """
        Checks validity of a specific input field.

        Args:
            error_message (str): Current error message to be updated if validation fails.
            widget (tk.Widget): Widget containing the value to validate.
            field_name (str): Name of the field being validated, used in error messages.
            is_float (bool): Flag indicating if the field value should be converted to a float.
            check_positive (bool): Flag indicating if the field value should be positive.
            check_nonzero (bool): Flag indicating if the field value should be non-zero.
            selected_combo (bool): Flag indicating if the field is a combobox. If true, it checks
                if a value has been selected.
            is_dir (bool): Flag indicating if the field value represents a directory path.
            excel (bool): Flag indicating if the field value should point to a valid Excel file.
            check_array (bool): Flag indicating if the field value should be a valid array.
            check_focus (bool): Flag indicating if the field value should meet set focus limits.

        Returns:
            str: Updated error message with details of any validation issues.
            str: Default text color based on appearance mode.
        """

        def_color = 'black'
        if ctk.get_appearance_mode() == 'Dark':
            def_color = 'white'

        widget.configure(text_color=def_color)
        value = widget.get()

        if is_dir:
            if not os.path.exists(value):
                widget.configure(text_color="red")
                error_message += 'Error: File doesn\'t exist. Please change value. \n '

            if excel:
                path, file_ext = os.path.splitext(value)
                excel_ext = ['.xlsx', '.xls', '.csv']
                if file_ext not in excel_ext:
                    widget.configure(text_color="red")
                    error_message += (f'Error: No {excel_ext} file is selected.'
                                      + ' Please select a file with {excel_ext}. \n ')
        elif selected_combo:
            if value == '':
                widget.configure(text_color="red")
                error_message += f'Error: A {field_name} must be selected. Please change value. \n '

        # Check if value is an array
        elif check_array:
            try:
                distance_str_array = value.strip('][').split(',')
                distance_array = []
                for value in distance_str_array:
                    error_message_result, is_valueError = self._value_checks(value, is_float,
                                                                             check_positive,
                                                                             check_nonzero,
                                                                             check_focus,
                                                                             field_name,
                                                                             widget,
                                                                             error_message)
                    if not is_valueError:
                        error_message = error_message_result
                        distance_array.append(float(value))
                    else:
                        # Ignore other remarks until valid input is given
                        widget.configure(text_color="red")
                        error_message += (f'Error: Value {value} of {field_name} is invalid. ' +
                                          'Please provide a valid array format (e.g., [1, 2, 3]' +
                                          '). \n')

                if not isinstance(distance_array, list):
                    raise ValueError
            except (ValueError, SyntaxError):
                widget.configure(text_color="red")
                error_message += (f'Error: The value of {field_name} is not a valid array. ' +
                                  'Please provide a valid array format (e.g., [1, 2, 3]). \n')

        else:
            error_message, is_valueError = self._value_checks(value, is_float, check_positive,
                                                              check_nonzero, check_focus,
                                                              field_name, widget, error_message)

        return error_message

    def _value_checks(self, value, is_float, check_positive, check_nonzero, check_focus, field_name,
                      widget, error_message):
        """
        Validates a value based on various criteria and updates the error message if validation
        fails.

        Parameters:
            value (str): The value to validate.
            is_float (bool): Whether the value should be a float (otherwise treated as an int).
            check_positive (bool): Flag to check if the value is non-negative.
            check_nonzero (bool): Flag to check if the value is non-zero.
            check_focus (bool): Flag to perform additional focus validation.
            field_name (str): Name of the field for error context.
            widget (customtkinter.CTkWidget): Widget to update styling for errors.
            error_message (str): Current error messages to append to.

        Returns:
            str: Updated error message if validation fails.

        Notes:
            - Converts the value to float or int based on `is_float`.
            - Checks for positivity, non-zero value, and specific focus constraints.
            - Validates sampling frequency multiplication factor (minimum 2) if applicable.
            - Handles invalid number formats and updates the widget's text color to red on error.
        """

        is_valueError = False
        try:
            if is_float:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            is_valueError = True
            widget.configure(text_color="red")
            error_message += (f'Error: value of {field_name} is not a number or contains a ' +
                              'comma as a decimal separator. Please change value or decimal' +
                              ' separator. \n ')

            return error_message, is_valueError

        if check_positive and value < 0:
            widget.configure(text_color="red")
            error_message += (f'Error: {field_name} cannot be a negative value.' +
                              ' Please change value. \n ')
        if check_nonzero and value == 0:
            widget.configure(text_color="red")
            error_message += (f'Error: {field_name} cannot be zero.' +
                              ' Please change value. \n ')
        if check_focus:
            error_message = self._check_focus(value, field_name, widget, error_message)

        if field_name == 'sampling frequency multiplication factor' and value < 2:
            widget.configure(text_color="red")
            error_message += ('Error: Picoscope sampling frequency multiplication' +
                              'factor needs to be at least 2. Please change value. \n ')

        return error_message, is_valueError

    def _check_focus(self, value, field_name, widget, error_message):
        """
        Validates the focus value against configured limits.

        Parameters:
            value (str): Input focus value to validate.
            field_name (str): Name of the field for error context.
            widget (customtkinter.CTkWidget): Widget to update styling for errors.
            error_message (str): Current error messages to append to.

        Returns:
            str: Updated error message if the focus value is out of bounds.

        Notes:
            - Converts the input focus to relative exit-plane value if needed.
            - Validates focus against pre-defined limits.
            - Sets the widget text color to red and appends an error message if out of bounds.
        """

        focus = float(value)

        chosen_focus = self.focus_combo.get()
        if chosen_focus == config['General']['Focus option.exit']:
            focus_wrt_exit_plane = focus
        elif chosen_focus == config['General']['Focus option.bowl']:
            # Convert wrt mid bowl to wrt exit plane
            if self._ds_tran_combo in self._equip_combos and self.ac_align_seq.DF2SF_a != 0:
                focus_wrt_exit_plane = (focus - self.ac_align_seq.DF2SF_b) / self.ac_align_seq.DF2SF_a
            else:
                focus_wrt_exit_plane = focus - self.input_param.tran.exit_plane_dist

        # Check if focus is within range if compensation equations are not applicable
        if self._ds_tran_combo not in self._equip_combos:
            low_lim = self.input_param.tran.min_foc
            up_lim = self.input_param.tran.max_foc

        else:
            low_lim = self.ac_align_seq.F2EQF1_low_lim
            up_lim = self.ac_align_seq.F2EQF2_up_lim

        if focus_wrt_exit_plane < low_lim or focus_wrt_exit_plane > up_lim:
            widget.configure(text_color="red")
            error_message += (f'Error: The value of {field_name} is not within ' +
                              f'set limits of {low_lim} and {up_lim} wrt exit plane [mm]. \n')

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
                    break

            # Save selected transducer object
            td_name = self.trans_combo.get()
            for tran in self.input_param.tran_list:
                if tran.name == td_name:
                    self.input_param.tran = tran
                    break

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
            if chosen_prot == config['Characterization']['Protocol.excel']:
                self.input_param.is_ac_align = False

                # Save protocol file path and main directory
                exc_path = self.path_prot.get()
                self.input_param.path_protocol_excel_file = exc_path
                self.input_param.dir_output = os.path.dirname(self.input_param.path_protocol_excel_file)
                filename_ext = os.path.basename(exc_path)
                self.input_param.protocol = os.path.splitext(filename_ext)

                self.ac_align_seq.is_ac_align = False
                self.input_param.sequences = []

            elif chosen_prot == config['Characterization']['Protocol.ac_align']:
                self.input_param.protocol = chosen_prot
                self.input_param.is_ac_align = True
                self.ac_align_seq.is_ac_align = True

                self.input_param.dir_output = self.output_path.get()

                self.ac_align_seq.pulse_dur = abs(float(self.pulse_dur.get()))/1e3  # [us] to [ms]
                self.ac_align_seq.pulse_rep_int = abs(float(self.pulse_rep_int.get()))  # [ms]
                self.ac_align_seq.pulse_train_dur = self.ac_align_seq.pulse_rep_int
                self.ac_align_seq.pulse_train_rep_int = self.ac_align_seq.pulse_rep_int
                self.ac_align_seq.pulse_train_rep_dur = self.ac_align_seq.pulse_rep_int/1000  # [s]

                # Assign the values from the input fields to the ac_align parameters
                # Parse float entries from entry fields
                distance_str_array = self.focus_dist.get().strip('][').split(',')
                distance_array = [float(value) for value in distance_str_array]

                self.ac_align_seq.ac_align['distance_from_foc'] = distance_array
                self.ac_align_seq.ac_align['init_line_len'] = abs(float(self.init_line_len.get()))
                self.ac_align_seq.ac_align['init_line_step'] = abs(float(self.init_line_step.get()))
                self.ac_align_seq.ac_align['init_threshold'] = abs(float(self.init_threshold.get()))

                # Parse float entry for reduction factor
                # TODO: reduction is disabled from the frontend
                # self.ac_align_seq.ac_align['reduction_factor'] = abs(float(self.reduc_factor.get()))

                # Parse integer entry for maximum reduction iterations
                # self.ac_align_seq.ac_align['max_red_iter'] = int(self.max_red_iter.get())

                # Parse boolean values from checkboxes
                self.ac_align_seq.ac_align['create_graphs'] = self.create_graphs.get() == 1
                self.ac_align_seq.ac_align['y_lim'] = float(self.y_lim.get())

                self.ac_align_seq.ac_align['create_axis_file'] = self.create_axis_file.get() == 1

                # Parse float entries for axis length and stepsize
                self.ac_align_seq.ac_align['axis_length'] = abs(float(self.axial_len.get()))
                self.ac_align_seq.ac_align['axis_stepsize'] = abs(float(self.axial_step.get()))

                # Extract focus at last to create sequences using the same parameters by only
                # changing the focus setting

                # Parse float entries from entry fields
                focus_str_array = self.focus_entry.get().strip('][').split(',')
                focus_array = [float(value) for value in focus_str_array]

                # Due to compensation equations, first set focus then the power value
                chosen_focus = self.focus_combo.get()
                chosen_power = self.power_combo.get()
                power_value = abs(float(self.power_entry.get()))
                sequences = []
                for focus in focus_array:
                    basic_seq = self.ac_align_seq.clone()

                    if chosen_focus == config['General']['Focus option.exit']:
                        basic_seq.focus_wrt_exit_plane = focus
                    elif chosen_focus == config['General']['Focus option.bowl']:
                        basic_seq.focus_wrt_mid_bowl = focus

                    if chosen_power == config['General']['Power option.glob_pow']:
                        basic_seq.global_power = power_value/1000  # SC: gp [W]
                    elif chosen_power == config['General']['Power option.press']:
                        basic_seq.press = power_value
                    elif chosen_power == config['General']['Power option.volt']:
                        basic_seq.volt = power_value
                    elif chosen_power == config['General']['Power option.ampl']:
                        basic_seq.ampl = power_value

                    sequences.append(basic_seq)

                self.input_param.sequences = sequences

            self.main_prot_entry.delete(0, tk.END)
            self.main_prot_entry.insert(0, self.input_param.protocol)

            # Close the dialog
            self._cancel_action()

    def _cancel_action(self):
        """
        Action function triggered when Cancel button is clicked.
        Closes the input dialog.
        """

        if self.win and self.win.winfo_exists():
            self.win.grab_release()  # release main dialog
            self.win.withdraw()  # hide subdialog
