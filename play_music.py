#!/usr/bin/python3
# -*- coding: utf-8 -*-


import time

import alsaaudio
import pygame

from config import DEF_PATH_MP3, MP3FileError, convert_fn
from helper import pr, prerr

DEF_AUDIO_DEVICE = 'PCM'

exit_thread = False
stop_playing = False
start_playing = False


def get_mp3_filename(map_station_mp3_color, cur_station, cur_color):
    for station, fn, color in map_station_mp3_color:
        if cur_station == station and \
                cur_color == color:
            return fn
    raise MP3FileError('Filename not defined for %s, %s' % (cur_station, cur_color))


def play(fn):
    global stop_playing
    pygame.mixer.music.load(fn)
    pygame.mixer.music.set_volume(1)  # Set to max
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
    pygame.init()
    pygame.mixer.init()
    m = alsaaudio.Mixer(DEF_AUDIO_DEVICE)
    vol_before = m.getvolume()[0]
    m.setvolume(100)
    vol_after = m.getvolume()[0]
    pr('Setting Alsa volume for %s to %d (was: %d)' % (DEF_AUDIO_DEVICE, vol_after, vol_before))


def main(map_station_mp3_color, station):
    global exit_thread
    global stop_playing
    global start_playing
    pr('play_music.main: Starting thread')
    setup()

    try:
        while 42:
            while not start_playing:
                time.sleep(0.1)
                if exit_thread:
                    pr('play_music.main: Exit thread')
                    return
            try:
                pr('Trying to find fn to play %s' % str(start_playing))
                fn = get_mp3_filename(map_station_mp3_color, station, start_playing)
                fn = DEF_PATH_MP3 + convert_fn(fn)
                play(fn)
                if exit_thread:
                    pr('play_music.main: Exit thread')
                    return
                time.sleep(1)
            except MP3FileError as e:
                pr(e)
                pass
            start_playing = False

    except KeyboardInterrupt:
        pass
