# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 Margely Cornelissen (Radboud University) and Erik Dumont (Image Guided Therapy)

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
If you use this software in your project, please include the following attribution:
Margely Cornelissen (Radboud University, Nijmegen, The Netherlands) & Erik Dumont (Image Guided
Therapy, Pessac, France) (2024), Radboud FUS measurement kit, SonoRover One Software (Version 0.8),
https://github.com/MaCuinea/Radboud-FUS-measurement-kit
"""

import sys
import os

import tkinter as tk
import customtkinter as ctk

import configparser
from datetime import datetime


class Transducer:
    def __init__(self):
        self.serial = None
        self.name = None
        self.manufact = None
        self.elements = 0
        self.fund_freq = 0
        self.natural_foc = 0
        self.min_foc = 0
        self.max_foc = 100
        self.steer_info = None
        self.is_active = True


class DrivingSystem:
    def __init__(self):
        self.serial = None
        self.name = None
        self.manufact = None
        self.available_ch = 0
        self.connect_info = None
        self.tran_comp = None
        self.is_active = True


class InputParameters:
    def __init__(self, config):
        self.temp_dir_output = os.path.join(config['General']['Temporary output path'],
                                            'General output folder')
        self.dir_output = ('//ru.nl//WrkGrp//FUS_Engineering//Hydrophone measurements'
                           + '//Measurements//2024//General output folder')
        self.main_dir = ('//ru.nl//WrkGrp//FUS_Engineering//Hydrophone measurements//Measurements'
                         + '//2024')
        self.path_protocol_excel_file = ('//ru.nl//WrkGrp//FUS_Engineering//'
                                         + 'Hydrophone measurements//Measurements//2024')

        self.config = config

        # get driving system information and set first one as default value
        serial_ds = config['Equipment']['Driving systems'].split(', ')

        self.driving_systems = []
        for serial in serial_ds:
            # only extract active driving systems
            if (config['Equipment.Driving system.' + serial]['Active?'] == 'True'):
                ds = DrivingSystem()
                ds.serial = serial
                ds.name = config['Equipment.Driving system.' + serial]['Name']
                ds.manufact = config['Equipment.Driving system.' + serial]['Manufacturer']
                ds.available_ch = int(config['Equipment.Driving system.' + serial]
                                      ['Available channels'])
                ds.connect_info = config['Equipment.Driving system.' + serial]['Connection info']
                ds.tran_comp = (config['Equipment.Driving system.' + serial]
                                ['Transducer compatibility'].split(', '))
                ds.is_active = (config['Equipment.Driving system.' + serial]['Active?'] == 'True')

                self.driving_systems.append(ds)

        if len(self.driving_systems) < 1:
            sys.exit('No driving systems found in configuration file.')

        self.driving_system = self.driving_systems[0]
        self.is_ds_com_port = 'COM' in self.driving_system.connect_info
        self.ds_names = [ds.name for ds in self.driving_systems]

        # get transducer information and set first one as default value
        serial_trans = config['Equipment']['Transducers'].split(', ')

        self.transducers = []
        for serial in serial_trans:
            # only extract active transducers
            if (config['Equipment.Transducer.' + serial]['Active?'] == 'True'):

                tran = Transducer()
                tran.serial = serial
                tran.name = config['Equipment.Transducer.' + serial]['Name']
                tran.manufact = config['Equipment.Transducer.' + serial]['Manufacturer']
                tran.elements = int(config['Equipment.Transducer.' + serial]['Elements'])
                tran.fund_freq = int(config['Equipment.Transducer.' + serial]['Fund. freq.'])
                tran.natural_foc = float(config['Equipment.Transducer.' + serial]['Natural focus'])
                tran.min_foc = float(config['Equipment.Transducer.' + serial]['Min. focus'])
                tran.max_foc = float(config['Equipment.Transducer.' + serial]['Max. focus'])
                tran.steer_info = config['Equipment.Transducer.' + serial]['Steer information']
                tran.is_active = (config['Equipment.Transducer.' + serial]['Active?'] == 'True')

                self.transducers.append(tran)

        if len(self.transducers) < 1:
            sys.exit('No transducers found in configuration file.')

        self.transducer = self.transducers[0]
        self.trans_names = [tran.name for tran in self.transducers]

        self.oper_freq = int(self.transducer.fund_freq) * 1e+3  # operating frequency in Hz

        self.pos_com_port = 'COM4'

        self.acquisition_time = 500  # microseconds
        self.sampl_freq_multi = 50
        self.coord_focus = [-50, -50, -150]
        self.perform_all_protocols = True

    def writeToIni(self):
        cached_input = configparser.ConfigParser()

        now = datetime.now()
        cached_input['Input parameters'] = {}
        cached_input['Input parameters']['Date'] = str(now.strftime("%Y/%m/%d"))
        cached_input['Input parameters']['Path and filename of protocol excel file'] = str(
            self.path_protocol_excel_file)

        cached_input['Input parameters']['Driving system.serial_number'] = self.driving_system.serial
        cached_input['Input parameters']['Driving system.name'] = self.driving_system.name
        cached_input['Input parameters']['Driving system.manufact'] = self.driving_system.manufact
        cached_input['Input parameters']['Driving system.available_ch'] = str(self.driving_system.available_ch)
        cached_input['Input parameters']['Driving system.connect_info'] = self.driving_system.connect_info
        cached_input['Input parameters']['Driving system.tran_comp'] = str(', '.join(self.driving_system.tran_comp))
        cached_input['Input parameters']['Driving system.is_active'] = str(self.driving_system.is_active)

        cached_input['Input parameters']['Transducer.serial_number'] = self.transducer.serial
        cached_input['Input parameters']['Transducer.name'] = self.transducer.name
        cached_input['Input parameters']['Transducer.manufact'] = self.transducer.manufact
        cached_input['Input parameters']['Transducer.elements'] = str(self.transducer.elements)
        cached_input['Input parameters']['Transducer.fund_freq'] = str(self.transducer.fund_freq)
        cached_input['Input parameters']['Transducer.natural_foc'] = str(self.transducer.natural_foc)
        cached_input['Input parameters']['Transducer.min_foc'] = str(self.transducer.min_foc)
        cached_input['Input parameters']['Transducer.max_foc'] = str(self.transducer.max_foc)
        cached_input['Input parameters']['Transducer.steer_info'] = self.transducer.steer_info
        cached_input['Input parameters']['Transducer.is_active'] = str(self.transducer.is_active)

        cached_input['Input parameters']['Operating frequency [Hz]'] = str(int(self.oper_freq))

        cached_input['Input parameters']['COM port of positioning system'] = str(self.pos_com_port)

        cached_input['Input parameters']['Hydrophone acquisition time [us]'] = str(self.acquisition_time)
        cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'] = str(self.sampl_freq_multi)

        cached_input['Input parameters']['Absolute G code x-coordinate of relative zero'] = str(self.coord_focus[0])
        cached_input['Input parameters']['Absolute G code y-coordinate of relative zero'] = str(self.coord_focus[1])
        cached_input['Input parameters']['Absolute G code z-coordinate of relative zero'] = str(self.coord_focus[2])

        cached_input['Input parameters']['Perform all protocols in sequence without waiting for user input?'] = str(self.perform_all_protocols)

        config_fold = self.config['General']['Configuration file folder']
        cached_filename = self.config['General']['Filename of input parameters cache']
        with open(os.path.join(config_fold, cached_filename), 'w') as inputfile:
            cached_input.write(inputfile)

    def convertIniToObject(self, cached_input):
        self.path_protocol_excel_file = cached_input['Input parameters']['Path and filename of protocol excel file']

        self.driving_system.serial = cached_input['Input parameters']['Driving system.serial_number']
        self.driving_system.name = cached_input['Input parameters']['Driving system.name']
        self.driving_system.manufact = cached_input['Input parameters']['Driving system.manufact']
        self.driving_system.available_ch = int(cached_input['Input parameters']['Driving system.available_ch'])
        self.driving_system.connect_info = cached_input['Input parameters']['Driving system.connect_info']
        self.is_ds_com_port = 'COM' in self.driving_system.connect_info

        self.driving_system.tran_comp = cached_input['Input parameters']['Driving system.tran_comp'].split(', ')
        self.driving_system.is_active = (cached_input['Input parameters']['Driving system.is_active'] == 'True')

        self.transducer.serial = cached_input['Input parameters']['Transducer.serial_number']
        self.transducer.name = cached_input['Input parameters']['Transducer.name']
        self.transducer.manufact = cached_input['Input parameters']['Transducer.manufact']
        self.transducer.elements = int(cached_input['Input parameters']['Transducer.elements'])
        self.transducer.fund_freq = int(cached_input['Input parameters']['Transducer.fund_freq'])
        self.transducer.natural_foc = float(cached_input['Input parameters']['Transducer.natural_foc'])
        self.transducer.min_foc = float(cached_input['Input parameters']['Transducer.min_foc'])
        self.transducer.max_foc = float(cached_input['Input parameters']['Transducer.max_foc'])
        self.transducer.steer_info = cached_input['Input parameters']['Transducer.steer_info']
        self.transducer.is_active = (cached_input['Input parameters']['Transducer.is_active'] == 'True')

        self.oper_freq = int(cached_input['Input parameters']['Operating frequency [Hz]'])

        self.pos_com_port = cached_input['Input parameters']['COM port of positioning system']

        self.acquisition_time = float(cached_input['Input parameters']['Hydrophone acquisition time [us]'])
        self.sampl_freq_multi = float(cached_input['Input parameters']['Picoscope sampling frequency multiplication factor'])

        self.coord_focus[0] = float(cached_input['Input parameters']['Absolute G code x-coordinate of relative zero'])
        self.coord_focus[1] = float(cached_input['Input parameters']['Absolute G code y-coordinate of relative zero'])
        self.coord_focus[2] = float(cached_input['Input parameters']['Absolute G code z-coordinate of relative zero'])

        self.perform_all_protocols = (cached_input['Input parameters']['Perform all protocols in sequence without waiting for user input?'] == 'True')

    def info(self):
        info = ""
        info = info + f"Path and filename of protocol excel file: {self.path_protocol_excel_file} \n "
        info = info + f"Temporary path of output: {self.temp_dir_output} \n "
        info = info + f"Path of output: {self.dir_output} \n "

        info = info + f"Driving system serial number: {self.driving_system.serial} \n "
        info = info + f"Driving system name: {self.driving_system.name} \n "
        info = info + f"Driving system manufacturer: {self.driving_system.manufact} \n "
        info = info + f"Driving system available channels: {self.driving_system.available_ch} \n "
        info = info + f"Driving system connection info: {self.driving_system.connect_info} \n "
        tran_comp = ', '.join(self.driving_system.tran_comp)
        info = info + f"Driving system transducer compatibility: {tran_comp} \n "

        info = info + f"Transducer serial number: {self.transducer.serial} \n "
        info = info + f"Transducer name: {self.transducer.name} \n "
        info = info + f"Transducer manufacturer: {self.transducer.manufact} \n "
        info = info + f"Transducer elements: {self.transducer.elements} \n "
        info = info + f"Transducer fundamental frequency [kHz]: {self.transducer.fund_freq} \n "
        info = info + f"Transducer natural focus: {self.transducer.natural_foc} \n "
        info = info + f"Transducer min. focus: {self.transducer.min_foc} \n "
        info = info + f"Transducer max. focus: {self.transducer.max_foc} \n "
        info = info + f"Transducer steer table: {self.transducer.steer_info} \n "

        info = info + f"Operating frequency [Hz]: {self.oper_freq} \n "

        info = info + f"COM port of positioning system: {self.pos_com_port} \n "
        info = info + f"Hydrophone acquisition time [us]: {self.acquisition_time} \n "
        info = info + f"Picoscope sampling frequency multiplication factor: {self.sampl_freq_multi} \n "

        info = info + f"Absolute G code xyz-coordinates of relative zero: [{self.coord_focus[0]}, {self.coord_focus[1]}, {self.coord_focus[2]}] \n "
        info = info + f"Perform all protocols in sequence without waiting for user input?: {self.perform_all_protocols} \n "

        return info


class InputDialog():
    def __init__(self, config):
        self.notExitedFlag = True
        self.win = ctk.CTk()

        self.inputParam = InputParameters(config)

        # Save driving system to later know when it is changed
        self.saved_ds = self.inputParam.driving_system

        self.updated_inputParam = None

        self.init_body()

    def init_body(self):
        # Get input parameters from user
        try:
            # Setting up theme of the app
            ctk.set_appearance_mode("System")

            # Set the geometry of tkinter frame
            self.win.geometry("920x540")
            self.win.title('Set input parameters')

            # Check if cached data exists
            config_fold = self.inputParam.config['General']['Configuration file folder']
            cached_file = self.inputParam.config['General']['Filename of input parameters cache']

            config_path = os.path.join(config_fold, cached_file)
            if os.path.exists(config_path):
                cached_input = configparser.ConfigParser()
                cached_input.read(config_path)

                # Check if it is the same day, otherwise use to default
                now = datetime.now()
                if cached_input['Input parameters']['Date'] == str(now.strftime("%Y/%m/%d")):
                    self.inputParam.convertIniToObject(cached_input)

            row_nr = 0
            ctk.CTkLabel(master=self.win, text="Path and filename of protocol excel file"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.path_prot = ctk.CTkEntry(master=self.win, width=350)
            self.path_prot.bind('<Return>', self.event_handling)
            self.path_prot.bind('<1>', self.event_handling)
            self.path_prot.insert(0, self.inputParam.path_protocol_excel_file)
            self.path_prot.grid(row=row_nr, column=1, pady=5, sticky="w")

            ctk.CTkButton(master=self.win, text="Browse",
                          command=self.getFileName).grid(row=row_nr, column=1, sticky="e")

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="US Driving System").grid(row=row_nr, column=0,
                                                                         padx=20, sticky='w')
            self.driving_sys_combo = ctk.CTkComboBox(master=self.win, width=500,
                                                     values=self.inputParam.ds_names,
                                                     command=self.ds_combo_action)
            self.driving_sys_combo.set(self.inputParam.driving_system.name)
            self.driving_sys_combo.bind('<1>', self.event_handling)
            self.driving_sys_combo.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Transducer"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.trans_combo = ctk.CTkComboBox(master=self.win, width=500,
                                               values=self.inputParam.trans_names,
                                               command=self.trans_combo_action)
            self.trans_combo.set(self.inputParam.transducer.name)
            self.trans_combo.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Operating frequency [kHz]"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.oper_freq_entr = ctk.CTkEntry(master=self.win, width=500)
            self.oper_freq_entr.bind('<Return>', self.event_handling)
            self.oper_freq_entr.bind('<1>', self.event_handling)
            self.oper_freq_entr.insert(0, int(self.inputParam.oper_freq/1000))
            self.oper_freq_entr.grid(row=row_nr, column=1, pady=5)

            if self.inputParam.is_ds_com_port:
                row_nr = row_nr + 1
                self.com_us_label = ctk.CTkLabel(master=self.win,
                                                 text="COM port of US driving system")
                self.com_us_label.grid(row=row_nr, column=0, padx=20, sticky='w')
                com_us_num = self.inputParam.driving_system.connect_info.removeprefix('COM')
                self.com_us = ctk.CTkEntry(master=self.win, width=500)
                self.com_us.bind('<Return>', self.event_handling)
                self.com_us.bind('<1>', self.event_handling)
                self.com_us.insert(0, com_us_num)
                self.com_us.grid(row=row_nr, column=1, pady=5)

                self.com_us_label.grid()
                self.com_us.grid()

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="COM port of positioning system"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            com_pos_num = self.inputParam.pos_com_port.removeprefix('COM')
            self.com_pos = ctk.CTkEntry(master=self.win, width=500)
            self.com_pos.bind('<Return>', self.event_handling)
            self.com_pos.bind('<1>', self.event_handling)
            self.com_pos.insert(0, com_pos_num)
            self.com_pos.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Hydrophone acquisition time [us]"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.acq_time = ctk.CTkEntry(master=self.win, width=500)
            self.acq_time.bind('<Return>', self.event_handling)
            self.acq_time.bind('<1>', self.event_handling)
            self.acq_time.insert(0, self.inputParam.acquisition_time)
            self.acq_time.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Picoscope sampling frequency multiplication factor"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.sampl_freq = ctk.CTkEntry(master=self.win, width=500)
            self.sampl_freq.bind('<Return>', self.event_handling)
            self.sampl_freq.bind('<1>', self.event_handling)
            self.sampl_freq.insert(0, self.inputParam.sampl_freq_multi)
            self.sampl_freq.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Absolute G code x-coordinate of relative zero"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.x_coord = ctk.CTkEntry(master=self.win, width=500)
            self.x_coord.bind('<Return>', self.event_handling)
            self.x_coord.bind('<1>', self.event_handling)
            self.x_coord.insert(0, self.inputParam.coord_focus[0])
            self.x_coord.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Absolute G code y-coordinate of relative zero"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.y_coord = ctk.CTkEntry(master=self.win, width=500)
            self.y_coord.bind('<Return>', self.event_handling)
            self.y_coord.bind('<1>', self.event_handling)
            self.y_coord.insert(0, self.inputParam.coord_focus[1])
            self.y_coord.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win, text="Absolute G code z-coordinate of relative zero"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            self.z_coord = ctk.CTkEntry(master=self.win, width=500)
            self.z_coord.bind('<Return>', self.event_handling)
            self.z_coord.bind('<1>', self.event_handling)
            self.z_coord.insert(0, self.inputParam.coord_focus[2])
            self.z_coord.grid(row=row_nr, column=1, pady=5)

            row_nr = row_nr + 1
            ctk.CTkLabel(master=self.win,
                         text="Perform all protocols in sequence without waiting for user input?"
                         ).grid(row=row_nr, column=0, padx=20, sticky='w')
            perform_bool = self.inputParam.perform_all_protocols
            perform_int = 0
            if perform_bool:
                perform_int = 1

            perform_var = tk.IntVar(value=perform_int)
            self.perform_check = ctk.CTkCheckBox(master=self.win, text='', variable=perform_var)
            self.perform_check.bind('<Return>', self.event_handling)
            self.perform_check.bind('<1>', self.event_handling)
            self.perform_check.grid(row=row_nr, column=1, padx=100)

            row_nr = row_nr + 1
            self.error_label = ctk.CTkLabel(master=self.win, text="")
            self.error_label.grid(row=row_nr, columnspan=2)

            row_nr = row_nr + 1
            self.ok_button = ctk.CTkButton(master=self.win, text="Ok", command=self.ok_action)
            self.ok_button.grid(row=row_nr, column=1, sticky='w', ipadx=53)
            self.ok_button.configure(state=tk.DISABLED)
            ctk.CTkButton(master=self.win, text="Cancel", command=self.cancel_action).grid(
                row=row_nr, column=1, sticky='e', ipadx=53)

            self.event_handling(None)

            self.win.lift()
            self.win.mainloop()

        finally:
            if self.notExitedFlag:
                self.win.destroy()

    def getFileName(self):
        fileName = tk.filedialog.askopenfilename(
            initialdir=self.inputParam.path_protocol_excel_file,
            filetypes=[('Excel files', '*.xlsx')])

        self.path_prot.delete(0, tk.END)
        self.path_prot.insert(0, fileName)

        self.event_handling(None)

    def ds_combo_action(self, event):
        # when new driving system has been selected, update required com port accordingly
        cur_ds = self.driving_sys_combo.get()

        if cur_ds != self.saved_ds:
            self.saved_ds = cur_ds

            for ds in self.inputParam.driving_systems:
                if ds.name == cur_ds:
                    if 'COM' in ds.connect_info:
                        self.inputParam.is_ds_com_port = True

                        self.com_us_label.grid()
                        self.com_us.grid()
                    else:
                        self.inputParam.is_ds_com_port = False

                        if hasattr(self, 'com_us'):
                            self.com_us_label.grid_remove()
                            self.com_us.grid_remove()

        # Follow normal path
        self.event_handling(event)
        return

    def trans_combo_action(self, event):
        # when new transducer has been selected, update operating frequency
        new_tran_name = self.trans_combo.get()

        for tran in self.inputParam.transducers:
            if tran.name == new_tran_name:
                new_tran = tran

        self.oper_freq_entr.delete(0, tk.END)
        self.oper_freq_entr.insert(0, new_tran.fund_freq)

        # Follow normal path
        self.event_handling(event)
        return

    def event_handling(self, event):
        error_message = ''

        def_color = 'black'
        if ctk.get_appearance_mode() == 'Dark':
            def_color = 'white'

        # Check existance of protocol excel file
        path_protocol_excel_file = os.path.join(self.path_prot.get())

        # Check if excel file is selected
        path, ext = os.path.splitext(path_protocol_excel_file)
        if ext not in ['.xlsx', '.xls', '.csv']:
            self.path_prot.configure(text_color="red")
            error_message = error_message + 'Error: No excel file is selected. Please selected a file with .xlsx or .xls extension. \n '
        else:
            if not os.path.exists(path_protocol_excel_file):
                self.path_prot.configure(text_color="red")
                error_message = error_message + 'Error: File doesn\'t exist. Please change value. \n '
            else:
                self.path_prot.configure(text_color=def_color)

        driving_system = self.driving_sys_combo.get()
        if driving_system == '':
            self.driving_sys_combo.configure(text_color="red")
            error_message = error_message + 'Error: A driving system must be selected. Please change value. \n '
        else:
            self.driving_sys_combo.configure(text_color=def_color)

        transducer = self.trans_combo.get()
        if transducer == '':
            self.trans_combo.configure(text_color="red")
            error_message = error_message + 'Error: A transducer must be selected. Please change value. \n '
        else:
            self.trans_combo.configure(text_color=def_color)

        # Check if operating frequency is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.oper_freq_entr, True,
                                                  'operating frequency')

        # Check if com port of driving system is a number
        if self.inputParam.is_ds_com_port:
            error_message, isFloat = checkIfNumAndPos(error_message, self.com_us, True,
                                                      'COM port number of driving system')

        # Check if com port of positioning system is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.com_pos, True,
                                                  'COM port number of positioning system')

        # Check if acquistion time is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.acq_time, True,
                                                  'acquisition time')

        # Check if sampling frequency multiplication factor is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.sampl_freq, True,
                                                  'sampling frequency multiplication factor')

        if isFloat:
            sampl_freq_multi = float(self.sampl_freq.get())
            if sampl_freq_multi < 2:
                self.sampl_freq.configure(text_color="red")
                error_message = (error_message
                                 + 'Error: Picoscope sampling frequency multiplication factor' +
                                 ' needs to be at least 2. Please change value. \n ')
            else:
                self.sampl_freq.configure(text_color=def_color)

        # Check if x coord is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.x_coord, False,
                                                  'x-coordinate')

        # Check if y coord is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.y_coord, False,
                                                  'y-coordinate')

        # Check if z coord is a number
        error_message, isFloat = checkIfNumAndPos(error_message, self.z_coord, False,
                                                  'z-coordinate')

        if error_message != '':
            self.error_label.configure(
                    text=error_message,
                    text_color="red",
                    )
            self.ok_button.configure(state=tk.DISABLED)
        else:
            self.error_label.configure(
                    text=error_message,
                    text_color=def_color,
                    )
            self.ok_button.configure(state=tk.NORMAL)

    def ok_action(self):
        # All values are correct, save them in inputParam object
        self.inputParam.path_protocol_excel_file = self.path_prot.get()

        self.inputParam.main_dir = os.path.dirname(self.inputParam.path_protocol_excel_file)

        driving_system = self.driving_sys_combo.get()
        # save whole transducer object
        for ds in self.inputParam.driving_systems:
            if ds.name == driving_system:
                self.inputParam.driving_system = ds

        transducer = self.trans_combo.get()
        # save whole transducer object
        for tran in self.inputParam.transducers:
            if tran.name == transducer:
                self.inputParam.transducer = tran

        head, tail = os.path.split(self.inputParam.path_protocol_excel_file)
        protocol_excel, ext = os.path.splitext(tail)

        folder_struct = 'Output of T [' + transducer + '] - DS [' + driving_system + ']'
        self.inputParam.temp_dir_output = os.path.join(self.inputParam.config['General']
                                                       ['Temporary output path'], folder_struct,
                                                       'P [' + protocol_excel + ']')
        self.inputParam.dir_output = os.path.join(self.inputParam.main_dir, folder_struct,
                                                  'P [' + protocol_excel + ']')

        # Check existance of directories
        if not os.path.exists(self.inputParam.temp_dir_output):
            os.makedirs(self.inputParam.temp_dir_output)

        if not os.path.exists(self.inputParam.dir_output):
            os.makedirs(self.inputParam.dir_output)

        self.inputParam.oper_freq = int(self.oper_freq_entr.get())*1e+3

        if self.inputParam.is_ds_com_port:
            self.inputParam.driving_system.connect_info = 'COM' + self.com_us.get()

        self.inputParam.pos_com_port = 'COM' + self.com_pos.get()
        self.inputParam.acquisition_time = float(self.acq_time.get())
        self.inputParam.sampl_freq_multi = float(self.sampl_freq.get())

        self.inputParam.coord_focus = [float(self.x_coord.get()), float(self.y_coord.get()),
                                       float(self.z_coord.get())]

        self.inputParam.perform_all_protocols = (self.perform_check.get() == 1)

        self.updated_inputParam = self.inputParam

        # Cache data
        self.updated_inputParam.writeToIni()

        if self.notExitedFlag:
            self.notExitedFlag = False
            self.win.destroy()

    def cancel_action(self):
        if self.notExitedFlag:
            self.notExitedFlag = False
            self.win.destroy()

        # Pipeline is cancelled by user
        sys.exit("Pipeline is cancelled by user.")


def checkIfNumAndPos(error_message, entry, check_pos, par_name):
    # Check which default text color is used
    def_color = 'black'
    if ctk.get_appearance_mode() == 'Dark':
        def_color = 'white'

    isFloat = True

    # Check if input is float
    parameter = entry.get()
    entry.configure(text_color=def_color)

    try:
        parameter = float(parameter)
        if check_pos:
            if parameter < 0:
                isFloat = False
                entry.configure(text_color="red")
                error_message = error_message + f'Error: {par_name} cannot be a negative value. Please change value. \n '
    except:
        isFloat = False
        entry.configure(text_color="red")
        error_message = error_message + f'Error: value of {par_name} is not a number or contains a comma as decimal separator. Please change value or decimal separator. \n '

    return error_message, isFloat
