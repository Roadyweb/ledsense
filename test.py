import unittest

import ledsense
import TCS34725

#########################################################
# IT'S NOT POSSIBLE TO CROSS DEVELOP THE TEST CASES!!!!!#
#                                                       #
# TEST NEED TO RUN ON TARGET (import RPi.GPIO as GPIO   #
#########################################################


class CreateRGBMeasurement(object):
    def __init__(self, inc=0.0):
        self.value = 0.0

    def set_value(self, value):
        self.value = value

    def get_value(self):
        tmp = self.value
        return tmp, tmp, tmp, tmp

    def get_value_inc(self, inc=1):
        tmp = self.value
        self.value += inc
        return (tmp, tmp, tmp, tmp)


class TestCaseGetStableRgb(unittest.TestCase):
    def dummyfunc(self):
        return 0, 0, 0, 0

    def setUp(self):
        self.rgb = CreateRGBMeasurement()
        # Dummy setup for TCS
        ledsense.tcs = tcs = TCS34725.TCS34725(integration_time=0, gain=0, i2c=1)

    def test_same_input(self):
        cnt = 10
        max_dist = 1
        ledsense.tcs.get_raw_data = self.rgb.get_value

        for i in range(0, 255, 10):
            for cnt in range(0, cnt, 2):
                self.rgb.set_value(i)
                ret = ledsense.get_stable_rgb(cnt, max_dist)
                self.assertEqual(ret, [i, i, i], 'Returned RGB must match input RGB')

    def test_slope_within_distance(self):
        cnt = 10
        max_dist = 10
        ledsense.tcs.get_raw_data = self.rgb.get_value_inc

        for i in range(0, 255, 10):
            sum = 0
            ret = 0
            cycle_cnt = max_dist - 1
            for cycle in range(0, cycle_cnt):
                sum += (cycle + i)
                self.rgb.set_value(i)
                ret = ledsense.get_stable_rgb(cnt, max_dist)
            avg = sum / cycle_cnt
            print(sum, avg, cycle_cnt, i)
            self.assertEqual(ret, [avg, avg, avg], 'Returned RGB must match input RGB')


if __name__ == '__main__':
    unittest.main()
