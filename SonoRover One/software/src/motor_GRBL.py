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

import serial
import serial.tools.list_ports as list_ports
import time
import logging
import re

MotorErrorCode = {
0 : 'Connection Error',
1 : 'Initialization Error',
2 : 'Range Error',
3 : 'Motor Firmware error',
4 : 'Undefined Error',
}


class MotorError(Exception):
    def __init__(self, logger_name, code=0, message="MotorError"):
        self.logger = logging.getLogger(logger_name)

        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'Motor error {self.code}: {self.message}'

class MotorsXYZ:
    """
    class to communicate with the motors at baudrate speed
    """
    def __init__(self, logger_name, baudrate=115200, timeout=4):
        self.logger = logging.getLogger(logger_name)

        self.logger_name = logger_name

        self._timeout = timeout
        self._baudrate = baudrate
        self._current_position =[-1.0,-1.0,-1.0]
        self._com_port = None ## self.scan_serial_ports()
        self.connected = False
        self._homed = False
        self.initialized = False
        self.ready = False
        self._busy = False
        self._alarm = False
        self.rangeXYZ = [0.0,0.0,0.0]
        self._axisLetter = [ 'X','Y', 'Z' ]
        self._last_move_duration = 0.0
        self._com = None
        self.com_port = None


    def _parse_hwid(self,hwid):
        dev=hwid.split()[0]
        nameVID = 'VID:PID='
        len_nameVID = len(nameVID)
        debVID =hwid.find('VID:PID=')+len_nameVID
        vid = hwid[debVID:debVID+4]
        pid = hwid[debVID+5:debVID+9]
##        print(f'hwid={hwid}')
##        print(f'vid={vid},pid={pid}')
        return dev,vid,pid


    def detect_com(self):
        finished=False
        error = False
        ok =False
        all_port_tuples = list_ports.comports()
        print(all_port_tuples)
        for port,desc, hwid in all_port_tuples:
            dev,vid,pid = self._parse_hwid(hwid)
            self.logger.info(f"port={port}\ndesc={desc}\ndev:{dev}, vid={vid},pid={pid}")
            if dev=='USB' and vid=='2341' and (pid=='0043' or pid=='0042'): # ARDUINO
                return port
        return None

    def connect(self, port='com11'):
        finished=False
        error = False
        ok =False
        if port: # port not None
            start_time=time.time()
            tooLong = False
            ser = serial.Serial(port, self._baudrate, timeout=self._timeout)
            line1=ser.readline()
            line2=ser.readline().decode('ascii',errors='ignore').strip().upper()
            print('second lines', line2)
            if line2.startswith('GRBL'):
                line3=ser.readline().decode('ascii',errors='ignore').strip()
                if line3[:1]=='[':
                    ok = True
                    self._com = ser
                    self.com_port = port
                    self.connected =True
                    self.logger.info('connected: {}, port: {}'.format(self.connected,port))
            else:
                ser.close()
        else:
            self.logger.error('error, no port detected')
        print('ok: ',ok,' error: ',error, ' tooLong: ',tooLong)
        print('Motor connected: ', self.connected)



    def _send_cmd(self,cmd):
        self._com.reset_output_buffer()
        self._com.reset_input_buffer()
        cmd+='\n'
        self.nb=self._com.write(cmd.encode('ascii'))

    def _read_ans(self,timeout=1):
        finished=False
        start_time=time.time()
        ans = ''
        while ( not finished ):
            line=self._com.readline().decode('ascii').strip()
            if line == 'ok':
                ok=True
                break
            else:
                ans = line
            finished = (time.time()-start_time)>timeout
        return ans

    def _read_params(self,timeout=4):
        ok = False
        if self.connected:
            self._busy = True
            finished=False
            start_time=time.time()
            cmd_params="$$"
            self._send_cmd(cmd_params)
            while ( not finished ):
                line=self._com.readline().decode('ascii').strip()
                if line == 'ok':
                    ok=True
                    break
                variable, value = line.split('=')
                if variable == '$130':
                    self.rangeXYZ[0]=float(value)
                if variable == '$131':
                    self.rangeXYZ[1]=float(value)
                if variable == '$132':
                    self.rangeXYZ[2]=float(value)
                finished = (time.time()-start_time)>timeout
        return ok

    def initialize(self):
        if not self.initialized:
            self.home()
            self.logger.debug('initialize')
            self._send_cmd('G91')
            ok=self._wait_for_ok()
            self._send_cmd('G21')
            self._wait_for_ok()
            self._send_cmd('F900')
            self._wait_for_ok()
            ok=self._read_params()
            self.logger.debug('rangeXYZ: {}'.format(self.rangeXYZ))
            if ok and not self._alarm:
                self.initialized = True
                self.ready = True
                self._send_cmd('$G')
                print('state: ', self._read_ans())

    def home(self,axis=['X','Y', 'Z'], together=True):
        self.logger.info('homing: $H')
        if self.connected:
            self._busy = True
            cmd_home="$H"
            if together:
                self._send_cmd(cmd_home)
                self.logger.debug(f'cmd_home: {cmd_home}')
                self._wait_for_ok(timeout=30)
            else:
                for axe in axis:
                    if axe in {'X','Y', 'Z'}:
                        cmd_home_axe = cmd_home + ' ' + axe
                        self._send_cmd(cmd_home_axe)
                        self._wait_for_ok(timeout=20)
            self.readPosition()
            self._busy = False
            if self._current_position[0]>= 0.0 and self._current_position[1]>= 0.0 and self._current_position[2]>= 0.0:
                self._homed=True
            else:
                self.raise_exception(1)
        else:
            self.raise_exception(0)

        # Reset zero to prevent error
        self.zero()

    def zero(self):
            self.logger.info('zeroing: G10 P0 L20 X0 Y0 Z0')
            self._send_cmd('G10 P0 L20 X0 Y0 Z0')
            self._wait_for_ok()

    def readPosition(self, forceRead=True, attempt = 0):
        if (forceRead):
            self._send_cmd("?")
            status_answer=self._com.readline()
            line = status_answer.decode('ascii')
            self.logger.debug('readPos: ' + line)
            
            try:
                split_str=re.split("[,:|]+", line[1:])
                self.status = split_str[0]
                mpos = split_str[1]
                self._current_position = [float(x) for x in split_str[2:5]]
            except:
                self.logger.debug('split_str: ' + ' '.join(split_str))
                self.logger.debug('Reading position failed. Try again.')
                
                if attempt < 5:
                    self.readPosition(attempt = attempt + 1)
                else:
                    self.logger.error('Reading position failed multiple times. Quitting.')
                
            self._wait_for_ok()
            msg = "Read current_position: {} ".format(self._current_position)
            self.logger.debug(msg)
        return self._current_position

    def _wait_for_ok(self,timeout=1):
        start_time=time.time()
        finished=False
        ok = False
        while ( not finished ):
            line=self._com.readline().decode('ascii').strip()
            self.logger.debug('line: {}'.format(line))
            if line == 'ok':
                ok=True
                break
            if line.upper().startswith('ERROR') or line.upper().startswith('ALARM'):
                self._alarm= True
                break
            finished = (time.time()-start_time)>timeout
        self.logger.debug('ok: {}'.format(ok))
        return ok

    def _wait_for_done(self,timeout=30):
        done=False
        if(self._wait_for_ok()):
            start_time=time.time()
            finished=False
            self._send_cmd('G4 P0')
            if(self._wait_for_ok(timeout=timeout)):
                done=True
        self.logger.debug('done: {}'.format(done))
        return done

    def wait_for_idle(self,timeout=30):
        start_time=time.time()
        finished=False
        ok = False
        while ( not finished ):
            pos=self.readPosition()
#            self.logger.debug('position: {:.3f}, {:.3f}, {:.3f} ; status: {}'.format(*pos,self.status))
            if self.status == 'Idle':
                ok=True
            time.sleep(0.05)
            timeout_error = (time.time()-start_time)>timeout
            finished = timeout_error or ok
        self.logger.debug('finished wait_for_idle; ok: {}, timeout_error: {}'.format(ok, timeout_error))
        return ok

    def moveAsync(self, XYZ, relative = True):
        if not self.ready :
            raise MotorError(self.logger_name, message="Motor not ready.")
        if relative:
            offsetXYZ=XYZ
            targetXYZ = [x+y for x,y in zip(self._current_position,offsetXYZ)]
        else:
            targetXYZ = XYZ
            offsetXYZ = [x-y for x,y in zip(targetXYZ,self._current_position)]
        self.logger.debug('target: {:.3f},{:.3f},{:.3f}; offset: {:.3f},{:.3f},{:.3f}'.format(*targetXYZ,*offsetXYZ))
        if self.isWithinRange(targetXYZ):
            offset = [round(x,3) if abs(x)>0.005 else 0.0 for x in offsetXYZ]
            move_cmd = 'G1 '
            for axe in range(len(offset)):
                if abs(offset[axe])>0.0:
                    move_cmd += "{}{:.3f}".format(self._axisLetter[axe], offset[axe])
            self.logger.debug('offset: {}, move_cmd: {}'.format(offset,move_cmd))
            self._send_cmd(move_cmd)
            ok=self._wait_for_ok()
            if not ok:
                raise MotorError(self.logger_name, message="error in motion: {}".format(move_cmd))
            self.readPosition()
        else:
            raise MotorError(self.logger_name, message="motion out of range: {}".format(targetXYZ))

    def move(self, XYZ, relative = True):
        if not self.ready :
            raise MotorError(self.logger_name, message="Motor not ready.")
        if relative:
            offsetXYZ=XYZ
            targetXYZ = [x+y for x,y in zip(self._current_position,offsetXYZ)]
        else:
            targetXYZ = XYZ
            offsetXYZ = [x-y for x,y in zip(targetXYZ,self._current_position)]
        if self.isWithinRange(targetXYZ):
            offset = [round(x,3) if abs(x)>0.005 else 0.0 for x in offsetXYZ]
            move_cmd = 'G1'
            for axe in range(len(offset)):
                if abs(offset[axe])>0.0:
                    move_cmd += " {}{:.3f}".format(self._axisLetter[axe], offset[axe])
            self.logger.debug('offset: {}, move_cmd: {}'.format(offset,move_cmd))
            self._send_cmd(move_cmd)
            ok=self._wait_for_ok()
            done=self.wait_for_idle()
            if not done:
                raise MotorError(self.logger_name, message="error in motion: {}".format(move_cmd))
            self.readPosition()
        else:
            raise MotorError(self.logger_name, message="motion out of range: {}".format(targetXYZ))

    def isWithinRange(self,destXYZ):
        ok = True
        for i in range(len(destXYZ)):
            ok = ok and -1*self.rangeXYZ[i]<=destXYZ[i]<=0.0
        return ok

    def print_ans(self):
        for line in self.ans:
            print(line.decode('ascii'))

    def raise_exception(self,i):
        raise MotorError(self.logger_name, i, MotorErrorCode[i])


    def disconnect(self):
        self.connected = False
        self._homed = False
        self.initialized = False
        self.ready = False
        self._com.close()


def test_parse_pos():
    line='<Idle|MPos:10.000,0.000,0.000|FS:0,0|WCO:0.000,0.000,0.000>'
    split_str=re.split("[,:|]+", line[1:])
    print(split_str)
    status = split_str[0]
    mpos = split_str[1]
    currentPos = [float(x) for x in split_str[2:5]]
    print('status: {}, MPos: {}, X: {:.3f},  Y: {:.3f}, Z: {:.3f}'.format(status,mpos,*currentPos))


def main():
    myMotor = MotorsXYZ('')
    myMotor.logger.info(myMotor.com_port)
    port=myMotor.detect_com()
    myMotor.logger.info(port)
    try:
        myMotor.connect()
        myMotor.initialize()
        myMotor._read_params()
        myMotor.logger.info('myMotor.rangeXYZ: ', myMotor.rangeXYZ)
        myMotor.logger.info('myMotor.currentPos: ', myMotor.readPosition(forceRead=False))
        myMotor.logger.info('myMotor.initialized: ', myMotor.initialized)
        myMotor.move([17.35,24.45,12.21], relative=False)
        myMotor.move([-2.0,+4.0,-3.50])
    finally:
        myMotor.disconnect()
##    print("is in range 10.0,10.0,200.1: ",myMotor.isWithinRange([10.0,10.0,200.1]))
##    print("is in range -0.1,200.0,199.0: ",myMotor.isWithinRange([-0.1,200.0,199.0]))
##    print("is in range -0.0,200.0,199.0: ",myMotor.isWithinRange([-0.0,200.0,199.0]))
##    myMotor.moveAbs([17.35,24.45,12.21])
##    myMotor.moveAbs([8.18,32.71,15.49])
##    myMotor.moveRel([-2.0,+4.0,-3.50])
##    myMotor.moveAbs([30.0,40.0,200.1])
##    for i in range(5):
##        try:
##                myMotor.raise_exception(i)
##        except MotorError as e:
##            print('except MotorError {}: {}'.format(e.code,e.message))


if __name__ == '__main__':
##    test_parse_pos()
    main()

