import re
import argparse
import sys

__version__ = VERSION = version = '1.6.1'

from .Date import Date
from .Range import Range
from .timestring_re import TIMESTRING_RE


def findall(text):
    results = TIMESTRING_RE.findall(text)
    dates = []
    for date in results:
        if re.compile('((next|last)\s(\d+|couple(\sof))\s(weeks|months|quarters|years))|(between|from)', re.I).match(date[0]):
            dates.append((date[0], Range(date[0])))
        else:
            dates.append((date[0], Date(date[0])))
    return dates


def main():
    parser = argparse.ArgumentParser(prog='timestring',
                                     add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=" ")
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('--verbose', '-v', action="store_true", help="Verbose mode")
    parser.add_argument('--range', '-r', action="store_true", help="As range mode")
    parser.add_argument('args', nargs="+", help="Time input")

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args.range:
            print(Range(" ".join(args.args), verbose=args.verbose))
        else:
            print(Date(" ".join(args.args), verbose=args.verbose))


if __name__ == '__main__':
    main()
