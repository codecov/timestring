import types
from datetime import datetime
import re
from timestring_re import TIMESTRING_RE
from Date import Date
import pytz


class Range:
    def __init__(self, start, end=None, offset=None, start_of_week=0, tz=None):
        """
        `start` can be type <class timestring.Date> or <type str> or <type None>
        """
        self._original = start
        self._dates = []
        end = end
        if tz:
            tz = pytz.timezone(tz)

        if type(start) in (types.StringType, types.UnicodeType):
            # Remove prefix
            start = re.sub('^(between|from)\s', '', start.lower())
            end = None
            now = datetime.now(tz)

            # Split the two requests
            if re.search(r'(\s(and|to)\s)', start):
                # Both arguments found in start variable
                r = tuple(re.split(r'(\s(and|to)\s)', start.strip()))
                start, end = r[0], r[-1]

            # Parse
            res = TIMESTRING_RE.search(start)
            if res:
                group = res.groupdict()
                #print dict(map(lambda a: (a, group.get(a)), filter(lambda a: group.get(a), group)))

                if group.get('ref') or group.get('ago') or group.get('delta'):
                    if group.get('delta').startswith('year'):
                        start = Date(datetime(now.year, 1, 1).replace(tzinfo=tz), offset=offset)
                    # month
                    elif group.get('delta').startswith('month'):
                        start = Date(datetime(now.year, now.month, 1).replace(tzinfo=tz), offset=offset)
                    # week
                    elif group.get('delta').startswith('week'):
                        start = Date("today", offset=offset) - (str(Date("today").date.weekday())+' days')
                    # day
                    elif group.get('delta').startswith('day'):
                        start = Date("today", offset=offset, tz=tz)
                    # hour
                    elif group.get('delta').startswith('hour'):
                        start = Date("today", offset=dict(hour=now.hour+1), tz=tz)
                    # minute
                    elif group.get('delta').startswith('hour'):
                        start = Date("now", tz=tz)
                    else:
                        raise ValueError("Not a valid time range.")

                    # make delta
                    delta = str(int(group['num'] or 1)) + ' ' + group['delta']

                    # this           [   x  ]
                    if group['ref'] == 'this':
                        end = start + delta

                    #next          x [      ]
                    elif group['ref'] == 'next':
                        start = start + ('1 ' + group['delta'])
                        if int(group['num'] or 1) > 1:
                            delta = str(int(group['num'] or 1) - 1) + ' ' + group['delta']
                        end = start + delta

                    # ago             [     ] x
                    elif group.get('ago') or group['ref'] == 'last' and int(group['num'] or 1) == 1:
                        #if group['ref'] == 'last' and int(group['num'] or 1) == 1:
                        #    start = start - ('1 ' + group['delta'])
                        end = start - delta

                    # last & no ref   [    x]
                    else:
                        # need to include today with this reference
                        if not (group.get('delta').startswith('hour') or group.get('delta').startswith('minute')):
                            start = Range('today').end
                        end = start - delta

                else:
                    start = Date(group, offset=offset)

            else:
                raise ValueError("Invalid timestring request")

        if end is None:
            end = start + '24 hours'

        # Flip if (move me to bottom)
        if start > end:
            start, end = end.__new__(), start.__new__()

        self._dates = [start if isinstance(start, Date) else Date(start, offset=offset, start_of_week=start_of_week),
                       end if isinstance(end, Date) else Date(end, offset=offset, start_of_week=start_of_week)]

    def __new__(self):
        return Range(self.start.__new__(), self.end.__new__())

    def __getitem__(self, index):
        return self._dates[index]

    def __str__(self):
        return self.format()

    def __nonzero__(self):
        # Ranges are natuarally always true in statments link: if Range
        return True

    def format(self, format_string='%x %X'):
        return "From %s to %s" % (self[0].format(format_string), self[1].format(format_string))

    @property
    def start(self):
        return self[0]

    @property
    def end(self):
        return self[1]

    @property
    def elapse(self, short=False, format=True, min=None, round=None):
        # years, months, days, hours, minutes, seconds
        full = [0, 0, 0, 0, 0, 0]
        elapse = self[1].date - self[0].date
        days = elapse.days
        if days > 365:
            years = days / 365
            full[0] = years
            days = elapse.days - (years*365)
        if days > 30:
            months = days / 30
            full[1] = months
            days = days - (days / 30)

        full[2] = days

        full[3], full[4], full[5] = tuple(map(int, map(float, str(elapse).split(', ')[-1].split(':'))))

        if round:
            r = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
            assert round in r[:-1], "round value is not allowed. Must be in "+",".join(r)
            if full[r.index(round)+1] > dict(months=6, days=15, hours=12, minutes=30, seconds=30).get(r[r.index(round)+1]):
                full[r.index(round)] += 1

            min = r[r.index(round)+1]

        if min:
            m = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
            assert min in m, "min value is not allowed. Must be in "+",".join(m)
            for x in range(6-m.index(min)):
                full[5-x] = 0

        if format:
            if short:
                return re.sub('((?<!\d)0\w\s?)', '', "%dy %dm %dd %dh %dm %ss" % tuple(full))
            else:
                return re.sub('((?<!\d)0\s\w+\s?)', '', "%d years %d months %d days %d hours %d minutes %d seconds" % tuple(full))
        return full

    def __len__(self):
        """Returns how many `seconds` the `Range` lasts.
        """
        return abs(int(self[1].to_unixtime() - self[0].to_unixtime()))

    def __cmp__(self, other):
        """*Note: checks Range.start() only*
        Key: self = [], other = {}
            * [   {----]----} => -1
            * {---[---}  ] => 1
            * [---]  {---} => -1
            * [---] same as {---} => 0
            * [--{-}--] => -1
        """
        if isinstance(other, Range):
            return 0 if (self.start == other.start and self.end == other.end) else -1 if other.start > self.start else 1
        elif isinstance(other, Date):
            return 0 if other == self.start else -1 if other > self.start else 1
        else:
            return self.__cmp__(Range(other))

    def __contains__(self, other):
        """*Note: checks Range.start() only*
        Key: self = [], other = {}
            * [---{-}---] => True else False
        """
        if isinstance(other, Date):
            return self.start.to_unixtime() <= other.to_unixtime() <= self.end.to_unixtime()
        elif isinstance(other, Range):
            return self.start.to_unixtime() <= other.start.to_unixtime() <= self.end.to_unixtime() and self.start.to_unixtime() <= other.end.to_unixtime() <= self.end.to_unixtime()
        else:
            return self.__contains__(Range(other))

    def to_mysql(self):
        '''
        Returns a well formatted string for postgresql to process.
        ex.
            between x and y
            > x
            >= x
            < y
        '''
        if self[0] is None:
            return '< %s' % self[1].to_mysql()
        else:
            return 'between %s and %s' % (self[0].to_mysql(), self[1].to_mysql())

    def to_postgresql(self):
        '''
        Returns a well formatted string for postgresql to process.
        '''
        if self[0] is None:
            return '< %s' % self[1].to_postgresql()
        else:
            return 'between %s and %s' % (self[0].to_postgresql(), self[1].to_postgresql())

    def cut(self, by, from_start=True):
        """ Cuts this object from_start to the number requestd
        """
        if from_start:
            self._dates[1] = self[0] + by
        else:
            self._dates[0] = self[1] - by
        return self

    def adjust(self, to):
        # return a new instane, like datetime does
        return Range(self.start.adjust(to),
                     self.end.adjust(to))

    def next(self, times=1):
        """Returns a new instance of self
        times is not supported yet.
        """
        return Range(self.end.__new__(),
                     self.end + self.elapse)

    def prev(self, times=1):
        """Returns a new instance of self
        times is not supported yet.
        """
        return Range(self.start - self.elapse,
                     self.start.__new__())

    def __add__(self, to):
        print '>>> Range.add', to
        return self.adjust(to)

    def __sub__(self, to):
        print '>>> Range.sub', to
        if type(to) in (types.StringType, types.UnicodeType):
            to = to[1:] if to.startswith('-') else ('-'+to)
        elif type(to) in (types.IntType, types.FloatType, types.LongType):
            to = to * -1
        return self.adjust(to)
