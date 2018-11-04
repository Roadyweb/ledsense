#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""LED Sensing.

Usage:
  led_sens.py app [CONFIG]
  led_sens.py app2 [-l logfile] [CONFIG]
  led_sens.py cal [-c count] [-l logfile] [CONFIG]
  led_sens.py cal analysis FILES ...
  led_sens.py color analysis [CONFIG]
  led_sens.py detect [CONFIG]
  led_sens.py diff
  led_sens.py meas (on|off|toggle) [CONFIG]
  led_sens.py play
  led_sens.py save_default
  led_sens.py rgb stable [CONFIG]
  led_sens.py test_speed

Options:
  -c count      Number of calibration cycles [default: 1]
  -l logfile    Log addtionally to logfile
  -h --help     Show this screen.
  --version     Show version.

"""

import copy
import datetime
import logging
import threading
import time

import RPi.GPIO as GPIO
import numpy
import pprint
import yaml
from docopt import docopt

import TCS34725
# Uncomment to remote debug
# import pydevd; pydevd.settrace('192.168.178.80')
import play_music
from config import save_default, load, check_color_vs_map_color_mp3, check_map_color_mp3_vs_color, \
    check_mp3_files, UndefinedStation, get_station, DEF_PATH_CAL
from helper import DrawDiagram, get_rgb_distance, get_rgb_length, get_rgb_median, get_rgb_std, pr, prdbg, prerr, prwarn

GPIO_LED = 4

tcs = None

# Should be probably left this value. Because it add 10% margin to the determined threshold
# 0.053 s = Threshold
LED_TOGGLE_HOLDOFF = 0.060

# LED_TOGGLE_HOLDOFF = 0.053

# Setup logging
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', '%Y.%m.%d %H:%M:%S')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

rootLogger.addHandler(consoleHandler)

LOG_RGB_INT = 10  # seconds
log_rgb_exit = False
last_rgb_measurement = [-1, -1, -1, -1]


def log_rgb():
    global log_rgb_exit
    log_rgb_exit = False
    pr('log_rgb: Starting thread')
    while 42:
        pr('RGBC : %s' % str(last_rgb_measurement))
        # Split wait time into smaller steps to make exiting thread more responsive
        steps = 100
        for i in range(steps):
            sleep_time = (1.0 * LOG_RGB_INT) / (1.0 * steps)
            time.sleep(sleep_time)
            if log_rgb_exit:
                pr('log_rgb: Exit thread')
                return


def measure(debug=False):
    global last_rgb_measurement
    r, g, b, c = tcs.get_raw_data()
    last_rgb_measurement = [r, b, b, c]
    if debug:
        prdbg('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
    return r, g, b, c


def measure_rgb(debug=False):
    r, g, b, c = measure(False)
    if debug:
        prdbg('R: %5d G: %5d B: %5d' % (r, g, b))
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
            prdbg('Cube detected: %4d < %4d' % (c, thres))
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
            prdbg('Cube removed:  %4d > %4d' % (c, thres))
            return c


def get_stable_rgb(count, dist_limit):
    """ If a number of consecutive (count) RGB measurements is within a maximum
        distance (dist_limit) the average of all measurements is calculated and returned.
    """
    if count < 2:
        raise ValueError('Count has to be larger than 2, is %d' % count)

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
            prdbg('Max Dist: %d Dist Limit: %d Restarting... ' % (max_dist, dist_limit))
            continue
        break
    return get_rgb_median(res)


def get_color(rgb, colors, max_rgb_dist):
    """ Takes an RGB list as argument and matches against DEF_COLORS the closest
        will be uses as match. Returns None if match distance is larger than
        max_rgb_distance.
    """
    min_dist = 999999999
    match = 0
    for color in colors:
        color_rgb = color[1]
        dist = get_rgb_distance(rgb, color_rgb)
        if dist < min_dist:
            min_dist = dist
            match = color

    pr('Found %-15s - Dist %d - Cur. RGB: %-20s RGB %-20s' %
       (match[0], min_dist, str(rgb), str(match[1])))

    if min_dist > max_rgb_dist:
        prdbg('Max RGB color dist: %d Dist Limit: %d Exiting... ' % (min_dist, max_rgb_dist))
        return None
    return match[0], match[1], min_dist


def app(config_det, config_rgb, config_color):
    global tcs
    det_threshold = config_det['threshold']
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    rgb_max_dist = config_rgb['max_dist']
    pr('Starting app with detection threshold: %d' % det_threshold)
    pr('Strating color detection with stable count: %d, stable_dist: %d using max distance: %d' %
       (rgb_stable_cnt, rgb_stable_dist, rgb_max_dist))
    while 42:
        detect_cube(det_threshold)
        led_on()
        res = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
        # print(res)
        color = get_color(res, config_color, rgb_max_dist)
        pr('%-15s - Distance: %5d - Cur. RGB: %-25s RGB %-20s' %
           (color[0], color[2], str(res), str(color[1])))
        detect_cube_removal(det_threshold)


def app2(config_det, config_rgb, config_color, map_station_mp3_color):
    global tcs
    global log_rgb_exit

    det_threshold = config_det['threshold']
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    rgb_max_dist = config_rgb['max_dist']
    pr('Starting with detection threshold: %d' % det_threshold)
    pr('Starting color detection with stable count: %d, stable_dist: %d using max distance: %d' %
       (rgb_stable_cnt, rgb_stable_dist, rgb_max_dist))

    check_color_vs_map_color_mp3(config_color, map_station_mp3_color)
    check_map_color_mp3_vs_color(config_color, map_station_mp3_color)

    check_mp3_files(map_station_mp3_color)

    try:
        station = get_station()
    except UndefinedStation as e:
        prerr('UndefinedStationError: %s . Exiting ...' % e)
        return

    # Start play_music and rbg_log threads
    pm = threading.Thread(target=play_music.main, name='play_music.main', args=(map_station_mp3_color, station))
    pm.start()
    rgb_log = threading.Thread(target=log_rgb, name='log_rgb')
    rgb_log.start()

    try:
        while 42:
            detect_cube(det_threshold)
            led_on()
            res = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
            color = get_color(res, config_color, rgb_max_dist)
            if not pm.is_alive():
                prerr('Thread %s unexpectedly died. Exiting...' % pm.getName())
                break
            if not rgb_log.is_alive():
                prerr('Thread %s unexpectedly died. Exiting...' % rgb_log.getName())
                break
            if color is not None:
                play_music.stop_playing = False
                play_music.start_playing = color[0]
            else:
                pr('Max RGB color distance exceeded. Not playing...')
            detect_cube_removal(det_threshold)
            play_music.stop_playing = True
    except KeyboardInterrupt:
        pr('Keyboard interrupt detected, Stopping threads ..')

    finally:
        play_music.exit_thread = True
        log_rgb_exit = True
        pm.join(3)
        rgb_log.join(3)


def cal(config_det, config_rgb, config_color, config_sensor, cnt):
    det_threshold = config_det['threshold']
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    rgb_max_dist = config_rgb['max_dist']
    cnt = int(cnt)
    pr('Starting with detection threshold: %d' % det_threshold)
    pr('Starting color detection with stable count: %d, stable_dist: %d using max distance: %d' %
       (rgb_stable_cnt, rgb_stable_dist, rgb_max_dist))

    try:
        station = get_station()
    except UndefinedStation as e:
        prerr('UndefinedStationError: %s . Exiting ...' % e)
        return

    res = {}
    # Init dict
    for color_name, config_rgb in config_color:
        res[color_name] = {}
        res[color_name]['config'] = config_rgb
        res[color_name]['values'] = []
        res[color_name]['mean'] = [0, 0, 0]
        res[color_name]['std'] = [0, 0, 0]

    # Do calibration loop
    first_run = True
    last_color_rgb = [0, 0, 0]
    for color_name, config_rgb in config_color:
        color_changed = False
        print('Put color %s on detector' % color_name)
        for cycle in range(cnt):
            while 42:
                detect_cube(det_threshold)
                led_on()
                rgb = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
                pr('Remove cube')
                detect_cube_removal(det_threshold)

                # Check if the cube color has really changed
                dist_last_rgb = get_rgb_distance(last_color_rgb, rgb)
                if first_run:
                    first_run = False
                    color_changed = True
                    break
                if color_changed:
                    break
                # TODO: Adjust threshold
                if dist_last_rgb > 300:
                    color_changed = True
                    break
                prwarn('Please use the correct color %s, it seems you still using the old one. Dist: %d' %
                       (color_name, dist_last_rgb))

            dist_config = get_rgb_distance(config_rgb, rgb)
            dist_mean = get_rgb_distance(res[color_name]['mean'], rgb)
            res[color_name]['values'].append(rgb)
            res[color_name]['mean'] = get_rgb_median(res[color_name]['values'])
            res[color_name]['std'] = get_rgb_std(res[color_name]['values'])
            pr('%-15s Distances: Config %d, Mean %d (%d of %d)' %
               (color_name, dist_config, dist_mean, cycle + 1, cnt))
        last_color_rgb = res[color_name]['mean']

    # Eval result
    for color_name, config_rgb in config_color:
        config_rgb = res[color_name]['config']
        mean_rgb = res[color_name]['mean']
        dist = get_rgb_distance(config_rgb, mean_rgb)
        std = int(numpy.linalg.norm(res[color_name]['std']))
        print('%-35s Distances: Config vs Mean %4d, Std %4s' %
              (color_name, dist, str(std)))

    # Print YAML file
    res_yaml = []
    res_yaml_values = []
    for color_name, _ in config_color:
        rgb = res[color_name]['mean']
        values = res[color_name]['values']
        res_yaml.append([color_name, rgb])
        res_yaml_values.append([color_name, values])
    print(80 * '*')
    print('Printing YAML config')
    print(yaml.dump(res_yaml))

    # Rewrite config file with new values
    timestamp = str(datetime.datetime.now())
    path = DEF_PATH_CAL + '%s_station_%d.yaml' % (timestamp, station)
    cfg = {
        'desc': 'Automatically created with calibration routine date: %s, station: %d' %
                (timestamp, station),
        'det': config_det,
        'rgb': config_rgb,
        'sensor': config_sensor,
        'color': res_yaml,
        'values': res_yaml_values,
        'station': station
    }

    pr('Also saving to %s' % path)
    with open(path, 'w') as outfile:
        yaml.dump(cfg, outfile, indent=4)


def cal_analysis(files):
    configs = []
    for file in files:
        configs.append(load(file))

    # check for same color count in values and color entries, use config #1 as reference
    pr('Checking for same colors in all configs (values and color entry) using %s as reference' %
       files[0])
    first_run = True
    color_cnt = 0
    colors = []
    for i, config in enumerate(configs):
        if first_run:
            config_color = config['color']
            color_cnt = len(config_color)
            for color in config_color:
                colors.append(color[0])
            first_run = False

        cur_color_cnt = len(config['color'])
        if cur_color_cnt != color_cnt:
            pr('Color count differs in %s [''color''](%d vs %d) Exiting' % (files[i], cur_color_cnt, color_cnt))
            return

        cur_values_cnt = len(config['values'])
        if cur_values_cnt != color_cnt:
            pr('Color count differs in %s [''values''](%d vs %d) Exiting' % (files[i], cur_color_cnt, color_cnt))
            return

        cur_colors = config['color']
        cur_values = config['values']
        for j, color_name in enumerate(colors):
            cur_color_name = cur_colors[j][0]
            if cur_color_name != color_name:
                pr('Color differs in %s [''color''](%s vs %s) Exiting' % (files[i], cur_color_name, color_name))
                return

            cur_values_name = cur_values[j][0]
            if cur_values_name != color_name:
                pr('Color differs in %s [''values''](%s vs %s) Exiting' % (files[i], cur_values_name, color_name))
                return
    pr('Everything is fine, lets start ...')

    # pprint.pprint(colors)

    # Calc overall means
    over_all_means = []
    over_all_std = []
    over_all_values = []
    for j, color_name in enumerate(colors):
        pr('Starting with %s' % color_name)
        cur_values_all = []
        for i, config in enumerate(configs):
            cur_values = config['values'][j][1]
            for values in cur_values:
                cur_values_all.append(values)
        # TODO: if the files contain different numbers of measures values the mean is calculated wrong!!!
        # TODO: solution, calc the mean of means on a per station basis
        over_all_means.append([color_name, get_rgb_median(cur_values_all)])
        over_all_std.append([color_name, get_rgb_std(cur_values_all)])
        over_all_values.append([color_name, cur_values_all])

    pprint.pprint(over_all_means)
    pprint.pprint(over_all_std)

    # Calc stats OK/NOK
    #                   Stat1   Stat2
    # Color 1            1/10    2/10
    # Color 2            9/10    3/10
    # ...

    # Calc stats dist
    #                   Stat1    Stat2
    #                 avg/max  avg/max
    # Color 1           1/ 10    2/ 10
    # Color 2           9/ 10    3/ 10
    # ...

    over_all_stats = []
    over_all_dists = []
    nok_stats = []
    for j, color_name in enumerate(colors):
        pr('Starting with %s' % color_name)
        station_stats = []
        station_dists = []
        for i, config in enumerate(configs):
            ok = 0
            cnt = 0
            color_values = config['values'][j][1]
            station_name = config['station']
            print('Station: %s' % station_name)
            dists = []
            for color_value in color_values:
                cnt += 1
                color_res, _, dist = get_color(color_value, over_all_means, 100000)
                if color_res == color_name:
                    ok += 1
                    dists.append(dist)
                else:
                    nok_stats.append([station_name, color_name, color_res])
            station_stats.append([ok, cnt])
            station_dists.append(dists)
        over_all_stats.append([color_name, station_stats])
        over_all_dists.append([color_name, station_dists])

    # and print it out in a nice table (OK/NOK)
    print(80 * '*')
    print(35 * ' ', end='')
    for config in configs:
        print('%9s' % config['station'], end='')
    print()
    print(35 * ' ', end='')
    for config in configs:
        print('   OK/CNT', end='')
    print()
    for color_name, results in over_all_stats:
        print('%35s' % color_name, end='')
        for result in results:
            ok = result[0]
            cnt = result[1]
            print('  %3d/%3d' % (ok, cnt), end='')
        print()

    # and print it out in a nice table (distances)
    print(80 * '*')
    print(35 * ' ', end='')
    for config in configs:
        print('%10s' % config['station'], end='')
    print()
    print(35 * ' ', end='')
    for config in configs:
        print('  AVG/ MAX', end='')
    print()
    for color_name, results in over_all_dists:
        print('%35s' % color_name, end='')
        for result in results:
            if len(result) == 0:
                max_dist = '----'
                avg_dist = '----'
            else:
                max_dist = max(result)
                avg_dist = int(numpy.mean(result))
            print(' %4s/%4s' % (avg_dist, max_dist), end='')
        print()

    print(80 * '*')
    for nok in nok_stats:
        print('Station: %2s: set: %30s - act: %30s' % tuple(nok))

    # Create a new config file with calculated values
    # Rewrite config file with new values
    timestamp = str(datetime.datetime.now())
    path = DEF_PATH_CAL + '%s_all.yaml' % timestamp
    desc = 'Automatically created with cal analysis routine date: %s ' % timestamp
    for i, file in enumerate(files):
        desc += 'File %d: ''%s'', ' % (i, file)

    cfg = {
        'desc': desc,
        'det': configs[0]['det'],
        'rgb': configs[0]['rgb'],
        'sensor': configs[0]['sensor'],
        'color': over_all_means,
    }

    pr('Also saving to %s' % path)
    with open(path, 'w') as outfile:
        yaml.dump(cfg, outfile, indent=4)


def color_analyse(config_color):
    def get_key(item):
        return item[0]

    # Print results
    print('******************** Distance between all result ********************')

    def dummy(x, y, z):
        return x, y, z

    cs_map = (
        ('RGB', dummy),
        # import colorsys
        # Pretty useless since differences in all colorspaces are the same
        # ('YIQ', colorsys.rgb_to_yiq),
        # ('HLS', colorsys.rgb_to_hls),
        # ('YIQ', colorsys.rgb_to_hsv)
    )
    for cs_name, cs_func in cs_map:
        res = []

        # Calculate distance between all colors
        config_color2 = copy.deepcopy(config_color)
        for color1 in config_color:
            del config_color2[0]
            for color2 in config_color2:
                # print(color1, color2)
                name1 = color1[0]
                name2 = color2[0]
                color1_converted = cs_func(color1[1][0], color1[1][1], color1[1][2])
                color2_converted = cs_func(color2[1][0], color2[1][1], color2[1][2])
                dist = get_rgb_distance(color1_converted, color2_converted)
                res.append((dist, (name1, color1_converted), (name2, color2_converted)))

        print('******************** Colorspace %s **********' % cs_name)
        # pprint.pprint(res)
        sorted_res = sorted(res, key=get_key)
        # pprint.pprint(sorted_res)
        for entry in sorted_res[:10]:
            # print(entry)
            # return
            dist = entry[0]
            name1 = entry[1][0]
            rgb1 = entry[1][1]
            name2 = entry[2][0]
            rgb2 = entry[2][1]
            rgb1_str = '(%5d %5d %5d)' % rgb1
            rgb2_str = '(%5d %5d %5d)' % rgb2
            print('%s: Dist: %4d (%-25s %-25s) : %s %s' %
                  (cs_name, dist, name1, name2, rgb1_str, rgb2_str))

        dist = []
        for i in sorted_res:
            dist.append(i[0])
        # print(dist)

        print('Distance   - Avg: %5d Std: %5d, Min: %5d, Max: %5d' %
              (int(numpy.mean(dist)), int(numpy.std(dist)), min(dist), max(dist)))

    print('******************** Length for all all colors ********************')

    rgb_len = []
    for i in config_color:
        rgb_len.append(get_rgb_length(i[1]))
    # print(rgb_len)

    print('RGB Length - Avg: %5d Std: %5d, Min: %5d, Max: %5d' %
          (int(numpy.mean(rgb_len)), int(numpy.std(rgb_len)), min(rgb_len), max(rgb_len)))


def detect(config):
    global tcs
    threshold = config['threshold']
    while 42:
        value = detect_cube(threshold)
        value = detect_cube_removal(threshold)


def diff():
    global tcs

    while 42:
        led_on()
        r, g, b, c = measure()
        prdbg('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))
        led_off()
        r2, g2, b2, c2 = measure()
        prdbg('R: %5d G: %5d B: %5d C: %5d' % (r2, g2, b2, c2))
        rgb = (r, g, b)
        rgb2 = (r2, g2, b2)
        rgb_len = get_rgb_length(rgb)
        rgb2_len = get_rgb_length(rgb2)
        rgb_diff = get_rgb_distance(rgb, rgb2)
        clear_diff = abs(c - c2)
        pr('Len %5d %5d %5d Clear: %5d %5d %5d' %
           (rgb_len, rgb2_len, rgb_diff, c, c2, clear_diff))


def meas(conf_led_on, toggle):
    global tcs

    dd = DrawDiagram(40)

    if toggle:
        while 42:
            led_on()
            for _ in range(3):
                r, g, b, c = measure()
                dd.add(r)
                pr('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                   (r, g, b, c, dd.getstr()))

            led_off()
            for _ in range(3):
                r, g, b, c = measure()
                dd.add(r)
                pr('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                   (r, g, b, c, dd.getstr()))

    led(conf_led_on)

    while 42:
        r, g, b, c = measure()
        pr('R: %5d G: %5d B: %5d C: %5d' % (r, g, b, c))


def rgb_stable(config_rgb):
    rgb_stable_cnt = config_rgb['stable_cnt']
    rgb_stable_dist = config_rgb['stable_dist']
    pr('Starting rgb_stable with stable count: %5d, stable_dist: %5d' %
       (rgb_stable_cnt, rgb_stable_dist))
    led_on()

    while 42:
        res = get_stable_rgb(rgb_stable_cnt, rgb_stable_dist)
        prdbg(res)
        pr('RGB: %25s' % str(res))


def test_speed():
    global LED_TOGGLE_HOLDOFF
    global tcs
    sleep_duration = 1.0
    #    LED_TOGGLE_HOLDOFF = 1.2 * LED_TOGGLE_HOLDOFF
    #    sleep_duration = LED_TOGGLE_HOLDOFF
    rep_cnt = 2
    cycle_cnt = 20

    dd = DrawDiagram(40)
    res = []

    try:
        while 42:
            sleep_duration = 0.98 * sleep_duration
            # LED_TOGGLE_HOLDOFF = sleep_duration
            tcs.set_sleep_factor(sleep_duration)

            start = datetime.datetime.now()
            for i in range(cycle_cnt):
                led_on()
                for _ in range(rep_cnt):
                    r, g, b, c = measure()
                    dd.add(r, expected=1)
                    print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                          (r, g, b, c, dd.getstr()))

                led_off()
                for _ in range(rep_cnt):
                    r, g, b, c = measure()
                    dd.add(r, expected=0)
                    print('R: %5d G: %5d B: %5d C: %5d | %-40s' %
                          (r, g, b, c, dd.getstr()))
            duration = datetime.datetime.now() - start
            duration_ms = int(duration.total_seconds() * 1000)
            meas_cnt = cycle_cnt * 2 * rep_cnt
            meas_avg_duration = duration_ms / meas_cnt
            print('**** Summary ****')
            print('Setting to %f' % sleep_duration)
            print('Duration for %d measurements: %5d ms' % (meas_cnt, duration_ms))
            print('Duration per measurements: %5d ms' % meas_avg_duration)
            res.append((sleep_duration,
                        dd.get_stat_cnt(),
                        dd.get_stat_good_percent(),
                        dd.get_stat_bad_dev(),
                        meas_avg_duration))
            dd.stat_reset()
            time.sleep(2)
    except KeyboardInterrupt:
        print('**** Stats for series ****')
        for i in res:
            print('Setting: %5.4fms Cnt: %3d Good: %6.2f%% Bad Dev: %6.1f Avg. Dura: %5.2f' % i)


def setup(config):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_LED, GPIO.OUT)
    time.sleep(0.05)
    global tcs
    integration_time = config['integration_time'][0]
    gain = config['gain'][0]
    pr('Setting TCS config: Integration time: %5d Gain: %5d' % (integration_time, gain))
    tcs = TCS34725.TCS34725(integration_time=integration_time,
                            gain=gain,
                            i2c=1)


def endprogram():
    GPIO.cleanup()


def main():
    args = docopt(__doc__, version='LED Sensing')
    # prdbg(args)

    # Check if we want also to log to a file
    if args['-l'] is not None:
        filehandler = logging.FileHandler(args['-l'])
        filehandler.setFormatter(logFormatter)
        rootLogger.addHandler(filehandler)

    config = load(args['CONFIG'])
    # pprint.pprint(config)
    setup(config['sensor'])

    try:
        if args['app']:
            app(config['det'], config['rgb'], config['color'])
        elif args['app2']:
            app2(config['det'], config['rgb'], config['color'], config['map_station_mp3_color'])
        elif args['cal'] and not args['analysis']:
            cal(config['det'], config['rgb'], config['color'], config['sensor'], args['-c'])
        elif args['cal'] and args['analysis']:
            cal_analysis(args['FILES'])
        elif args['color'] and args['analysis']:
            color_analyse(config['color'])
        elif args['detect']:
            detect(config['det'])
        elif args['diff']:
            diff()
        elif args['meas']:
            meas(args['on'], args['toggle'])
        elif args['rgb'] and args['stable']:
            rgb_stable(config['rgb'])
        elif args['save_default']:
            save_default()
        elif args['test_speed']:
            test_speed()
        else:
            pr('Not implemented')

    except KeyboardInterrupt:
        endprogram()


if __name__ == '__main__':
    # cProfile.run('main()', 'restats')
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative')
    # p.print_stats()
    # p.strip_dirs().sort_stats(-1).print_stats()
    main()
