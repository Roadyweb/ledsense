import logging
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

DEF_STATION_GPIOS = [21, 20, 26, 16, 19, 13, 12, 6, 5, 7]
DEF_STATION_GPIO_MAP = (
    ((0, 1, 1, 1, 1, 1, 1, 1, 1, 1), 1),
    ((1, 0, 1, 1, 1, 1, 1, 1, 1, 1), 2),
    ((1, 1, 0, 1, 1, 1, 1, 1, 1, 1), 3),
    ((1, 1, 1, 0, 1, 1, 1, 1, 1, 1), 4),
    ((1, 1, 1, 1, 0, 1, 1, 1, 1, 1), 5),
    ((1, 1, 1, 1, 1, 0, 1, 1, 1, 1), 6),
    ((1, 1, 1, 1, 1, 1, 0, 1, 1, 1), 7),
    ((1, 1, 1, 1, 1, 1, 1, 0, 1, 1), 8),
    ((1, 1, 1, 1, 1, 1, 1, 1, 0, 1), 9),
    ((1, 1, 1, 1, 1, 1, 1, 1, 1, 0), 10)
)

DEF_STATION_COLOR_MP3_MAP = (
    (1, "011_Ti1_Rollenspiel_Albrecht-Duerer.mp3"       , "RAL 1003 gelb"          ),
    (1, "011e_Ti1_Roleplay_Albrecht-Duerer.mp3"         , "RAL 1001 beige"         ),
    (1, "012_Ti1_Rollenspiel_Lara-Croft.mp3"            , "RAL 5024 pastelblau"    ),
    (1, "012e_Ti1_Roleplay_Lara-Croft.mp3"              , "RAL 5019 capriblau"     ),
    (1, "013_Ti1_Rollenspiel_Manga.mp3"                 , "RAL 3022 lachsrot"      ),
    (1, "013e_Ti1_Roleplay_Manga.mp3"                   , "RAL 3013 tomatenrot"    ),
    (1, "014_Ti1_Rollenspiel_Nbg-Docke.mp3"             , "RAL 5018 türkisblau"    ),
    (1, "014e_Ti1_Roleplay_Nbg-Docke.mp3"               , "RAL 6034 pasteltürkis"  ),
    (1, "015_Ti1_Rollenspiel_Roboter.mp3"               , "RAL 1000 grünbeige"     ),
    (1, "015e_Ti1_Roleplay_Roboter.mp3"                 , "RAL 6021 blassgrün"     ),
    (2, "021_Ti2_bauen-konstruieren_Albrecht-Duerer.mp3", "RAL 1003 gelb"          ),
    (2, "021e_Ti2_construction_Albrecht-Duerer.mp3"     , "RAL 1001 beige"         ),
    (2, "022_Ti2_bauen-konstruieren_Lara-Croft.mp3"     , "RAL 5024 pastelblau"    ),
    (2, "022e_Ti2_construction_Lara-Croft.mp3"          , "RAL 5019 capriblau"     ),
    (2, "023_Ti2_bauen-konstruieren_Manga.mp3"          , "RAL 3022 lachsrot"      ),
    (2, "023e_Ti2_construction_Manga.mp3"               , "RAL 3013 tomatenrot"    ),
    (2, "024_Ti2_bauen-konstruieren_Nbg-Docke.mp3"      , "RAL 5018 türkisblau"    ),
    (2, "024e_Ti2_construction_Nbg-Docke.mp3"           , "RAL 6034 pasteltürkis"  ),
    (2, "025_Ti2_bauen-konstruieren_Roboter.mp3"        , "RAL 1000 grünbeige"     ),
    (2, "025e_Ti2_construction_Roboter.mp3"             , "RAL 6021 blassgrün"     ),
    (3, "031_Ti3_Geschicklichkeit_Albrecht-Duerer.mp3"  , "RAL 1003 gelb"          ),
    (3, "031e_Ti3_skill_Albrecht-Duerer.mp3"            , "RAL 1001 beige"         ),
    (3, "032_Ti3_Geschicklichkeit_Lara-Croft.mp3"       , "RAL 5024 pastelblau"    ),
    (3, "032e_Ti3_skill_Lara-Croft.mp3"                 , "RAL 5019 capriblau"     ),
    (3, "033_Ti3_Geschicklichkeit_Manga.mp3"            , "RAL 3022 lachsrot"      ),
    (3, "033e_Ti3_skill_Manga.mp3"                      , "RAL 3013 tomatenrot"    ),
    (3, "034_Ti3_Geschicklichkeit_Nbg-Docke.mp3"        , "RAL 5018 türkisblau"    ),
    (3, "034e_Ti3_skill_Nbg-Docke.mp3"                  , "RAL 6034 pasteltürkis"  ),
    (3, "035_Ti3_Geschicklichkeit_Roboter.mp3"          , "RAL 1000 grünbeige"     ),
    (3, "035e_Ti3_skill_Roboter.mp3"                    , "RAL 6021 blassgrün"     ),
    (4, "041_Ti4_Beziehung_Albrecht-Duerer.mp3"         , "RAL 1003 gelb"          ),
    (4, "041e_Ti4_relationship_Albrecht-Duerer.mp3"     , "RAL 1001 beige"         ),
    (4, "042_Ti4_Beziehung_Lara-Croft.mp3"              , "RAL 5024 pastelblau"    ),
    (4, "042e_Ti4_relationship_Lara-Croft.mp3"          , "RAL 5019 capriblau"     ),
    (4, "043_Ti4_Beziehung_Manga.mp3"                   , "RAL 3022 lachsrot"      ),
    (4, "043e_Ti4_relationship_Manga.mp3"               , "RAL 3013 tomatenrot"    ),
    (4, "044_Ti4_Beziehung_Nbg-Docke.mp3"               , "RAL 5018 türkisblau"    ),
    (4, "044e_Ti4_relationship_Nbg-Docke.mp3"           , "RAL 6034 pasteltürkis"  ),
    (4, "045_Ti4_Beziehung_Roboter.mp3"                 , "RAL 1000 grünbeige"     ),
    (4, "045e_Ti4_relationship_Roboter.mp3"             , "RAL 6021 blassgrün"     ),
    (5, "051_Ti5_Begreifen_Albrecht-Duerer.mp3"         , "RAL 1003 gelb"          ),
    (5, "051e_Ti5_toknow_Albrecht-Duerer.mp3"           , "RAL 1001 beige"         ),
    (5, "052_Ti5_Begreifen_Lara-Croft.mp3"              , "RAL 5024 pastelblau"    ),
    (5, "052e_Ti5_toknow_Lara-Croft.mp3"                , "RAL 5019 capriblau"     ),
    (5, "053_Ti5_Begreifen_Manga.mp3"                   , "RAL 3022 lachsrot"      ),
    (5, "053e_Ti5_toknow_Manga.mp3"                     , "RAL 3013 tomatenrot"    ),
    (5, "054_Ti5_Begreifen_Nbg-Docke.mp3"               , "RAL 5018 türkisblau"    ),
    (5, "054e_Ti5_toknow_Nbg-Docke.mp3"                 , "RAL 6034 pasteltürkis"  ),
    (5, "055_Ti5_Begreifen_Roboter.mp3"                 , "RAL 1000 grünbeige"     ),
    (5, "055e_Ti5_toknow_Roboter.mp3"                   , "RAL 6021 blassgrün"     ),
    (6, "061_Ti6_Strategie_Albrecht-Duerer.mp3"         , "RAL 1003 gelb"          ),
    (6, "061e_Ti6_strategy_Albrecht-Duerer.mp3"         , "RAL 1001 beige"         ),
    (6, "062_Ti6_Strategie_Lara-Croft.mp3"              , "RAL 5024 pastelblau"    ),
    (6, "062e_Ti6_strategy_Lara-Croft.mp3"              , "RAL 5019 capriblau"     ),
    (6, "063_Ti6_Strategie_Manga.mp3"                   , "RAL 3022 lachsrot"      ),
    (6, "063e_Ti6_strategy_Manga.mp3"                   , "RAL 3013 tomatenrot"    ),
    (6, "064_Ti6_Strategie_Nbg-Docke.mp3"               , "RAL 5018 türkisblau"    ),
    (6, "064e_Ti6_strategy_Nbg-Docke.mp3"               , "RAL 6034 pasteltürkis"  ),
    (6, "065_Ti6_Strategie_Roboter.mp3"                 , "RAL 1000 grünbeige"     ),
    (6, "065e_Ti6_strategy_Roboter.mp3"                 , "RAL 6021 blassgrün"     ),
    (7, "071_Ti7_Technik_Albrecht-Duerer.mp3"           , "RAL 1003 gelb"          ),
    (7, "071e_Ti7_technics_Albrecht-Duerer.mp3"         , "RAL 1001 beige"         ),
    (7, "072_Ti7_Technik_Lara-Croft.mp3"                , "RAL 5024 pastelblau"    ),
    (7, "072e_Ti7_technics_Lara-Croft.mp3"              , "RAL 5019 capriblau"     ),
    (7, "073_Ti7_Technik_Manga.mp3"                     , "RAL 3022 lachsrot"      ),
    (7, "073e_Ti7_technics_Manga.mp3"                   , "RAL 3013 tomatenrot"    ),
    (7, "074_Ti7_Technik_Nbg-Docke.mp3"                 , "RAL 5018 türkisblau"    ),
    (7, "074e_Ti7_technics_Nbg-Docke.mp3"               , "RAL 6034 pasteltürkis"  ),
    (7, "075_Ti7_Technik_Roboter.mp3"                   , "RAL 1000 grünbeige"     ),
    (7, "075e_Ti7_technics_Roboter.mp3"                 , "RAL 6021 blassgrün"     ),
    (8, "081_Ti8_Wirtschaften_Albrecht-Duerer.mp3"      , "RAL 1003 gelb"          ),
    (8, "081e_Ti8_economics_Albrecht-Duerer.mp3"        , "RAL 1001 beige"         ),
    (8, "082_Ti8_Wirtschaften_Lara-Croft.mp3"           , "RAL 5024 pastelblau"    ),
    (8, "082e_Ti8_economics_Lara-Croft.mp3"             , "RAL 5019 capriblau"     ),
    (8, "083_Ti8_Wirtschaften_Manga.mp3"                , "RAL 3022 lachsrot"      ),
    (8, "083e_Ti8_economics_Manga.mp3"                  , "RAL 3013 tomatenrot"    ),
    (8, "084_Ti8_Wirtschaften_Nbg-Docke.mp3"            , "RAL 5018 türkisblau"    ),
    (8, "084e_Ti8_economics_Nbg-Docke.mp3"              , "RAL 6034 pasteltürkis"  ),
    (8, "085_Ti8_Wirtschaften_Roboter.mp3"              , "RAL 1000 grünbeige"     ),
    (8, "085e_Ti8_economics_Roboter.mp3"                , "RAL 6021 blassgrün"     )
)

DEF_PATH_MP3 = './mp3/'


def config_save_default():
    pr('Saving default config to %s' % DEF_CONFIG_FN)
    with open(DEF_CONFIG_FN, 'w') as outfile:
        yaml.dump(DEF_CONFIG, outfile, indent=4)


def config_load(fname):
    if fname is None:
        pr('No config file given. Using default')
        return DEF_CONFIG

        pr('Trying to load config file: %s' % fname)
    with open(fname, 'r') as infile:
        return yaml.load(infile)