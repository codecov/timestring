import re
import sys
import argparse
from datetime import datetime

__version__ = VERSION = version = '1.6.2'


class TimestringInvalid(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return self.reason


from .Date import Date
from .Range import Range
from .timestring_re import TIMESTRING_RE


try:
    """Register psycopg2 Adapters

    if psycopg2 is installed then automatically register
    the adapters for Date and Range.

    >>> db.mogrify("insert into my_table (range) values (%s);", 
                   timestring.Range("next week"))
    "insert into my_table (range) values (tstzrange('2014-03-03 00:00:00'::timestamptz, '2014-03-10 00:00:00'::timestamptz));"
    """ 
    from psycopg2.extensions import register_adapter
    from psycopg2.extensions import AsIs

    def adapt_date(date):
        if date.tz:
            return AsIs("'%s'::timestamptz" % str(date.date))
        else:
            return AsIs("'%s'::timestamp" % str(date.date))

    def adapt_range(_range):
        if _range.start.tz:
            return AsIs("tstzrange('%s', '%s')" % (str(_range.start.date), str(_range.end.date)))
        else:
            return AsIs("tsrange('%s', '%s')" % (str(_range.start.date), str(_range.end.date)))

    register_adapter(Date, adapt_date)
    register_adapter(Range, adapt_range)

except ImportError:
    pass


def findall(text):
    """Find all the timestrings within a block of text.

    >>> timestring.findall("once upon a time, about 3 weeks ago, there was a boy whom was born on august 15th at 7:20 am. epic.")
    [
     ('3 weeks ago,', <timestring.Date 2014-02-09 00:00:00 4483019280>),
     ('august 15th at 7:20 am', <timestring.Date 2014-08-15 07:20:00 4483019344>)
    ]
    """
    results = TIMESTRING_RE.findall(text)
    dates = []
    for date in results:
        if re.compile('((next|last)\s(\d+|couple(\sof))\s(weeks|months|quarters|years))|(between|from)', re.I).match(date[0]):
            dates.append((date[0].strip(), Range(date[0])))
        else:
            dates.append((date[0].strip(), Date(date[0])))
    return dates


def parse(string):
    try:
        matches = TIMESTRING_RE.search(string).groupdict()
        date = Date(string)
        result = {}
        for k,v in matches.items():
            if v:
                arg = k.split('_', 1)[0]
                if arg in ('year', 'month', 'day', 'hour', 'minute', 'second'):
                    result.setdefault(arg, getattr(date, arg))

        if result.get('day'):
            result['weekday'] = date.weekday

        return result
    except:
        return None



def now():
    return Date(datetime.now())


def main():
    parser = argparse.ArgumentParser(prog='timestring',
                                     add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=""" """)
    parser.add_argument('--version', action='version', version="timestring v%s - http://github.com/stevepeak/timestring" % version)
    parser.add_argument('-d', '--date', action='store_true')
    parser.add_argument('--verbose', '-v', action="store_true", help="Verbose mode")
    parser.add_argument('args', nargs="+", help="Time input")

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        args = parser.parse_args()
        if args.date:
            print(Date(" ".join(args.args), verbose=args.verbose))
        else:
            print(Range(" ".join(args.args), verbose=args.verbose))

if __name__ == '__main__':
    main()
