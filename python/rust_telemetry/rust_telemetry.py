import sys
import time
import datetime
import argparse
import struct
import math

import serial
import pygame
from pygame.locals import *

sys.path.append('../lib')
import hdlc

SCR_WIDTH = 800
SCR_HEIGHT = 600

black = (0,0,0)
light_gray = (224,224,224)
white = (255,255,255)
red = (255,0,0)

FIX_DIV = 65536.0

VAL_SQRT_1_DIV_2 = 0.70710678118654752440084436210485
VAL_SQRT_3_DIV_2 = 0.86602540378443864676372317075294
VAL_1_DIV_45 = 1. / 45.
VAL_1_DIV_128 = 1. / 128.

SIDE_X_OFFSET = 3.5
SIDE_Y_OFFSET = 5
FRONT_SIDE_X_OFFSET = 2.5
FRONT_SIDE_Y_OFFSET = 1
FRONT_Y_OFFSET = 4

parser = argparse.ArgumentParser(description="RustTelemetry", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--port", type=str, default="/dev/tty.usbserial-A8008iwL", help="usb serial port device eg. /dev/ttyUSB0")
args = parser.parse_args()

s = serial.Serial(args.port, 57600, timeout=0.001);
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

def p(x, y):
    return (int(SCR_WIDTH / 2 + 3*x), int(SCR_HEIGHT - 3*y - SCR_HEIGHT / 8))

def run():
    time = left = right = front_left = front_right = front = mc_x = mc_y = mc_dist = mc_angle = steerPwm = speedPwm = battery = 0
    lx = ly = flx = fly = fx = fy = frx = fry = rx = ry = 0

    pygame.init()
    pygame.display.set_caption("RustTelemetry")
    # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
    myfont = pygame.font.SysFont("monospace", 20)

    screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
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
                    automatic = 0
                    steering_pwm += 1
                    if steering_pwm > 180:
                        steering_pwm = 180
                    print 'steering pwm %u' % steering_pwm
                elif event.key == K_LEFT:
                    automatic = 0
                    steering_pwm -= 1
                    if steering_pwm < 0:
                        steering_pwm = 0
                    print 'steering pwm %u' % steering_pwm
                elif event.key == K_UP:
                    automatic = 0
                    drive_pwm += 1
                    #drive_pwm = 105
                    if drive_pwm > 180:
                        drive_pwm = 180
                    print 'drive pwm %u' % drive_pwm
                elif event.key == K_DOWN:
                    automatic = 0
                    drive_pwm -= 1
                    #drive_pwm = 60
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
                time, left, right, front_left, front_right, front, mc_x, mc_y, mc_dist, mc_angle, automatic, steerPwm, speedPwm, battery = struct.unpack("<IiiiiiiiiiBBBH", packet[1:])
                left /= FIX_DIV
                front_left /= FIX_DIV
                front /= FIX_DIV
                front_right /= FIX_DIV
                right /= FIX_DIV
                mc_x /= FIX_DIV
                mc_y /= FIX_DIV
                mc_dist /= FIX_DIV
                mc_angle /= FIX_DIV
                #mc_angle_rad = math.radians(mc_angle)
                #mc_x_calc = mc_dist * math.cos(mc_angle_rad)
                #mc_y_calc = mc_dist * math.sin(mc_angle_rad)

                a1 = left * VAL_SQRT_1_DIV_2
                lx = -(a1 + SIDE_X_OFFSET)
                ly = a1 - SIDE_Y_OFFSET
                flx = -(front_left * 0.5 + FRONT_SIDE_X_OFFSET)
                fly = front_left * VAL_SQRT_3_DIV_2 + FRONT_SIDE_Y_OFFSET
                fx = 0
                fy = front + FRONT_Y_OFFSET
                frx = front_right * 0.5 + FRONT_SIDE_X_OFFSET
                fry = front_right * VAL_SQRT_3_DIV_2 + FRONT_SIDE_Y_OFFSET
                a2 = right * VAL_SQRT_1_DIV_2
                rx = a2 + SIDE_X_OFFSET
                ry = a2 - SIDE_Y_OFFSET

                #print("battery: %u" % battery)
                print("l:%.2f fl:%.2f f:%.2f fr:%.2f r:%.2f mc(%.f,%.2f;%.2f,%.2f %3u %3u)" % (left, front_left, front, front_right, right, mc_x, mc_y, mc_dist, mc_angle, steerPwm, speedPwm))
                sys.stdout.flush()

        # erase the screen
        screen.fill(white)
        
        if lx != 0:
            pts = [p(lx, 0), p(lx, ly), p(flx, fly), p(fx, fy), p(frx, fry), p(rx, ry), p(rx, 0)]
            pygame.draw.polygon(screen, light_gray, pts, 0)
            pygame.draw.polygon(screen, black, pts, 3)
            pygame.draw.lines(screen, red, False, [p(0,0), p(mc_x, mc_y)], 3)
            pygame.draw.circle(screen, black, p(0, 0), 10, 0)
            pygame.draw.circle(screen, red, p(mc_x, mc_y), 10, 0)
            # render text
            label = myfont.render("battery: %.3fV" % (battery / 1000.0,), 1, (255,125,125))
            screen.blit(label, (0, 0))

        # update the screen
        pygame.display.update()

if __name__=="__main__":
    run()
