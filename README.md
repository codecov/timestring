# daterange

Daterange is a python module that handles dates and ranges more effectively by changing common phrases into usable objects.
These objects can be changed into `mysql` and `postgresql` to easily query a date range.

Daterange is licensed under the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html).

## Usage

**Simple Example**
```
import daterange
print str(daterange.Range('this month'))
>>> From 2013/01/01 00:00:00 to 2013/02/01 00:00:00
```
This example takes a simple phrase, such as `this month` and changes it into two `datetime` objects.

_More examples coming soon_
