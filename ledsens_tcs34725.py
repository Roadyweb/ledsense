#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import TCS34725
import numpy
import pprint
import pydevd
import time

#pydevd.settrace('192.168.178.80')


GPIO_LED=4

DET_CUBE_THRESHOLD=2

STABLE_RGB_CNT=5
STABLE_RGB_DIST=10

tcs = None

COLORS = [
    ['RAL 1005', [3232.0, 2102.0, 1196.0]],
    ['RAL 1006', (0,0,0)],
    ['RAL 1007', (0,0,0)],
    ['RAL 1011', (0,0,0)],
    ['RAL 1012', (0,0,0)],
]


def measure(debug=False):
    r, g, b, c = tcs.get_raw_data()
    time.sleep(0.05)
    if debug:
        print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
    return r, g, b, c


def measure_rgb(debug=False):
    r, g, b, c = measure(False)
    if debug:
        print('R: %5d G: %5d B: %5d' % (r, g, b))
    return r, g, b


def led_on():
    GPIO.output(GPIO_LED, GPIO.HIGH)


def led_off():
    GPIO.output(GPIO_LED, GPIO.LOW)


def detect_cube(thres=DET_CUBE_THRESHOLD):
    ''' Cube is detected by measuring the clear brightness. If the brightness
        falls below the threshold it is assumed the the cube shields all
        surrounding light.
    '''
    led_off()
    while 42:
        r, g, b, c = measure(True)
        if c < thres:
            return


def get_rgb_distance(rgb1, rgb2):
    ''' This function expects to tuples with RGB values and calculates the distance between both
        vectors.
    '''
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)
    return numpy.linalg.norm(rgb1 - rgb2)


def get_stable_rgb(count=STABLE_RGB_CNT, dist_limit=STABLE_RGB_DIST):
    ''' If a number of consecutive (count) RGB measurements is within a maximum
        distance (dist_limit) the average of all measurements is calculated and returned.
    '''
    while 42:
        res = []
        max_dist = 0
        for i in range(count):
            res.append(measure_rgb(False))
        for i in range(count-1):
            act_dist = get_rgb_distance(res[i], res[i+1])
            if act_dist > max_dist:
                max_dist = act_dist
        if max_dist > dist_limit:
            print('Max Dist: %d Dist Limit: %d Restarting... ' % (max_dist, dist_limit))
            continue
        break
    median = list(numpy.median(res, axis=0))
    return median


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_LED, GPIO.OUT)
    time.sleep(0.3)
    global tcs 
    tcs = TCS34725.TCS34725(integration_time=TCS34725.TCS34725_INTEGRATIONTIME_50MS,
                            gain            =TCS34725.TCS34725_GAIN_16X,
                            i2c=1)


def loop():
    global tcs
    while 42:
        detect_cube()
        print('Cube detected')
        led_on()
        time.sleep(0.1)
        res = get_stable_rgb()
        print(res)
        led_off()
        time.sleep(1)

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
