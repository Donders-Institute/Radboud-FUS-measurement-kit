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

#-------------------------------------------------------------------------------
# Name:        pico
# Purpose:     connect and control a picoscope
#
# Author:      Frederic Salabartan
#
# Created:     05/11/2018
# Copyright:   (c) Image Guided Therapy

#-------------------------------------------------------------------------------

"""Python interface to control Pico Technology's suite of oscilloscopes."""

import os
import time
from ctypes import windll, c_int16, c_uint16, c_int32, c_void_p, c_float, c_uint32, byref, POINTER, sizeof, create_string_buffer, CFUNCTYPE
#, pointer, CFUNCTYPE
import numpy

# Note on Picoscope function calls:
# Every call to a Pico C-API function must be preceded by a comment containing the function signature.
# This is required in order to use checkAPI.py script to check for consistency and detect API changes.
# For functions called in the common part (in Scope abstract class), function names must start with
# "ps????", and in those signatures, usually enums are model-specific (PS3000A_xxx, PS4000_xxx, ...)
# in which case you can replace their type by "enum". Same thing for struct pointers with "struct*".
# Of course, for the check to be meaningfull you have to make sure that the values passed as arguments
# do match the types in the comment.

# The Pico API uses a lot of enums as arguments, the value passed for them should be a c_int32 in calls.

# Note from ctypes
# None, integers, longs, byte strings and unicode strings are the only native Python objects that can
# directly be used as parameters in function calls.
# - None is passed as a C NULL pointer,
# - byte strings and unicode strings are passed as pointer to the memory block that contains their data (char * or wchar_t *).
# - Python integers/longs are passed as the platforms default C int type, their value is masked to fit into the C type.

version = (1, 3, 0)
"""Module version as a tuple of integers (major, minor, bugfix)."""

versionstr = ".".join(map(str,version))
"""Module version as a string "major.minor.bugfix"."""


LOG_NONE = 0       # no message at all
LOG_WARNING = 10   # only warnings
LOG_VERBOSE = 100  # all messages
# Global flag to control the use of print()s
_LOG_LEVEL = LOG_WARNING
def setLogLevel(level):
	global _LOG_LEVEL
	_LOG_LEVEL = level


UNIT_INFOS = {
	"PICO_DRIVER_VERSION"   : 0,
	"PICO_USB_VERSION"      : 1,
	"PICO_HARDWARE_VERSION" : 2,
	"PICO_VARIANT_INFO"     : 3,
	"PICO_BATCH_AND_SERIAL" : 4,
	"PICO_CAL_DATE"         : 5,
	"PICO_KERNEL_VERSION"   : 6
}


class PicoscopeModel(object):
	Name = { 0:'3204A', 1:'3204D', 2:'4226', 3:'5242', 4:'5442', 5:'dummy' }
	Number = { v: k for k, v in Name.items() }


class Resolution(object):
	DR_8BIT  = 0
	DR_12BIT = 1
	DR_14BIT = 2
	DR_15BIT = 3
	DR_16BIT = 4

	@staticmethod
	def inBits(res):
		"""Returns the resolution in number of bits.
		:param res: a resolution, one of Resolution.DR_*.
		:return: an integer, the number of bits.
		:raise: PicoError if the resolution is not supported."""
		try:
			return (8, 12, 14, 15, 16)[res]
		except:
			raise PicoError("Unsupported resolution (%s)." % str(res))


class Channel(object):
	A    = 0
	B    = 1
	C    = 2
	D    = 3
	EXT  = 4
	LAST = EXT
	#AUX  = 5

	NAME = { A : "A", B : "B", C : "C", D : "D", EXT : "EXT" }

def channelName (ch):
	"""
	Returns the name of the given channel.

	:param ch: one of Channel.A-.D or .EXT.
	:return: (string) the name of the channel.
	"""
	if ch in Channel.NAME:
		return Channel.NAME[ch]
	return "Channel%s" % str(ch)


class Probe(object):
	"""Probe attenuation."""
	MIN = 0
	x1  = 0
	x10 = 1
	MAX = 2


class Coupling(object):
	MIN = 0
	AC  = 0
	DC  = 1
	MAX = 2


class Range(object):
	"""Range for channels acquisition, based on signal value (ignoring attenuation)."""
	# TODO: Warning changing the min. range available this way breaks compatibility:
	#   all models do not share the same limits anymore!
	# It seems necessary to introduce a new method in Scope class to ask for min/max range,
	# based on model and probe. And then to remove PROBE_MIN and PROBE_MAX here.
	# Fix the implementation of ChannelSettings.init().

	RANGE_10mV  =  0  # [-10, +10] mV, only with Probe.x1, not available on 3000, 4000 series
	RANGE_20mV  =  1  # [-20, +20] mV, only with Probe.x1, not available on 3000, 4000 series
	RANGE_50mV  =  2  # [-50, +50] mV, only with Probe.x1
	RANGE_100mV =  3  # [-0.1, +0.1] V
	RANGE_200mV =  4  # [-0.2, +0.2] V
	RANGE_500mV =  5  # [-0.5, +0.5] V
	RANGE_1V    =  6  # [-1, +1] V
	RANGE_2V    =  7  # [-2, +2] V
	RANGE_5V    =  8  # [-5, +5] V
	RANGE_10V   =  9  # [-10, +10] V
	RANGE_20V   = 10  # [-20, +20] V
	RANGE_50V   = 11  # [-50, +50] V,   only with Probe.x10
	RANGE_100V  = 12  # [-100, +100] V, only with Probe.x10
	RANGE_200V  = 13  # [-200, +200] V, only with Probe.x10
	MAX = 14

	PROBE_MIN = { Probe.x1 : RANGE_10mV, Probe.x10 : RANGE_100mV }
	PROBE_MAX = { Probe.x1 : RANGE_20V,  Probe.x10 : RANGE_200V }

	# Width in Volt for all ranges
	WIDTH = {
		RANGE_10mV : 0.02,
		RANGE_20mV : 0.04,
		RANGE_50mV : 0.1,
		RANGE_100mV: 0.2,
		RANGE_200mV: 0.4,
		RANGE_500mV: 1.0,
		RANGE_1V   : 2.0,
		RANGE_2V   : 4.0,
		RANGE_5V   : 10.0,
		RANGE_10V  : 20.0,
		RANGE_20V  : 40.0,
		RANGE_50V  : 100.0,
		RANGE_100V : 200.0,
		RANGE_200V : 400.0
	}

	# Upper bound voltage for all ranges
	RANGE_VALUES = {
		0.01 : 0,
		0.02 : 1,
		0.05 : 2,
		0.10 : 3,
		0.20 : 4,
		0.50 : 5,
		1.00 : 6,
		2.00 : 7,
		5.00 : 8,
		10.0 : 9,
		20.0 : 10,
		50.0 : 11,
		100.0: 12,
		200.0: 13
	}

	UPPER_BOUND = {
		RANGE_10mV : 0.01,
		RANGE_20mV : 0.02,
		RANGE_50mV : 0.05,
		RANGE_100mV: 0.1,
		RANGE_200mV: 0.2,
		RANGE_500mV: 0.5,
		RANGE_1V   : 1.0,
		RANGE_2V   : 2.0,
		RANGE_5V   : 5.0,
		RANGE_10V  : 10.0,
		RANGE_20V  : 20.0,
		RANGE_50V  : 50.0,
		RANGE_100V : 100.0,
		RANGE_200V : 200.0
	}


class ETSMode(object):
	OFF  = 0
	FAST = 1
	SLOW = 2


class TimeUnits(object):
	FS = 0
	PS = 1
	NS = 2
	US = 3
	MS = 4
	S  = 5


class SweepType(object):
	UP      = 0
	DOWN    = 1
	UP_DOWN = 2
	DOWN_UP = 3


class Generator(object):
	class Wave(object):
		# Basic built-in wave types
		SINE        = 0
		SQUARE      = 1
		TRIANGLE    = 2
		RAMP_UP     = 3
		RAMP_DOWN   = 4
		SINC        = 5
		GAUSSIAN    = 6
		HALF_SINE   = 7
		DC_VOLTAGE  = 8
		WHITE_NOISE = 9
		LAST_3000   = DC_VOLTAGE
		LAST_4000   = WHITE_NOISE

		# Extended (arbitrary) wave types
		ARB_ES_OFF      = 0  # normal signal generator operation specified by wavetype
		ARB_WHITE_NOISE = 1  # White noise (pkToPk, offsetVoltage)
		ARB_PRBS        = 2  # Random Bit Stream

		MIN_FREQUENCY = 0.03
		MAX_FREQUENCY = 1e6

	class TriggerType(object):
		RISING    = 0
		FALLING   = 1
		GATE_HIGH = 2
		GATE_LOW  = 3

	class TriggerSource(object):
		NONE        = 0
		SCOPE_TRIG  = 1
		AUX_IN      = 2
		EXT_IN      = 3
		SOFT_TRIG   = 4
		TRIGGER_RAW = 5


class IndexMode(object):
	SINGLE = 0
	DUAL   = 1
	QUAD   = 2


class Trigger(object):  # this is called threshold in Pico docs
	MODE_LEVEL  = 0
	MODE_WINDOW = 1

	class Direction(object):
		ABOVE             = 0
		BELOW             = 1
		RISING            = 2
		FALLING           = 3
		RISING_OR_FALLING = 4  # last value usable with initTrigger()
		ABOVE_LOWER       = 5
		BELOW_LOWER       = 6
		RISING_LOWER      = 7
		FALLING_LOWER     = 8
		# Windowing using both thresholds
		INSIDE            = ABOVE
		OUTSIDE           = BELOW
		ENTER             = RISING
		EXIT              = FALLING
		ENTER_OR_EXIT     = RISING_OR_FALLING
		POSITIVE_RUNT     = 9
		NEGATIVE_RUNT     = 10
		# no trigger set
		NONE              = RISING


class RatioMode(object):
	"""Used in GetValues()."""
	NONE      = 0

	# Reduces every block of nvalues to just two values: a minimum and a maximum.
	# The minimum and maximum values are returned in two separate buffers.
	AGGREGATE = 1

	# Reduces every block of nvalues to a single value representing the average
	# (arithmetic mean) of all the values.
	AVERAGE   = 2

	# Reduces every block of nvalues to just the first value in the block,
	# discarding all the other values.
	DECIMATE  = 4


class PulseWidth(object):
	"""Used in SetPulseWidthQualifier()."""
	PW_TYPE_NONE         = 0
	PW_TYPE_LESS_THAN    = 1
	PW_TYPE_GREATER_THAN = 2
	PW_TYPE_IN_RANGE     = 3
	PW_TYPE_OUT_OF_RANGE = 4


class Status(object):
	"""The possible codes returned by the Pico API functions."""
	@staticmethod
	def message(code):
		"""Returns the message corresponding to the code."""
		if code in Status.MESSAGES:
			return Status.MESSAGES[code]
		return "Unknown code (%d)" % code

	@staticmethod
	def name(code):
		"""Returns the code name as a string.

		:param int code: a status code returned by a Pico function."""
		if not hasattr(Status, "NAMES"):
			# the first time this function is called, create a dict NAMES = { code : "code" }
			#print ("building NAMES")
			Status.NAMES = {}
			for c in dir(Status):
				if c[:5] == "PICO_":
					Status.NAMES[getattr(Status, c)] = c
		return Status.NAMES[code]

	PICO_OK                                         = 0x000
	PICO_MAX_UNITS_OPENED                           = 0x001
	PICO_MEMORY_FAIL                                = 0x002
	PICO_NOT_FOUND                                  = 0x003
	PICO_FW_FAIL                                    = 0x004
	PICO_OPEN_OPERATION_IN_PROGRESS                 = 0x005
	PICO_OPERATION_FAILED                           = 0x006
	PICO_NOT_RESPONDING                             = 0x007
	PICO_CONFIG_FAIL                                = 0x008
	PICO_KERNEL_DRIVER_TOO_OLD                      = 0x009
	PICO_EEPROM_CORRUPT                             = 0x00A
	PICO_OS_NOT_SUPPORTED                           = 0x00B
	PICO_INVALID_HANDLE                             = 0x00C
	PICO_INVALID_PARAMETER                          = 0x00D
	PICO_INVALID_TIMEBASE                           = 0x00E
	PICO_INVALID_VOLTAGE_RANGE                      = 0x00F
	PICO_INVALID_CHANNEL                            = 0x010
	PICO_INVALID_TRIGGER_CHANNEL                    = 0x011
	PICO_INVALID_CONDITION_CHANNEL                  = 0x012
	PICO_NO_SIGNAL_GENERATOR                        = 0x013
	PICO_STREAMING_FAILED                           = 0x014
	PICO_BLOCK_MODE_FAILED                          = 0x015
	PICO_NULL_PARAMETER                             = 0x016
	PICO_ETS_MODE_SET                               = 0x017
	PICO_DATA_NOT_AVAILABLE                         = 0x018
	PICO_STRING_BUFFER_TOO_SMALL                    = 0x019
	PICO_ETS_NOT_SUPPORTED                          = 0x01A
	PICO_AUTO_TRIGGER_TIME_TOO_SHORT                = 0x01B
	PICO_BUFFER_STALL                               = 0x01C
	PICO_TOO_MANY_SAMPLES                           = 0x01D
	PICO_TOO_MANY_SEGMENTS                          = 0x01E
	PICO_PULSE_WIDTH_QUALIFIER                      = 0x01F
	PICO_DELAY                                      = 0x020
	PICO_SOURCE_DETAILS                             = 0x021
	PICO_CONDITIONS                                 = 0x022
	PICO_USER_CALLBACK                              = 0x023
	PICO_DEVICE_SAMPLING                            = 0x024
	PICO_NO_SAMPLES_AVAILABLE                       = 0x025
	PICO_SEGMENT_OUT_OF_RANGE                       = 0x026
	PICO_BUSY                                       = 0x027
	PICO_STARTINDEX_INVALID                         = 0x028
	PICO_INVALID_INFO                               = 0x029
	PICO_INFO_UNAVAILABLE                           = 0x02A
	PICO_INVALID_SAMPLE_INTERVAL                    = 0x02B
	PICO_TRIGGER_ERROR                              = 0x02C
	PICO_MEMORY                                     = 0x02D
	PICO_SIG_GEN_PARAM                              = 0x02E
	PICO_SHOTS_SWEEPS_WARNING                       = 0x02F
	PICO_SIGGEN_TRIGGER_SOURCE                      = 0x030
	PICO_AUX_OUTPUT_CONFLICT                        = 0x031
	PICO_AUX_OUTPUT_ETS_CONFLICT                    = 0x032
	PICO_WARNING_EXT_THRESHOLD_CONFLICT             = 0x033
	PICO_WARNING_AUX_OUTPUT_CONFLICT                = 0x034
	PICO_SIGGEN_OUTPUT_OVER_VOLTAGE                 = 0x035
	PICO_DELAY_NULL                                 = 0x036
	PICO_INVALID_BUFFER                             = 0x037
	PICO_SIGGEN_OFFSET_VOLTAGE                      = 0x038
	PICO_SIGGEN_PK_TO_PK                            = 0x039
	PICO_CANCELLED                                  = 0x03A
	PICO_SEGMENT_NOT_USED                           = 0x03B
	PICO_INVALID_CALL                               = 0x03C
	PICO_GET_VALUES_INTERRUPTED                     = 0x03D
	PICO_NOT_USED                                   = 0x03F
	PICO_INVALID_SAMPLERATIO                        = 0x040
	PICO_INVALID_STATE                              = 0x041
	PICO_NOT_ENOUGH_SEGMENTS                        = 0x042
	PICO_DRIVER_FUNCTION                            = 0x043
	PICO_INVALID_COUPLING                           = 0x045
	PICO_BUFFERS_NOT_SET                            = 0x046
	PICO_RATIO_MODE_NOT_SUPPORTED                   = 0x047
	PICO_RAPID_NOT_SUPPORT_AGGREGATION              = 0x048
	PICO_INVALID_TRIGGER_PROPERTY                   = 0x049
	PICO_INTERFACE_NOT_CONNECTED                    = 0x04A
	PICO_SIGGEN_WAVEFORM_SETUP_FAILED               = 0x04D
	PICO_FPGA_FAIL                                  = 0x04E
	PICO_POWER_MANAGER                              = 0x04F
	PICO_INVALID_ANALOGUE_OFFSET                    = 0x050
	PICO_PLL_LOCK_FAILED                            = 0x051
	PICO_ANALOG_BOARD                               = 0x052
	PICO_CONFIG_FAIL_AWG                            = 0x053
	PICO_INITIALISE_FPGA                            = 0x054
	PICO_EXTERNAL_FREQUENCY_INVALID                 = 0x056
	PICO_CLOCK_CHANGE_ERROR                         = 0x057
	PICO_TRIGGER_AND_EXTERNAL_CLOCK_CLASH           = 0x058
	PICO_PWQ_AND_EXTERNAL_CLOCK_CLASH               = 0x059
	PICO_UNABLE_TO_OPEN_SCALING_FILE                = 0x05A
	PICO_MEMORY_CLOCK_FREQUENCY                     = 0x05B
	PICO_I2C_NOT_RESPONDING                         = 0x05C
	PICO_NO_CAPTURES_AVAILABLE                      = 0x05D
	PICO_NOT_USED_IN_THIS_CAPTURE_MODE              = 0x05E
	PICO_GET_DATA_ACTIVE                            = 0x103
	PICO_IP_NETWORKED                               = 0x104
	PICO_INVALID_IP_ADDRESS                         = 0x105
	PICO_IPSOCKET_FAILED                            = 0x106
	PICO_IPSOCKET_TIMEDOUT                          = 0x107
	PICO_SETTINGS_FAILED                            = 0x108
	PICO_NETWORK_FAILED                             = 0x109
	PICO_WS2_32_DLL_NOT_LOADED                      = 0x10A
	PICO_INVALID_IP_PORT                            = 0x10B
	PICO_COUPLING_NOT_SUPPORTED                     = 0x10C
	PICO_BANDWIDTH_NOT_SUPPORTED                    = 0x10D
	PICO_INVALID_BANDWIDTH                          = 0x10E
	PICO_AWG_NOT_SUPPORTED                          = 0x10F
	PICO_ETS_NOT_RUNNING                            = 0x110
	PICO_SIG_GEN_WHITENOISE_NOT_SUPPORTED           = 0x111
	PICO_SIG_GEN_WAVETYPE_NOT_SUPPORTED             = 0x112
	PICO_INVALID_DIGITAL_PORT                       = 0x113
	PICO_INVALID_DIGITAL_CHANNEL                    = 0x114
	PICO_INVALID_DIGITAL_TRIGGER_DIRECTION          = 0x115
	PICO_SIG_GEN_PRBS_NOT_SUPPORTED                 = 0x116
	PICO_ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS      = 0x117
	PICO_WARNING_REPEAT_VALUE                       = 0x118
	PICO_POWER_SUPPLY_CONNECTED                     = 0x119
	PICO_POWER_SUPPLY_NOT_CONNECTED                 = 0x11A
	PICO_POWER_SUPPLY_REQUEST_INVALID               = 0x11B
	PICO_POWER_SUPPLY_UNDERVOLTAGE                  = 0x11C
	PICO_CAPTURING_DATA                             = 0x11D
	PICO_USB3_0_DEVICE_NON_USB3_0_PORT              = 0x11E
	PICO_NOT_SUPPORTED_BY_THIS_DEVICE               = 0x11F
	PICO_INVALID_DEVICE_RESOLUTION                  = 0x120
	PICO_INVALID_NUMBER_CHANNELS_FOR_RESOLUTION     = 0x121
	PICO_CHANNEL_DISABLED_DUE_TO_USB_POWERED        = 0x122
	PICO_SIGGEN_DC_VOLTAGE_NOT_CONFIGURABLE         = 0x123
	PICO_NO_TRIGGER_ENABLED_FOR_TRIGGER_IN_PRE_TRIG = 0x124
	PICO_TRIGGER_WITHIN_PRE_TRIG_NOT_ARMED          = 0x125
	PICO_TRIGGER_WITHIN_PRE_NOT_ALLOWED_WITH_DELAY  = 0x126
	PICO_TRIGGER_INDEX_UNAVAILABLE                  = 0x127
	PICO_AWG_CLOCK_FREQUENCY                        = 0x128
	PICO_TOO_MANY_CHANNELS_IN_USE                   = 0x129
	PICO_NULL_CONDITIONS                            = 0x12A
	PICO_DUPLICATE_CONDITION_SOURCE                 = 0x12B
	PICO_INVALID_CONDITION_INFO                     = 0x12C
	PICO_SETTINGS_READ_FAILED                       = 0x12D
	PICO_SETTINGS_WRITE_FAILED                      = 0x12E
	PICO_ARGUMENT_OUT_OF_RANGE                      = 0x12F
	PICO_HARDWARE_VERSION_NOT_SUPPORTED             = 0x130
	PICO_DIGITAL_HARDWARE_VERSION_NOT_SUPPORTED     = 0x131
	PICO_ANALOGUE_HARDWARE_VERSION_NOT_SUPPORTED    = 0x132
	PICO_UNABLE_TO_CONVERT_TO_RESISTANCE            = 0x133
	PICO_DUPLICATED_CHANNEL                         = 0x134
	PICO_INVALID_RESISTANCE_CONVERSION              = 0x135
	PICO_INVALID_VALUE_IN_MAX_BUFFER                = 0x136
	PICO_INVALID_VALUE_IN_MIN_BUFFER                = 0x137
	PICO_SIGGEN_FREQUENCY_OUT_OF_RANGE              = 0x138
	PICO_EEPROM2_CORRUPT                            = 0x139
	PICO_EEPROM2_FAIL                               = 0x13A
	PICO_DEVICE_TIME_STAMP_RESET                    = 0x01000000
	PICO_WATCHDOGTIMER                              = 0x10000000
	PICO_CUSTOM_ERROR                               = 0xFF00FF

	MESSAGES = {
		PICO_OK                                         : "The PicoScope is functioning correctly",
		PICO_MAX_UNITS_OPENED                           : "An attempt has been made to open more than PS3000A_MAX_UNITS.",
		PICO_MEMORY_FAIL                                : "Not enough memory could be allocated on the host machine",
		PICO_NOT_FOUND                                  : "No PicoScope could be found",
		PICO_FW_FAIL                                    : "Unable to download firmware",
		PICO_OPEN_OPERATION_IN_PROGRESS                 : "The driver is busy opening a device.",
		PICO_OPERATION_FAILED                           : "An unspecified error occurred.",
		PICO_NOT_RESPONDING                             : "The PicoScope is not responding to commands from the PC",
		PICO_CONFIG_FAIL                                : "The configuration information in the PicoScope has become corrupt or is missing",
		PICO_KERNEL_DRIVER_TOO_OLD                      : "The picopp.sysfile is too old to be used with the device driver",
		PICO_EEPROM_CORRUPT                             : "The EEPROM has become corrupt, so the device will use a default setting",
		PICO_OS_NOT_SUPPORTED                           : "The operating system on the PC is not supported by this driver",
		PICO_INVALID_HANDLE                             : "There is no device with the handle value passed",
		PICO_INVALID_PARAMETER                          : "A parameter value is not valid",
		PICO_INVALID_TIMEBASE                           : "The timebase is not supported or is invalid",
		PICO_INVALID_VOLTAGE_RANGE                      : "The voltage range is not supported or is invalid",
		PICO_INVALID_CHANNEL                            : "The channel number is not valid on this device or no channels have been set",
		PICO_INVALID_TRIGGER_CHANNEL                    : "The channel set for a trigger is not available on this device",
		PICO_INVALID_CONDITION_CHANNEL                  : "The channel set for a condition is not available on this device",
		PICO_NO_SIGNAL_GENERATOR                        : "The device does not have a signal generator",
		PICO_STREAMING_FAILED                           : "Streaming has failed to start or has stopped without user request",
		PICO_BLOCK_MODE_FAILED                          : "Block failed to start - a parameter may have been set wrongly",
		PICO_NULL_PARAMETER                             : "A parameter that was required is NULL",
		PICO_ETS_MODE_SET                               : "The function call failed because ETSmode is being used.",
		PICO_DATA_NOT_AVAILABLE                         : "No data is available from a run block call",
		PICO_STRING_BUFFER_TOO_SMALL                    : "The buffer passed for the information was too small",
		PICO_ETS_NOT_SUPPORTED                          : "ETS is not supported on this device variant",
		PICO_AUTO_TRIGGER_TIME_TOO_SHORT                : "The auto trigger time is less than the time it will take to collect the pre-trigger data",
		PICO_BUFFER_STALL                               : "The collection of data has stalled as unread data would be overwritten",
		PICO_TOO_MANY_SAMPLES                           : "Number of samples requested is more than available in the current memory segment",
		PICO_TOO_MANY_SEGMENTS                          : "Not possible to create number of segments requested",
		PICO_PULSE_WIDTH_QUALIFIER                      : "A null pointer has been passed in the trigger function or one of the parameters is out of range",
		PICO_DELAY                                      : "One or more of the hold-off parameters are out of range",
		PICO_SOURCE_DETAILS                             : "One or more of the source details are incorrect",
		PICO_CONDITIONS                                 : "One or more of the conditions are incorrect",
		PICO_USER_CALLBACK                              : "The driver's thread is currently in the ps3000a...Readycallback function and therefore the action cannot be carried out",
		PICO_DEVICE_SAMPLING                            : "An attempt is being made to get stored data while streaming. Either stop streaming by calling ps3000aStop,or use ps3000aGetStreamingLatestValues",
		PICO_NO_SAMPLES_AVAILABLE                       : "...because a run has not been completed",
		PICO_SEGMENT_OUT_OF_RANGE                       : "The memory index is out of range",
		PICO_BUSY                                       : "Data cannot be returned yet",
		PICO_STARTINDEX_INVALID                         : "The start time to get stored data is out of range",
		PICO_INVALID_INFO                               : "The information number requested is not a valid number",
		PICO_INFO_UNAVAILABLE                           : "The handle is invalid so no information is available about the device. Only PICO_DRIVER_VERSION is available.",
		PICO_INVALID_SAMPLE_INTERVAL                    : "The sample interval selected for streaming is out of range",
		PICO_TRIGGER_ERROR                              : "ETS is set but no trigger has been set. A trigger setting is required for ETS.",
		PICO_MEMORY                                     : "Driver cannot allocate memory",
		PICO_SIG_GEN_PARAM                              : "Error in signal generator parameter",
		PICO_SHOTS_SWEEPS_WARNING                       : "The signal generator will output the signal required but sweeps and shots will be ignored. Only one parameter can be non-zero.",
		PICO_SIGGEN_TRIGGER_SOURCE                      : "A software trigger has been sent but the trigger source is not a software trigger.",
		PICO_AUX_OUTPUT_CONFLICT                        : "A ps4000SetTrigger...call has found a conflict between the trigger source and the AUX output enable.",
		PICO_AUX_OUTPUT_ETS_CONFLICT                    : "ETSmode is being used and AUX is set as an input.",
		PICO_WARNING_EXT_THRESHOLD_CONFLICT             : "The EXT threshold is being set in both a ps4000SetTrigger... function and in the signal generator but the threshold values differ. The last value set will be used.",
		PICO_WARNING_AUX_OUTPUT_CONFLICT                : "A ps4000SetTrigger...function has set AUX as an output and the signal generator is using it as a trigger.",
		PICO_SIGGEN_OUTPUT_OVER_VOLTAGE                 : "The combined peak to peak voltage and the analog offset voltage exceed the allowable voltage the signal generator can produce",
		PICO_DELAY_NULL                                 : "NULLpointer passed as delay parameter",
		PICO_INVALID_BUFFER                             : "The buffers for overview data have not been set while streaming",
		PICO_SIGGEN_OFFSET_VOLTAGE                      : "The analog offset voltage is out of range",
		PICO_SIGGEN_PK_TO_PK                            : "The analog peak to peak voltage is out of range",
		PICO_CANCELLED                                  : "A block collection has been cancelled",
		PICO_SEGMENT_NOT_USED                           : "The segment index is not currently being used",
		PICO_INVALID_CALL                               : "The wrong GetValuesfunction has been called for the collection mode in use",
		PICO_GET_VALUES_INTERRUPTED                     : "PICO_GET_VALUES_INTERRUPTED",
		PICO_NOT_USED                                   : "The function is not available",
		PICO_INVALID_SAMPLERATIO                        : "The aggregationratio requested is out of range",
		PICO_INVALID_STATE                              : "Device is in an invalid state",
		PICO_NOT_ENOUGH_SEGMENTS                        : "The number of segments allocated is fewer than the number of captures requested",
		PICO_DRIVER_FUNCTION                            : "You called a driver function while another driver function was still being processed",
		PICO_INVALID_COUPLING                           : "An invalid coupling type was specified in ps3000aSetChannel",
		PICO_BUFFERS_NOT_SET                            : "An attempt was made to get data before a data bufferwas defined",
		PICO_RATIO_MODE_NOT_SUPPORTED                   : "The selected downsampling mode(used for data reduction) is not allowed",
		PICO_RAPID_NOT_SUPPORT_AGGREGATION              : "Aggregation was requested in rapid block mode.",
		PICO_INVALID_TRIGGER_PROPERTY                   : "An invalid parameter was passed to ps3000aSetTriggerChannelProperties",
		PICO_INTERFACE_NOT_CONNECTED                    : "The driver was unable to contact the oscilloscope",
		PICO_SIGGEN_WAVEFORM_SETUP_FAILED               : "A problem occurred in ps3000aSetSigGenBuiltInor ps3000aSetSigGenArbitrary",
		PICO_FPGA_FAIL                                  : "PICO_FPGA_FAIL",
		PICO_POWER_MANAGER                              : "PICO_POWER_MANAGER",
		PICO_INVALID_ANALOGUE_OFFSET                    : "An impossible analogue offset value was specified in ps3000aSetChannel",
		PICO_PLL_LOCK_FAILED                            : "Unable to configure the PicoScope",
		PICO_ANALOG_BOARD                               : "The oscilloscope's analog board is not detected, or is not connected to the digital board",
		PICO_CONFIG_FAIL_AWG                            : "Unable to configure the signal generator",
		PICO_INITIALISE_FPGA                            : "The FPGA cannot be initialized, so unit cannot be opened",
		PICO_EXTERNAL_FREQUENCY_INVALID                 : "The frequency for the external clock is not within ±5% of the stated value",
		PICO_CLOCK_CHANGE_ERROR                         : "The FPGA could not lock the clock signal",
		PICO_TRIGGER_AND_EXTERNAL_CLOCK_CLASH           : "You are trying to configure the AUX input as both a trigger and a reference clock",
		PICO_PWQ_AND_EXTERNAL_CLOCK_CLASH               : "You are trying to congfigure the AUX input as both a pulse width qualifier and a reference clock",
		PICO_UNABLE_TO_OPEN_SCALING_FILE                : "The scaling file set can not be opened.",
		PICO_MEMORY_CLOCK_FREQUENCY                     : "The frequency of the memory is reporting incorrectly.",
		PICO_I2C_NOT_RESPONDING                         : "The I2C that is being actioned is not responding to requests",
		PICO_NO_CAPTURES_AVAILABLE                      : "There are no captures available and therefore no data can be returned.",
		PICO_NOT_USED_IN_THIS_CAPTURE_MODE              : "The capture mode the device is currently running in does not support the current request.",
		PICO_GET_DATA_ACTIVE                            : "Reserved",
		PICO_IP_NETWORKED                               : "The device is currently connected via the IP Network socket and thus the call made is not supported.",
		PICO_INVALID_IP_ADDRESS                         : "An IP address that is not correct has been passed to the driver.",
		PICO_IPSOCKET_FAILED                            : "The IP socket has failed.",
		PICO_IPSOCKET_TIMEDOUT                          : "The IP socket has timed out.",
		PICO_SETTINGS_FAILED                            : "The settings requested have failed to be set.",
		PICO_NETWORK_FAILED                             : "The network connection has failed.",
		PICO_WS2_32_DLL_NOT_LOADED                      : "Unable to load the WS2 dll.",
		PICO_INVALID_IP_PORT                            : "The IP port is invalid",
		PICO_COUPLING_NOT_SUPPORTED                     : "The type of coupling requested is not supported on the opened variant.",
		PICO_BANDWIDTH_NOT_SUPPORTED                    : "Bandwidth limit is not supported on the opened variant.",
		PICO_INVALID_BANDWIDTH                          : "The value requested for the bandwidth limit is out of range.",
		PICO_AWG_NOT_SUPPORTED                          : "The arbitary waveform generator is not supported by the opened variant.",
		PICO_ETS_NOT_RUNNING                            : "Data has been requested with ETS mode set but run block has not been called, or stop has been called.",
		PICO_SIG_GEN_WHITENOISE_NOT_SUPPORTED           : "White noise is not supported on the opened variant.",
		PICO_SIG_GEN_WAVETYPE_NOT_SUPPORTED             : "The wave type requested is not supported by the opened variant.",
		PICO_INVALID_DIGITAL_PORT                       : "A port number that does not evaluate to either PS3000A_DIGITAL_PORT0 orPS3000A_DIGITAL_PORT1, the ports that are supported.",
		PICO_INVALID_DIGITAL_CHANNEL                    : "The digital channel is not in the range PS3000A_DIGITAL_CHANNEL0 to PS3000_DIGITAL_CHANNEL15, the digital channels that are supported.",
		PICO_INVALID_DIGITAL_TRIGGER_DIRECTION          : "The digital trigger direction is not a valid trigger direction and should be equal in value to one of the PS3000A_DIGITAL_DIRECTION enumerations.",
		PICO_SIG_GEN_PRBS_NOT_SUPPORTED                 : "Siggen does not generate pseudo-random bit stream.",
		PICO_ETS_NOT_AVAILABLE_WITH_LOGIC_CHANNELS      : "When a digital port is enabled, ETS sample mode is not available for use.",
		PICO_WARNING_REPEAT_VALUE                       : "Not applicable to this device.",
		PICO_POWER_SUPPLY_CONNECTED                     : "4-Channel only - The DC power supply is connected.",
		PICO_POWER_SUPPLY_NOT_CONNECTED                 : "4-Channel only - The DC power supply isn’t connected.",
		PICO_POWER_SUPPLY_REQUEST_INVALID               : "Incorrect power mode passed for current power source.",
		PICO_POWER_SUPPLY_UNDERVOLTAGE                  : "The supply voltage from the USB source is too low.",
		PICO_CAPTURING_DATA                             : "The oscilloscope is in the process of capturing data.",
		PICO_USB3_0_DEVICE_NON_USB3_0_PORT              : "A USB 3.0 device is connected to a non-USB 3.0 port.",
		PICO_NOT_SUPPORTED_BY_THIS_DEVICE               : "A function has been called that is not supported by the current device variant.",
		PICO_INVALID_DEVICE_RESOLUTION                  : "The device resolution is invalid (out of range).",
		PICO_INVALID_NUMBER_CHANNELS_FOR_RESOLUTION     : "The number of channels which can be enabled is limited in 15 and 16-bit modes",
		PICO_CHANNEL_DISABLED_DUE_TO_USB_POWERED        : "USB Power not sufficient to power all channels.",
	}


class PicoError(Exception):
	"""A simple name to catch it easily. Use .message to get the reason."""
	def __init__ (self, title, status=Status.PICO_CUSTOM_ERROR):
		"""
		:param str title: a text to insert at the beginning of the message
		:param int status: one of Status.PICO_*
		"""
		if status == Status.PICO_CUSTOM_ERROR:
			msg = title
		else:
			msg = title + "(" + Status.name(status) + ") " + Status.message(status)
		Exception.__init__(self, msg)
#


class ChannelSettings(object):
	def __init__ (self, channel):
		self.channel = channel
		self.overflow = False     # tells if an overflow occurred during last acquisition
		self.enabled = False
		self.range = None         # None or int (Range enum) : range of the signal as set by the user (not the Pico DLL value)
		self.coupling = None      # None or int (Coupling enum)
		self.probe = None         # None or int (Probe enum)
		self.disable()

	def init (self, vRange, coupling, probe):
		if probe < Probe.MIN or probe >= Probe.MAX:
			raise PicoError ("Invalid probe value (%s) for channel %s." % (str(probe), channelName(self.channel)))
		if coupling < Coupling.MIN or coupling >= Coupling.MAX:
			raise PicoError ("Invalid coupling value (%s) for channel %s." % (str(coupling), channelName(self.channel)))
		if vRange < Range.PROBE_MIN[probe]:
			raise PicoError ("Invalid range (lower than min) for the selected probe on channel %s (see Range comments)." % (channelName(self.channel)))
		if vRange > Range.PROBE_MAX[probe]:
			raise PicoError ("Invalid range (higher than max) for the selected probe on channel %s (see Range comments)." % (channelName(self.channel)))
		self.enabled = True
		self.range = vRange
		self.coupling = coupling
		self.probe = probe

	def disable (self):
		self.enabled = False
		self.probe = None
		self.overflow = False
		if self.channel != Channel.EXT:
			self.range = None
			self.coupling = None

	def picoRange (self):
		"""Returns the Pico DLL range value."""
		if self.probe == Probe.x1:
			return self.range
		elif self.probe == Probe.x10:
			return self.range - 3
		else:
			raise PicoError ("Invalid probe for channel %s." % channelName(self.channel))
#


class AcquisitionSettings(object):
	def __init__ (self):
		self.sampleCount = None  # None or int (a sample count)
		self.timebase = None     # None or int
		#self.clear()

	def clear (self):
		self.sampleCount = None  # None or int (a sample count)
		self.timebase = None     # None or int

	def init (self, samples, timebase):
		self.sampleCount = samples
		self.timebase = timebase
#


class ModelSpecification(object):
	def __init__ (self, model, dll, prefix):
		self.modelName = model             # (string) name of the PicoScope model, for ex. "3204A"
		self.dllName = dll                 # (string) name of the .dll file
		self.funcPrefix = prefix           # (string) prefix to
		self.channelCount = 0              # (int) total number of acquisition channels
		self.minADC = 0                    # (int) minimum ADC value (PS?000_MIN_VALUE)
		self.maxADC = 0                    # (int) maximum ADC value (PS?000_MAX_VALUE)
		self.dll = None                    # (None or ctype.LoadLibrary) loaded library
		self.handle = None                 # (None or ctype.int16_t) handle on the open device
		self.resolution = None             # (None or int) set on openUnit for models that support it
		self.maxGeneratorFrequency = 0     # (float) MAX_SIG_GEN_FREQ
		self.maxTimeBase = 0               # (int)
		self.maxHighSamplingRate = 0       # (float)
		self.maxLowSamplingRate = 0        # (float)
		self.EXTRange = 0                  # (int) fixed Range.? of the EXT input
		self.EXTmaxADC = 0                 # (int) maximum ADC value on the EXT channel (PS?000_EXT_MAX_VALUE)

		# Determine if we are in 32 or 64 bits mode
		self.platform = 32
		if sizeof(c_void_p()) == 8:
			self.platform = 64

		# First try to load the help DLL (PicoIpp) common for all models
		thisPath = os.path.dirname(__file__)
		helperDLLName = os.path.join(thisPath, "pico%d" % self.platform, "PicoIpp.dll")
		if not os.path.isfile(helperDLLName):
			raise PicoError ("Please install the PicoDLLs in the same directory as pico.py.")

		if not windll.LoadLibrary(helperDLLName):
			raise PicoError ("Can not load %s library." % helperDLLName)

		# Then the specific DLL for this model.
		self.dllName = os.path.join(thisPath, "pico%d" % self.platform, dll)
		self.dll = windll.LoadLibrary(self.dllName)
		if not self.dll:
			raise PicoError("Can not load %s library." % self.dllName)
#


StreamingReadyFunc = CFUNCTYPE(None, c_int16, c_int32, c_uint32, c_int16, c_uint32, c_int16, c_int16, c_void_p)

class AbstractStreamingCallBack(object):
	"""
	Abstract class to define call back method for streaming mode.
	"""

	def __init__(self, scope, scopeBuffers):
		self.scope = scope
		# does the streaming need to stop variable
		self.autoStop = False
		# application buffers. (one per scope channels)
		self.appBuffers = numpy.array([0]*len(self.scope.channelSettings), dtype=object)
		# scope buffers. (one per scope channels)
		self.scopeBuffers = scopeBuffers
		# number of samples reads
		self.sampleCount = 0
		# the callback function to be used by ps????GetStreamingLatestValues.
		self.callback = StreamingReadyFunc(self.streamingReady)

	def allocateAppBuffer(self, size):
		"""
		Allocate the application buffer.

		:param size: number of samples to store in the application buffer per active scope channel.
		:warning: this method needs to be called after opening at least one channel.
		"""
		for i, chSet in enumerate(self.scope.channelSettings):
			if chSet.enabled:
				self.appBuffers[i] = numpy.zeros(size, dtype=numpy.int16)

	def streamingReady(self, handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, pParameter):
		"""
		Callback method called when streaming mode data is ready.

		:param handle: the handle of the device returning the samples.
		:param noOfSamples: the number of samples to collect.
		:param startIndex: an index to the first valid sample in the buffer.
		:param overflow: returns a set of flags that indicate whether an overvoltage has occurred on any of the
			channels. It is a bit pattern with bit 0 denoting Channel A.
		:param triggerAt: an index to the buffer indicating the location of the trigger point relative to startIndex.
			This parameter is valid only when triggered is non-zero.
		:param triggered: a flag indicating whether a trigger occurred. If non- zero, a trigger occurred at the location
			indicated by triggerAt.
		:param autoStop: the flag that was set in the call to ps????RunStreaming.
		:param pParameter: flag to communicate the status to the application.
		"""
		raise NotImplementedError("streamingReady()")


class FullStreamingCallBack(AbstractStreamingCallBack):
	"""
	Save all data in application buffer until the end of the acquisition.
	"""
	def __init__(self, scope, scopeBuffers):
		super(FullStreamingCallBack, self).__init__(scope, scopeBuffers)
		self.currentIndex = 0

	def streamingReady(self, handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, pParameter):
		"""
		Callback method called when streaming mode data is ready.

		:param handle: the handle of the device returning the samples.
		:param noOfSamples: the number of samples to collect.
		:param startIndex: an index to the first valid sample in the buffer.
		:param overflow: returns a set of flags that indicate whether an overvoltage has occurred on any of the
			channels. It is a bit pattern with bit 0 denoting Channel A.
		:param triggerAt: an index to the buffer indicating the location of the trigger point relative to startIndex.
			This parameter is valid only when triggered is non-zero.
		:param triggered: a flag indicating whether a trigger occurred. If non- zero, a trigger occurred at the location
			indicated by triggerAt.
		:param autoStop: the flag that was set in the call to ps????RunStreaming.
		:param pParameter: flag to communicate the status to the application.
		"""
		self.sampleCount = noOfSamples
		self.autoStop = autoStop

		if self.sampleCount != 0:
			for chSet in self.scope.channelSettings:
				if chSet.enabled:
					#print("startIndex: {0}, noOfSamples: {1}, currentIndex: {2}, len(self.appBuffers[chSet.channel]): {3}".format(startIndex, noOfSamples, self.currentIndex, len(self.appBuffers[chSet.channel])))
					self.appBuffers[chSet.channel][self.currentIndex:self.currentIndex + noOfSamples] = self.scopeBuffers[chSet.channel][startIndex:startIndex + noOfSamples]
			self.currentIndex += self.sampleCount


class Scope(object):
	def __init__ (self):
		self.model = None
		#self._clearSettings() this must be called in derived classes
		self.channelSettings = None  # only contains settings for channels A to D (channelCount), not EXT or GEN
		self.extSettings = None      # settings for EXT channel only
		self.acquisitionSettings = None


	def _clearSettings (self):
		self.channelSettings = []  # list of ChannelSettings
		for i in range(self.model.channelCount):
			self.channelSettings.append(ChannelSettings(i))
		self.extSettings = ChannelSettings(Channel.EXT)
		self.acquisitionSettings = AcquisitionSettings()


	def _func (self, name):
		"""
		Retrieves a function of the loaded library based on its name (without prefix).

		:param str name: name of the function (for example "CloseUnit" for "ps4000CloseUnit")
		:return: a function on success
		:raises: PicoError
		"""
		cmd = self.model.funcPrefix + name
		try:
			func = getattr (self.model.dll, cmd)
		except AttributeError:
			raise PicoError("The command '%s' is not available in this library (%s)." % (cmd, self.model.dllName), Status.PICO_NOT_USED)
		return func


	def _openUnit (self, resolution):
		raise NotImplementedError ("_openUnit()")

	def openUnit (self, resolution=None):
		"""
		Opens the Python interface to the first detected unit.

		:raises: PicoError
		"""
		status = self._openUnit(resolution)
		if status == Status.PICO_POWER_SUPPLY_CONNECTED or status == Status.PICO_POWER_SUPPLY_NOT_CONNECTED:
			status = self._changePowerSource(status)
		elif status == Status.PICO_USB3_0_DEVICE_NON_USB3_0_PORT:
			status = self._changePowerSource(Status.PICO_POWER_SUPPLY_NOT_CONNECTED)
		if status != Status.PICO_OK:
			self.model.handle = None
			self.model.resolution = resolution
			raise PicoError("openUnit(): ", status)
		self._clearSettings()
	#self._initState()

	def _changePowerSource(self, status):
		raise NotImplementedError ("_changePowerSource()")

	def _initState(self):
		"""Forces initial state of most hardware components."""
		# Disables ETS (Equivalent Time Sampling) mode.
		#ps????SetEts(int16_t handle, enum mode, int16_t etsCycles, int16_t etsInterleave, int32_t* sampleTimePicoseconds)
		status = self._func("SetEts")(self.model.handle, c_int32(ETSMode.OFF), c_int16(0), c_int16(0), c_void_p())
		if status != Status.PICO_OK:
			raise PicoError("_initState(disabling ETS): ", status)

		# for i in range(self.model.channelCount):
		# self.openChannel (Channel.A+i, Range.RANGE_5V, Coupling.DC, Probe.x10)

		# Disables trigger by calling the low-level functions
		#ps????SetTriggerChannelProperties(int16_t handle, struct* channelProperties, int16_t nChannelProperties, int16_t auxOutputEnable, int32_t autoTriggerMilliseconds)
		status = self._func("SetTriggerChannelProperties")(self.model.handle, c_void_p(), c_int16(0), c_int16(0), c_int32(0))
		if status != Status.PICO_OK:
			raise PicoError("_initState(SetTriggerChannelProperties): ", status)
		#ps????SetTriggerChannelConditions(int16_t handle, struct* conditions, int16_t nConditions)
		status = self._func("SetTriggerChannelConditions")(self.model.handle, c_void_p(), c_int16(0))
		if status != Status.PICO_OK:
			raise PicoError("_initState(SetTriggerChannelConditions): ", status)
		#ps????SetTriggerChannelDirections(int16_t handle, enum channelA, enum channelB, enum channelC, enum channelD, enum ext, enum aux)
		noTrigDir = c_int32(Trigger.Direction.NONE)
		status = self._func("SetTriggerChannelDirections")(self.model.handle, noTrigDir, noTrigDir, noTrigDir, noTrigDir, noTrigDir, noTrigDir)
		if status != Status.PICO_OK:
			raise PicoError("_initState(SetTriggerChannelDirections): ", status)
		#ps????SetTriggerDelay(int16_t handle, uint32_t delay)
		status = self._func("SetTriggerDelay")(self.model.handle, c_uint32(0))
		if status != Status.PICO_OK:
			raise PicoError("_initState(SetTriggerDelay): ", status)
		#ps????SetPulseWidthQualifier(int16_t handle, struct *conditions, int16_t nConditions, enum direction, uint32_t lower, uint32_t upper, enum type)
		status = self._func("SetPulseWidthQualifier")(self.model.handle, c_void_p(), c_int16(0), noTrigDir, c_uint32(0), c_uint32(0), c_int32(PulseWidth.PW_TYPE_NONE))
		if status != Status.PICO_OK:
			raise PicoError("_initState(SetPulseWidthQualifier): ", status)

		#C if (unit->digitalPorts) // false for 3204A
		#C	ps3000aSetTriggerDigitalPortProperties(unit->handle, digitalDirections, nDigitalDirections)


	def resolution(self):
		"""Returns the current resolution, one of Resolution.DR_*."""
		return self.model.resolution

	def setResolution (self, resolution):
		"""
		Changes the current resolution (if this model supports it).
		:param resolution: one of Resolution.DR_*.
		"""
		self._setResolution(resolution)

	def _setResolution (self, resolution):
		raise NotImplementedError ("_setResolution()")


	def modelName (self):
		"""Returns the name of this model."""
		return self.model.modelName


	def channelCount (self):
		"""Returns the number of 'normal' channels (ignores EXT or GEN)."""
		return self.model.channelCount


	def unitInfo (self):
		"""Returns a dictionary with details about the open unit."""
		#ps????GetUnitInfo(int16_t handle, int8_t* string, int16_t stringLength, int16_t* requiredSize, PICO_INFO info)
		info = create_string_buffer(20) # " " * 20
		infoLen = c_int16()
		infos = {}      # return a dictionary of strings with same keys as in UNIT_INFOS
		for i in UNIT_INFOS.keys():
			status = self._func("GetUnitInfo") (self.model.handle, info, len(info), byref(infoLen), UNIT_INFOS[i])
			if status == Status.PICO_OK:
				infos[i] = str(info.value[:infoLen.value - 1]) # -1 to remove \0 at the end (C-string)
			else:
				raise PicoError("unitInfo(): ", status)
		return infos


	def closeUnit (self):
		"""Closes the unit."""
		if self.model.handle is None:
			# silently ignore
			#raise PicoError ("closeUnit(): ", Status.PICO_NOT_FOUND)
			return

		#ps????CloseUnit(int16_t handle)
		status = self._func("CloseUnit") (self.model.handle)
		if status != Status.PICO_OK:
			raise PicoError("closeUnit(): ", status)
		self._clearSettings()
		self.model.handle = None


	def _channelSettings (self, channel):
		if channel < self.model.channelCount:
			cset = self.channelSettings[channel]
		else:
			raise PicoError("_channelSettings(%s): " % channelName(channel), Status.PICO_INVALID_CHANNEL)
		return cset


	def _openChannel (self, channel, vRange, coupling):
		raise NotImplementedError ("_openChannel()")

	def openChannel (self, channel, vRange, coupling, probe):
		"""
		Enables one channel and configures it for the next acquisitions.

		:param int channel: Channel.A to D, but not EXT
		:param int vRange: Range.RANGE_*
		:param int coupling: Coupling.*
		:param int probe: Probe.*
		"""
		if channel == Channel.EXT:  # check this to provide a more helpful message
			raise PicoError("openChannel(): EXT channel not allowed, see initEXTTrigger() instead.")
		cset = self._channelSettings(channel)
		cset.init(vRange, coupling, probe)
		status = self._openChannel (channel, cset.picoRange(), coupling)
		if status != Status.PICO_OK:
			cset.disable()
			raise PicoError("openChannel(%s): " % channelName(channel), status)


	def _closeChannel (self, channel):
		raise NotImplementedError ("_closeChannel()")

	def closeChannel (self, channel):
		"""
		Disables the specified channel.

		:param int channel: Channel.A to D, but not EXT
		"""
		cset = self._channelSettings(channel) # will raise if EXT
		cset.disable()
		status = self._closeChannel (channel)
		if status != Status.PICO_OK:
			raise PicoError("closeChannel(%s): " % channelName(channel), status)


	def closeChannels (self):
		"""Closes all available channels."""
		for ch in range(self.channelCount()):
			self.closeChannel(ch)


	def _debugTimebase (self, timeBase, sampleCount):
		raise NotImplementedError ("_debugTimebase()")

	def debugTimebase (self, timeBase, sampleCount):
		"""
		Debug function only here to test the protocol command with same name.
		Note that the channels and resolution must be configured BEFORE calling this function.

		:param int timeBase: the requested time base
		:param int sampleCount: the exepected number of samples
		:return: a tuple (sampleInterval, maxSamples) as (float in nanoseconds, int).
		"""
		return self._debugTimebase(timeBase, sampleCount)


	def currentTimeBase (self):
		"""
		Returns the current(last) time base set in startAcquisition() with samplingRate.

		:return int: the current time base or None if not set.
		"""
		return self.acquisitionSettings.timebase


	def currentSamplingRate (self):
		"""
		Returns the current(last) sampling rate used in startAcquisition().
		Note that the value can be different than the one really provided,
		since it is converted in one of the available timebases.

		:return: a sampling rate in Hz or 0 if none configured.
		"""
		tb = self.acquisitionSettings.timebase
		if tb is None:
			return 0.0
		return self.samplingRate (tb)


	def _timeBase (self, samplingRate):
		raise NotImplementedError ("_timeBase()")

	def timeBase (self, samplingRate):
		"""
		Returns the time base to use to acquire samples at the given sampling rate.

		:param number samplingRate: the expected acquisition sampling rate in Hz
		:return int: the nearest time base usable in startAcquisition().
		"""
		if samplingRate <= 0:
			raise PicoError("timeBase(): ", Status.PICO_INVALID_PARAMETER)

		tb = self._timeBase(samplingRate)

		if tb < 0:
			tb = 0
		elif tb > self.model.maxTimeBase:
			tb = self.model.maxTimeBase
		return int(tb)


	def _samplingRate (self, timeBase):
		raise NotImplementedError ("_samplingRate()")

	def samplingRate (self, timeBase):
		"""
		Returns the acquisition frequency corresponding to the given time base.

		:param int timeBase: a time base as used in startAcquisition().
		:return float: the sampling rate corresponding to the time base, in Hz.
		"""
		return self._samplingRate(timeBase)


	def sampleInterval (self, timeBase):
		"""
		Returns the duration of one sample in seconds, when using the given time base.

		:param int timeBase: the time base as used in startAcquisition().
		:return float: sample duration in seconds.
		"""
		return 1.0 / self._samplingRate(timeBase)

		# def testTB(self):
		# if _LOG_LEVEL < LOG_VERBOSE:
		# return
		# print ("Testing time bases for model %s" % self.modelName())
		# for tb in range(10):
		# print ("%2d -> F=%10d Hz = %g ns" % (tb, self.samplingRate(tb), self.sampleInterval(tb)*1e9))


	def startAcquisition (self, sampleCount, samplingRate, wait = None, preTriggerSamples=0):
		"""
		Starts a non-blocking acquisition with given settings.

		:param int sampleCount: the total amount of samples to acquire (including optional preTriggerSamples).
			sampleCount must be > preTriggerSamples.
		:param float samplingRate: the acquisition frequency in Hz
		:param float wait: time to wait after starting the acquisition, in seconds,
			None means no wait,
			<=0 means to wait the time estimated by the picoscope itself (useless when using trigger),
			>0 time to wait in seconds.
		:param int preTriggerSamples: number of samples acquired before the trigger event.
			If no trigger is configured, this value is simply added to sampleCount.
		"""
		timebase = self.timeBase(samplingRate)
		if _LOG_LEVEL >= LOG_VERBOSE:
			print ("startAcquisition(%d samples @ %d Hz) -> timebase=%d, samplingRate=%d Hz, interval=%d ns." % (sampleCount, samplingRate, timebase, self.samplingRate(timebase), self.sampleInterval(timebase)*1e9))
		self.startAcquisitionTB (sampleCount, timebase, wait, preTriggerSamples)


	def _runBlock(self, preSamples, postSamples, timebase):
		raise NotImplementedError ("_runBlock()")

	def startAcquisitionTB (self, sampleCount, timebase, wait=None, preTriggerSamples=0):
		"""
		Starts a non-blocking acquisition with given settings.

		:param int sampleCount: the total amount of samples to acquire (including optional preTriggerSamples).
			sampleCount must be > preTriggerSamples.
		:param int timebase: the acquisition time base
		:param float wait: time to wait after starting the acquisition, in seconds,
			None means no wait,
			<=0 means to wait the time estimated by the picoscope itself (useless when using trigger),
			>0 time to wait in seconds.
		:param int preTriggerSamples: number of samples acquired before the trigger event.
			If no trigger is configured, this value is simply added to sampleCount.
		"""
		sampleCount = int(sampleCount)
		timebase = int(timebase)
		preTriggerSamples = int(preTriggerSamples)
		if preTriggerSamples > sampleCount:
			raise PicoError("startAcquisitionTB(): preTriggerSamples (%d) must be < sampleCount (%d)" % (preTriggerSamples, sampleCount))
		self.acquisitionSettings.init (sampleCount, timebase)
		if _LOG_LEVEL >= LOG_VERBOSE:
			print ("startAcquisitionTB(%d samples, timebase=%d, %d preSamples) -> samplingRate=%d Hz, interval=%d ns." % (sampleCount, timebase, preTriggerSamples, self.samplingRate(timebase), self.sampleInterval(timebase)*1e9))
		status, estimated_ms = self._runBlock (preTriggerSamples, sampleCount-preTriggerSamples, timebase)
		if status != Status.PICO_OK:
			self.acquisitionSettings.clear()
			raise PicoError("startAcquisitionTB(): ", status)
		if wait is None:
			return
		if wait <= 0:
			sleep_s = estimated_ms / 1000.0
		else:
			sleep_s = wait
		time.sleep(sleep_s)


	def startStreaming(self, samplingRate, sampleCount, bufferSampleCount=50000):
		"""
		Starts a non-blocking acquisition in streaming mode.
		You need to call waitStreamingAcquisition method to get the acquisition results.
		This method permits to acquire long shots with big precision.

		:param int samplingRate: the acquisition frequency in Hz
		:param int sampleCount: amount of samples to acquire.
		:param int bufferSampleCount: size of the buffer for the streaming acquisition
		:return: a list of scope buffer to give to :meth:`Scope.waitStreamingAcquisition` method.
			The size of this list is equals to the number of scope channels.
		"""
		sampleInterval = 1.0 / samplingRate
		if sampleInterval > 1 :
			sampleInterval = int(sampleInterval)
			timeUnit = TimeUnits.S
		elif sampleInterval * 1e3 > 1:
			sampleInterval = int(sampleInterval*1e3)
			timeUnit = TimeUnits.MS
		elif sampleInterval * 1e6 > 1:
			sampleInterval = int(sampleInterval*1e6)
			timeUnit = TimeUnits.US
		elif sampleInterval * 1e9 > 1:
			sampleInterval = int(sampleInterval*1e9)
			timeUnit = TimeUnits.NS

		if _LOG_LEVEL >= LOG_VERBOSE:
			print ("startStreaming({0} samplingRate) -> sampleInterval = {1}; timeUnit -> {2} ".format(samplingRate,
																									   sampleInterval,
																									   timeUnit))
		buffers = []
		for cset in self.channelSettings:
			if cset.enabled:
				buf = numpy.zeros(bufferSampleCount, dtype=numpy.int16)  #c_int16(0) * sampleCount
				self._setBuffer(cset.channel, buf)
			else:
				buf = None
			buffers.append(buf)

		# PICO_STATUS ps????RunStreaming(int16_t handle, uint32_t * sampleInterval, PS????_TIME_UNITS sampleIntervalTimeUnits,
		# 								 uint32_t maxPreTriggerSamples, uint32_t maxPostTriggerSamples, int16_t autoStop,
		# 								 uint32_t downSampleRatio, PS????_RATIO_MODE downSampleRatioMode, uint32_t overviewBufferSize)
		status = self._func("RunStreaming")(self.model.handle, byref(c_int16(sampleInterval)), c_int32(timeUnit),
											c_int32(0), c_int32(sampleCount), c_int16(1), c_int32(1), c_int32(RatioMode.NONE),
											c_uint32(bufferSampleCount))
		if status != Status.PICO_OK:
			self._stop()
			raise PicoError("startStreaming(): ", status)

		return buffers


	def waitStreamingAcquisition(self, streamingCallback):
		"""
		Wait and acquire signal. You must call startStreaming before.

		:param AbstractStreamingCallBack streamingCallback: AbstractStreamingCallBack object
		:return: True on success, False on error.
		"""
		status = None
		while not streamingCallback.autoStop:
			time.sleep(0)
			status = self._func("GetStreamingLatestValues")(self.model.handle, streamingCallback.callback, c_void_p(0))
			# if status != Status.PICO_OK:
			# 	break

		if (status is not None) and (status != Status.PICO_OK):
			raise PicoError("waitStreamingAcquisition", status)

		res = status == Status.PICO_OK
		status = self._stop()
		return res and (status == Status.PICO_OK)

	def _stop(self):
		"""
		Stop scope acquisition (used for streaming mode).
		:return PICO_STATUS
		"""
		return self._func("Stop")(self.model.handle)

	def waitAcquisition (self):
		"""
		Waits for the ongoing acquisition to terminate.

		:return bool: True on success, False on error.
		"""
		#ps????IsReady(int16_t handle, int16_t* ready)
		#ps????Stop(int16_t handle)
		ok = c_int16(0)
		loop = 0
		while not ok:
			status = self._func("IsReady") (self.model.handle, byref(ok))
			if status != Status.PICO_OK:
				if _LOG_LEVEL >= LOG_WARNING:
					print ("Bad status while waiting end of acquisition (%s), aborting." % Status.name(status))
				self._func("Stop")(self.model.handle)
				return False
			time.sleep(0.05)  # 50ms
			loop += 1
			if loop > 1000:
				if _LOG_LEVEL >= LOG_WARNING:
					print ("Looks like infinite loop, stopping.")
				return False
		return True


	def _setBuffer (self, channel, vbuffer):
		raise NotImplementedError("_setBuffer() must be implemented")

	def _getValues (self, sampleCount):
		raise NotImplementedError("_getValues() must be implemented")


	def readSamples (self):
		"""
		Returns the samples from the last terminated acquisition.

		:return: a list of channelCount() buffers (always the same size no matter how many channels are enabled).
			Each item is either None if the corresponding channel is disabled, or a numpy array of 16-bits integers (ADC values).
		"""
		if self.acquisitionSettings.sampleCount is None:
			return [ None for _ in range(self.model.channelCount) ]
		buffers = []
		sampleCount = self.acquisitionSettings.sampleCount
		for cset in self.channelSettings:
			if cset.enabled:
				buf = numpy.zeros(sampleCount, dtype=numpy.int16)  #c_int16(0) * sampleCount
				self._setBuffer(cset.channel, buf)
			else:
				buf = None
			buffers.append(buf)
		samplesRead, overflowMask = self._getValues(sampleCount) # must be called only once for all buffers.
		if samplesRead != sampleCount:
			if _LOG_LEVEL >= LOG_WARNING:
				print ("Not all samples have been acquired: %d / %d" % (samplesRead, sampleCount))

		for i in range(self.model.channelCount):
			over = (overflowMask & (1 << i)) != 0
			if over:
				if _LOG_LEVEL >= LOG_WARNING:
					print ("Overflow detected on channel %s." % channelName(i))
			self.channelSettings[i].overflow = over

		return buffers


	def ADCToVolts (self, array, channel):
		"""
		Returns an array or value converted into Volts.

		:param array: value or array of ADC values, as returned by readSamples() for example.
		:param int channel: Channel.A to D, including EXT
		:return: array converted into Volts
		"""
		if channel == Channel.EXT:
			vRange = self.model.EXTRange
		else:
			cset = self._channelSettings(channel)  # will raise if EXT
			if not cset.enabled:
				raise PicoError("ADCToVolts(): channel %s is not configured yet (use openChannel())" % channelName(channel))
			vRange = cset.range
		return self.ADCToVoltsForRange (array, vRange)


	def ADCToVoltsForRange (self, array, vRange):
		"""
		Returns an array or a value converted into Volts.

		:param array: value or array of ADC values, as returned by readSamples() for example.
		:param Pico.Range vRange: range used to acquire those values, as specified in openChannel().
		:return: array converted into Volts.
		"""
		if not (vRange in Range.UPPER_BOUND):
			raise PicoError("ADCToVoltsForRange(): invalid range (%s)" % str(vRange))
##		return array * (Range.UPPER_BOUND[vRange] / float(self.model.maxADC))
		return array * numpy.float32(Range.UPPER_BOUND[vRange] / float(self.model.maxADC)) # ED: no reason for float64


	def readVolts (self):
		"""
		Returns the samples from the last terminated acquisition.

		:return: list of buffers, one per channel enabled.
			Each buffer is a numpy array of floats (Volt values).
		"""
		buffers = self.readSamples()
		buffersV = []
		for cset in self.channelSettings:
			if cset.enabled:
				bufV = self.ADCToVoltsForRange (buffers[cset.channel], cset.range)
			else:
				bufV = None
			buffersV.append(bufV)
		return buffersV


	def getOverflowMask (self):
		"""
		Checks if an overflow occurred for all channels during the last acquisition.

		:return: list of channelCount() booleans, True=overflow / False=OK.
		"""
		mask = []
		for channel in self.channelSettings:
			mask.append (channel.overflow)
		return mask


	def voltsToADC (self, valueInVolts, channel):
		"""
		Converts a Volt value in ADC using the current channel settings.
		openChannel() should have been called.

		:param float valueInVolts: a value in Volts
		:param int channel: Channel.A to D, including EXT
		:return int: the corresponding ADC value based on the current range. -1 if not configured.
		"""
		if channel == Channel.EXT:
			maxADC = self.model.EXTmaxADC
			vRange = self.model.EXTRange
		else:
			cset = self._channelSettings(channel)  # will raise if EXT
			if not cset.enabled:
				raise PicoError("voltsToADC(): channel %s is not configured yet (use openChannel())" % channelName(channel))
			maxADC = self.model.maxADC
			vRange = cset.range
		return int((valueInVolts * float(maxADC)) / (Range.UPPER_BOUND[vRange]))


	def initTrigger (self, channel, threshold, direction=Trigger.Direction.RISING, ignoredSamples=0, timeout=0):
		"""
		Configures the trigger on the specified channel.
		This function only supports LEVEL trigger type, on one channel only.

		:param int channel: Channel.A to D, but not EXT (see initEXTTrigger()).
		:param float threshold: the threshold value to trigger on, in Volts (independant of the probe).
		:param int direction: Trigger.Direction.ABOVE, BELOW, RISING, FALLING, RISING_OR_FALLING.
		:param int ignoredSamples: samples to ignore at the beginning of the acquisition
		:param float timeout: time to wait in seconds before starting automatically if no trigger occurs (max 32s).
		"""
		self._initTrigger (channel, None, threshold, direction, ignoredSamples, timeout)


	def initEXTTrigger (self, probe, threshold, direction=Trigger.Direction.RISING, ignoredSamples=0, timeout=0):
		"""
		Configures the trigger on the EXT channel.
		This function only supports LEVEL trigger type, on one channel only.

		:param int probe: Probe.x1 or x10
		:param float threshold: the threshold value to trigger on, in Volts (independant of the probe).
		:param int direction: Trigger.Direction.ABOVE, BELOW, RISING, FALLING, RISING_OR_FALLING.
		:param int ignoredSamples: samples to ignore at the beginning
		:param float timeout: time to wait in seconds before starting automatically if no trigger occurs (max 32s).
		"""
		self._initTrigger (Channel.EXT, probe, threshold, direction, ignoredSamples, timeout)


	def _initTrigger (self, channel, probe, threshold, direction, ignoredSamples, timeout):
		"""
		Configures the trigger on the specified channel.
		This function only supports LEVEL trigger type, on one channel only.

		:param int channel: Channel.A to D, including EXT.
		:param int or None probe: Probe.x1 or x10
		:param float threshold: the threshold value to trigger on, in Volts (independant of the probe).
		:param int direction: Trigger.Direction.ABOVE, BELOW, RISING, FALLING, RISING_OR_FALLING.
		:param int ignoredSamples: samples to ignore at the beginning of the acquisition
		:param float timeout: time to wait in seconds before starting automatically if no trigger occurs (max 32s).
		"""
		#ps????SetSimpleTrigger (int16_t handle, int16_t enable, enum source, int16_t threshold, enum direction, uint32_t delay, int16_t autoTrigger_ms)
		if channel == Channel.EXT and probe == Probe.x10:
			threshold_adc = self.voltsToADC(threshold / 10.0, channel)
		else:
			threshold_adc = self.voltsToADC(threshold, channel)
		if _LOG_LEVEL >= LOG_VERBOSE:
			print ("initTrigger(%s): threshold=%g -> ADC=%d" % (channelName(channel), threshold, threshold_adc))
		if threshold_adc < self.model.minADC:
			threshold_min = self.ADCToVolts(self.model.minADC, channel)
			msg = "initTrigger(%s) threshold below min: %g < %g (in ADC: %d < %d)." % (channelName(channel), threshold, threshold_min, threshold_adc, self.model.minADC)
			raise PicoError (msg)
		elif threshold_adc > self.model.maxADC:
			threshold_max = self.ADCToVolts(self.model.maxADC, channel)
			msg = "initTrigger(%s) threshold above max: %g > %g (in ADC: %d > %d)." % (channelName(channel), threshold, threshold_max, threshold_adc, self.model.maxADC)
			raise PicoError (msg)
		if timeout > 32.76:
			raise PicoError("initTrigger(%s): timeout too large(%g), must be < 32s" % (channelName(channel), timeout))
		timeout_ms = int(timeout * 1000.0)
		status = self._func("SetSimpleTrigger")(self.model.handle, c_int16(1), c_int32(channel), c_int16(threshold_adc), c_int32(direction), c_uint32(ignoredSamples), c_int16(timeout_ms))
		if status != Status.PICO_OK:
			raise PicoError("initTrigger(): ", status)


	def closeTrigger (self, channel):
		"""
		Disables the trigger on the given channel.

		:param int channel: Channel.A to D or EXT.
		"""
		#ps????SetSimpleTrigger (int16_t handle, int16_t enable, enum source, int16_t threshold, enum direction, uint32_t delay, int16_t autoTrigger_ms)
		status = self._func("SetSimpleTrigger")(self.model.handle, c_int16(0), c_int32(channel), c_int16(0), c_int32(Trigger.Direction.NONE), c_uint32(0), c_int16(0))
		if status != Status.PICO_OK:
			raise PicoError("closeTrigger(): ", status)


	def maxGeneratorFrequency (self):
		return self.model.maxGeneratorFrequency


	def _generateSignal (self, amplitude, frequency, wavetype, voffset, cycles):
		raise NotImplementedError("_generateSignal() must be implemented")

	def generateSignal (self, amplitude, frequency, wavetype=Generator.Wave.SINE, voffset=0.0, cycles=0):
		"""
		Generates a signal on the dedicated output with given settings.

		:param float amplitude: peak-to-peak voltage in Volts
		:param float frequency: frequency of the signal in Hz
		:param int wavetype: one of Generator.Wave
		:param float voffset: voltage offset in Volts
		:param int cycles: number of cycles to generate (does not really work).
		"""
		if frequency > self.maxGeneratorFrequency():
			raise PicoError("generateSignal(): frequency out of range (%f) should be in [0, %f]" % (frequency, self.maxGeneratorFrequency()))

		status = self._generateSignal(amplitude, frequency, wavetype, voffset, cycles)
		if status != Status.PICO_OK:
			raise PicoError("generateSignal(): ", status)


	def controlGenerator (self, enabled):
		"""
		Starts or stops the signal generator, using the configured settings.
		Warning: the generator must then use TriggerType.GATE_HIGH and TriggerSource.SOFT_TRIG to work.
		Disabled for now since it only seems to work with 3204A (4226 returns PICO_NOT_USED).

		:param bool enabled: True to start, False to stop.
		"""
		#ps????SigGenSoftwareControl (int16_t handle, int16_t state)
		if enabled:
			state = c_int16(1) # Generator.TriggerType.GATE_HIGH)
		else:
			state = c_int16(0) # Generator.TriggerType.GATE_LOW)
		status = self._func("SigGenSoftwareControl")(self.model.handle, state)
		if status != Status.PICO_OK:
			raise PicoError("controlGenerator(): ", status)
#

class Scope5000(Scope):
	def __init__ (self):
		Scope.__init__(self)

	def _openUnit (self, resolution):
		#ps5000aOpenUnit(int16_t* handle, int8_t* serial, PS5000A_DEVICE_RESOLUTION resolution)
		if resolution is None:
			resolution = Resolution.DR_14BIT  # best resolution with 2 channels
		# self._setResolution(resolution)  do not call it here since the handle is not ready yet
		self.model.handle = c_int16()
		status = self._func("OpenUnit")(byref(self.model.handle), c_void_p(0), c_int32(resolution))
		self.model.resolution = resolution
		self._updateResolutionLimits()
		return status

	def _changePowerSource(self, status):
		#ps5000aChangePowerSource(int16_t handle, PICO_STATUS powerState)
		return self._func("ChangePowerSource")(self.model.handle, c_int32(status))

	def _setResolution (self, resolution):
		#ps5000aSetDeviceResolution(int16_t handle, PS5000A_DEVICE_RESOLUTION resolution)
		status = self._func("SetDeviceResolution")(self.model.handle, c_int32(resolution))
		if status != Status.PICO_OK:
			raise PicoError("_setResolution(): ", status)
		self.model.resolution = resolution

	def _updateResolutionLimits(self):
		if self.model.resolution == Resolution.DR_8BIT:
			self.model.minADC = -32512
			self.model.maxADC = 32512
		else:
			self.model.minADC = -32767
			self.model.maxADC = 32767

	def _openChannel (self, channel, vRange, coupling):
		#ps5000aSetChannel(int16_t handle, PS5000A_CHANNEL channel, int16_t enabled, PS5000A_COUPLING type, PS5000A_RANGE range, float analogOffset)
		return self._func("SetChannel")(self.model.handle, c_int32(channel), c_int16(1), c_int32(coupling), c_int32(vRange), c_float(0.0))

	def _closeChannel (self, channel):
		#ps5000aSetChannel(int16_t handle, PS5000A_CHANNEL channel, int16_t enabled, PS5000A_COUPLING type, PS5000A_RANGE range, float analogOffset)
		return self._func("SetChannel")(self.model.handle, c_int32(channel), c_int16(0), c_int32(0), c_int32(0), c_float(0.0))

	def _debugTimebase (self, timeBase, sampleCount):
		#ps5000aGetTimebase2 (int16_t handle, uint32_t timebase, int32_t noSamples, float* timeIntervalNanoseconds, int32_t* maxSamples, uint32_t segmentIndex)
		timeIntervalNanoseconds = c_float()
		maxSamples = c_int32()
		status = self._func("GetTimebase2") (self.model.handle, c_uint32(timeBase), c_int32(sampleCount), byref(timeIntervalNanoseconds), byref(maxSamples), c_uint16(0))
		if status != Status.PICO_OK:
			raise PicoError("getTimebase(%d,%d): " % (timeBase, sampleCount), status)
		return (timeIntervalNanoseconds.value, maxSamples.value)

	def _timeBase (self, samplingRate):
		samplingRate = float(samplingRate)
		if self.model.resolution == Resolution.DR_8BIT:
			if samplingRate > self.model.maxHighSamplingRate / 2.0:
				tb = 0
			elif self.model.maxHighSamplingRate / 4.0 < samplingRate <= self.model.maxHighSamplingRate / 2.0:
				tb = 1
			elif self.model.maxLowSamplingRate < samplingRate <= self.model.maxHighSamplingRate / 4.0:
				tb = 2
			else:
				tb = int(2 + (self.model.maxLowSamplingRate / samplingRate))

		elif self.model.resolution == Resolution.DR_12BIT:
			if samplingRate > self.model.maxHighSamplingRate / 4.0:
				tb = 1
			elif self.model.maxLowSamplingRate < samplingRate <= self.model.maxHighSamplingRate / 4.0:
				tb = 2
			elif self.model.maxLowSamplingRate / 2.0 < samplingRate <= self.model.maxLowSamplingRate:
				tb = 3
			else:
				tb = int(3 + (self.model.maxLowSamplingRate / (samplingRate * 2.0)))

		elif (self.model.resolution == Resolution.DR_14BIT) or (self.model.resolution == Resolution.DR_15BIT):
			tb = max(int(2 + (self.model.maxLowSamplingRate / samplingRate)), 3)

		elif self.model.resolution == Resolution.DR_16BIT:
			tb = max(int(3 + (self.model.maxLowSamplingRate / (samplingRate * 2.0))), 4)
		else:
			raise PicoError("_timeBase(): invalid resolution")
		return int(tb)

	def _samplingRate (self, timeBase):
		if self.model.resolution == Resolution.DR_8BIT:
			if timeBase < 0 or timeBase > 4294967295:  # 2^32-1
				raise PicoError("_samplingRate(): invalid timebase for this model/resolution")
			elif timeBase < 3:
				return self.model.maxHighSamplingRate / (2.0 ** timeBase)
			else:
				return self.model.maxLowSamplingRate / (timeBase - 2.0)

		elif self.model.resolution == Resolution.DR_12BIT:
			if timeBase < 1 or timeBase > 4294967294:  # 2^32-2
				raise PicoError("_samplingRate(): invalid timebase for this model/resolution")
			elif timeBase < 4:
				return self.model.maxHighSamplingRate / (2.0 ** timeBase)
			else:
				return self.model.maxLowSamplingRate / ((timeBase - 3.0) * 2.0)

		elif (self.model.resolution == Resolution.DR_14BIT) or (self.model.resolution == Resolution.DR_15BIT):
			if timeBase < 3 or timeBase > 4294967295:  # 2^32-1
				raise PicoError("_samplingRate(): invalid timebase for this model/resolution")
			else:
				return self.model.maxLowSamplingRate / (timeBase - 2.0)

		elif self.model.resolution == Resolution.DR_16BIT:
			if timeBase < 4 or timeBase > 4294967294:  # 2^32-2
				raise PicoError("_samplingRate(): invalid timebase for this model/resolution")
			else:
				return self.model.maxLowSamplingRate / ((timeBase - 3.0) * 2.0)
		else:
			raise PicoError("_samplingRate(): invalid resolution")

	def _setBuffer (self, channel, vbuffer):
		#ps5000aSetDataBuffer(int16_t handle, PS5000A_CHANNEL channel, int16_t* buffer, int32_t bufferLth, uint32_t segmentIndex, PS5000A_RATIO_MODE mode)
		status = self._func("SetDataBuffer")(self.model.handle, c_int32(channel), vbuffer.ctypes.data_as(POINTER(c_int16)), c_int32(len(vbuffer)), c_uint32(0), c_int32(RatioMode.NONE))
		if status != Status.PICO_OK:
			raise PicoError("_setBuffer(): ", status)

	def _runBlock(self, preSamples, postSamples, timebase):
		#ps5000aRunBlock(int16_t handle, int32_t noOfPreTriggerSamples, int32_t noOfPostTriggerSamples, uint32_t timebase, int32_t* timeIndisposedMs, uint32_t segmentIndex, ps5000aBlockReady lpReady, void* pParameter)
		estimated_ms = c_int32()
		status = self._func("RunBlock")(self.model.handle, c_int32(preSamples), c_int32(postSamples), c_uint32(timebase), byref(estimated_ms), c_uint32(0), c_void_p(0), c_void_p(0))
		return (status, estimated_ms)

	def _getValues (self, sampleCount):
		#ps5000aGetValues(int16_t handle, uint32_t startIndex, uint32_t* noOfSamples, uint32_t downSampleRatio, PS5000A_RATIO_MODE downSampleRatioMode, uint32_t segmentIndex, int16_t* overflow)
		sampleCount = int(sampleCount)
		retSamples = c_uint32(sampleCount)
		overflow = c_int16(0)
		status = self._func("GetValues")(self.model.handle, c_uint32(0), byref(retSamples), c_uint32(0), c_int32(RatioMode.NONE), c_uint32(0), byref(overflow))
		if status != Status.PICO_OK:
			raise PicoError("_getValues(): ", status)
		return (retSamples.value, int(overflow.value))

	def _generateSignal (self, amplitude, frequency, wavetype, voffset, cycles):
		#ps5000aSetSigGenBuiltIn(int16_t handle, int32_t offsetVoltage, uint32_t pkToPk, PS5000A_WAVE_TYPE waveType, float startFrequency, float stopFrequency, float increment, float dwellTime, PS5000A_SWEEP_TYPE sweepType, PS5000A_EXTRA_OPERATIONS operation, uint32_t shots, uint32_t sweeps, PS5000A_SIGGEN_TRIG_TYPE triggerType, PS5000A_SIGGEN_TRIG_SOURCE triggerSource, int16_t extInThreshold)
		offsetVoltage = c_int32(int(voffset * 1e6)) # in microvolts
		pkToPk = c_uint32(int(amplitude * 1e6)) # in microvolts
		waveType = c_int32(wavetype)
		startFrequency = c_float(frequency)
		stopFrequency = c_float(frequency)
		freqInc = c_float(0)
		dwellTime = c_float(0)
		sweepType = c_int32(0)
		operation = c_int32(0)
		cycles = int(cycles)
		shots = c_uint32(cycles)
		sweeps = c_uint32(0)
		extInThresh = c_int16(0)
		if cycles == 0:
			triggerType = c_int32(Generator.TriggerType.RISING) # .GATE_HIGH
			triggerSource = c_int32(Generator.TriggerSource.NONE) # .SOFT_TRIG
		else:
			triggerType = c_int32(Generator.TriggerType.RISING)
			triggerSource = c_int32(Generator.TriggerSource.SOFT_TRIG)
		return self._func("SetSigGenBuiltIn")(self.model.handle, offsetVoltage, pkToPk, waveType, startFrequency, stopFrequency, freqInc, dwellTime, sweepType, operation, shots, sweeps, triggerType, triggerSource, extInThresh)


class Scope5242A(Scope5000):
	"""
	Model 5242A (A/B: max 20V, EXT/GEN: max 5V), builtin generator.
	Bandwidth: 60MHz, Resolution 8/12/14/15/16 bits,1e3/500/125/125/62.5 MS/s, 16 MS, input :1 Mohm || 13 pF, +/-1 pF
	"""
	def __init__ (self):
		Scope5000.__init__(self)
		self.model = ModelSpecification("5242A", "PS5000a.dll", "ps5000a")
		self.model.handle = None
		self.model.channelCount = 2
		self.model.maxGeneratorFrequency = 20e6  # 20 MHz and min = 0
		self.model.maxTimeBase = (2 ** 32) - 1
		self.model.maxLowSamplingRate = 125e6
		self.model.maxHighSamplingRate = 1e9
		self.model.EXTRange = Range.RANGE_5V
		self.model.EXTmaxADC = 32767  # PS5000A_EXT_MAX_VALUE
		# self.model.resolution = None  # set in OpenUnit
		self._clearSettings()


class Scope5442A(Scope5000):
	"""
	Model 5442A (A/B: max 20V, EXT/GEN: max 5V), builtin generator.
	Bandwidth: 60MHz, Resolution 8/12/14/15/16 bits,1e3/500/125/125/62.5 MS/s, 16 MS, input :1 Mohm || 13 pF, +/-1 pF
	"""
	def __init__ (self):
		Scope5000.__init__(self)
		self.model = ModelSpecification("5442A", "PS5000a.dll", "ps5000a")
		self.model.handle = None
		self.model.channelCount = 4
		self.model.maxGeneratorFrequency = 20e6  # 20 MHz and min = 0
		self.model.maxTimeBase = (2 ** 32) - 1
		self.model.maxLowSamplingRate = 125e6
		self.model.maxHighSamplingRate = 1e9
		self.model.EXTRange = Range.RANGE_5V
		self.model.EXTmaxADC = 32767  # PS5000A_EXT_MAX_VALUE
		# self.model.resolution = None  # set in OpenUnit
		self._clearSettings()

class Scope5244D(Scope5000):
	"""
	Model 5244D (A/B: max 20V, EXT/GEN: max 5V), builtin generator.
	Bandwidth: 200MHz, Resolution 8/12/14/15/16 bits, 125/125 MS/s, ? MS, input: 1 Mohm || 14 pF, +/-1 pF
	"""
	def __init__ (self):
		Scope5000.__init__(self)
		self.model = ModelSpecification("5244A", "PS5000a.dll", "ps5000a")
		self.model.handle = None
		self.model.channelCount = 2
		self.model.maxGeneratorFrequency = 20e6  # 20 MHz and min = 0
		self.model.maxTimeBase = (2 ** 32) - 1
		self.model.maxLowSamplingRate = 125e6
		self.model.maxHighSamplingRate = 1e9
		self.model.EXTRange = Range.RANGE_5V
		self.model.EXTmaxADC = 32767  # PS5000A_EXT_MAX_VALUE
		# self.model.resolution = None  # set in OpenUnit
		self._clearSettings()

def getScope(modelName):
	"""
	Returns an instance of the Scope object for the requested model.

	:param modelName: usually a string, but can be a number if not ambiguous.
	:return: an instance of the corresponding Scope object.
	:raise: a PicoError if the model is not supported.
	"""
	if modelName.startswith("5242"):
		return Scope5242A()
	elif modelName.startswith("5442"):
		return Scope5442A()
	elif modelName.startswith("5244"):
		return Scope5244D()
	raise PicoError("Unsupported model (%s)." % modelName)
