timestring
=========

*Currently in `beta`, so pardon the mess*

## Description
**timestring** is a python module that handles dates and ranges more effectively by changing common phrases into usable objects.
These objects. These objects, known as `Date` or `Range` can be easily converted into `mysql` or `postgresql` friendly queries.

## License
**timestring** is licensed under the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html).

## Install
`pip install timestring`


## Usage

### timestring.Ranges

```python
>>> str(timestring.Range("this week"))
'From 04/29/13 00:00:00 to 05/06/13 00:00:00'
>>> str(timestring.Range("last 15 days"))
'From 04/18/13 00:00:00 to 05/03/13 17:43:20'
>>> timestring.Range("feb 15th to may 1st").to_mysql()
"between date '2013-02-15 00:00:00' and date '2013-05-01 00:00:00'"
>>> timestring.Range("17 days ago").to_postgresql()
"between '2013-04-16 00:00:00'::date and '2013-05-03 17:45:17.919822'::date"
```


## Roadmap

See [issues](https://github.com/stevepeak/timestring/issues)
