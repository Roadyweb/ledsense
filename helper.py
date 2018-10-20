
import numpy
import logging


class draw_diagram(object):
    def __init__(self, width, bin=0.01):
        """ width: set the width of the string that is returned as result
            bin: bin size precent, All values that fall in the range
                 0% to bin   <==> 100% - bin to 100%
                 e.g. for bin = 0.01 = 1%
                 0% to 1%    <==>  99% to 100% (is evaluated as good)
                       1%    to    99%         (is evaluated as bad)
        """
        self.width = width
        self.bin = bin
        self.max = 1
        self.max_updated = False
        self.last_value = 0
        self.stat_reset()
        self.stat_cnt = 0
        self.stat_good = 0
        self.stat_bad_dev = []

    def stat_reset(self):
        self.stat_cnt = 0
        self.stat_good = 0
        self.stat_bad_dev = []

    def add(self, value, expected=None):
        """

        :param value:    current value to be added
        :param expected: None = no expection for value
                         0 = expected in the lower bin
                         1 = expected in the upper bin
        :return:
        """
        self.last_value = value
        self.stat_cnt += 1
        lower_limit = self.max * self.bin
        upper_limit = self.max * (1.0 - self.bin)
        if value < lower_limit or value > upper_limit:
            self.stat_good += 1
        else:
            if expected is not None and expected == 0:
                self.stat_bad_dev.append(value - (self.bin * self.max))
            if expected is not None and expected == 1:
                inter = self.max - value
                self.stat_bad_dev.append(inter - (self.bin * self.max))

        if value > self.max:
            self.max = value
            self.max_updated = True
            self.stat_reset()

    def getstr(self):
        pos_raw = 1.0 * self.last_value / self.max
        pos = round(1.0 * pos_raw * self.width)
        # print('%5f %5f %f' % (pos_raw, pos, self.max))
        str = '%s%s' % (pos * ' ', 'O')
        if self.max_updated:
            str += (self.width - 2 - pos) * ' ' + ' !!! Max Updated !!!'
            self.max_updated = False
        return str

    def get_stat_good_percent(self):
        return 100.0 * self.stat_good / self.stat_cnt

    def get_stat_cnt(self):
        return self.stat_cnt

    def get_stat_bad_dev(self):
        if len(self.stat_bad_dev) == 0:
            return 0
        return numpy.mean(self.stat_bad_dev)


def get_rgb_distance(rgb1, rgb2):
    """ This function expects two tuples with RGB values and calculates the distance between both
        vectors.
    """
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)
    return numpy.linalg.norm(rgb1 - rgb2)


def get_rgb_length(rgb):
    """ This function expects one tuples with RGB values and calculates the length of the vector.
    """
    return numpy.linalg.norm(rgb)


def pr(str2log):
    logging.info(str2log)


def prdbg(str2log):
    logging.debug(str2log)


def prwarn(str2log):
    logging.warn(str2log)

def prerr(str2log):
    logging.error(str2log)
