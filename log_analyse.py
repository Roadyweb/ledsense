#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy
import pprint
import re

REGEX_RGBC = r'[\d\.\:\s]*INFO\sRGBC.*'

REGEX_STATION = r'[\d\.\:\s]*INFO\sFound\sstation\:\s(\w)*'

REGEX_COLOR = r'[\d\.\:\s]*INFO\sFound\s([\w\s\=äüö]*)\s\-\sDist\s(\d*)\s\-\sCur.\sRGB\:\s\[(.*)\]\s*RGB\s*\[(.*)\]\s*(\w*)'


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


def clean_log(lines_list):
    ret = []
    for line in lines_list:
        line = line.replace('\n', '')
        matchObj = re.search(REGEX_RGBC, line, re.S)
        if not matchObj:
            ret.append(line)
        else:
            print('Removing line: %s' % line)
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
    unique_station_list = list(set(station_list))
    print(unique_station_list)
    return station_list


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
            print('No color result found in %s' % line)
    return ret


def extract_unique_color_names(raw_data):
    unique_colors = {}
    for station, station_results in raw_data.items():
        for result in station_results:
            color_name = result['color_name']
            if color_name not in unique_colors:
                unique_colors[color_name] = 1
            else:
                unique_colors[color_name] +=1
    return unique_colors


def extract_distance_per_color(raw_data):
    color_distances = {}
    for station, station_results in raw_data.items():
        for result in station_results:
            color_name = result['color_name']
            color_dist = result['dist']
            if color_name not in color_distances:
                color_distances[color_name] = {}
                color_distances[color_name]['values'] = [color_dist]
            else:
                color_distances[color_name]['values'].append(color_dist)
    #pprint.pprint(color_distances)

    # Add some stats
    for color_name, res in color_distances.items():
        value_list = res['values']
        color_distances[color_name]['cnt'] = len(value_list)
        color_distances[color_name]['min'] = min(value_list)
        color_distances[color_name]['max'] = max(value_list)
        color_distances[color_name]['avg'] = int(numpy.mean(value_list))

    return color_distances


def main():
    raw_data = {}
    fn_list = ['station1.log', 'station2.log', 'station12.log']
    for fn in fn_list:
        with open(fn, 'r') as file:
            content = file.readlines()
        content = clean_log(content)
        stations = extract_station(content)
        if len(stations) > 1:
            print('Ignoring log file %s. Contains multiple station entries %s' % (fn, stations))
            continue
        res = extract_color_results(content)
        raw_data[stations[0]] = res

    # Start analysis
    print('Info: Extracting unique color names over all stations')
    res = extract_unique_color_names(raw_data)
    pprint.pprint(res, width=120)
    print(80 * '*')

    print('Info: Extracting unique color names per station')
    # Now do this per station
    # to reuse code we feed only per station data to the same function
    for station_name, res in raw_data.items():
        print('Results for station %s' % station_name)
        raw_data_part = {}
        raw_data_part[station_name] = res
        res = extract_unique_color_names(raw_data)
        pprint.pprint(res, width=120)
    print(80 * '*')

    print('Analysing deviation from configured rgb values over all stations')
    res = extract_distance_per_color(raw_data)
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
        raw_data_part = {}
        raw_data_part[station_name] = res
        res = extract_distance_per_color(raw_data)
        for color_name, res in res.items():
            cnt = res['cnt']
            min = res['min']
            max = res['max']
            avg = res['avg']
            print('Color %-35s cnt: %2d min: %4d, avg: %4d, max: %4d' % (color_name, cnt, min, avg, max))
    print(80 * '*')




if __name__ == '__main__':
    # cProfile.run('main()', 'restats')
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative')
    # p.print_stats()
    # p.strip_dirs().sort_stats(-1).print_stats()
    main()
