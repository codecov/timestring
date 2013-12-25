# `Timestring` [![Build Status](https://secure.travis-ci.org/stevepeak/timestring.png)](http://travis-ci.org/stevepeak/timestring) [![Version](https://pypip.in/v/timestring/badge.png)](https://github.com/stevepeak/timestring)

## Description
Converting strings into usable time objects. The time objects, known as `Date` and `Range` have a number of methods that allow 
you to easily change and manage your useres input dynamically.




## Ranges

### Overview Examples
...
...
...

### References

* `this` => `[ - - x - - ]`
    - `this month` is from start of month to end of month. Therefore today **is** included.
    - ```Range("today") in Range("this month") == True```
* `next` => `x [ - - - - ]`
    - `next 3 weeks` takes today and finds the start of next weeks and continues to contain 3 weeks.
    - `Range("today") in Range("next 5 days") == False` and `Range("tomorrow") in Range("next 5 days") == True`
* `ago` => `[ - - - - ] x`
    - same as `next` but in the past
* `last` and empty => `[ - - - - x ]`
    - `last 6 days` takes all of Today and encapsulates the last 6 days
    - ```Range("today") in Range("last 6 days") == True```
    - empty reference ex `10 days`

### Samples
The examples below all work with the following terms `minute`, `hour`, `day`, `month` and `year` work for the examples below. fyi `Today is 5/14/2013`

> `this` will look at the references in its entirety
```python
>>> Range('this year')
From 01/01/13 00:00:00 to 01/01/14 00:00:00
```

*Notice how this year is from jan 1s to jan 1st of next year* The full year, all 12 months, is **this year**


> `ago` and `last` will reference in the past
```python
>>> Range('1 year ago')
From 01/01/11 00:00:00 to 01/01/12 00:00:00
```
`1 year ago` is equivalent to `year ago`, and `last year`

*Note* you add more years like this `5 years ago` which will be `From 01/01/07 00:00:00 to 01/01/08 00:00:00`

### Constants
* Plural words are *not sensitive* ex `17 minute ago` == `17 minutes ago`





### For more examples see the [test file](https://github.com/stevepeak/timestring/blob/master/timestring/tests.py)

More examples / documentation coming soon.

## License
**timestring** is licensed under the Apache Licence, Version 2.0 (http://www.apache.org/licenses/LICENSE-2.0.html).

## Install
`pip install timestring`

