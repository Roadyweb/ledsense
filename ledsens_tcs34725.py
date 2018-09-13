#!/usr/bin/python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import TCS34725
import numpy
import pprint
import sys
import time

# Uncomment to remote debug
#import pydevd; pydevd.settrace('192.168.178.80')


GPIO_LED=4

DET_CUBE_THRESHOLD=2

STABLE_RGB_CNT=5
STABLE_RGB_DIST=10

tcs = None

COLORS = [
    # Gelbtöne
    ['RAL 1000 - Grünbeige'    , [3877.0, 3134.0, 2231.0]],
    ['RAL 1001 - Beige'        , [3854.0, 2844.0, 2110.0]],
    ['RAL 1002 - Sandgelb'     , [3888.0, 2799.0, 1889.0]],
    ['RAL 1003 - Signalgelb'   , [4812.0, 2828.0, 1466.0]],
    ['RAL 1004 - Goldgelb'     , [4172.0, 2535.0, 1356.0]],
    ['RAL 1005 - Honiggelb'    , [3232.0, 2102.0, 1196.0]],
    ['RAL 1006 - Maisgelb'     , [4016.0, 2272.0, 1310.0]],
    ['RAL 1007 - Narzissengelb', [4048.0, 2140.0, 1228.0]],
    ['RAL 1011 - Braunbeige'   , [2764.0, 1849.0, 1347.0]],
    ['RAL 1012 - Zitronengelb' , [3851.0, 2708.0, 1530.0]],
    ['RAL 1013 - Perlweiß'     , [5165.0, 4411.0, 3649.0]],
    ['RAL 1014 - Elfenbein'    , [4541.0, 3593.0, 2631.0]],
    ['RAL 1015 - Hellelfenbein', [5117.0, 4189.0, 3297.0]],
    ['RAL 1016 - Schwefelgelb' , [5651.0, 4455.0, 2353.0]],
    ['RAL 1017 - Safrangelb'   , [4890.0, 2856.0, 1728.0]],
    # Blautöne
    ['RAL 1012', [0,0,0]],
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
        r, g, b, c = measure()
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

def get_color(rgb):
    ''' Takes an RGB list as argument and matches against COLORS the closest
        will be uses as match
    '''
    min_dist = 999999999
    match = 0
    for color in COLORS:
        color_name = color[0]
        color_rgb = color[1]
        dist = get_rgb_distance(rgb, color_rgb)
        if dist < min_dist:
            min_dist = dist
            match = color
    return match[0], match[1], min_dist



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
        print('Waiting for Cube ...')
        detect_cube()
        led_on()
        time.sleep(0.1)
        res = get_stable_rgb()
        color = get_color(res)
        print('%20s - Distance: %5d - Cur. RGB: %s RGB %s' % 
              (color[0], color[2], str(res), str(color[1])))
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
