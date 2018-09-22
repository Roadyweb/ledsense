import TCS34725
import yaml

DEF_CONFIG_FN = 'config_default.yaml'
DEF_DESCRIPTION = 'DEFAULT DESCRIPTION'
DEF_DET_THRESHOLD = 2
DEF_RGB_STABLE_CNT = 5
DEF_RGB_STABLE_DIST = 10
DEF_COLORS = [
    # Gelbtöne
    ['RAL 1000 - Grünbeige', [4080.0, 3300.0, 2328.0]],
    ['RAL 1001 - Beige', [4188.0, 3079.0, 2263.0]],
    ['RAL 1002 - Sandgelb', [3888.0, 2799.0, 1889.0]],
    ['RAL 1003 - Signalgelb', [4812.0, 2828.0, 1466.0]],
    ['RAL 1004 - Goldgelb', [4172.0, 2535.0, 1356.0]],
    ['RAL 1005 - Honiggelb', [3232.0, 2102.0, 1196.0]],
    ['RAL 1006 - Maisgelb', [4016.0, 2272.0, 1310.0]],
    ['RAL 1007 - Narzissengelb', [4048.0, 2140.0, 1228.0]],
    ['RAL 1011 - Braunbeige', [2764.0, 1849.0, 1347.0]],
    ['RAL 1012 - Zitronengelb', [3851.0, 2708.0, 1530.0]],
    ['RAL 1013 - Perlweiß', [5165.0, 4411.0, 3649.0]],
    ['RAL 1014 - Elfenbein', [4541.0, 3593.0, 2631.0]],
    ['RAL 1015 - Hellelfenbein', [5117.0, 4189.0, 3297.0]],
    ['RAL 1016 - Schwefelgelb', [5651.0, 4455.0, 2353.0]],
    ['RAL 1017 - Safrangelb', [4890.0, 2856.0, 1728.0]],
    # Blautöne
    ['RAL 5008 - Graublau', [1026.0, 914.0, 842.0]],
    ['RAL 5009 - Azurblau', [1116.0, 1216.0, 1280.0]],
    ['RAL 5010 - Enzianblau', [973.0, 1073.0, 1316.0]],
    ['RAL 5011 - Stahlblau', [887.0, 783.0, 752.0]],
    ['RAL 5012 - Lichtblau', [1476.0, 1990.0, 2394.0]],
    ['RAL 5013 - Kobaltblau', [926.0, 839.0, 878.0]],
    ['RAL 5014 - Taubenblau', [1761.0, 1764.0, 1822.0]],
    ['RAL 5015 - Himmelblau', [1249.0, 1745.0, 2243.0]],
    ['RAL 5017 - Verkehrsblau', [984.0, 1202.0, 1554.0]],
    ['RAL 5018 - Türkisblau', [1451.0, 1959.0, 1856.0]],
    ['RAL 5019 - Capriblau', [1022.0, 1207.0, 1422.0]],
    ['RAL 5020 - Ozeanblau', [894.0, 888.0, 873.0]],
    ['RAL 5021 - Wasserblau', [1114.0, 1494.0, 1449.0]],
    ['RAL 5022 - Nachtblau', [952.0, 851.0, 912.0]],
    ['RAL 5023 - Fernblau', [1351.0, 1440.0, 1592.0]],
]
DEF_SENSOR_INTEGRATIONTIME = TCS34725.TCS34725_INTEGRATIONTIME_50MS,
DEF_SENSOR_GAIN = TCS34725.TCS34725_GAIN_16X,
DEF_CONFIG = {
    'desc': DEF_DESCRIPTION,
    'det': {'threshold': DEF_DET_THRESHOLD},
    'rgb': {
        'stable_cnt': DEF_RGB_STABLE_CNT,
        'stable_dist': DEF_RGB_STABLE_DIST
    },
    'color': DEF_COLORS,
    'sensor': {
        'integration_time': DEF_SENSOR_INTEGRATIONTIME,
        'gain': DEF_SENSOR_GAIN
    }
}


def config_save_default():
    print('Saving default config to %s' % DEF_CONFIG_FN)
    with open(DEF_CONFIG_FN, 'w') as outfile:
        yaml.dump(DEF_CONFIG, outfile, indent=4)


def config_load(fname):
    if fname is None:
        print('No config file given. Using default')
        return DEF_CONFIG

    print('Trying to load config file: %s' % fname)
    with open(fname, 'r') as infile:
        return yaml.load(infile)