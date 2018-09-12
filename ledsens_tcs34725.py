#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import RPi.GPIO as GPIO
import TCS34725
import numpy
import time
from string import upper


GPIO_LED=4


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_LED, GPIO.OUT)
    time.sleep(0.3)


def led_on():
    GPIO.output(GPIO_LED, GPIO.HIGH)


def led_off():
    GPIO.output(GPIO_LED, GPIO.LOW)


def loop():
    tcs = TCS34725.TCS34725(i2c=1)
    tcs.set_interrupt(False)
    tcs.set_integration_time(TCS34725.TCS34725_INTEGRATIONTIME_24MS)
    tcs.set_gain(TCS34725.TCS34725_GAIN_60X)
    while 42:
        led_on()
        time.sleep(0.05)
        ron, gon, bon, con = tcs.get_raw_data()
        led_off()
        time.sleep(0.05)
        roff, goff, boff, coff = tcs.get_raw_data()
        print('ON R: %3d G: %3d B: %3d C: %3d  OFF R: %3d G: %3d B: %3d C: %3d' %
              (ron, gon, bon, con, roff, goff, boff, coff))

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
