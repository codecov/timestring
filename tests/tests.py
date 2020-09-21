import os
import time
import unittest
from ddt import ddt, data
from six import u
from datetime import datetime, timedelta

from timestring import Date
from timestring import Range
from timestring import parse
from timestring.text2num import text2num


@ddt
class timestringTests(unittest.TestCase):
    def test_fullstring(self):
        now = datetime.now()

        #
        # DATE
        #
        date = Date("01/10/2015 at 7:30pm")
        self.assertEqual(date.year, 2015)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 10)
        self.assertEqual(date.hour, 19)
        self.assertEqual(date.minute, 30)

        date = Date("may 23rd, 1988 at 6:24 am")
        self.assertEqual(date.year, 1988)
        self.assertEqual(date.month, 5)
        self.assertEqual(date.day, 23)
        self.assertEqual(date.hour, 6)
        self.assertEqual(date.minute, 24)

        #
        # RANGE
        #
        r = Range('From 04/17/13 04:18:00 to 05/01/13 17:01:00', tz='US/Central')
        self.assertEqual(r.start.year, 2013)
        self.assertEqual(r.start.month, 4)
        self.assertEqual(r.start.day, 17)
        self.assertEqual(r.start.hour, 4)
        self.assertEqual(r.start.minute, 18)
        self.assertEqual(r.end.year, 2013)
        self.assertEqual(r.end.month, 5)
        self.assertEqual(r.end.day, 1)
        self.assertEqual(r.end.hour, 17)
        self.assertEqual(r.end.minute, 1)

        _range = Range("between january 15th at 3 am and august 5th 5pm")
        self.assertEqual(_range[0].year, now.year)
        self.assertEqual(_range[0].month, 1)
        self.assertEqual(_range[0].day, 15)
        self.assertEqual(_range[0].hour, 3)
        self.assertEqual(_range[1].year, now.year)
        self.assertEqual(_range[1].month, 8)
        self.assertEqual(_range[1].day, 5)
        self.assertEqual(_range[1].hour, 17)

        _range = Range("2012 feb 2 1:13PM to 6:41 am on sept 8 2012")
        self.assertEqual(_range[0].year, 2012)
        self.assertEqual(_range[0].month, 2)
        self.assertEqual(_range[0].day, 2)
        self.assertEqual(_range[0].hour, 13)
        self.assertEqual(_range[0].minute, 13)
        self.assertEqual(_range[1].year, 2012)
        self.assertEqual(_range[1].month, 9)
        self.assertEqual(_range[1].day, 8)
        self.assertEqual(_range[1].hour, 6)
        self.assertEqual(_range[1].minute, 41)

        date = Date('2013-09-10T10:45:50')
        self.assertEqual(date.year, 2013)
        self.assertEqual(date.month, 9)
        self.assertEqual(date.day, 10)
        self.assertEqual(date.hour, 10)
        self.assertEqual(date.minute, 45)
        self.assertEqual(date.second, 50)

        _range = Range('tomorrow 10am to 5pm')
        tomorrow = now + timedelta(days=1)
        self.assertEquals(_range.start.year, tomorrow.year)
        self.assertEquals(_range.end.year, tomorrow.year)
        self.assertEquals(_range.start.month, tomorrow.month)
        self.assertEquals(_range.end.month, tomorrow.month)
        self.assertEquals(_range.start.day, tomorrow.day)
        self.assertEquals(_range.end.day, tomorrow.day)
        self.assertEquals(_range.start.hour, 10)
        self.assertEquals(_range.end.hour, 17)

    def test_dates(self):
        date = Date("August 25th, 2014 12:30 PM")
        [self.assertEqual(*m) for m in ((date.year, 2014), (date.month, 8), (date.day, 25), (date.hour, 12), (date.minute, 30), (date.second, 0))]

        date = Date("may 23, 2018 1 pm")
        [self.assertEqual(*m) for m in ((date.year, 2018), (date.month, 5), (date.day, 23), (date.hour, 13), (date.minute, 0), (date.second, 0))]

        date = Date("1-2-13 2 am")
        [self.assertEqual(*m) for m in ((date.year, 2013), (date.month, 1), (date.day, 2), (date.hour, 2), (date.minute, 0), (date.second, 0))]

        date = Date("dec 15th '01 at 6:25:01 am")
        [self.assertEqual(*m) for m in ((date.year, 2001), (date.month, 12), (date.day, 15), (date.hour, 6), (date.minute, 25), (date.second, 1))]

    def test_singles(self):
        now = datetime.now()
        #
        # Single check
        #
        self.assertEqual(Date("2012").year, 2012)
        self.assertEqual(Date("January 2013").month, 1)
        self.assertEqual(Date("feb 2011").month, 2)
        self.assertEqual(Date("05/23/2012").month, 5)
        self.assertEqual(Date("01/10/2015 at 7:30pm").month, 1)
        self.assertEqual(Date("today").day, now.day)
        self.assertEqual(Range('january')[0].month, 1)
        self.assertEqual(Range('january')[0].day, 1)
        self.assertEqual(Range('january')[0].hour, 0)
        self.assertEqual(Range('january')[1].month, 2)
        self.assertEqual(Range('january')[1].day, 1)
        self.assertEqual(Range('january')[1].hour, 0)
        self.assertEqual(Range('2010')[0].year, 2010)
        self.assertEqual(Range('2010')[0].month, 1)
        self.assertEqual(Range('2010')[0].day, 1)
        self.assertEqual(Range('2010')[0].hour, 0)
        self.assertEqual(Range('2010')[1].year, 2011)
        self.assertEqual(Range('2010')[1].month, 1)
        self.assertEqual(Range('2010')[1].day, 1)
        self.assertEqual(Range('2010')[1].hour, 0)

        self.assertEqual(Range('january 2011')[0].year, 2011)
        self.assertEqual(Range('january 2011')[0].month, 1)
        self.assertEqual(Range('january 2011')[0].day, 1)
        self.assertEqual(Range('january 2011')[0].hour, 0)
        self.assertEqual(Range('january 2011')[1].year, 2011)
        self.assertEqual(Range('january 2011')[1].month, 2)
        self.assertEqual(Range('january 2011')[1].day, 1)
        self.assertEqual(Range('january 2011')[1].hour, 0)

        self.assertEqual(Date(1374681560).year, 2013)
        self.assertEqual(Date(1374681560).month, 7)
        self.assertEqual(Date(1374681560).day, 24)
        self.assertEqual(Date(str(1374681560)).year, 2013)
        self.assertEqual(Date(str(1374681560)).month, 7)
        self.assertEqual(Date(str(1374681560)).day, 24)

        self.assertEqual(Range(1374681560).start.day, 24)
        self.assertEqual(Range(1374681560).end.day, 25)

        # offset timezones
        self.assertEqual(Date("2014-03-06 15:33:43.764419-05").hour, 20)

    def test_this(self):
        now = datetime.now()
        #
        # this year
        #
        year = Range('this year')
        self.assertEqual(year.start.year, now.year)
        self.assertEqual(year.start.month, 1)
        self.assertEqual(year.start.day, 1)
        self.assertEqual(year.start.hour, 0)
        self.assertEqual(year.start.minute, 0)
        self.assertEqual(year.end.year, now.year+1)
        self.assertEqual(year.end.month, 1)
        self.assertEqual(year.end.day, 1)
        self.assertEqual(year.end.hour, 0)
        self.assertEqual(year.end.minute, 0)

        #
        # 1 year (from now)
        #
        year = Range('1 year')
        self.assertEqual(year.start.year, (now + timedelta(days=1)).year-1)
        self.assertEqual(year.start.month, (now + timedelta(days=1)).month)
        self.assertEqual(year.start.day, (now + timedelta(days=1)).day)
        self.assertEqual(year.start.hour, 0)
        self.assertEqual(year.start.minute, 0)
        self.assertEqual(year.end.year, (now + timedelta(days=1)).year)
        self.assertEqual(year.end.month, (now + timedelta(days=1)).month)
        self.assertEqual(year.end.day, (now + timedelta(days=1)).day)
        self.assertEqual(year.end.hour, 0)
        self.assertEqual(year.end.minute, 0)

        #
        # this month
        #
        month = Range('this month')
        self.assertEqual(month.start.year, now.year)
        self.assertEqual(month.start.month, now.month)
        self.assertEqual(month.start.day, 1)
        self.assertEqual(month.start.hour, 0)
        self.assertEqual(month.start.minute, 0)
        self.assertEqual(month.end.year, month.start.year + (1 if month.start.month+1 == 13 else 0))
        self.assertEqual(month.end.month, (month.start.month + 1) if month.start.month+1 < 13 else 1)
        self.assertEqual(month.end.day, 1)
        self.assertEqual(month.end.hour, 0)
        self.assertEqual(month.end.minute, 0)

        #
        # this month w/ offset
        #
        mo = Range('this month', offset=dict(hour=6))
        self.assertEqual(mo.start.year, now.year)
        self.assertEqual(mo.start.month, now.month)
        self.assertEqual(mo.start.day, 1)
        self.assertEqual(mo.start.hour, 6)
        self.assertEqual(mo.start.minute, 0)
        self.assertEqual(mo.end.year, mo.start.year + (1 if mo.start.month+1 == 13 else 0))
        self.assertEqual(mo.end.month, (mo.start.month + 1) if mo.start.month+1 < 13 else 1)
        self.assertEqual(mo.end.day, 1)
        self.assertEqual(mo.end.hour, 6)
        self.assertEqual(mo.end.minute, 0)

        self.assertEqual(len(Range('6d')), 518400)
        self.assertEqual(len(Range('6 d')), 518400)
        self.assertEqual(len(Range('6 days')), 518400)
        self.assertEqual(len(Range('12h')), 43200)
        self.assertEqual(len(Range('6 h')), 21600)
        self.assertEqual(len(Range('10m')), 600)
        self.assertEqual(len(Range('10 m')), 600)
        self.assertEqual(len(Range('10 s')), 10)
        self.assertEqual(len(Range('10s')), 10)

    def test_dow(self):
        #
        # DOW
        #
        for x, day in enumerate(('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')):
            d, r = Date(day), Range(day)
            self.assertEqual(d.hour, 0)
            self.assertEqual(d.weekday, 1 + x)
            # length is 1 day in seconds
            self.assertEqual(len(r), 86400)
            self.assertEqual(r.start.hour, 0)
            self.assertEqual(r.end.hour, 0)
            self.assertEqual(r.end.weekday, 1 if x+1 == 7 else (2+x))

    def test_offset(self):
        now = datetime.now()

        #
        # Offset
        #
        self.assertEqual(Date("today", offset=dict(hour=6)).hour, 6)
        self.assertEqual(Date("today", offset=dict(hour=6)).day, now.day)
        self.assertEqual(Range("this week", offset=dict(hour=10)).start.hour, 10)
        self.assertEqual(Date("yesterday", offset=dict(hour=10)).hour, 10)
        self.assertEqual(Date("august 25th 7:30am", offset=dict(hour=10)).hour, 7)

    def test_lengths(self):
        #
        # Lengths
        #
        self.assertEqual(len(Range("next 10 weeks")), 5443200)
        self.assertEqual(len(Range("this week")), 604800)
        self.assertEqual(len(Range("3 weeks")), 1814400)
        self.assertEqual(len(Range('yesterday')), 86400)

    def test_in(self):
        #
        # in
        #
        self.assertTrue(Date('yesterday') in Range("last 7 days"))
        self.assertTrue(Date('today') in Range('this month'))
        self.assertTrue(Date('today') in Range('this month'))
        self.assertTrue(Range('this month') in Range('this year'))
        self.assertTrue(Range('this day') in Range('this week'))
        # these might not always be true because of end of week
        # self.assertTrue(Range('this week') in Range('this month'))
        # self.assertTrue(Range('this week') in Range('this year'))

    def test_tz(self):
        #
        # TZ
        #
        self.assertEqual(Date('today', tz="US/Central").tz.zone, 'US/Central')

    def test_cut(self):
        #
        # Cut
        #
        self.assertTrue(Range('from january 10th 2010 to february 2nd 2010').cut('10 days') == Range('from january 10th 2010 to jan 20th 2010'))
        self.assertTrue(Date("jan 10") + '1 day' == Date("jan 11"))
        self.assertTrue(Date("jan 10") - '5 day' == Date("jan 5"))

    def test_compare(self):
        self.assertFalse(Range('10 days') == Date('yestserday'))
        self.assertTrue(Date('yestserday') in Range('10 days'))
        self.assertTrue(Range('10 days') in Range('100 days'))
        self.assertTrue(Range('next 2 weeks') > Range('1 year'))
        self.assertTrue(Range('yesterday') < Range('now'))

    def test_last(self):
        now = datetime.now()
        #
        # last year
        #
        year = Range('last year')
        self.assertEqual(year.start.year, now.year - 1)
        self.assertEqual(year.start.month, now.month)
        self.assertEqual(year.start.day, now.day)
        self.assertEqual(year.start.hour, 0)
        self.assertEqual(year.start.minute, 0)
        self.assertEqual(year.end.year, now.year)
        self.assertEqual(year.end.month, now.month)
        self.assertEqual(year.end.day, now.day)
        self.assertEqual(year.end.hour, 0)
        self.assertEqual(year.end.minute, 0)
        self.assertTrue(Date('today') in year)

        self.assertTrue(Date('last tuesday') in Range('8 days'))
        self.assertTrue(Date('monday') in Range('8 days'))
        self.assertTrue(Date('last fri') in Range('8 days'))
        self.assertEqual(Range('1 year ago'), Range('last year'))
        self.assertEqual(Range('year ago'), Range('last year'))

    def test_psql_infinity(self):
        d = Date('infinity')
        self.assertTrue(d > 'now')
        self.assertTrue(d > 'today')
        self.assertTrue(d > 'next week')

        self.assertFalse(d in Range('this year'))
        self.assertFalse(d in Range('next 5 years'))

        self.assertTrue(Range('month') < d)

        r = Range('today', 'infinity')

        self.assertTrue('next 5 years' in r)
        self.assertTrue(Date('today') in r)
        self.assertTrue(d in r)
        self.assertFalse(d > r)
        self.assertFalse(r > d)

        r = Range('["2013-12-09 06:57:46.54502-05",infinity)')
        self.assertTrue(r.end == 'infinity')
        self.assertTrue('next 5 years' in r)
        self.assertTrue(Date('today') in r)
        self.assertTrue(d in r)
        self.assertFalse(d > r)
        self.assertFalse(r > d)
        self.assertEqual(r.start.year, 2013)
        self.assertEqual(r.start.month, 12)
        self.assertEqual(r.start.day, 9)
        self.assertEqual(r.start.hour, 11)
        self.assertEqual(r.start.minute, 57)
        self.assertEqual(r.start.second, 46)

    def test_date_adjustment(self):
        d = Date("Jan 1st 2014 at 10 am")
        self.assertEqual(d.year, 2014)
        self.assertEqual(d.month, 1)
        self.assertEqual(d.day, 1)
        self.assertEqual(d.hour, 10)
        self.assertEqual(d.minute, 0)
        self.assertEqual(d.second, 0)

        d.hour = 5
        d.day = 15
        d.month = 4
        d.year = 2013
        d.minute = 40
        d.second = 14

        self.assertEqual(d.year, 2013)
        self.assertEqual(d.month, 4)
        self.assertEqual(d.day, 15)
        self.assertEqual(d.hour, 5)
        self.assertEqual(d.minute, 40)
        self.assertEqual(d.second, 14)

        self.assertEqual(str(d.date), "2013-04-15 05:40:14")

    def test_parse(self):
        self.assertEqual(parse('tuesday at 10pm')['hour'], 22)
        self.assertEqual(parse('tuesday at 10pm')['weekday'], 2)
        self.assertEqual(parse('may of 2014')['year'], 2014)

    @data((1, "one"),
          (12, "twelve"),
          (72, "seventy two"),
          (300, "three hundred"),
          (1200, "twelve hundred"),
          (12304, "twelve thousand three hundred four"),
          (6000000, "six million"),
          (6400005, "six million four hundred thousand five"),
          (123456789012, "one hundred twenty three billion four hundred fifty six million seven hundred eighty nine thousand twelve"),
          (4000000000000000000000000000000000, "four decillion"))
    def test_string_to_number(self, data):
        (equals, string) = data
        self.assertEqual(text2num(string), equals)
        self.assertEqual(text2num(u(string)), equals)

    def test_plus(self):
        date1 = Date("october 18, 2013 10:04:32 PM")
        date2 = date1 + "10 seconds"
        self.assertEqual(date1.second + 10, date2.second)


def main():
    os.environ['TZ'] = 'UTC'
    time.tzset()
    unittest.main()


if __name__ == '__main__':
    main()
