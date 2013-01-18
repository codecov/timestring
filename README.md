daterange
=========

Daterange is (for the time begin) a python module that handles dates and ranges more effectively by changing common phrases into usable objects.
These objects can be changed into `mysql` and `postgresql` to easily query a date range.

daterange is licensed under the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html).

## Usage

1. `mysql` and `postgresql` queries
2. parsing large blocks of text
 * `daterange.findall` will find all date and range objects in a block of text.

The creation of `daterange` was to create quick strings of dates that can be used in queries.
This example below takes a simple string and changes it into a mysql query range: 
```python
"select columns from table where timestamp %s" % daterange.Range('last 7 days').to_mysql()
```
**Results in:** select columns from table where timestamp between date '2013-01-11 00:00:00' and date '2013-01-18 10:08:38.313109'


### Parsing Examples
```python
daterange.Range('this month')
>>> "From 2013/01/01 00:00:00 to 2013/02/01 00:00:00"
print daterange.Range('last 7 days')
>>> "From 01/11/13 00:00:00 to 01/18/13 10:05:05"
```

Parsing numbers

```python
print daterange.Range('three days ago')
>>> "From 01/15/13 00:00:00 to 01/18/13 10:15:21
```

Parsing a date
```python
print daterange.Date('jan 15th 2012')
>>> "2012-01-15 00:00:00"
print daterange.Date('1/10/2012 at 6:30 pm')
>>> "2012-01-10 18:30:00"
print daterange.Range('from jan 16 to feb 19th at 5:17 am')
>>> "From 01/16/13 00:00:00 to 02/19/13 05:17:00"
```

## Roadmap
1. Creating native `mysql` functions that use the same algorithm.
 * ex. `select * from table where daterange(timestamp, '7 days ago');`
2. Create native `javascript` functions for client side parsing.







