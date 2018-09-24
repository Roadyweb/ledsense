import unittest

import ledsens
import TCS34725

#########################################################
# IT'S NOT POSSIBLE TO CROSS DEVELOP THE TEST CASES!!!!!#
#                                                       #
# TEST NEED TO RUN ON TARGET (import RPi.GPIO as GPIO   #
#########################################################


class CreateRGBMeasurement(object):
    def __init__(self, inc=0.0):
        self.inc = inc
        self.value = 0.0
        self.last_value = 0.0

    def set_value(self, value, inc=0.0):
        self.last_value = value
        self.value = value
        self.inc = inc

    def get_value(self):
        tmp = self.value
        self.value += self.inc
        return (tmp, tmp, tmp, tmp)

class TestCaseGetRgbStable(unittest.TestCase):
    def dummyfunc(self):
        return 0, 0, 0, 0

    def setUp(self):
        self.rgb = CreateRGBMeasurement()
        # Dummy setup for TCS
        ledsens.tcs = tcs = TCS34725.TCS34725(integration_time=0, gain=0,
                            i2c=1)

    def test_same_input(self):
        CNT = 10
        MAX_DIST = 1

        for i in range(0, 255, 10):
            for cnt in range(0, CNT, 2):
                self.rgb.set_value(i)
                ledsens.tcs.get_raw_data = self.rgb.get_value

                ret = ledsens.get_stable_rgb(CNT, MAX_DIST)
                f
                self.assertEqual(ret, [i, i, i],
                                 'Returned RGB must match input RGB')

    def test_slope_within_distance(self):
        CNT = 10
        MAX_DIST = 1

        for i in range(0, 255, 10):
            self.rgb.set_value(i, 1)
            ledsens.tcs.get_raw_data = self.rgb.get_value

            ret = ledsens.get_stable_rgb(CNT, MAX_DIST)
            print(ret)
            self.assertEqual(ret, [i, i, i],
                             'Returned RGB must match input RGB')



if __name__ == '__main__':
    unittest.main()
