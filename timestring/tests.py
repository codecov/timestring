from timestring.Range import Range
from timestring.Date import Date
import datetime
import unittest


class Tests(unittest.TestCase):

    def testOne(self):
        now = datetime.datetime.now()

        #
        # Single check
        #
        self.assertEqual(Date("2012").year, 2012)
        self.assertEqual(Date("January 2013").year, 2013)
        self.assertEqual(Date("february 2011").month, 2)
        self.assertEqual(Date("05/23/2012").month, 5)
        self.assertEqual(Date("01/10/2015 at 7:30pm").month, 1)
        self.assertEqual(Range('this year').start.year, now.year)
        self.assertEqual(Range('this year').start.month, 1)
        self.assertEqual(Date("today").day, now.day)

        #
        # Full string check
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

        date = Range("between january 15th at 3 am and august 5th 5pm")
        self.assertEqual(date[0].year, now.year)
        self.assertEqual(date[0].month, 1)
        self.assertEqual(date[0].day, 15)
        self.assertEqual(date[0].hour, 3)
        self.assertEqual(date[1].year, now.year)
        self.assertEqual(date[1].month, 8)
        self.assertEqual(date[1].day, 5)
        self.assertEqual(date[1].hour, 17)

        date = Range("feb 2 to 6:30 am on sept 8")
        self.assertEqual(date[0].month, 2)
        self.assertEqual(date[0].day, 2)
        self.assertEqual(date[1].month, 9)
        self.assertEqual(date[1].day, 8)
        self.assertEqual(date[1].hour, 6)
        self.assertEqual(date[1].minute, 30)

        # date = Date("4th of july")
        # assert date.year == now.year, "Invalid year"
        # assert date.month == 7, "Invalid month"
        # assert date.day == 4, "Invalid day"
        # assert date.hour == 0, "Invalid hour"
        # assert date.minute == 0, "Invalid minute"

        #
        # DOY
        #
        for x, day in enumerate(('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'Satruday', 'sunday')):
            self.assertEqual(Date(day).weekday, 1 + x)
            self.assertEqual(len(Range(day)), 86400)

        #
        # Offset
        #
        self.assertEqual(Date("today", offset=dict(hour=6)).hour, 6)
        self.assertEqual(Date("today", offset=dict(hour=6)).day, datetime.datetime.now().day)
        self.assertEqual(Range("this week", offset=dict(hour=10)).start.hour, 10)
        self.assertEqual(Date("yesterday", offset=dict(hour=10)).hour, 10)
        self.assertEqual(Date("august 25th 7:30am", offset=dict(hour=10)).hour, 7)

        #
        # Lengths
        #
        self.assertTrue(len(Range("next 10 weeks")) < 6048000)
        self.assertEqual(len(Range("this week")), 604800)
        self.assertTrue(1814400 < len(Range("3 weeks")) < 1900800)
        self.assertEqual(len(Range('yesterday')), 86400)

        #
        # in
        #
        self.assertTrue(Date('yesterday') in Range("last 7 days"))
        self.assertTrue(Date('today') in Range('this month'))

        #
        # TZ
        #
        self.assertEqual(Date('today', tz="US/Central").tz.zone, 'US/Central')

        #
        # Cut
        #
        self.assertTrue(Range('from january 10th to february 2nd').cut('10 days') == Range('from january 10th to jan 20th'))
        self.assertTrue(Date("jan 10") + '1 day' == Date("jan 11"))
        self.assertTrue(Date("jan 10") - '5 day' == Date("jan 5"))


def main():
    unittest.main()


if __name__ == '__main__':
    main()
