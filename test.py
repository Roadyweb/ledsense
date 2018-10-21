import unittest

import numpy

import ledsense
import helper
import TCS34725

#########################################################
# IT'S NOT POSSIBLE TO CROSS DEVELOP THE TEST CASES!!!!!#
#                                                       #
# TEST NEED TO RUN ON TARGET (import RPi.GPIO as GPIO   #
#########################################################


class CreateRGBMeasurement(object):
    def __init__(self, inc=0.0):
        self.value = 0.0
        self.inc = inc
        self.inc_cnt = 0

    def set_value(self, value):
        self.value = value

    def get_value(self):
        tmp = self.value
        return tmp, tmp, tmp, tmp

    def set_inc(self, inc):
        self.inc = inc

    def set_max_inc_cnt(self, inc_cnt):
        self.inc_cnt = inc_cnt

    def get_value_inc(self):
        self.inc_cnt -= 1
        tmp = self.value
        if self.inc_cnt > 0:
            self.value += self.inc
        return (tmp, tmp, tmp, tmp)


class TestCaseGetStableRgb(unittest.TestCase):
    def dummyfunc(self):
        return 0, 0, 0, 0

    def setUp(self):
        self.rgb = CreateRGBMeasurement()
        # Dummy setup for TCS
        ledsense.tcs = tcs = TCS34725.TCS34725(integration_time=0, gain=0, i2c=1)

    def test_same_input_cnt_gt_2(self):
        cnt = 10
        max_dist = 1
        ledsense.tcs.get_raw_data = self.rgb.get_value

        for i in range(0, 255, 10):
            for cnt in range(2, cnt, 2):
                self.rgb.set_value(i)
                ret = ledsense.get_stable_rgb(cnt, max_dist)
                self.assertEqual(ret, [i, i, i], 'Returned RGB must match input RGB')

    def test_same_input_cnt_le_2(self):
        max_dist = 1
        ledsense.tcs.get_raw_data = self.rgb.get_value

        for i in range(0, 255, 10):
            for cnt in range(0, 2):
                self.rgb.set_value(i)
                self.assertRaises(ValueError, ledsense.get_stable_rgb, cnt, max_dist)

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
                self.rgb.set_inc(1)
                self.rgb.set_max_inc_cnt(1000)
                ret = ledsense.get_stable_rgb(cnt, max_dist)
            avg = sum / cycle_cnt
            print(sum, avg, cycle_cnt, i)
            self.assertEqual(ret, [avg, avg, avg], 'Returned RGB must match input RGB')

    def test_slope_without_distance(self):
        cnt = 10
        max_dist = 10
        inc = max_dist * 2.0
        ledsense.tcs.get_raw_data = self.rgb.get_value_inc

        for i in range(0, 255, 10):
            self.rgb.set_value(i)
            self.rgb.set_inc(inc)
            self.rgb.set_max_inc_cnt(10)
            ret = ledsense.get_stable_rgb(cnt, max_dist)
            avg = self.rgb.get_value()[0]
            # print('get_stable_ret: %s avg: %s' % (ret, avg))
            self.assertEqual(ret, [avg, avg, avg], 'Returned RGB must match input RGB')


if __name__ == '__main__':
    unittest.main()
