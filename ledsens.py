#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import numpy
import time
from string import upper



s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 20
WAIT_AFT_SWITCH = 0.0


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
    return color / 50


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2, GPIO.OUT)
    GPIO.setup(s3, GPIO.OUT)
    time.sleep(0.3)
    print("\n")


def loop():
    while 1:
        arr_red = []
        arr_green = []
        arr_blue = []
    
        for i in range(10):
            set('RED')
            red = measure()
            arr_red.append(red)
    
            set('BLUE')
            blue = measure()
            arr_blue.append(blue)
    
            set('GREEN')
            green = measure()
            arr_green.append(green)

            # print('R: %5d, G: %5d, B: %5d' %
            #       (red, green, blue))
    
        print('R: %5d (+/-%5d), G: %5d  (+/-%5d), B: %5d  (+/-%5d)' %
              (numpy.mean(arr_red), numpy.std(arr_red),
               numpy.mean(arr_green), numpy.std(arr_green),
               numpy.mean(arr_blue), numpy.std(arr_blue))
        )


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
