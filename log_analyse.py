#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy
import numpy
import pprint
import re

import config

REGEX_RGBC = r'[\d\.\:\s]*INFO\sRGBC.*'

REGEX_STATION = r'[\d\.\:\s]*INFO\sFound\sstation\:\s(\w)*'

REGEX_COLOR = r'[\d\.\:\s]*INFO\sFound\s([\w\s\=äüö]*)\s\-\sDist\s(\d*)\s\-\sCur.\sRGB\:\s\[(.*)\]\s*RGB\s*\[(.*)\]\s*([\w-]*)'

'''
raw_data structure
rawdata = {station_name1: [ {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            ...
                          ]
          },
          {station_name2: [ {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            {color_name: x, dist: y, rgb_meas: [r, g, b], rgb_config: [r, g, b], result: v},
                            ...
                          ],
          },
          ...
          }
'''

def unique_list_entries(some_list):
    # a set can only contain unique elements
    return list(set(some_list))


def clean_log(lines_list):
    ret = []
    for line in lines_list:
        line = line.replace('\n', '')
        matchObj = re.search(REGEX_RGBC, line, re.S)
        if not matchObj:
            ret.append(line)
        else:
            # print('Removing line: %s' % line)
            pass
    removed_lines = len(lines_list) - len(ret)
    print('Removed %d of %d lines' % (removed_lines, len(lines_list)))
    return ret


def extract_station(lines_list):
    station_list = []
    # First extract all the station numbers
    for line in lines_list:
        matchObj = re.search(REGEX_STATION, line, re.S)
        if matchObj:
            station_list.append(int(matchObj.group(1)))
    # Now check that the station number is unique
    unique_station_list = unique_list_entries(station_list)
    # print(unique_station_list)
    return unique_station_list


def extract_color_results(lines_list):
    ret = []
    for line in lines_list:
        matchObj = re.search(REGEX_COLOR, line, re.S)
        res = {}
        if matchObj:
            res['color_name'] = str(matchObj.group(1))
            res['dist'] = int(matchObj.group(2))
            res['rgb_meas'] = matchObj.group(3)
            res['rgb_config'] = matchObj.group(4)
            res['result'] = matchObj.group(5)
            ret.append(res)
        else:
            # print('No color result found in %s' % line)
            pass
    return ret


def check_for_common_rgb_config(color_results):
    # dict for check rgb_config vs color_name
    unique_rgb_config1 = {}
    # dict for check color_name vs rgb_config
    unique_rgb_config2 = {}
    for color_result in color_results:
        # pprint.pprint(color_result)
        rgb_config = color_result['rgb_config']
        color_name = color_result['color_name']
        if rgb_config not in unique_rgb_config1:
            unique_rgb_config1[rgb_config] = color_name
        else:
            # Should happen not very often, that the same RGB configuration has different names
            if unique_rgb_config1[rgb_config] != color_name:
                print('Warning: color names for rgb_config %s differ (%s vs %s)' %
                      (rgb_config, unique_rgb_config1[rgb_config], color_name))
                return None
        if color_name not in unique_rgb_config2:
            unique_rgb_config2[color_name] = rgb_config
        else:
            # Should happen not very often, that the same RGB configuration has different names
            if unique_rgb_config2[color_name] != rgb_config:
                print('Warning: rgb_config for color_name %s differ (%s vs %s)' %
                      (color_name, unique_rgb_config2[color_name], rgb_config))
                return None
    return unique_rgb_config1


def check_for_common_rgb_config_over_raw_data(raw_rgb_config_data):
    rgb_configs = {}
    color_names = []
    for station, station_results in raw_rgb_config_data.items():
        # convert station_results to list, later to set
        rgb_config_color_name_list = []
        for rgb_config, color_name in station_results.items():
            rgb_config_color_name_list.append(color_name + ' ' + rgb_config)
            color_names.append(color_name)
        rgb_configs[station] = set(rgb_config_color_name_list)
    color_names_unique = unique_list_entries(color_names)

    # pprint.pprint(rgb_configs)

    # Find a union set of rgb configs over all stations
    union_set = set()
    for station, rgb_config_color_name in rgb_configs.items():
        union_set = union_set.union(rgb_config_color_name)

    # Find intersection
    inter_set = copy.deepcopy(union_set)
    for station, rgb_config_color_name in rgb_configs.items():
        inter_set = inter_set.intersection(rgb_config_color_name)

    print('Found %d different RGB config. %d were common to all logs' % (len(union_set), len(inter_set)))

    for station, rgb_config_color_name in rgb_configs.items():
        missing_set = union_set.difference(rgb_config_color_name)
        if len(missing_set) > 0:
            print('For station %s are missing:' % station)
            for missing in missing_set:
                print('   RGB Config: %s' % missing)
        else:
            print('For station %s nothing is missing hooray' % station)
    return color_names_unique


def eval_unique_color_names(raw_data):
    unique_colors = {}
    for station, station_results in raw_data.items():
        for result in station_results:
            color_name = result['color_name']
            if color_name not in unique_colors:
                unique_colors[color_name] = 1
            else:
                unique_colors[color_name] += 1
    return unique_colors


def eval_distance_per_color(raw_data, ignore_nok=False, ignore_undef=False):
    color_distances = {}
    for station, station_results in raw_data.items():
        for result in station_results:
            color_name = result['color_name']
            color_dist = result['dist']
            ok_nok_undef = result['result']
            if ignore_nok and ok_nok_undef == config.STR_NOK:
                continue
            if ignore_undef and ok_nok_undef == config.STR_UNDEF:
                continue
            if color_name not in color_distances:
                color_distances[color_name] = {}
                color_distances[color_name]['values'] = [color_dist]
            else:
                color_distances[color_name]['values'].append(color_dist)
    # pprint.pprint(color_distances)

    # Add some stats
    for color_name, res in color_distances.items():
        value_list = res['values']
        color_distances[color_name]['cnt'] = len(value_list)
        color_distances[color_name]['min'] = min(value_list)
        color_distances[color_name]['max'] = max(value_list)
        color_distances[color_name]['avg'] = int(numpy.mean(value_list))

    return color_distances


def eval_ok_nok_undef(raw_data):
    color_ok_nok_undef = {}
    for station, station_results in raw_data.items():
        for result in station_results:
            color_name = result['color_name']
            color_res = result['result']
            if color_name not in color_ok_nok_undef:
                color_ok_nok_undef[color_name] = {}
                color_ok_nok_undef[color_name]['ok'] = 0
                color_ok_nok_undef[color_name]['nok'] = 0
                color_ok_nok_undef[color_name]['undef'] = 0
            if color_res == 'OK':
                color_ok_nok_undef[color_name]['ok'] += 1
            elif color_res == 'NOK':
                color_ok_nok_undef[color_name]['nok'] += 1
            elif color_res == '---':
                color_ok_nok_undef[color_name]['undef'] += 1
            else:
                print('WARNING: Unexpected res %s, should be OK, NOK or ---' % color_res)
    return color_ok_nok_undef


def main():
    raw_data = {}
    raw_rgb_config_data = {}
    fn_list = ['station1.log', 'station1a.log', 'station1b.log', 'station2.log', 'station12.log', 'station3.log',
               'station4.log', 'station5.log', 'station35.log']
    for fn in fn_list:
        with open(fn, 'r') as file:
            content = file.readlines()
        print(80 * '*')
        print('Analysing logfile %s' % fn)
        # content = clean_log(content)
        stations = extract_station(content)
        if len(stations) > 1:
            print('WARNUNG: Ignoring log file %s. Contains multiple station entries %s' % (fn, stations))
            continue
        res = extract_color_results(content)

        # convert result to raw_data with only one station to be able to reuse func later
        res_rgb_config = check_for_common_rgb_config(res)
        if res_rgb_config is None:
            print('WARNUNG: Ignoring log file %s. RGB config is redefined' % fn)
            continue

        # pprint.pprint(res_rgb_config, width=120)

        print('Logfile %s OK' % fn)

        raw_data[stations[0]] = res
        raw_rgb_config_data[stations[0]] = res_rgb_config

    # pprint.pprint(raw_data)

    print(80 * '*')
    print('Checking RGB config consistency over all logs')
    color_names_unique = check_for_common_rgb_config_over_raw_data(raw_rgb_config_data)

    # Start analysis
    print(80 * '*')
    print('Analysing deviation from configured rgb values over all stations')
    res = eval_distance_per_color(raw_data)
    for color_name, res in res.items():
        cnt = res['cnt']
        min = res['min']
        max = res['max']
        avg = res['avg']
        print('Color %-35s cnt: %2d min: %4d, avg: %4d, max: %4d' % (color_name, cnt, min, avg, max))

    print(80 * '*')
    print('Analysing deviation from configured rgb values per stations')
    # Now do this per station
    # to reuse code we feed only per station data to the same function
    for station_name, res in raw_data.items():
        print('Results for station %s' % station_name)
        raw_data_part = {station_name: res}
        res_part = eval_distance_per_color(raw_data_part)
        for color_name, res_color in res_part.items():
            cnt = res_color['cnt']
            min = res_color['min']
            max = res_color['max']
            avg = res_color['avg']
            print('Color %-35s cnt: %2d min: %4d, avg: %4d, max: %4d' % (color_name, cnt, min, avg, max))

    print(80 * '*')
    print('Analysing deviation from configured rgb values over all stations, ignore NOK and UNDEF')
    res = eval_distance_per_color(raw_data, ignore_nok=True, ignore_undef=True)
    for color_name, res in res.items():
        cnt = res['cnt']
        min = res['min']
        max = res['max']
        avg = res['avg']
        print('Color %-35s cnt: %2d min: %4d, avg: %4d, max: %4d' % (color_name, cnt, min, avg, max))

    print(80 * '*')
    print('Analysing deviation from configured rgb values per stations, ignore NOK and UNDEF')
    # Now do this per station
    # to reuse code we feed only per station data to the same function
    for station_name, res in raw_data.items():
        print('Results for station %s' % station_name)
        raw_data_part = {station_name: res}
        res_part = eval_distance_per_color(raw_data_part, ignore_nok=True, ignore_undef=True)
        for color_name, res_color in res_part.items():
            cnt = res_color['cnt']
            min = res_color['min']
            max = res_color['max']
            avg = res_color['avg']
            print('Color %-35s cnt: %2d min: %4d, avg: %4d, max: %4d' % (color_name, cnt, min, avg, max))

    print(80 * '*')
    print('Analysing OKs, NOKs and undefs over all stations')
    res = eval_ok_nok_undef(raw_data)
    for color_name, res in res.items():
        ok = res['ok']
        nok = res['nok']
        undef = res['undef']
        cnt = ok + nok + undef
        print('Color %-35s cnt: %2d ok: %2d, nok: %4d, undef: %4d' % (color_name, cnt, ok, nok, undef))

    print(80 * '*')
    print('Analysing OKs, NOKs and undefs per stations')
    # Now do this per station
    # to reuse code we feed only per station data to the same function
    for station_name, res in raw_data.items():
        print('Results for station %s' % station_name)
        raw_data_part = {station_name: res}
        res_part = eval_ok_nok_undef(raw_data_part)
        for color_name, res_color in res_part.items():
            ok = res_color['ok']
            nok = res_color['nok']
            undef = res_color['undef']
            cnt = ok + nok + undef
            print('Color %-35s cnt: %2d ok: %2d, nok: %4d, undef: %4d' % (color_name, cnt, ok, nok, undef))

    print(80 * '*')


if __name__ == '__main__':
    # cProfile.run('main()', 'restats')
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative')
    # p.print_stats()
    # p.strip_dirs().sort_stats(-1).print_stats()
    main()
