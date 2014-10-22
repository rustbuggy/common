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

FIX_DIV = 65536.0

parser = argparse.ArgumentParser(description="RustTelemetry", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--port", type=str, default="/dev/tty.usbserial-A8008iwL", help="usb serial port device eg. /dev/ttyUSB0")
args = parser.parse_args()

s = serial.Serial(args.port, 57600, timeout=0.1);
s.flushInput()
s.flushOutput()

parser = hdlc.HdlcChecksummed()

# header bytes
BC_TELEMETRY = 0x01
CB_MOTOR_COMMAND = 0x02

AUTOMATIC_DEFAULT = 0
STEERING_PWM_DEFAULT = 90
DRIVING_PWM_DEFAULT = 92

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
	automatic = AUTOMATIC_DEFAULT
	steering_pwm = STEERING_PWM_DEFAULT # center
	drive_pwm = DRIVING_PWM_DEFAULT # stop

	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == KEYUP:
				if event.key == K_SPACE:
					automatic = 0 if automatic == 1 else 1
					steering_pwm = STEERING_PWM_DEFAULT # center
					drive_pwm = DRIVING_PWM_DEFAULT # stop
			elif event.type == KEYDOWN:
				if event.key == K_RIGHT:
					steering_pwm += 1
					if steering_pwm > 180:
						steering_pwm = 180
					print 'steering pwm %u' % steering_pwm
				elif event.key == K_LEFT:
					steering_pwm -= 1
					if steering_pwm < 0:
						steering_pwm = 0
					print 'steering pwm %u' % steering_pwm
				elif event.key == K_UP:
					drive_pwm += 1
					if drive_pwm > 180:
						drive_pwm = 180
					print 'drive pwm %u' % drive_pwm
				elif event.key == K_DOWN:
					drive_pwm -= 1
					if drive_pwm < 0:
						drive_pwm = 0
					print 'drive pwm %u' % drive_pwm
				elif event.key == K_SPACE:
					pass # handled in event.type == KEYUP
				elif event.key == K_ESCAPE:
					running = False
					#kill
					automatic = AUTOMATIC_DEFAULT
					steering_pwm = STEERING_PWM_DEFAULT # center
					drive_pwm = DRIVING_PWM_DEFAULT # stop
					continue
				else:
					#kill
					automatic = AUTOMATIC_DEFAULT
					steering_pwm = STEERING_PWM_DEFAULT # center
					drive_pwm = DRIVING_PWM_DEFAULT # stop

				#time.sleep(0.05)
				motor_command = struct.pack("<BBBB", CB_MOTOR_COMMAND, automatic, steering_pwm, drive_pwm)
				send_packet(motor_command)

		# read serial
		data = s.read(20)
		if data:
			parser.put(data)

		for packet in parser:
			header, = struct.unpack("<B", packet[:1])
			if header == BC_TELEMETRY:
				time, left, right, front_left, front_right, front, mc_x, mc_y, mc_dist, mc_angle, steerPwm, speedPwm = struct.unpack("<Iiiiiiiiiiii", packet[1:])
				#print("l %3.2f r %3.2f fl %3.2f fr %3.2f f %3.2f" % (left / FIX_DIV, right / FIX_DIV, front_left / FIX_DIV, front_right / FIX_DIV, front / FIX_DIV))
				print("mc(%.2f, %.2f; %.2f, %.2f)\tsteer: %3u drive: %3u\n" % (mc_x / FIX_DIV, mc_y / FIX_DIV, mc_dist / FIX_DIV, mc_angle / FIX_DIV, steerPwm, speedPwm))
				sys.stdout.flush()


if __name__=="__main__":
	run()
