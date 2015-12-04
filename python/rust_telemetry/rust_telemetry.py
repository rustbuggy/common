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
DRIVING_PWM_DEFAULT = 90

def send_packet(data):
    data = hdlc.add_checksum(data)
    data = hdlc.escape_delimit(data)
    s.write(data)

def p(x, y):
    return (int(SCR_WIDTH / 2 + 3*x), int(SCR_HEIGHT - 3*y - SCR_HEIGHT / 8))

def run():
    time = cycles = left = right = front_left = front_right = front = mc_x = mc_y = mc_dist = mc_angle = steerPwm = speedPwm = battery = 0
    lx = ly = flx = fly = fx = fy = frx = fry = rx = ry = 0
    accel_x = accel_y = accel_z = speed_x = speed_y = speed_z = 0.0
    last_time = last_cycles = 0
    state = 0

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
                    
                    motor_command = struct.pack("<BBBB", CB_MOTOR_COMMAND, automatic, steering_pwm, drive_pwm)
                    send_packet(motor_command)
                    print(automatic, steering_pwm, drive_pwm)
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
                    if drive_pwm > 180:
                        drive_pwm = 180
                    print 'drive pwm %u' % drive_pwm
                elif event.key == K_DOWN:
                    automatic = 0
                    drive_pwm -= 1
                    if drive_pwm < 0:
                        drive_pwm = 0
                    print 'drive pwm %u' % drive_pwm
                elif event.key == K_p:
                    automatic = 0
                    drive_pwm = 105
                    print 'drive pwm %u' % drive_pwm
                elif event.key == K_SPACE:
                    continue # handled in event.type == KEYUP
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

                motor_command = struct.pack("<BBBB", CB_MOTOR_COMMAND, automatic, steering_pwm, drive_pwm)
                send_packet(motor_command)
                print(automatic, steering_pwm, drive_pwm)

        # read serial
        data = s.read(20)
        if data:
            parser.put(data)

        for packet in parser:
            header, = struct.unpack("<B", packet[:1])
            if header == BC_TELEMETRY:
                last_cycles = cycles
                last_time = time
                time, cycles, left, right, front_left, front_right, front, mc_x, mc_y, mc_dist, mc_angle, accel_x, accel_y, accel_z, speed_x, speed_y, speed_z, automatic, steerPwm, speedPwm, battery, state = struct.unpack("<IIiiiiiiiiiffffffBBBHB", packet[1:])
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
                if automatic:
                    print("%.2f %.2f %.2f %.2f %.2f (%.f,%.2f;%.2f,%.2f %3u %3u %u)" % (left, front_left, front, front_right, right, mc_x, mc_y, mc_dist, mc_angle, steerPwm, speedPwm, state))
                #if math.sqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z) > 0.1:
                #    print("%f\t%f %3u" % (accel_x, speed_x, speedPwm))
                
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
            screen.blit(label, (10, 10))
            if automatic == 1:
                label = myfont.render("automatic: yes", 1, (255,0,0))
            else:
                label = myfont.render("automatic: no", 1, (0,255,0))
            screen.blit(label, (10, 40))
            label = myfont.render("accel: %+0.4f %+0.4f %+0.4f" % (accel_x, accel_y, accel_z), 1, (125,125,255))
            screen.blit(label, (10, 70))
            label = myfont.render("speed: %+0.4f %+0.4f %+0.4f" % (speed_x, speed_y, speed_z), 1, (125,125,255))
            screen.blit(label, (10, 100))
            label = myfont.render("cycles per millisecond: %0.2f" % (float(cycles - last_cycles) / float(time - last_time)), 1, (125,255,125))
            screen.blit(label, (10, 130))
            label = myfont.render("steer: %3u drive: %3u" % (steerPwm, speedPwm), 1, (255,125,255))
            screen.blit(label, (10, SCR_HEIGHT - 30))

        # update the screen
        pygame.display.update()

if __name__=="__main__":
    run()
