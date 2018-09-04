#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time



s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 100
WAIT_AFT_SWITCH = 0.1

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(s2, GPIO.OUT)
    GPIO.setup(s3, GPIO.OUT)
    print("\n")


def loop():
    while(1):

        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.LOW)
        time.sleep(WAIT_AFT_SWITCH)
        start = time.time()
        for _ in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration_red = time.time() - start      # seconds to run for loop
        red = NUM_CYCLES / duration_red         # in Hz
        # print("red value - ",red)

        GPIO.output(s2, GPIO.LOW)
        GPIO.output(s3, GPIO.HIGH)
        time.sleep(WAIT_AFT_SWITCH)
        start = time.time()
        for _ in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration_blue = time.time() - start
        blue = NUM_CYCLES / duration_blue
        # print("blue value - ",blue)

        GPIO.output(s2, GPIO.HIGH)
        GPIO.output(s3, GPIO.HIGH)
        time.sleep(WAIT_AFT_SWITCH)
        start = time.time()
        for _ in range(NUM_CYCLES):
            GPIO.wait_for_edge(signal, GPIO.FALLING)
        duration_green = time.time() - start
        green = NUM_CYCLES / duration_green
        # print("green value - ",green)
        # time.sleep(2)

        print('R: %5d, G: %5d, B: %5d RD: %5f GD: %5f BD: %5f' %
              (red, green, blue,
               duration_red, duration_green, duration_blue))


def endprogram():
    GPIO.cleanup()


if __name__ == '__main__':

    setup()

    try:
        loop()

    except KeyboardInterrupt:
        endprogram()
