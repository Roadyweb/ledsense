#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import time
from string import upper



s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 100
WAIT_AFT_SWITCH = 0.3


def set(color):
    color = upper(color)
    if color == 'R' or color == 'RED':
        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.LOW)
    elif color == 'G' or color == 'GREEN':
        GPIO.output(s2, GPIO.HIGH)
        GPIO.output(s3, GPIO.HIGH)
    elif color == 'B' or color == 'BLUE':
        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.HIGH)
    elif color == 'C' or color == 'CLEAR':
        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.HIGH)
    else:
        raise TypeError('Use R, G, B or C as parameter')
    time.sleep(WAIT_AFT_SWITCH)


def measure():
    start = time.time()
    for _ in range(NUM_CYCLES):
        GPIO.wait_for_edge(signal, GPIO.FALLING)
    duration = time.time() - start      # seconds to run for loop
    color = NUM_CYCLES / duration         # in Hz
    return color


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2, GPIO.OUT)
    GPIO.setup(s3, GPIO.OUT)
    print("\n")


def loop():
    while 1:
        set('RED')
        red = measure()

        set('BLUE')
        blue = measure()

        set('GREEN')
        green = measure()

        set('CLEAR')
        clear = measure()

        print('R: %5d, G: %5d, B: %5d C: %5d' %
              (red, green, blue, clear))


def endprogram():
    GPIO.cleanup()


def main():
    setup()

    try:
        loop()

    except KeyboardInterrupt:
        endprogram()


if __name__ == '__main__':
    main()
