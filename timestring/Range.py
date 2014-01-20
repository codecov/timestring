from datetime import datetime
import re
import pytz
from copy import copy

from .timestring_re import TIMESTRING_RE
from .Date import Date

try:
    unicode
except NameError:
    unicode = str
    long = int

class Range(object):
    def __init__(self, start, end=None, offset=None, start_of_week=0, tz=None, verbose=False):
        """
        `start` can be type <class timestring.Date> or <type str> or <type None>
        """
        self._original = start
        self._dates = []
        pgoffset = None

        if type(start) in (str, unicode):
            if start == 'infinity':
                self._dates = [Date('infinity'),
                               Date('infinity') if end is None or end == 'infinity' else Date(end, offset=offset, tz=tz)]
                return
            
            # Remove prefix
            start = re.sub('^(between|from)\s', '', start.lower())
            now = datetime.now()

            # postgresql tsrange and tstzranges support
            if re.match(r"(\[|\()((\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+(\+|\-)\d{2}\")|infinity),((\"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+(\+|\-)\d{2}\")|infinity)(\]|\))", start):
                start = re.sub('[^\w\s\-\:\.\+\,]', '', start).replace(',', ' to ')

            # no tz info but offset provided, we are UTC so convert
            if re.search(r"(\+|\-)\d{2}$", start):
                # postgresql tsrange and tstzranges
                pgoffset = re.search(r"(\+|\-)\d{2}$", start).group() + " hours"

            # tz info provided
            if tz:
                now = now.replace(tzinfo=pytz.timezone(str(tz)))

            # Split the two requests
            if re.search(r'(\s(and|to)\s)', start):
                # Both arguments found in start variable
                r = tuple(re.split(r'(\s(and|to)\s)', start.strip()))
                start, end = r[0], r[-1]

            # Parse
            res = TIMESTRING_RE.search(start)
            if res:
                group = res.groupdict()
                if verbose:
                    print(dict(map(lambda a: (a, group.get(a)), filter(lambda a: group.get(a), group))))
                if (group.get('delta') or group.get('delta_2')) is not None:
                    delta = (group.get('delta') or group.get('delta_2')).lower()
                    if delta.startswith('y'):
                        start = Date(datetime(now.year, 1, 1), offset=offset, tz=tz)
                    # month
                    elif delta.startswith('month'):
                        start = Date(datetime(now.year, now.month, 1), offset=offset, tz=tz)
                    # week
                    elif delta.startswith('w'):
                        start = Date("today", offset=offset, tz=tz) - (str(Date("today", tz=tz).date.weekday())+' days')
                    # day
                    elif delta.startswith('d'):
                        start = Date("today", offset=offset, tz=tz)
                    # hour
                    elif delta.startswith('h'):
                        start = Date("today", offset=dict(hour=now.hour+1), tz=tz)
                    # minute, second
                    elif delta.startswith('m') or delta.startswith('s'):
                        start = Date("now", tz=tz)
                    else:
                        raise ValueError("Not a valid time range.")

                    # make delta
                    di = "%s %s" % (str(int(group['num'] or 1)), delta)

                    # this           [   x  ]
                    if group['ref'] == 'this':
                        end = start + di

                    #next          x [      ]
                    elif group['ref'] == 'next':
                        start = start + ('1 ' + delta)
                        if int(group['num'] or 1) > 1:
                            di = "%s %s" % (str(int(group['num'] or 1) - 1), delta)
                        end = start + di

                    # ago             [     ] x
                    elif group.get('ago') or group['ref'] == 'last' and int(group['num'] or 1) == 1:
                        #if group['ref'] == 'last' and int(group['num'] or 1) == 1:
                        #    start = start - ('1 ' + delta)
                        end = start - di

                    # last & no ref   [    x]
                    else:
                        # need to include today with this reference
                        if not (delta.startswith('h') or delta.startswith('m') or delta.startswith('s')):
                            start = Range('today', offset=offset, tz=tz).end
                        end = start - di

                elif group.get('month_1'):
                    # a single month of this yeear
                    start = Date(start, offset=offset, tz=tz)
                    start = start.replace(day=1)
                    end = start + '1 month'

                elif group.get('year_5'):
                    # a whole year
                    start = Date(start, offset=offset, tz=tz)
                    start = start.replace(day=1, month=1)
                    end = start + '1 year'

                else:
                    # Pass off to Date to figure out.
                    start = Date(start, offset=offset, tz=tz)
                    # if end and :
                    #     print('---- here', start, end)
                    #     end = Date(end, offset=offset, tz=tz)

            else:
                raise ValueError("Invalid timestring request")

        elif type(start) in (int, long, float) and re.match('^\d{10}$', str(start)):
            start = Date(start)
            if type(end) in (int, long, float) and re.match('^\d{10}$', str(end)):
                end = Date(end)

        if end is None:
            # no end provided, so assume 24 hours
            end = start + '24 hours'

        if not isinstance(start, Date):
            start = Date(start, offset=offset, start_of_week=start_of_week, tz=tz)
        if not isinstance(end, Date):
            end = Date(end, offset=offset, start_of_week=start_of_week, tz=tz)

        if start > end:
            start, end = copy(end), copy(start)

        if pgoffset:
            start = start - pgoffset
            end = end - pgoffset

        self._dates = (start, end)

    def __repr__(self):
        return "<timestring.Range %s %s>" % (str(self), id(self))

    def __getitem__(self, index):
        return self._dates[index]

    def __str__(self):
        return self.format()

    def __nonzero__(self):
        # Ranges are natuarally always true in statments link: if Range
        return True

    def format(self, format_string='%x %X'):
        return "From %s to %s" % (self[0].format(format_string) if isinstance(self[0], Date) else str(self[0]),
                                  self[1].format(format_string) if isinstance(self[1], Date) else str(self[1]))

    @property
    def start(self):
        return self[0]

    @property
    def end(self):
        return self[1]

    @property
    def elapse(self, short=False, format=True, min=None, round=None):
        if self.start == 'infinity' or self.end == 'infinity':
            return "infinity"
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

    def __lt__(self, other):
        return self.cmp(other) == -1

    def __gt__(self, other):
        return self.cmp(other) == 1

    def __eq__(self, other):
        return self.cmp(other) == 0

    def cmp(self, other):
        """*Note: checks Range.start() only*
        Key: self = [], other = {}
            * [   {----]----} => -1
            * {---[---}  ] => 1
            * [---]  {---} => -1
            * [---] same as {---} => 0
            * [--{-}--] => -1
        """
        if isinstance(other, Range):
            if other.start.tz and self.start.tz is None:
                return 0 if (self.start.replace(tzinfo=other.start.tz) == other.start and self.end.replace(tzinfo=other.start.tz) == other.end) else -1 if other.start > self.start.replace(tzinfo=other.start.tz) else 1
            return 0 if (self.start == other.start and self.end == other.end) else -1 if other.start > self.start else 1
        elif isinstance(other, Date):
            if other.tz and self.start.tz is None:
                return 0 if other == self.start.replace(tzinfo=other.tz) else -1 if other > self.start.replace(tzinfo=other.start.tz) else 1
            return 0 if other == self.start else -1 if other > self.start else 1
        else:
            return self.cmp(Range(other, tz=self.start.tz))

    def __contains__(self, other):
        """*Note: checks Range.start() only*
        Key: self = [], other = {}
            * [---{-}---] => True else False
        """
        if isinstance(other, Date):
            if self.start == 'infinity':
                return True
            elif self.end == 'infinity' and self.start < other:
                return True
            elif other.date == 'infinity':
                return True
            elif other.tz and self.start.tz is None:
                # we can safely update tzinfo
                return self.start.replace(tzinfo=other.tz).to_unixtime() <= other.to_unixtime() <= self.end.replace(tzinfo=other.tz).to_unixtime()
            return self.start <= other <= self.end
        elif isinstance(other, Range):
            if self.start == 'infinity':
                return self.end >= other.end
            elif self.end == 'infinity':
                return self.start <= other.start
            elif other.start.tz and self.start.tz is None:
                return self.start.replace(tzinfo=other.start.tz).to_unixtime() <= other.start.to_unixtime() <= self.end.replace(tzinfo=other.start.tz).to_unixtime() \
                       and self.start.replace(tzinfo=other.start.tz).to_unixtime() <= other.end.to_unixtime() <= self.end.replace(tzinfo=other.start.tz).to_unixtime()
            return self.start <= other.start <= self.end and self.start <= other.end <= self.end
        else:
            return self.__contains__(Range(other, tz=self.start.tz))

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
        returns new instance
        """
        s, e = copy(self.start), copy(self.end)
        if from_start:
           e = s + by
        else:
            s = e - by
        return Range(s, e, tz=self.start.tz)

    def adjust(self, to):
        # return a new instane, like datetime does
        return Range(self.start.adjust(to),
                     self.end.adjust(to), tz=self.start.tz)

    def next(self, times=1):
        """Returns a new instance of self
        times is not supported yet.
        """
        return Range(copy(self.end),
                     self.end + self.elapse, tz=self.start.tz)

    def prev(self, times=1):
        """Returns a new instance of self
        times is not supported yet.
        """
        return Range(self.start - self.elapse,
                     copy(self.start), tz=self.start.tz)

    def __add__(self, to):
        return self.adjust(to)

    def __sub__(self, to):
        if type(to) in (str, unicode):
            to = to[1:] if to.startswith('-') else ('-'+to)
        elif type(to) in (int, long, float):
            to = to * -1
        return self.adjust(to)
