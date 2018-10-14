#!/usr/bin/python3
# -*- coding: utf-8 -*-


import time

import alsaaudio
import RPi.GPIO as GPIO
import os.path
import pygame


from config import DEF_STATION_GPIOS, DEF_STATION_GPIO_MAP, DEF_STATION_COLOR_MP3_MAP, DEF_PATH_MP3
from helper import pr, prdbg


DEF_AUDIO_DEVICE = 'PCM'

exit_thread = False
stop_playing = False
start_playing = False

class UndefinedError(Exception):
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
        pr('Stations: %s %s %s' % (str(gpios_in), str(gpios), str(station)))
        if tuple(gpios_in) == gpios:
            return station

    raise UndefinedError('Station %s not defined' % str(gpios_in))


def get_mp3_filename(cur_station, cur_color):
    for station, fn, color in DEF_STATION_COLOR_MP3_MAP:
        if cur_station == station and \
           cur_color == color:
            return fn
    raise UndefinedError('Filename not defined for %s, %s' %(cur_station, cur_color) )


def convert_fn(fn):
    return fn.split('_')[0] + '.mp3'


def check_mp3_files():
    # pygame.mixer.init()
    for station, fn, color in DEF_STATION_COLOR_MP3_MAP:
        fn = convert_fn(fn)
        path = DEF_PATH_MP3 + fn
        if not(os.path.isfile(path)):
            raise MP3FileError('File %s does not exist' % path)
        # TODO: look for a way to determine a valid mp3 file

def play(fn):
    global stop_playing
    pygame.mixer.music.load(fn)
    pygame.mixer.music.set_volume(1)    # Set to max
    pr('Playing %s with volume %d' % (fn, 100 * pygame.mixer.music.get_volume()))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        if stop_playing or exit_thread:
            pr('Stopping to play')
            pygame.mixer.music.stop()
            stop_playing = False
            return
        pygame.time.Clock().tick(10)

    pr('Finished playing')


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for gpio in DEF_STATION_GPIOS:
        GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    pygame.init()
    pygame.mixer.init()
    m = alsaaudio.Mixer(DEF_AUDIO_DEVICE)
    vol_before = m.getvolume()[0]
    m.setvolume(100)
    vol_after = m.getvolume()[0]
    pr('Setting Alsa volume for %s to %d (was: %d)' % (DEF_AUDIO_DEVICE, vol_after, vol_before))


def endprogram():
    GPIO.cleanup()


def main():
    global exit_thread
    global stop_playing
    global start_playing
    setup()
    check_mp3_files()
    station = get_station()
    try:
        while 42:
            while start_playing == False:
                time.sleep(0.1)
                if exit_thread:
                    pr('Exit Thread')
                    endprogram()
                    return
            try:
                pr('Trying to find fn to play %s' % str(start_playing))
                fn = get_mp3_filename(station, start_playing)
                fn = DEF_PATH_MP3 + convert_fn(fn)
                play(fn)
                if exit_thread == True:
                    pr('Exit Thread')
                    endprogram()
                    return
                time.sleep(1)
            except UndefinedError as e:
                pr(e)
                pass
            start_playing = False

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
