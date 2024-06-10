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

import logging
import time
import re
import sys

class tpoCommunication():
    def __init__(self, logger_name, tpo):
        self.logger = logging.getLogger(logger_name)
        self.tpo = tpo

    def sendCommand(self, command, sleep_time_s = 1):
        self.tpo.write(command.encode("ascii"))
        self.logger.info(f"Sent to TPO: {command.strip()}")
        time.sleep(sleep_time_s)
        response = self.tpo.readline().decode("ascii").rstrip()
        self.logger.info("Response from TPO: %response", response)
    
        if response == 'E2':
            self.logger.error("Error E2")
            sys.exit()
    
        return response
    
    def resetParameters(self):
        # Make sure TPO is not in advanced mode
        command = 'LOCAL=1\r\n'
        self.sendCommand(command)
        self.resetRamping()
        
    def resetRamping(self):
        # Make sure ramping is off prior to experiment 
        command = 'ABORT\r\n'
        self.sendCommand(command, 0.5)
        
        command = 'RAMPMODE=0\r\n'
        self.sendCommand(command)
        
    def setOperatingFreq(self, oper_freq):
        # Set operating frequency on TPO
        command = f'GLOBALFREQ={oper_freq}\r\n'
        self.sendCommand(command)
        
    def setFocus(self, focus):
        # Set focus on TPO
        command = f'FOCUS={focus}\r\n'
        self.sendCommand(command)
        
    def setGlobalPower(self, global_power):
        command = f'GLOBALPOWER={global_power}\r\n'
        self.sendCommand(command, 0.1)
        
    def setBurstLength(self, burst):
        # Set pulse duration (PD)
        command = f'BURST={burst}\r\n'
        self.sendCommand(command, 0.1)
        
    def setPeriod(self, period):
        # Set pulse repetition period (PRP)
        command = f'PERIOD={period}\r\n'
        self.sendCommand(command, 0.1)
        
    def setBurstAndPeriod(self, des_burst, des_period):
        # Get current pulse repetition period (PRP) 
        command = 'PERIOD?\r\n'
        
        feedback =  self.sendCommand(command, 0.1)
        matches = re.findall(r'\d+\.?\d*', feedback) # extract the number
        read_PRP = float(matches[0]) # convert to float
        
        # Depending on current settings, set PD and PRP in the appropriate order
        # Check if desired PD is larger than the current PRP
        if des_burst > read_PRP:
            self.setPeriod(des_period)
            self.setBurstLength(des_burst)
        else:
            self.setBurstLength(des_burst)
            self.setPeriod(des_period)
            
    def setTimer(self, timer):
        # Set sonication duration (SD)
        command = f'TIMER={timer}\r\n'
        self.sendCommand(command, 0.1)
            
    def setRamping(self, ramp_mode, ramp_length, row_number):
        if ramp_mode == 0:
            self.resetRamping()
            
            # Send abort command to allow further control after applying ramping 
            command = 'ABORT\r\n'
            self.sendCommand(command, 0.1)
        elif ramp_mode == 2:
            command = 'RAMPMODE={ramp_mode}\r\n'
            self.sendCommand(command)
            
            command = f'RAMPLENGTH={ramp_length}\r\n'
            self.sendCommand(command)
        else:
            self.logger.error(f"Unknown modulation value: {ramp_mode} for protocol {row_number}")
            sys.exit(f"Unknown modulation value: {ramp_mode} for protocol {row_number}")
        