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


class ACDParamDialog():
    """
    GUI dialog for setting additional ACD procesing parameters.

    Attributes:
        win (tk.Tk or None): The main tkinter window.
        not_exited_flag (bool): Flag indicating whether the dialog has not been exited.
        row_nr (int): Current row number for grid layout in the tkinter window.
        acd_param (dict): Dictionary storing ACD processing parameters.
    """

    def __init__(self, acd_param, adjust_param):
        """
        Initializes the ACDParamDialog instance.
        """

        self.win = None
        self.not_exited_flag = True
        self.row_nr = 0

        self.acd_param = acd_param
        self.adjust_param = adjust_param

        self._build_dialog()

    def _build_dialog(self):
        """
        Initializes the GUI components of the dialog.
        """

        # Get input parameters from user
        try:
            self.win = ctk.CTk()
            ctk.set_appearance_mode("System")
            self.win.title('Set ACD processing parameters')

            self._create_entries()
            self._create_buttons()

            self._event_handling(None)  # perform initial event handling

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

    def _create_entries(self):
        """
        Creates entry fields for various ACD processing parameters.
        """

        # Define processing window
        self.begus = self._create_entry("Beginning time of processing window [us]",
                                        self.acd_param["begus"],
                                        is_event=True, event_handling=self._event_handling,
                                        width=200)

        self.endus = self._create_entry("End time of processing window [us]",
                                        self.acd_param["endus"],
                                        is_event=True, event_handling=self._event_handling,
                                        width=200)

        self.adjust = self._create_combo("Moving processing window along?",
                                         self.adjust_param, self.acd_param["adjust"],
                                         self._event_handling)

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
        self.ok_button.grid(row=self.row_nr, column=0, sticky='w', ipadx=53, padx=10, pady=10)
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
        combo = ctk.CTkComboBox(master=self.win, width=200, values=value_list, command=combo_action)

        combo.set(def_value)
        combo.grid(row=self.row_nr, column=1, padx=10, pady=5, sticky="w")

        return combo

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
            'beginning time': (self.begus, True, True, None, False),
            'end time': (self.endus, True, True, None, False),
            'adjust': (self.adjust, False, False, None, True),
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
            self.acd_param["begus"] = self.begus.get()
            self.acd_param["endus"] = self.endus.get()
            self.acd_param["adjust"] = self.adjust.get()

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
