#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""LED Sensing.

Usage:
  led_sens.py app [CONFIG]
  led_sens.py color analyse [CONFIG]
  led_sens.py detect [CONFIG]
  led_sens.py diff
  led_sens.py meas (on|off|toggle)
  led_sens.py play
  led_sens.py save_default
  led_sens.py rgb stable [CONFIG]
  led_sens.py test_speed

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
import copy
import datetime
import numpy
import pprint
import sys
import time

from docopt import docopt

# Uncomment to remote debug
# import pydevd; pydevd.settrace('192.168.178.80')
from config import DEF_CONFIG, config_save_default, config_load

GPIO_LED = 4

tcs = None

LED_TOGGLE_HOLDOFF = 0.60


def measure(debug=False):
    r, g, b, c = tcs.get_raw_data()
    if debug:
        print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
    return r, g, b, c


def measure_rgb(debug=False):
    r, g, b, c = measure(False)
    if debug:
        print('R: %5d G: %5d B: %5d' % (r, g, b))
    return r, g, b


def led(on_off):
    if on_off:
        led_on()
    else:
        led_off()


def led_on():
    GPIO.output(GPIO_LED, GPIO.HIGH)
    time.sleep(LED_TOGGLE_HOLDOFF)


def led_off():
    GPIO.output(GPIO_LED, GPIO.LOW)
    time.sleep(LED_TOGGLE_HOLDOFF)


def detect_cube(thres):
    """ Cube is detected by measuring the clear brightness. If the brightness
        falls below the threshold it is assumed the the cube shields all
        surrounding light, returns the measured clear reading.
    """
    led_off()
    while 42:
        r, g, b, c = measure()
        if c < thres:
            return c


def detect_cube_removal(thres):
    """ Cube is detected by measuring the clear brightness. If the brightness
        falls below the threshold it is assumed the the cube shields all
        surrounding light, returns the measured clear reading.
    """
    led_off()
    while 42:
        r, g, b, c = measure()
        if c > thres:
            return c


def get_rgb_distance(rgb1, rgb2):
    """ This function expects two tuples with RGB values and calculates the distance between both
        vectors.
    """
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)
    return numpy.linalg.norm(rgb1 - rgb2)


def get_rgb_length(rgb):
    """ This function expects one tuples with RGB values and calculates the length of the vector.
    """
    return numpy.linalg.norm(rgb)


def get_stable_rgb(count, dist_limit):
    """ If a number of consecutive (count) RGB measurements is within a maximum
        distance (dist_limit) the average of all measurements is calculated and returned.
    """
    while 42:
        res = []
        max_dist = 0
        for i in range(count):
            res.append(measure_rgb(False))
        for i in range(count - 1):
            act_dist = get_rgb_distance(res[i], res[i + 1])
            if act_dist > max_dist:
                max_dist = act_dist
        if max_dist > dist_limit:
            # print('Max Dist: %d Dist Limit: %d Restarting... ' % (max_dist, dist_limit))
            continue
        break
    median = list(numpy.median(res, axis=0))
    return median


def get_color(rgb, colors):
    """ Takes an RGB list as argument and matches against DEF_COLORS the closest
        will be uses as match
    """
    min_dist = 999999999
    match = 0
    for color in colors:
        color_name = color[0]
        color_rgb = color[1]
        dist = get_rgb_distance(rgb, color_rgb)
        if dist < min_dist:
            min_dist = dist
            match = color
    return match[0], match[1], min_dist


def setup(config):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_LED, GPIO.OUT)
    time.sleep(0.05)
    global tcs
    integration_time = config['integration_time'][0]
    gain = config['gain'][0]
    print('Setting TCS config: Integration time: %5d Gain: %5d' % (integration_time, gain))
    tcs = TCS34725.TCS34725(integration_time=integration_time,
                            gain=gain,
                            i2c=1)


def app(config_det, config_rgb, config_color):
    global tcs
    det_threshold = config_det['threshold']
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    print('Starting app with thres: %5d, stable count: %5d, stable_dist: %5d' %
          (det_threshold, rgb_stable_cnt, rgb_stable_dist))
    while 42:
        detect_cube(det_threshold)
        led_on()
        res = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
        # print(res)
        color = get_color(res, config_color)
        print('%-30s - Distance: %5d - Cur. RGB: %-25s RGB %-20s' %
              (color[0], color[2], str(res), str(color[1])))
        detect_cube_removal(det_threshold)


def color_analyse(config_color):
    def getKey(item):
        return item[0]

    res = []

    # Calculate distance between all colors
    config_color2 = copy.deepcopy(config_color)
    for color1 in config_color:
        del config_color2[0]
        for color2 in config_color2:
            # print(color1, color2)
            dist = get_rgb_distance(color1[1], color2[1])
            res.append((dist, color1, color2))

    # Print results
    # pprint.pprint(res)
    sorted_res = sorted(res, key=getKey)
    # pprint.pprint(sorted_res)
    for entry in sorted_res:
        dist = entry[0]
        name1 = entry[1][0]
        rgb1 = entry[1][1]
        name2 = entry[2][0]
        rgb2 = entry[2][1]
        print('Dist: %4d (%-25s %-25s) : %25s %25s' %
              (dist, name1, name2, str(rgb1), str(rgb2)))

    dist = []
    for i in sorted_res:
        dist.append(i[0])
    # print(dist)

    print('Distance   - Avg: %5d Std: %5d, Min: %5d, Max: %5d' %
          (numpy.mean(dist), numpy.std(dist), min(dist), max(dist)))

    rgb_len = []
    for i in config_color:
        rgb_len.append(get_rgb_length(i[1]))
    # print(rgb_len)

    print('RGB Length - Avg: %5d Std: %5d, Min: %5d, Max: %5d' %
          (numpy.mean(rgb_len), numpy.std(rgb_len), min(rgb_len), max(rgb_len)))


def detect(config):
    global tcs
    threshold = config['threshold']
    while 42:
        value = detect_cube(threshold)
        print('Cube detected           %5d - %5d' % (value, threshold))
        value = detect_cube_removal(threshold)
        print('Cube removal detected   %5d - %5d' % (value, threshold))


def diff():
    global tcs

    while 42:
        led_on()
        r, g, b, c = measure()
        # print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
        led_off()
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


def meas(conf_led_on, toggle):
    global tcs

    dd = draw_diagram(40)

    if toggle:
        while 42:
            led_on()
            for _ in range(3):
                r, g, b, c = measure()
                dd.add(r)
                print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                      (r, g, b, c, dd.getstr()))

            led_off()
            for _ in range(3):
                r, g, b, c = measure()
                dd.add(r)
                print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                      (r, g, b, c, dd.getstr()))

    led(conf_led_on)

    while 42:
        r, g, b, c = measure()
        print('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))


class draw_diagram(object):
    def __init__(self, width):
        self.width = width
        self.max = 1
        self.max_updated = False
        self.last_value = 0

    def add(self, value):
        self.last_value = value
        if value > self.max:
            self.max = value
            self.max_updated = True

    def getstr(self):
        pos_raw = 1.0 * self.last_value / self.max
        pos = round(1.0 * pos_raw * self.width)
        # print('%5f %5f %f' % (pos_raw, pos, self.max))
        str = '%s%s' % (pos * ' ', 'O')
        if self.max_updated:
            str += (self.width - 2 - pos) * ' ' + ' !!! Max Updated !!!'
            self.max_updated = False
        return str


def test_speed():
    global LED_TOGGLE_HOLDOFF
    LED_TOGGLE_HOLDOFF = 2 * LED_TOGGLE_HOLDOFF
    sleep_duration = LED_TOGGLE_HOLDOFF
    rep_cnt = 2
    cycle_cnt = 10

    dd = draw_diagram(40)

    while 42:
        sleep_duration = 0.95 * sleep_duration
        LED_TOGGLE_HOLDOFF = sleep_duration
        start = datetime.datetime.now()
        for i in range(cycle_cnt):
            led_on()
            for _ in range(rep_cnt):
                r, g, b, c = measure()
                dd.add(r)
                print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                      (r, g, b, c, dd.getstr()))

            led_off()
            for _ in range(rep_cnt):
                r, g, b, c = measure()
                dd.add(r)
                print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                      (r, g, b, c, dd.getstr()))
        duration = datetime.datetime.now() - start
        duration_ms = int(duration.total_seconds() * 1000)
        meas_cnt = cycle_cnt * 2 * rep_cnt
        print('**** Summary ****')
        print('Setting to %f' % LED_TOGGLE_HOLDOFF)
        print('Duration for %d measurements: %5d ms' % (meas_cnt, duration_ms))
        print('Duration per measurements: %5d ms' % (duration_ms / meas_cnt))
        time.sleep(2)

def play():
    pass


def rgb_stable(config_rgb):
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    print('Starting rgb_stable with stable count: %5d, stable_dist: %5d' %
          (rgb_stable_cnt, rgb_stable_dist))
    led_on()

    while 42:
        res = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
        # print(res)
        print('RGB: %25s' % str(res))


def endprogram():
    GPIO.cleanup()


def main():
    args = docopt(__doc__, version='LED Sensing')
    print(args)
    config = config_load(args['CONFIG'])
    pprint.pprint(config)
    setup(config['sensor'])

    try:
        if args['app']:
            app(config['det'], config['rgb'], config['color'])
        elif args['color'] == True and args['analyse'] == True:
            color_analyse(config['color'])
        elif args['detect']:
            detect(config['det'])
        elif args['diff']:
            diff()
        elif args['meas']:
            meas(args['on'], args['toggle'])
        elif args['play']:
            play()
        elif args['rgb'] == True and args['stable'] == True:
            rgb_stable(config['rgb'])
        elif args['save_default']:
            config_save_default()
        elif args['test_speed']:
            test_speed()
        else:
            print('Not implemented')

    except KeyboardInterrupt:
        endprogram()


if __name__ == '__main__':
    import cProfile
    import pstats

    # cProfile.run('main()', 'restats')
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative')
    # p.print_stats()
    #p.strip_dirs().sort_stats(-1).print_stats()
    main()
