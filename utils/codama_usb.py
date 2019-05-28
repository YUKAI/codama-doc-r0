# -*- coding: utf-8 -*-

# This code is modified from
# https://github.com/respeaker/usb_4_mic_array
# Code licensed under the Apache License v2.0.
# For details, see http://www.apache.org/licenses/LICENSE-2.0.
# Modifications copyright (C) 2019 Yukai Engineering Inc.

import sys
import struct
import usb.core
import usb.util

USAGE = """Usage: python {} -h
        -p      show all parameters
        NAME    get the parameter with the NAME
        NAME VALUE  set the parameter with the NAME and the VALUE
"""



# parameter list
# name: (id, offset, type, max, min , r/w, info)
PARAMETERS = {
    'HPFONOFF': (18, 27, 'int', 3, 0, 'read-write', 'High-pass Filter on microphone signals.', '0 = OFF', '1 = ON - 70 Hz cut-off', '2 = ON - 125 Hz cut-off', '3 = ON - 180 Hz cut-off'),
    'AECSILENCELEVEL': (18, 30, 'float', 1, 1e-09, 'read-write', 'Threshold for signal detection in AEC [-inf .. 0] dBov (Default: -80dBov = 10log10(1x10-8))'),
    'AECSILENCEMODE': (18, 31, 'int', 1, 0, 'read-only', 'AEC far-end silence detection status. ', '0 = false (signal detected) ', '1 = true (silence detected)'),

    'AGCONOFF': (19, 0, 'int', 1, 0, 'read-write', 'Automatic Gain Control. ', '0 = OFF ', '1 = ON'),
    'AGCMAXGAIN': (19, 1, 'float', 1000, 1, 'read-write', 'Maximum AGC gain factor. ', '[0 .. 60] dB (default 30dB = 20log10(31.6))'),
    'AGCDESIREDLEVEL': (19, 2, 'float', 0.99, 1e-08, 'read-write', 'Target power level of the output signal. ', '[−inf .. 0] dBov (default: −23dBov = 10log10(0.005))'),
    'AGCGAIN': (19, 3, 'float', 1000, 1, 'read-write', 'Current AGC gain factor. ', '[0 .. 60] dB (default: 0.0dB = 20log10(1.0))'),
    'AGCTIME': (19, 4, 'float', 1, 0.1, 'read-write', 'Ramps-up / down time-constant in seconds.'),

    'BEAMWIDTH': (19, 8, 'float', 1, 0.2, 'read-write', 'Width of the beam for desired speech sources.','[23 .. 180] (default: 60 = sin-1(0.5) 360/ pi)'),
    'BEAMANGLE': (19, 9, 'float', 1, -1, 'read-write', 'Center of the beam for desired speech sources.','[-90 .. 90] (default: 0 = sin-1(0.0) 360/2pi)'),

    'STATNOISEONOFF': (19, 10, 'int', 1, 0, 'read-write', 'Stationary noise suppression.', '0 = OFF', '1 = ON'),
    'GAMMA_NS': (19, 11, 'float', 3, 0, 'read-write', 'Over-subtraction factor of stationary noise. min .. max attenuation'),
    'MIN_NS': (19, 12, 'float', 1, 0, 'read-write', 'Gain-floor for stationary noise suppression.', '[−inf .. 0] dB (default: −16dB = 20log10(0.15))'),
    'NONSTATNOISEONOFF': (19, 13, 'int', 1, 0, 'read-write', 'Non-stationary noise suppression.', '0 = OFF', '1 = ON'),
    'GAMMA_NN': (19, 14, 'float', 3, 0, 'read-write', 'Over-subtraction factor of non- stationary noise. min .. max attenuation'),
    'MIN_NN': (19, 15, 'float', 1, 0, 'read-write', 'Gain-floor for non-stationary noise suppression.', '[−inf .. 0] dB (default: −10dB = 20log10(0.3))'),
    'ECHOONOFF': (19, 16, 'int', 1, 0, 'read-write', 'Echo suppression.', '0 = OFF', '1 = ON'),

    'VOICEACTIVITY': (19, 37, 'int', 1, 0, 'read-only', 'VAD voice activity status.', '0 = false (no voice activity)', '1 = true (voice activity)'),

    'SR_GAMMA_VAD': (19, 45, 'float', 1000, 0, 'read-write', 'Set the threshold for voice activity detection.', '[−inf .. 60] dB (default: 3.5dB 20log10(1.5))'),

    'KEYWORDDETECT': (0x14, 0, 'int', 1, 0, 'read-only', 'Keyword detected (read clear). '),

    'DOAANGLE': (0x15, 0, 'int', 359, 0, 'read-only', 'DOA angle. Current value. Orientation depends on build configuration.'),

    'DOAANGLEKWD': (0x20, 0, 'int', 359, 0, 'read-only', 'DOA angle when keyword detects. '),
    'SOFTRESET': (0x20, 1, 'int', 1, 0, 'write-only', 'Soft reset request.'),
    'MIC_ATTEN': (0x20, 2, 'int', 0, -100, 'read-write', 'MIC input signal attenuator in decibels.','[0 .. -100] dB (Default 0dB)'),
    'AEC_REF_ATTEN': (0x20, 3, 'int', 0, -100, 'read-write', 'AEC reference signal attenuator in decibels.','[0 .. -100] dB (Default: 0dB)'),
    'VERSION': (0x20, 4, 'int', 2**31-1, 0, 'read-only', 'Version number')
}


class Tuning:
    TIMEOUT = 100000

    def __init__(self, dev):
        self.dev = dev

    def write(self, name, value):
        try:
            data = PARAMETERS[name]
        except KeyError:
            return

        if data[5] == 'ro':
            raise ValueError('{} is read-only'.format(name))

        id = data[0]

        # 4 bytes offset, 4 bytes value, 4 bytes type
        if data[2] == 'int':
            payload = struct.pack(b'iii', data[1], int(value), 1)
        else:
            payload = struct.pack(b'ifi', data[1], float(value), 0)

        self.dev.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, 0, id, payload, self.TIMEOUT)

    def read(self, name):
        try:
            data = PARAMETERS[name]
        except KeyError:
            return

        id = data[0]

        cmd = 0x80 | data[1]
        if data[2] == 'int':
            cmd |= 0x40

        length = 8

        response = self.dev.ctrl_transfer(
            usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, cmd, id, length, self.TIMEOUT)

        response = struct.unpack(b'ii', response.tobytes())

        if data[2] == 'int':
            result = response[0]
        else:
            result = response[0] * (2.**response[1])

        return result


    @property
    def version(self):
        return self.dev.ctrl_transfer(
            usb.util.CTRL_IN | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, 0x80, 0, 1, self.TIMEOUT)[0]

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.dev)


def find(vid=0x237B, pid=0x24DD):
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if not dev:
        return

    # configuration = dev.get_active_configuration()

    # interface_number = None
    # for interface in configuration:
    #     interface_number = interface.bInterfaceNumber

    #     if dev.is_kernel_driver_active(interface_number):
    #         dev.detach_kernel_driver(interface_number)

    return Tuning(dev)



def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '-p':
            print('parameter\t\ttype\tmax\t\tmin\t\tr/w\t\tinfo')
            print('---------\t\t----\t---\t\t---\t\t---\t\t----')
            for name in sorted(PARAMETERS.keys()):
                data = PARAMETERS[name]
                print('{:16}\t{}\t\t{}\t\t{}\t{}'.format(name, '\t'.join([str(i) for i in data[2:4]]), '\t'.join([str(j) for j in data[4:5]]), '\t'.join([str(k) for k in data[5:6]]), '\t'.join([str(l) for l in data[6:7]])))
                for extra in data[7:]:
                    print('{}{}'.format(' '*80, extra))
        else:
            dev = find()
            if not dev:
                print('No device found')
                sys.exit(1)

            # print('version: {}'.format(dev.version))

            name = sys.argv[1].upper()
            if name in PARAMETERS:
                if len(sys.argv) > 2:
                    dev.write(name, sys.argv[2])
                    
                if (name == "VERSION"):
                    print('{}: {:X}'.format(name, dev.read(name)))
                elif (name != "SOFTRESET"):
                    print('{}: {}'.format(name, dev.read(name)))

                # only for SOFTRESET
                if (name == "SOFTRESET") and (len(sys.argv) == 1):
                    dev.write(name, 1)
            else:
                print('{} is not a valid name'.format(name))

            dev.close()
    else:
        print(USAGE.format(sys.argv[0]))

if __name__ == '__main__':
    main()
