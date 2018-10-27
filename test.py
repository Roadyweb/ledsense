import unittest

import numpy
import pprint
import os
import shutil
import subprocess

import ledsense
import config
import TCS34725

#########################################################
# IT'S NOT POSSIBLE TO CROSS DEVELOP THE TEST CASES!!!!!#
#                                                       #
# TEST NEED TO RUN ON TARGET (import RPi.GPIO as GPIO   #
#########################################################

MP3_TEST_FILE = 'test.mp3'
MP3_TEST_FILE_COPY = 'test.copy.mp3'

DEF_PATH_MP3 = config.DEF_PATH_MP3


def replace_byte_with_zero(path, byte_pos):
    """
    Replace randomly a byte with zero in a file
    :param path: filename
    """
    import random
    size = os.path.getsize(path)
    print('File size for %s is %d bytes' % (path, size))
    print('Random number is %d bytes' % byte_pos)
    ret = subprocess.check_output(
        ["dd", 'if=/dev/zero', 'of=%s' % path, 'bs=1', 'seek=%d' % byte_pos, 'count=1', 'conv=notrunc'])
    print(ret)
    size = os.path.getsize(path)
    print('File size for %s is %d bytes' % (path, size))


def remove_bytes_from_file(path, byte_pos, num_of_bytes=2):
    """
    Replace randomly a byte with zero in a file
    :param path: filename
    """
    import random
    size = os.path.getsize(path)
    print('File size for %s is %d bytes' % (path, size))
    print('Random number is %d bytes' % byte_pos)
    ret = subprocess.check_output(['dd', 'if=%s' % path, 'of=%s' % (path + '_start'), 'bs=2', 'count=%d' % byte_pos])
    ret = subprocess.check_output(['dd', 'if=%s' % path, 'of=%s' % (path + '_end'), 'bs=2', 'skip=%d' % (byte_pos + 1)])
    ret = subprocess.check_output(['cat %s %s > %s' % (path + '_start', path + '_end', path)], shell=True)
    ret = subprocess.check_output(['rm', path + '_end'])
    ret = subprocess.check_output(['rm', path + '_start'])

    size = os.path.getsize(path)
    print('File size for %s is %d bytes' % (path, size))


def test_convert_fn(fn):
    # dummy function to be able to test check_mp3_files
    return fn


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


class TestCaseGetColor(unittest.TestCase):
    def setUp(self):
        self.config_color = []
        color = 0
        for i in range(0, 1000, 100):
            colorname = str(i)
            self.config_color.append([colorname, [i, i, i]])
            color += 100

    def test_color_correct(self):
        for i in range(0, 1000, 100):
            color = ledsense.get_color([i, i, i], self.config_color, 1)
            print(color)
            colorname = color[0]
            self.assertEqual(colorname, str(i), 'Expected %s, got %s' % (str(i), color))

    def test_color_correct_with_offset(self):
        max_dist = 10
        for i in range(0, 1000, 100):
            for dist in range(0, max_dist + 1):
                color = ledsense.get_color([i + dist, i, i], self.config_color, max_dist)
                colorname = color[0]
                colordist = color[2]
                self.assertEqual(colorname, str(i), 'Colorname: Expected %s, got %s' % (str(i), color))
                self.assertEqual(colordist, dist, 'Colordistance: Expected %s, got %s' % (dist, colordist))

    def test_color_correct_with_offset_exceeds_max_dist(self):
        max_dist = 10
        for i in range(0, 1000, 100):
            for dist in range(max_dist + 1, max_dist + 10):
                color = ledsense.get_color([i + dist, i, i], self.config_color, max_dist)
                self.assertEqual(color, None, 'Colorname: Expected %s, got %s' % (str(i), color))


class TestCaseCheckConfigsColorVsMapMp3(unittest.TestCase):
    def setUp(self):
        self.station_cnt = 10
        self.config_color = []
        self.map_station_mp3_color = []
        for i in range(ord('a'), ord('n')):
            color = 10 * chr(i)
            self.config_color.append([color, [0, 0, 0]])
            for station in range(self.station_cnt):
                self.map_station_mp3_color.append([station, 'dummy_fn', color])

    def test_correct_configs(self):
        warn = config.check_color_vs_map_color_mp3(self.config_color, self.map_station_mp3_color)
        self.assertEqual(warn, 0, 'Expected return is 0 warning, but %d occured' % warn)

    def test_less_colors_in_map(self):
        exp_warn = 0
        while len(self.map_station_mp3_color) > 0:
            # pprint.pprint(self.map_station_mp3_color)
            for _ in range(self.station_cnt):
                warn = config.check_color_vs_map_color_mp3(self.config_color, self.map_station_mp3_color)
                self.assertEqual(warn, exp_warn, 'Expected return is %d warning, but %d occured' % (exp_warn, warn))
                self.map_station_mp3_color.pop()
            exp_warn += 1
            warn = config.check_color_vs_map_color_mp3(self.config_color, self.map_station_mp3_color)
            self.assertEqual(warn, exp_warn, 'Expected return is %d warning, but %d occured' % (exp_warn, warn))


class TestCaseCheckConfigsMapMp3VsColors(unittest.TestCase):
    def setUp(self):
        self.station_cnt = 10
        self.config_color = []
        self.map_station_mp3_color = []
        for i in range(ord('a'), ord('n')):
            color = 10 * chr(i)
            self.config_color.append([color, [0, 0, 0]])
            for station in range(self.station_cnt):
                self.map_station_mp3_color.append([station, 'dummy_fn', color])

    def test_correct_configs(self):
        warn = config.check_map_color_mp3_vs_color(self.config_color, self.map_station_mp3_color)
        self.assertEqual(warn, 0, 'Expected return is 0 warning, but %d occured' % warn)

    def test_less_colors_in_map(self):
        exp_warn = 0
        while len(self.config_color) > 0:
            # pprint.pprint(self.map_station_mp3_color)
            warn = config.check_map_color_mp3_vs_color(self.config_color, self.map_station_mp3_color)
            self.assertEqual(warn, exp_warn, 'Expected return is %d warning, but %d occured' % (exp_warn, warn))
            self.config_color.pop()
            exp_warn += self.station_cnt


class TestCaseCheckForValidMp3(unittest.TestCase):
    def setUp(self):
        shutil.copyfile(DEF_PATH_MP3 + MP3_TEST_FILE, DEF_PATH_MP3 + MP3_TEST_FILE_COPY)

    def test_correct_file(self):
        ret = config.check_valid_mp3_content(DEF_PATH_MP3 + MP3_TEST_FILE_COPY)
        self.assertEqual(ret['result'], 'Ok',
                         'Expected return is Ok, but was %s (All return: %s)' % (ret['result'], ret))

    def test_incorrect_file_with_removed_bytes(self):
        # replace_byte_with_zero(MP3_TEST_FILE_COPY, i)
        remove_bytes_from_file(DEF_PATH_MP3 + MP3_TEST_FILE_COPY, 6000)
        ret = config.check_valid_mp3_content(DEF_PATH_MP3 + MP3_TEST_FILE_COPY)
        print(ret)
        self.assertEqual(ret['result'], 'Bad',
                         'Expected return is Bad, but was %s (All return: %s)' %
                         (ret['result'], ret))

    def tearDown(self):
        os.remove(DEF_PATH_MP3 + MP3_TEST_FILE_COPY)


class TestCaseCheckMp3Files(unittest.TestCase):
    def setUp(self):
        shutil.copyfile(DEF_PATH_MP3 + MP3_TEST_FILE, DEF_PATH_MP3 + MP3_TEST_FILE_COPY)
        config.convert_fn = test_convert_fn

    def test_correct_files(self):
        # Setup config map_station_mp3_color and test after each step
        station_cnt = 5
        map_station_mp3_color = []
        for i in range(ord('a'), ord('c')):
            color = 10 * chr(i)
            for station in range(station_cnt):
                map_station_mp3_color.append([station, MP3_TEST_FILE_COPY, color])
                errors = config.check_mp3_files(map_station_mp3_color)
                self.assertEqual(errors, 0,
                                 'Expected return is 0, but was %d' % (errors))

    def test_corrupted_files(self):
        remove_bytes_from_file(DEF_PATH_MP3 + MP3_TEST_FILE_COPY, 6000)
        # Setup config map_station_mp3_color and test after each step
        station_cnt = 5
        map_station_mp3_color = []
        exp_errors = 0
        for i in range(ord('a'), ord('c')):
            color = 10 * chr(i)
            for station in range(station_cnt):
                exp_errors += 1
                map_station_mp3_color.append([station, MP3_TEST_FILE_COPY, color])
                errors = config.check_mp3_files(map_station_mp3_color)
                self.assertEqual(errors, exp_errors,
                                 'Expected return is %d, but was %d' % (exp_errors, errors))

    def test_missing_file(self):
        # Setup config map_station_mp3_color and test after each step
        station_cnt = 10
        map_station_mp3_color = []
        for i in range(ord('a'), ord('n')):
            color = 10 * chr(i)
            for station in range(station_cnt):
                map_station_mp3_color.append([station, 'dummy_fn', color])
                self.assertRaises(config.MP3FileError, config.check_mp3_files, map_station_mp3_color)

    def tearDown(self):
        os.remove(DEF_PATH_MP3 + MP3_TEST_FILE_COPY)


if __name__ == '__main__':
    unittest.main()
