import sys
import time
import datetime
import argparse
import struct

import serial

sys.path.append('../lib')
import hdlc

parser = argparse.ArgumentParser(description="RustTelemetry", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--port", type=str, default="/dev/tty.usbserial-A8008iwL", help="usb serial port device eg. /dev/ttyUSB0")
args = parser.parse_args()

s = serial.Serial(args.port, 57600, timeout=0.01);
s.flushInput()
s.flushOutput()

parser = hdlc.HdlcChecksummed()

BC_TELEMETRY = 0x00

while 1:
    data = s.read(20)
    if data:
        parser.put(data)

    for packet in parser:
        header, = struct.unpack("<B", packet[:1])
        if header == BC_TELEMETRY:
            left, right, front_left, front_right = struct.unpack("<BBBB", packet[1:])
            print "l %u r %u fl %u fr %u" % (left, right, front_left, front_right)

    time.sleep(0.001)
