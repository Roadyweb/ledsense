#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""LED Sensing.

Usage:q
  led_sens.py app [CONFIG]
  led_sens.py detect
  led_sens.py diff
  led_sens.py meas (on|off)
  led_sens.py play
  led_sens.py ship new <name>...
  led_sens.py ship <name> move <x> <y> [--speed=<kn>]
  led_sens.py ship shoot <x> <y>
  led_sens.py mine (set|remove) <x> <y> [--moored | --drifting]
  led_sens.py (-h | --help)
  led_sens.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.

"""

from __future__ import print_function

import RPi.GPIO as GPIO
import TCS34725
import numpy
import pprint
import sys
import time
import yaml

from docopt import docopt

# Uncomment to remote debug
#import pydevd; pydevd.settrace('192.168.178.80')


GPIO_LED=4

DEF_DET_THRESHOLD=2

DEF_RGB_STABLE_CNT=5
DEF_RGB_STABLE_DIST=10

DEF_COLORS = [
    # Gelbtöne
    ['RAL 1000 - Grünbeige'    , [4080.0, 3300.0, 2328.0]],
    ['RAL 1001 - Beige'        , [4188.0, 3079.0, 2263.0]],
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
    ['RAL 5008 - Graublau'     , [1026.0,  914.0,  842.0]],
    ['RAL 5009 - Azurblau'     , [1116.0, 1216.0, 1280.0]],
    ['RAL 5010 - Enzianblau'   , [ 973.0, 1073.0, 1316.0]],
    ['RAL 5011 - Stahlblau'    , [ 887.0,  783.0,  752.0]],
    ['RAL 5012 - Lichtblau'    , [1476.0, 1990.0, 2394.0]],
    ['RAL 5013 - Kobaltblau'   , [ 926.0,  839.0,  878.0]],
    ['RAL 5014 - Taubenblau'   , [1761.0, 1764.0, 1822.0]],
    ['RAL 5015 - Himmelblau'   , [1249.0, 1745.0, 2243.0]],
    ['RAL 5017 - Verkehrsblau' , [ 984.0, 1202.0, 1554.0]],
    ['RAL 5018 - Türkisblau'   , [1451.0, 1959.0, 1856.0]],
    ['RAL 5019 - Capriblau'    , [1022.0, 1207.0, 1422.0]],
    ['RAL 5020 - Ozeanblau'    , [ 894.0,  888.0,  873.0]],
    ['RAL 5021 - Wasserblau'   , [1114.0, 1494.0, 1449.0]],
    ['RAL 5022 - Nachtblau'    , [ 952.0,  851.0,  912.0]],
    ['RAL 5023 - Fernblau'     , [1351.0, 1440.0, 1592.0]],
]

DEF_SENSOR_INTEGRATIONTIME = TCS34725.TCS34725_INTEGRATIONTIME_50MS,
DEF_SENSOR_GAIN = TCS34725.TCS34725_GAIN_16X,

DEF_CONFIG = {
    'det': {'threshold': DEF_DET_THRESHOLD},
    'rgb': {
        'stable_cnt' : DEF_RGB_STABLE_CNT,
        'stable_dist': DEF_RGB_STABLE_DIST
     },
    'color': DEF_COLORS,
    'sensor': {
        'integration_time': DEF_SENSOR_INTEGRATIONTIME,
        'gain':             DEF_SENSOR_GAIN
    }
}


tcs = None


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


def led(on_off):
    if on_off == True:
        led_on()
    else:
        led_off()


def led_on():
    GPIO.output(GPIO_LED, GPIO.HIGH)


def led_off():
    GPIO.output(GPIO_LED, GPIO.LOW)


def detect_cube(thres=DEF_DET_THRESHOLD):
    ''' Cube is detected by measuring the clear brightness. If the brightness
        falls below the threshold it is assumed the the cube shields all
        surrounding light, returns the measured clear reading.
    '''
    led_off()
    time.sleep(0.1)
    while 42:
        r, g, b, c = measure()
        if c < thres:
            return c


def detect_cube_removal(thres=DEF_DET_THRESHOLD):
    ''' Cube is detected by measuring the clear brightness. If the brightness
        falls below the threshold it is assumed the the cube shields all
        surrounding light, returns the measured clear reading.
    '''
    led_off()
    time.sleep(0.1)
    while 42:
        r, g, b, c = measure()
        if c > thres:
            return c


def get_rgb_distance(rgb1, rgb2):
    ''' This function expects two tuples with RGB values and calculates the distance between both
        vectors.
    '''
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)
    return numpy.linalg.norm(rgb1 - rgb2)


def get_rgb_length(rgb):
    ''' This function expects one tuples with RGB values and calculates the length of the vector.
    '''
    return numpy.linalg.norm(rgb)


def get_stable_rgb(count=DEF_RGB_STABLE_CNT, dist_limit=DEF_RGB_STABLE_DIST):
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
            # print('Max Dist: %d Dist Limit: %d Restarting... ' % (max_dist, dist_limit))
            continue
        break
    median = list(numpy.median(res, axis=0))
    return median


def get_color(rgb):
    ''' Takes an RGB list as argument and matches against DEF_COLORS the closest
        will be uses as match
    '''
    min_dist = 999999999
    match = 0
    for color in DEF_COLORS:
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


def app():
    global tcs
    while 42:
        detect_cube()
        led_on()
        time.sleep(0.1)
        res = get_stable_rgb()
        #print(res)
        color = get_color(res)
        print('%-30s - Distance: %5d - Cur. RGB: %-25s RGB %-20s' % 
              (color[0], color[2], str(res), str(color[1])))
        detect_cube_removal()


def detect():
    global tcs
    while 42:
        print('Dectect Threshold: %5d' % DET_CUBE_THRESHOLD)
        value = detect_cube(DET_CUBE_THRESHOLD)
        print('Cube detected           %5d' % value)
        value = detect_cube_removal(DET_CUBE_THRESHOLD)
        print('Cube removal detected   %5d' % value)


def diff():
    global tcs

    while 42:
        led_on()
        time.sleep(0.1)
        r, g, b, c = measure()
        # print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
        led_off()
        time.sleep(0.1)
        r2, g2, b2, c2 = measure()
        # print('R: %5d G: %5d B: %5d C: %5d' % (r2, g2, b2, c2))
        rgb = (r, g, b)
        rgb2 = (r2, g2, b2)
        rgb_len = get_rgb_length(rgb)
        rgb2_len = get_rgb_length(rgb2)
        rgb_diff = get_rgb_distance(rgb, rgb2)
        clear_diff = abs(c - c2)
        print('Len %5d %5d %5d Clear: %5d %5d %5d' %
              (rgb_len, rgb2_len, rgb_diff, c, c2, clear_diff))


def meas(led_on):
    global tcs

    led(led_on)

    while 42:
        time.sleep(0.1)
        r, g, b, c = measure()
        print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))


def play():
    data = DEF_CONFIG
    
    with open('config_default.yaml', 'w') as outfile:
        yaml.dump(data, outfile, indent=4)

def endprogram():
    GPIO.cleanup()


def main():
    args = docopt(__doc__, version='LED Sensing')
    print(args)
    setup()

    try:
        if args['app'] == True:
            app()
        elif args['detect'] == True:
            detect()
        elif args['diff'] == True:
            diff()
        elif args['meas'] == True:
            meas(args['on'])
        elif args['play'] == True:
            play()
        else:
            print('Not implemented')

    except KeyboardInterrupt:
        endprogram()


if __name__ == '__main__':
    main()
