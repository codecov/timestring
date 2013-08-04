import types
from datetime import datetime, timedelta
import time
import re
from string_to_number import string_to_number
from timestring_re import TIMESTRING_RE
import pytz


class Date:
    def __init__(self, date, offset=None, start_of_week=None, tz=None, verbose=False):
        # The original request
        self._original = date
        if tz:
            tz = pytz.timezone(str(tz))

        # Determinal starting date.
        if type(date) in (types.StringType, types.UnicodeType):
            '''
            The date is a string and needs to be converted into a <dict> for processesing
            '''
            _date = date.lower()
            res = TIMESTRING_RE.search(_date.strip())
            if res:
                date = res.groupdict()
                if verbose:
                    print "Matches:\n", ''.join(["\t%s: %s\n" % (k, v) for k, v in date.iteritems() if v])
            else:
                raise ValueError('Invlid date string >> %s' % date)

            date = dict((k, v if type(v) is str else v) for k, v in date.iteritems() if v)
            #print _date, dict(map(lambda a: (a, date.get(a)), filter(lambda a: date.get(a), date)))

        if isinstance(date, dict):
            # Initial date.
            new_date = datetime(*time.localtime()[:3])
            if tz:
                #
                # The purpose here is to adjust what day it is based on the timezeone
                #
                ts = datetime.now()
                # Daylight savings === second Sunday in March and reverts to standard time on the first Sunday in November
                # Monday is 0 and Sunday is 6.
                # 14 days - dst_start.weekday()
                dst_start = datetime(ts.year, 3, 1, 2, 0, 0) + timedelta(13 - datetime(ts.year, 3, 1).weekday())
                dst_end = datetime(ts.year, 11, 1, 2, 0, 0) + timedelta(6 - datetime(ts.year, 11, 1).weekday())

                ts = ts + tz.utcoffset(new_date, is_dst=(dst_start < ts < dst_end))
                new_date = datetime(ts.year, ts.month, ts.day)

            if date.get('unixtime'):
                new_date = datetime.fromtimestamp(int(date.get('unixtime')))

            # !number of (days|...) (ago)?
            elif date.get('num') and (date.get('delta') or date.get('delta_2')):
                if date.get('num', '').find('couple') > -1:
                    i = 2 * int(1 if date.get('ago', True) or date.get('ref') == 'last' else -1)
                else:
                    i = int(string_to_number(date.get('num', 1))) * int(1 if date.get('ago') or (date.get('ref', '') or '') == 'last' else -1)

                delta = (date.get('delta') or date.get('delta_2')).lower()
                if delta.startswith('y'):
                    try:
                        new_date = new_date.replace(year=(new_date.year - i))
                    # day is out of range for month
                    except ValueError:
                        new_date = new_date - timedelta(days=(365*i))
                elif delta.startswith('month'):
                    try:
                        new_date = new_date.replace(month=(new_date.month - i))
                    # day is out of range for month
                    except ValueError:
                        new_date = new_date - timedelta(days=(30*i))

                elif delta.startswith('q'):
                    '''
                    This section is not working...
                    Most likely need a generator that will take me to the right quater.
                    '''
                    q1, q2, q3, q4 = datetime(new_date.year, 1, 1), datetime(new_date.year, 4, 1), datetime(new_date.year, 7, 1), datetime(new_date.year, 10, 1)
                    if q1 <= new_date < q2:
                        # We are in Q1
                        if i == -1:
                            new_date = datetime(new_date.year-1, 10, 1)
                        else:
                            new_date = q2
                    elif q2 <= new_date < q3:
                        # We are in Q2
                        pass
                    elif q3 <= new_date < q4:
                        # We are in Q3
                        pass
                    else:
                        # We are in Q4
                        pass
                    new_date = new_date - timedelta(days=(91*i))

                elif delta.startswith('w'):
                    new_date = new_date - timedelta(days=(i * 7))

                else:
                    new_date = new_date - timedelta(**{('days' if delta.startswith('d') else 'hours' if delta.startswith('h') else 'minutes' if delta.startswith('m') else 'seconds'): i})

            # !dow
            if [date.get(key) for key in ('day', 'day_2', 'day_3') if date.get(key)]:
                dow = max([date.get(key) for key in ('day', 'day_2', 'day_3') if date.get(key)])
                iso = dict(monday=1, tuesday=2, wednesday=3, thursday=4, friday=5, saturday=6, sunday=7, mon=1, tue=2, tues=2, wed=3, wedn=3, thu=4, thur=4, fri=5, sat=6, sun=7).get(dow)
                if iso:
                    # determin which direction
                    if date.get('ref') not in ('this', 'next'):
                        days = iso - new_date.isoweekday() - (7 if iso >= new_date.isoweekday() else 0)
                    else:
                        days = iso - new_date.isoweekday() + (7 if iso < new_date.isoweekday() else 0)

                    new_date = new_date + timedelta(days=days)

                elif dow == 'yesterday':
                    new_date = new_date - timedelta(days=1)
                elif dow == 'tomorrow':
                    new_date = new_date + timedelta(days=1)
                elif dow == 'now':
                    new_date = datetime(*time.localtime()[:5])

            # !year
            year = [date.get(key) for key in ('year', 'year_2', 'year_3', 'year_4', 'year_5', 'year_6') if date.get(key)]
            if year:
                y = int(max(year))
                if len(str(y)) != 4:
                    y += 2000 if y <= 40 else 1900
                new_date = new_date.replace(year=y)

            # !month
            month = [date.get(key) for key in ('month', 'month_1', 'month_2', 'month_3', 'month_4') if date.get(key)]
            if month:
                new_date = new_date.replace(day=1)
                new_date = new_date.replace(month=int(max(month)) if re.match('^\d+$', max(month)) else dict(january=1, february=2, march=3, april=4, june=6, july=7, august=8, september=9, october=10, november=11, december=12, jan=1, feb=2, mar=3, apr=4, may=5, jun=6, jul=7, aug=8, sep=9, sept=9, oct=10, nov=11, dec=12).get(max(month),  new_date.month))

            # !day
            day = [date.get(key) for key in ('date', 'date_2', 'date_3') if date.get(key)]
            if day:
                new_date = new_date.replace(day=int(max(day)))

            # !daytime
            if date.get('daytime'):
                if date['daytime'].find('this time') >= 1:
                    new_date = new_date.replace(hour=datetime(*time.localtime()[:5]).hour,
                                                minute=datetime(*time.localtime()[:5]).minute)
                else:
                    new_date = new_date.replace(hour=dict(morning=9, noon=12, afternoon=15, evening=18, night=21, nighttime=21, midnight=24).get(date.get('daytime'), 12))
                # No offset because the hour was set.
                offset = False

            # !hour
            hour = [date.get(key) for key in ('hour', 'hour_2', 'hour_3') if date.get(key)]
            if hour:
                new_date = new_date.replace(hour=int(max(hour)))
                am = [date.get(key) for key in ('am', 'am_1') if date.get(key)]
                if am and max(am) in ('p', 'pm'):
                    new_date = new_date.replace(hour=int(max(hour))+12)
                # No offset because the hour was set.
                offset = False

                #minute
                minute = [date.get(key) for key in ('minute', 'minute_2') if date.get(key)]
                if minute:
                    new_date = new_date.replace(minute=int(max(minute)))

                #second
                seconds = date.get('seconds', 0)
                if seconds:
                    new_date = new_date.replace(second=int(seconds))

            self.date = new_date

        elif type(date) in (types.IntType, types.LongType, types.FloatType) and re.match('^\d{10}$', str(date)):
            self.date = datetime.fromtimestamp(int(date))

        elif isinstance(date, datetime):
            self.date = date

        elif date is None:
            self.date = datetime.now()

        else:
            # Set to the current date Y, M, D, H0, M0, S0
            self.date = datetime(*time.localtime()[:3])

        if tz:
            self.date = self.date.replace(tzinfo=tz)

        # end if type(date) is types.DictType: and self.date.hour == 0:
        if offset and isinstance(offset, dict):
            self.date = self.date.replace(**offset)

    @property
    def year(self):
        return self.date.year

    @property
    def month(self):
        return self.date.month

    @property
    def day(self):
        return self.date.day

    @property
    def hour(self):
        return self.date.hour

    @property
    def minute(self):
        return self.date.minute

    @property
    def second(self):
        return self.date.second

    @property
    def weekday(self):
        return self.date.isoweekday()

    @property
    def tz(self):
        return self.date.tzinfo

    def replace(self, **k):
        """Note returns a new Date obj"""
        return Date(self.date.replace(**k))

    def adjust(self, to):
        '''
        Adjusts the time from kwargs to timedelta
        **Will change this object**

        return new copy of self
        '''
        new = self.__new__()
        if type(to) in (types.StringType, types.UnicodeType):
            to = to.lower()
            res = TIMESTRING_RE.search(to)
            if res:
                rgroup = res.groupdict()
                if (rgroup.get('delta') or rgroup.get('delta_2')):
                    i = int(string_to_number(rgroup.get('num', 1))) * (-1 if to.startswith('-') else 1)
                    delta = (rgroup.get('delta') or rgroup.get('delta_2')).lower()
                    if delta.startswith('y'):
                        try:
                            new.date = new.date.replace(year=(new.date.year + i))
                        except ValueError:
                            # day is out of range for month
                            new.date = new.date + timedelta(days=(365 * i))
                    elif delta.startswith('month'):
                        try:
                            new.date = new.date.replace(month=(new.date.month + i))
                        except ValueError:
                            #day is out of range for month
                            new.date = new.date + timedelta(days=(30 * i))
                    elif delta.startswith('q'):
                        # NP
                        pass
                    elif delta.startswith('w'):
                        new.date = new.date + timedelta(days=(7 * i))
                    else:
                        new.date = new.date + timedelta(**{('days' if delta.startswith('d') else 'hours' if delta.startswith('h') else 'minutes' if delta.startswith('m') else 'seconds'): i})
                    return new
        else:
            new.date = new.date + timedelta(seconds=int(to))
            return new

        raise ValueError('Invalid addition request')

    def __nonzero__(self):
        return True

    def __new__(self):
        return Date(datetime(self.date.year,
                             self.date.month,
                             self.date.day,
                             self.date.hour,
                             self.date.minute,
                             self.date.second), tz=self.tz)

    def __add__(self, to):
        return self.__new__().adjust(to)

    def __sub__(self, to):
        if type(to) in (types.StringType, types.UnicodeType):
            to = to[1:] if to.startswith('-') else ('-'+to)
        elif type(to) in (types.IntType, types.FloatType, types.LongType):
            to = to * -1
        return self.__new__().adjust(to)

    def __format__(self, _):
        return self.date.strftime('%x %X')

    def __str__(self):
        """Returns date in representation of `%x %X` ie `2013-02-17 00:00:00`"""
        return str(self.date)

    def __cmp__(self, to):
        if isinstance(to, Date):
            return 1 if self.date > to.date else 0 if self.date == to.date else -1
        else:
            return self.__cmp__(Date(to))

    def format(self, format_string='%x %X'):
        return self.date.strftime(format_string)

    def to_unixtime(self):
        return time.mktime(self.date.timetuple())

    def to_mysql(self):
        return "date '%s'" % str(self.format("%Y-%m-%d %H:%M:%S"))

    def to_postgresql(self):
        return "'%s'::date" % str(self.date)
