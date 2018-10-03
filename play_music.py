#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import print_function

import RPi.GPIO as GPIO
import os.path
import pprint
import pygame
import sys
import time

from docopt import docopt

# Uncomment to remote debugledsens.py
# import pydevd; pydevd.settrace('192.168.178.80')
from config import DEF_STATION_GPIOS, DEF_STATION_GPIO_MAP, DEF_STATION_COLOR_MP3_MAP, DEF_PATH_MP3


class UndefinedStationError(Exception):
    def __init__(self, message):
        self.message = message


class MP3FileError(Exception):
    def __init__(self, message):
        self.message = message


def get_station():
    gpios_in = []
    for gpio in DEF_STATION_GPIOS:
        gpios_in.append(GPIO.input(gpio))

    for gpios, station in DEF_STATION_GPIO_MAP:
        print(gpios_in, gpios, station)
        if tuple(gpios_in) == gpios:
            return station

    raise UndefinedStationError('Station %s not defined' % str(gpios_in))


def get_mp3_filename(cur_station, cur_color):
    for station, fn, color in DEF_STATION_COLOR_MP3_MAP:
        if cur_station == station and \
           cur_color == color:
            return fn


def convert_fn(fn):
    return fn.split('_')[0] + '.mp3'


def check_mp3_files():
    # pygame.mixer.init()
    for station, fn, color in DEF_STATION_COLOR_MP3_MAP:
        fn = convert_fn(fn)
        path = DEF_PATH_MP3 + fn
        print(path)
        if not(os.path.isfile(path)):
            raise MP3FileError('File %s does not exist' % path)
        # TODO: look for a way to determine a valid mp3 file

def play(fn):
    pygame.mixer.init()
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(fn)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for gpio in DEF_STATION_GPIOS:
        GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def endprogram():
    GPIO.cleanup()


def main():
    setup()
    check_mp3_files()

    try:
        while 42:
            station = get_station()
            color = "RAL 1003 gelb"
            fn = get_mp3_filename(station, color)
            fn = DEF_PATH_MP3 + convert_fn(fn)
            print('Playing %s' % fn)
            play(fn)

            time.sleep(1)
    except KeyboardInterrupt:
        endprogram()


if __name__ == '__main__':
    import cProfile
    import pstats

    # cProfile.run('main()', 'restats')
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative')
    # p.print_stats()
    # p.strip_dirs().sort_stats(-1).print_stats()
    main()
