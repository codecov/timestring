from timestring.Range import Range
from timestring.Date import Date
import datetime

if __name__ == '__main__':
    now = datetime.datetime.now()

    # year
    assert Date("2012").year == 2012, "Invalid year"
    assert Date("January 2013").year == 2013, "Invalid year"
    # month
    assert Date("february 2011").month == 2, "Invalid month"
    assert Date("05/23/2012").month == 5, "Invalid month"
    assert Date("01/10/2015 at 7:30pm").month == 1, "Invalid month"

    #full checks
    date = Date("01/10/2015 at 7:30pm")
    assert date.year == 2015, "Invalid year"
    assert date.month == 1, "Invalid month"
    assert date.day == 10, "Invalid day"
    assert date.hour == 19, "Invalid hour"
    assert date.minute == 30, "Invalid minute"

    date = Date("may 23rd, 1988 at 6:24 am")
    assert date.year == 1988, "Invalid year"
    assert date.month == 5, "Invalid month"
    assert date.day == 23, "Invalid day"
    assert date.hour == 6, "Invalid hour"
    assert date.minute == 24, "Invalid minute"

    date = Range("between january 15th at 3 am and august 5th 5pm")
    assert date[0].year == now.year, "Invalid year"
    assert date[0].month == 1, "Invalid month"
    assert date[0].day == 15, "Invalid day"
    assert date[0].hour == 3, "Invalid hour"
    assert date[1].year == now.year, "Invalid year"
    assert date[1].month == 8, "Invalid month"
    assert date[1].day == 5, "Invalid day"
    assert date[1].hour == 17, "Invalid hour"

    date = Range("feb 2 to 6:30 am on sept 8")
    assert date[0].month == 2, "Invalid month"
    assert date[0].day == 2, "Invalid day"
    assert date[1].month == 9, "Invalid month"
    assert date[1].day == 8, "Invalid day"
    assert date[1].hour == 6, "Invalid hour"
    assert date[1].minute == 30, "Invalid hour"

    # date = Date("4th of july")
    # assert date.year == now.year, "Invalid year"
    # assert date.month == 7, "Invalid month"
    # assert date.day == 4, "Invalid day"
    # assert date.hour == 0, "Invalid hour"
    # assert date.minute == 0, "Invalid minute"

    for x, day in enumerate(('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'Satruday', 'sunday')):
        assert Date(day).weekday == 1 + x, "Invalid isoweekday"
        assert len(Range(day)) == 86400, "Invalid day length"

    #
    # Offset
    #
    assert Date("today", offset=dict(hour=6)).hour == 6, "Invalid offset hour."
    assert Date("today", offset=dict(hour=6)).day == datetime.datetime.now().day, "Invalid offset hour"
    assert Range("this week", offset=dict(hour=10)).start.hour == 10, "Invalid offset hour"
    assert Date("yesterday", offset=dict(hour=10)).hour == 10, "Invalid offset hour"
    assert Date("august 25th 7:30am", offset=dict(hour=10)).hour == 7, "Invalid offset hour"

    #
    # Lengths
    #
    assert len(Range("next 10 weeks")) < 6048000, "Length of 10 weeks invalid"
    assert len(Range("this week")) == 604800, "Length of this week is invalid"
    assert 1814400 < len(Range("3 weeks")) < 1900800, "Weeks are to long"
    assert len(Range('yesterday')) == 86400, "yesterday is to long"

    #
    #
    #
    assert Date('yesterday') in Range("last 7 days"), "Date not in range"

    #
    # Cut
    #
    Range('from january 10th to february 2nd').cut('10 days')
    Range('from january 10th to february 2nd').adjust('1 month')
