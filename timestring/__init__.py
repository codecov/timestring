import re

__version__ = VERSION = version = '1.4.4'

from Date import Date
from Range import Range
from timestring_re import TIMESTRING_RE


def findall(text):
    results = TIMESTRING_RE.findall(text)
    dates = []
    for date in results:
        if re.compile('((next|last)\s(\d+|couple(\sof))\s(weeks|months|quarters|years))|(between|from)', re.I).match(date[0]):
            dates.append((date[0], Range(date[0])))
        else:
            dates.append((date[0], Date(date[0])))
    return dates
