import sys
import time
import datetime
import argparse
import struct

import serial
import pygame
from pygame.locals import *

sys.path.append('../lib')
import hdlc

parser = argparse.ArgumentParser(description="RustTelemetry", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--port", type=str, default="/dev/tty.usbserial-A8008iwL", help="usb serial port device eg. /dev/ttyUSB0")
args = parser.parse_args()

s = serial.Serial(args.port, 57600, timeout=0.01);
s.flushInput()
s.flushOutput()

parser = hdlc.HdlcChecksummed()

# header bytes
BC_TELEMETRY = 0x00
CB_MOTOR_COMMAND = 0x01

def send_packet(data):
    data = hdlc.add_checksum(data)
    data = hdlc.escape_delimit(data)
    s.write(data)



def run():
    pygame.init()
    pygame.display.set_caption("RustTelemetry")

    screen = pygame.display.set_mode((600,480))
    # by default the key repeat is disabled, enable it
    pygame.key.set_repeat(50, 50)

    running = True
    steering_pwm = 185 # center
    drive_pwm = 190 # stop

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    steering_pwm += 5
                    if steering_pwm > 253:
                        steering_pwm = 253
                    print 'steering pwm %u' % steering_pwm
                elif event.key == K_LEFT:
                    steering_pwm -= 5
                    if steering_pwm < 140:
                        steering_pwm = 140
                    print 'steering pwm %u' % steering_pwm
                elif event.key == K_DOWN:
                    drive_pwm += 1
                    if drive_pwm > 255:
                        drive_pwm = 255
                    print 'drive pwm %u' % drive_pwm
                elif event.key == K_UP:
                    drive_pwm -= 1
                    if drive_pwm < 135:
                        drive_pwm = 135
                    print 'drive pwm %u' % drive_pwm
                else:
                    #kill
                    steering_pwm = 185 # center
                    drive_pwm = 190 # stop

                motor_command = struct.pack("<BBB", CB_MOTOR_COMMAND, steering_pwm, drive_pwm)
                send_packet(motor_command)

        # read serial
        data = s.read(20)
        if data:
            parser.put(data)

        for packet in parser:
            header, = struct.unpack("<B", packet[:1])
            if header == BC_TELEMETRY:
                left, right, front_left, front_right = struct.unpack("<BBBB", packet[1:])
                #print "l %u r %u fl %u fr %u" % (left, right, front_left, front_right)


if __name__=="__main__":
    run()
