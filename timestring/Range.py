import types
import datetime
import re
from timestring_re import TIMESTRING_RE
from Date import Date


class Range:
    def __init__(self, start, offset=None, start_of_week=0):
        """
        `start` can be type <class timestring.Date> or <type str> or <type None>
        """
        self._original = start
        self._dates = []
        end = None

        if type(start) in (types.StringType, types.UnicodeType):
            # Remove prefix
            start = re.sub('^(between|from)\s', '', start.lower())
            end = None
            now = datetime.datetime.now()

            # Split the two requests
            if re.search(r'(\s(and|to)\s)', start):
                # Both arguments found in start variable
                r = tuple(re.split(r'(\s(and|to)\s)', start.strip()))
                start, end = r[0], r[-1]

            # Parse
            res = TIMESTRING_RE.search(start)
            if res:
                group = res.groupdict()
                #print dict(map(lambda a: (a, group.get(a)), filter(lambda a: group.get(a), group))), start, end
                if group.get('ref') is None:
                    group['ref'] = 'last'

                if group['ref'] in ('next', 'last', 'this') and group.get('delta'):
                    if group.get('delta').startswith('week'):
                        if group['ref'] == 'this':
                            # go to start of week and add 7 days
                            start = Date("today", offset=offset) - (str(Date("today").date.weekday())+' days')
                            end = start + '7 days'
                        elif group['ref'] == 'next':
                            start = Date("now")
                            end = start.replace(hour=0, minute=0) + (str(int(group.get('num', 1)))+' weeks')
                        else:
                            end = Date("now")
                            start = end.replace(hour=0, minute=0) - (str(int(group.get('num', 1)))+' weeks')

                    elif group.get('delta').startswith('month'):
                        if group['ref'] == 'this':
                            # go to start of week and add 7 days
                            start = datetime.datetime(now.year, now.month, 1)
                            if offset:
                                start.replace(**offset)
                            start = Date(start)
                            end = start + '1 month'
                        elif group['ref'] == 'next':
                            start, end = (Date("today") + (str(int(group.get('num', 1)))+' month')), (Date("today") + (str(int(group.get('num', 1))+1)+' months'))
                            if offset:
                                start.replace(**offset)
                                end.replace(**offset)
                        else:
                            end, start = (Date("today") - (str(int(group.get('num', 1)))+' month')), (Date("today") - (str(int(group.get('num', 1))+1)+' months'))
                            if offset:
                                start.replace(**offset)
                                end.replace(**offset)

                    elif group.get('delta').startswith('quarter'):
                        pass

                    elif group.get('delta').startswith('day'):
                        if group['ref'] == 'this':
                            start = Date("today", offset=offset)
                            end = start + '1 day'
                        elif group['ref'] == 'next':
                            start = Date("now")
                            end = start.replace(hour=0, minute=0) + (str(int(group.get('num', 1)))+' days')
                        else:
                            end = Date("now")
                            start = end.replace(hour=0, minute=0) - (str(int(group.get('num', 1)))+' days')

                    elif group.get('delta').startswith('year'):
                        if group['ref'] == 'this':
                            start = Date(datetime.datetime(now.year, 1, 1), offset=offset)
                            end = start + '1 year'
                        elif group['ref'] == 'next':
                            start = Date("today", offset=offset)
                            end = Date(datetime.datetime(now.year+1, 1, 1), offset=offset) + (str(int(group.get('num', 1)))+' years')
                        else:
                            end = Date('today', offset=offset)
                            start = Date(datetime.datetime(now.year, 1, 1), offset=offset) - (str(int(group.get('num', 1)))+' years')

                    elif group.get('delta').startswith('hour'):
                        if group['ref'] == 'this':
                            start = Date("today", offset=dict(hour=now.hour))
                            end = start + '1 hour'
                        elif group['ref'] == 'next':
                            start = Date("today", offset=dict(hour=now.hour))
                            end = start + (str(int(group.get('num', 1)))+' hours')
                        else:
                            end = Date("today", offset=dict(hour=now.hour))
                            start = end - (str(int(group.get('num', 1)))+' hours')

                    elif group.get('delta').startswith('minute'):
                        if group['ref'] == 'this':
                            start = Date("now")
                            end = start + '1 minute'
                        elif group['ref'] == 'next':
                            start = Date("now")
                            end = start + (str(int(group.get('num', 1)))+' minute')
                        else:
                            end = Date("now")
                            start = end - (str(int(group.get('num', 1)))+' minute')

                    else:
                        raise ValueError("Invalid timestring request")

                else:
                    start = Date(group, offset=offset)

            else:
                raise ValueError("Invalid timestring request")

        if end is None:
            end = start + '24 hours'

        self._dates = [start if isinstance(start, Date) else Date(start, offset=offset, start_of_week=start_of_week),
                       end if isinstance(end, Date) else Date(end, offset=offset, start_of_week=start_of_week)]

    def __getitem__(self, index):
        return self._dates[index]

    def __iter__(self):
        self.ii = -1
        return self

    def next(self):
        self.ii += 1
        if self.ii > 1:
            raise StopIteration
        return self[self.ii]

    def __str__(self):
        return self.format()

    def __nonzero__(self):
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

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end

    def __lt__(self, other):
        # checks start only
        return self.start < other.start

    def __gt(self, other):
        # checks start only
        return self.start > self.start

    def __contains__(self, other):
        if isinstance(other, Date):
            return self.start.to_unixtime() <= other.to_unixtime() <= self.end.to_unixtime()
        elif isinstance(other, Range):
            return self.start.to_unixtime() <= other.start.to_unixtime() <= self.end.to_unixtime() and self.start.to_unixtime() <= other.end.to_unixtime() <= self.end.to_unixtime()

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
        self[0].adjust(to)
        self[1].adjust(to)
        return self

    def __new__(self):
        return Range(self.start.__new__(), self.end.__new__())

    def __iadd__(self, to):
        return self.adjust(to)

    def __isub__(self, to):
        if type(to) in (types.StringType, types.UnicodeType):
            to = to[1:] if to.startswith('-') else ('-'+to)
        elif type(to) in (types.IntType, types.FloatType, types.LongType):
            to = to * -1
        return self.adjust(to)

    def __add__(self, to):
        """Increases this
        #### Accepts
        1. another `Range` object
        2. `string` then converted into a `Range`
        3. `numbers` converted into `seconds`
        The added `Range` will be counted via `len()` then added.
        """
        return self.__new__().adjust(to)

    def __sub__(self, to):
        """Reduces the range
        #### Accepts
        1. another `Range` object
        2. `string` then converted into a `Range`
        3. `numbers` converted into `seconds`
        The added `Range` will be counted via `len()` then reduced.
        """
        if type(to) in (types.StringType, types.UnicodeType):
            to = to[1:] if to.startswith('-') else ('-'+to)
        elif type(to) in (types.IntType, types.FloatType, types.LongType):
            to = to * -1
        return self.__new__().adjust(to)
