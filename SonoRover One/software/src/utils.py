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

import time
import unifus
import logging

class ExecListener(unifus.FUSListener):
	"""
	A listener class used to illustrate how to receive events sent by the FUS object,
	and also how to wait for the end of an execution properly.
	"""

	def __init__(self):
		unifus.FUSListener.__init__(self)
		self._connecting = False
		# for ultrasounds
		self._running = False
		self.pulseResults = []
		self.execResult = None
		# for mechanics
		self._findingOrigin = False
		self._moving = False
		self.mechResult = None

	def onConnectStart (self):
		self._connecting = True
		print ("Listener: CONNECTING")

	def onConnectResult (self, result):
		self._connecting = False
		if result == unifus.ConnectResult.Success:
			print ("Listener: CONNECTED")
		else:
			print ("Listener: CONNECTION FAILED (%s)" % str(result))

	def onDisconnect (self, reason):
		self._running = False
		print ("Listener: DISCONNECTED (%s)" % str(reason))

	def onSequenceStart (self, execID, buffer, count, delay, flags):
		self._running = True
		self.pulseResults = []
		print ("Listener: EXEC START (buff: %d, count: %d, delay: %g)" % (buffer, count, delay))

	def onPulseResult (self, result):
		self.pulseResults.append (result)
		print ("Listener: PULS RESULT (exec: %d, pulse: %d, duration: %g ms, elapsed: %g ms)" %
			(result.execIndex(), result.pulseIndex(), result.duration(), result.msFromStart()))
		measures = result.sharedMeasurements()
		if measures is not None:
			print ("          Available: %d measures for %d board(s), %d measures for %d channel(s)" %
				(measures.boardMeasureCount(), measures.boardCount(), measures.channelMeasureCount(), measures.channelCount()))
			for channel in range(measures.channelCount()):
				# Note: it is advised to call measures.physicalChannelMeasureAvailable(measure) to check
				# before calling .channelPhysicalValue (channel, measure).
				if measures.channelMeasureCount() == 5:
					print ("    ch[%d] V=%#4.3g V, I=%#4.3g A, PhaseV/I=%#4.3g°, PhaseV/Vref=%#5.4g°, Freq=%7d Hz, Pow=%#g W" % (channel,
						measures.channelPhysicalValue (channel, 0), measures.channelPhysicalValue (channel, 1),
						measures.channelPhysicalValue (channel, 2), measures.channelPhysicalValue (channel, 3),
						measures.channelRawValue (channel, 4), measures.power(channel)))
				else:
					# TODO: improve this!
					logger = logging.getLogger('equipment_characterization_pipeline')
					logger.info ("    ch[%d] Vfwd=%#4.3g V, Vrev=%#4.3g V, PhaseV/Vref=%#5.4g°, Freq=%7d Hz, Pow=%#g W" % (channel,
						measures.channelPhysicalValue (channel, 0), measures.channelPhysicalValue (channel, 1),
						measures.channelPhysicalValue (channel, 2), measures.channelRawValue (channel, 3), measures.power(channel)))
		
	def onSequenceResult (self, execID, execIndex, pulseIndex, errorCode):
		self._running = False
		if errorCode == 0:
			print ("Listener: EXEC RESULT SUCCESS (exec: %d)" % (execIndex))
		else:
			print ("Listener: EXEC RESULT ERROR (code: %d, on exec: %d, pulse: %d)" % (errorCode, execIndex, pulseIndex))

	def onMechOriginStart (self):
		self._findingOrigin = True
		print ("Listener: START  finding mech origins")

	def onMechOriginResult (self, result, msg):
		self._findingOrigin = False
		print ("Listener: RESULT finding mech origins: %s (%s)" % (result.name, msg))
	
	def onMechStart (self, execID, count):
		self._moving = True
		self.mechResult = None
		print ("Listener: START  motion (id: %d, count: %d)" % (execID, count))

	def onMechResult (self, execID, result, errorCode):
		self._moving = False
		self.mechResult = result
		if errorCode == 0:
			print ("Listener: RESULT motion success (id: %d)" % (execID))
		else:
			print ("Listener: RESULT motion error (id: %d, code: %d, result: %s)" % (execID, errorCode, str(result)))


	def waitConnection (self, timeout=5.0):
		maxWait = time.time() + timeout
		while True:
			time.sleep(0.2)
			if not self._connecting:
				return True
			if time.time() > maxWait:
				return False

	def waitSequence (self, timeout=5.0):
		"""Wait until the current ultrasound sequence is finished, or specified timeout in seconds."""
		maxWait = time.time() + timeout
		# Start with a sleep to make sure the start event has been received
		# and _running has been set to true.
		while True:
			time.sleep(0.010)
			if not self._running:
				return
			if time.time() > maxWait:
				return False
	
	def waitOrigins (self, timeout=20.0):
		"""Wait until the mechanical origins are found, or specified timeout in seconds."""
		maxWait = time.time() + timeout
		# Start with a sleep to make sure the start event has been received
		# and _moving has been set to true.
		while True:
			time.sleep(0.2)
			if not self._findingOrigin:
				return
			if time.time() > maxWait:
				return False
	
	def waitMotion (self, timeout=30.0):
		"""Wait until the current motion is finished, or specified timeout in seconds."""
		maxWait = time.time() + timeout
		# Start with a sleep to make sure the start event has been received
		# and _moving has been set to true.
		while True:
			time.sleep(0.050)# modified by Erik
			if not self._moving:
				return
			if time.time() > maxWait:
				return False


	def printExecResult (self):
		msg = "Execution result: "
		if self.execResult is None:
			msg += "Nothing received"
		elif self.execResult.isError():
			msg += "ERROR\n"
			msg += "  code: %d / %s\n" % (self.execResult.status(), self.execResult.statusName())
			msg += "  message: " + self.execResult.errorMessage()
		else:
			msg += "SUCCESS"
		print (msg)
