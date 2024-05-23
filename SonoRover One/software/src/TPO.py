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

import serial
import time
from psychopy import gui
import numpy as np
import sys
import re

class USProtocol:
    def __init__(self):
        self.driving_system_com_port = 'COM8'    # com port of driving system
        self.pulse_dur = 250                      # Pulse duration in us
        self.pulse_rep_int = 200000              # Pulse repetition interval in us
        self.pulse_train_dur = 1000000           # Pulse train duration in us
        self.global_power = 2500                 # Global power in mW
        self.focus = 40000                       # Focus in um

    def convertToOkData(self):
        ok_data = np.empty(6,dtype=object)

        ok_data = [self.driving_system_com_port,
                   self.pulse_dur / 1000,
                   self.pulse_rep_int / 1000,
                   self.pulse_train_dur / 1e6,
                   self.global_power,
                   self.focus / 1000]

        return ok_data

def setInputParameters(ok_data, color_field_num = 0, text = ' '):
    dialog = gui.Dlg(title="Set US protocol parameters")
    dialog.addText(text)
    dialog.addField('COM port of US driving system*:', ok_data[0], color=checkFieldColor(color_field_num, 1))
    dialog.addField('Pulse duration [ms]*:', ok_data[1], color=checkFieldColor(color_field_num, 2))
    dialog.addField('Pulse repetition interval [ms]*:', ok_data[2], color=checkFieldColor(color_field_num, 3))
    dialog.addField('Pulse train duration [s]*:', ok_data[3], color=checkFieldColor(color_field_num, 4))
    dialog.addField('Global power [mW]*:', ok_data[4], color=checkFieldColor(color_field_num, 5))
    dialog.addField('Focus [mm]*:', ok_data[5], color=checkFieldColor(color_field_num, 6))

    ok_data = dialog.show()
    
    if dialog.OK:
        ok_data = checkValues(ok_data)

        usProt.driving_system_com_port = ok_data[0]
        usProt.pulse_dur = ok_data[1] * 1000
        usProt.pulse_rep_int = ok_data[2] * 1000
        usProt.pulse_train_dur = ok_data[3] * 1e6
        usProt.global_power = ok_data[4]
        usProt.focus = ok_data[5] * 1000

        return ok_data
    else:
        # Pipeline is cancelled by user
        sys.exit("Pipeline is cancelled by user.")

def checkValues(ok_data):
        driving_system_com_port = ok_data[0]
        pulse_dur = ok_data[1]
        pulse_rep_int = ok_data[2]
        pulse_train_dur = ok_data[3]
        global_power = ok_data[4]
        focus = ok_data[5]

        match_result = re.search(r'\d+$', driving_system_com_port)
        # Check if tpo com port is correctly written
        if not driving_system_com_port.startswith('COM'):
            # Redo until tpo com port is correct
            ok_data = setInputParameters(ok_data, 1, text = 'Error: Com port must start with COM. Please change value.')
        # if the string ends in digits, match will be a Match object, or None otherwise.
        elif match_result is None:
            # Redo until tpo com port is correct
            ok_data = setInputParameters(ok_data, 1, text = 'Error: Com port must end with a number. Please change value.')

        # Check if pulse duration is a number
        ok_data = checkIfNumAndPos(pulse_dur, True, ok_data, 2, 'pulse duration')

        # Check if pulse repetition interval is a number
        ok_data = checkIfNumAndPos(pulse_rep_int, True, ok_data, 3, 'pulse repetition interval')

        # Check if pulse train duration is a number
        ok_data = checkIfNumAndPos(pulse_train_dur, True, ok_data, 4, 'pulse train duration')

        # Check if global power is a number
        ok_data = checkIfNumAndPos(global_power, True, ok_data, 5, 'global power')

        # Check if focus is a number
        ok_data = checkIfNumAndPos(focus, True, ok_data, 6, 'focus')

        return ok_data

def checkFieldColor(color_field_num, field_num):
    if color_field_num == field_num:
        color = 'Red'
    else:
        color = ''
    return color

def checkIfNumAndPos(parameter, check_pos, ok_data, color_field_num, par_name):
    # Check if input is float
    try:
        parameter = float(parameter)
        if check_pos:
            if parameter < 0:
                # Redo until input is correct
                ok_data = setInputParameters(ok_data, color_field_num = color_field_num, text = f'Error: {par_name} cannot be a negative value. Please change value.')
    except:
        # Redo until input is correct
        ok_data = setInputParameters(ok_data, color_field_num = color_field_num, text = f'Error: value of {par_name} is not a number or contains a comma as decimal separator. Please change value or decimal separator.')

    return ok_data

if __name__ == '__main__':

    usProt = USProtocol()
    setInputParameters(usProt.convertToOkData())

    with serial.Serial(usProt.driving_system_com_port, 115200, timeout=1) as ser:
    		time.sleep(1)
    		line = ser.readline().decode("ascii")
    		print(f'connect: {line}')
    		cmd=f'BURST={usProt.pulse_dur}\r'
    		nb=ser.write(cmd.encode('ascii'))
    		time.sleep(1)
    		line = ser.readline().decode("ascii")
    		print(f'connect: {line}')
    		cmd=f'PERIOD={usProt.pulse_rep_int}\r'
    		nb=ser.write(cmd.encode('ascii'))
    		time.sleep(1)
    		line = ser.readline().decode("ascii").rstrip()
    		print(f'PERIOD: {line}')
    		cmd=f'TIMER={usProt.pulse_train_dur}\r'
    		nb=ser.write(cmd.encode('ascii'))
    		time.sleep(1)
    		line = ser.readline().decode("ascii").rstrip()
    		print(f'TIMER: {line}')
    		cmd=f'GLOBALPOWER={usProt.global_power}\r'
    		nb=ser.write(cmd.encode('ascii'))
    		time.sleep(1)
    		line = ser.readline().decode("ascii")
    		print(f'GLOBALPOWER: {line}')
    		cmd=f'FOCUS={usProt.focus}\r'
    		nb=ser.write(cmd.encode('ascii'))
    		time.sleep(1)
    		line = ser.readline().decode("ascii")
    		print(f'FOCUS: {line}')
    		time.sleep(1)
    		for i in range(1000):
     			cmd='START\r'
     			nb=ser.write(cmd.encode('ascii'))
     			time.sleep(0.5)
     			line = ser.readline().decode("ascii")
     			print(f'PERIOD: {line}')
    
    #		cmd=f'ABORT\r'
    #		nb=ser.write(cmd.encode('ascii'))
    #		time.sleep(1)



