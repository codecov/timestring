import re, types, datetime, time

timestring_RE = re.compile(re.sub('[\t\n]','',re.sub('(\(\?\#[^\)]+\))','',r'''
	(
		((?P<prefix>between|from|before|after|\>=?|\<=?|greater\sth(a|e)n(\sa)?|less\sth(a|e)n(\sa)?)\s)?
		(
			(
				((?P<ref>next|last|prev(ious)?|this)\s)?
				(?P<main>
					(?# =-=-=-= Matches:: number-frame-ago?, "4 weeks", "sixty days ago" =-=-=-= )
					(
						(?P<num>((\d+|couple(\sof)?|one|two|twenty|twelve|three|thirty|thirteen|four(teen|ty)?|five|fif(teen|ty)|six(teen|ty)?|seven(teen|ty)?|eight(een|y)?|nine(teen|ty)?|ten|eleven|hundred)\s)*)
						(?P<delta>minutes?|hours?|days?|weeks?|months?|quarters?|years?)(\s(?P<ago>ago))?
					)
						|
					
					(?# =-=-=-= Matches Days =-=-=-= )	
					(?P<day_2>yesterday|today|now|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tues?|wedn?|thur?|fri|sat|sun)
						|
						
					(?# =-=-=-= Matches "january 5, 2012", "january 5th, '12", "jan 5th 2012" =-=-=-= )
					((?P<month>january|february|march|april|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)\s((?P<date>\d{1,2})(th|nd|st|rd)?)(,?\s(?P<year>([12][089]|')?\d{2}))?)
						|
						
					(?# =-=-=-= Matches "5/23/2012", "2012/12/11" =-=-=-= )
					(
						((?P<year_3>[12][089]\d{2})[/-](?P<month_3>[01]?\d)([/-](?P<date_3>[0-3]?\d))?)
							|
						((?P<month_2>[01]?\d)[/-](?P<date_2>[0-3]?\d)[/-](?P<year_2>([12][089])?\d{2}))
					)
						|
						
					(?# =-=-=-= Matches "01:20", "6:35 pm", "7am", "noon" =-=-=-= )
					((
						((?P<hour>[012]?[0-9]):(?P<minute>[0-5]\d)\s?(?P<am>am|pm|p|a))
							|
						((?P<hour_2>[012]?[0-9]):(?P<minute_2>[0-5]\d))
							|
						((?P<hour_3>[012]?[0-9])\s?(?P<am_1>am|pm|p|a|o'?clock))
							|
						(?P<daytime>(after)?noon|morning|((around|about|near|by)\s)?this\stime|evening|(mid)?night(time)?)
					))
				)
			)
			(?# =-=-=-= Conjunctions =-=-=-= )
			,?(\s(on|at|of|by|and|to|@))?\s?
		)+
	)
	''')), re.I)


# !findall
def findall(text):
	results = timestring_RE.findall(text)
	dates = []
	for date in results:
		if re.compile('((next|last)\s(\d+|couple(\sof))\s(weeks|months|quarters|years))|(between|from)',re.I).match(date[0]):
			dates.append((date[0], Range(date[0])))
		else:
			dates.append((date[0], Date(date[0])))
	if kwargs.get('replace', False):
		for date in dates:
			text = text.replace(date[0], '{{%s}}'%str(hash(date[1])))
		return (dates, text)
	else:
		return dates
			

# !common
def now(**k):
	return Date('now',**k)
	
def today(**k):
	return Date('today', **k)
	


# !Date
class Date:
	
	def __init__(self, date=None, live=False, **kwargs):
		# The original request
		self.original = date
		self.live = live
		
		# Determinal starting date.
		if type(date) in (types.StringType, types.UnicodeType):
			'''
			The date is a string and needs to be converted into a <dict> for processesing
			'''
			res = timestring_RE.search(date.strip())
			if res:
				date = res.groupdict()
			else:
				raise ValueError('Invlid date string >> %s'%date)

			date = dict((k,v.lower() if type(v) is str else v) for k, v in date.iteritems() if v)
			
		if type(date) is types.DictType:
			# Initial date.
			new_date = datetime.datetime(*time.localtime()[:3])
			
			# !number of (days|...) (ago)?
			if date.get('num') or date.get('delta'):
				if date.get('num','').find('couple')>-1:
					i = 2 * int(1 if date.get('ago') or (date.get('ref','') or '').lower()=='last' else -1)
				else:
					i = int(string_to_number(date.get('num',1))) * int(1 if date.get('ago') or (date.get('ref','') or '').lower()=='last' else -1)
				delta = date.get('delta')
				delta = delta if delta.endswith('s') else delta+'s'
				
				if delta == 'years':
					try:
						new_date = new_date.replace(year=(new_date.year - i))
					except ValueError: #day is out of range for month
						new_date = new_date - datetime.timedelta(days=(365*i))
				elif delta == 'months':
					try:
						new_date = new_date.replace(month=(new_date.month - i))
					except ValueError: #day is out of range for month
						new_date = new_date - datetime.timedelta(days=(30*i))
				elif delta == 'quarters':
					''' 
					This section is not working... 
					Most likely need a generator that will take me to the right quater.
					'''
					q1, q2, q3, q4 = datetime.datetime(new_date.year, 1, 1), datetime.datetime(new_date.year, 4, 1), datetime.datetime(new_date.year, 7, 1), datetime.datetime(new_date.year, 10, 1)
					if q1 <= new_date < q2:
						# We are in Q1
						if i == -1:
							new_date = datetime.datetime(new_date.year-1, 10, 1)
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
					new_date = new_date - datetime.timedelta(days=(91*i))
					''' end '''
				else:
					new_date = new_date - datetime.timedelta(**{delta:i})
			
			# !dow
			if [date.get(key) for key in ('day','day_2','day_3') if date.get(key)]:
				dow = max([date.get(key) for key in ('day','day_2','day_3') if date.get(key)]).lower()
				iso = dict(monday=1,tuesday=2,wednesday=3,thursday=4,friday=5,saturday=6,sunday=7,mon=1,tue=2,tues=2,wed=3,wedn=3,thu=4,thur=4,fri=5,sat=6,sun=7).get(dow)
				if iso:
					# Must not be today
					if new_date.isoweekday() != iso:
						# determin which direction
						if date.get('ref') not in ('this','next'):
							days =  iso - new_date.isoweekday() - (7 if iso>new_date.isoweekday() else 0)
						else:
							days = iso - new_date.isoweekday() + (7 if iso<new_date.isoweekday() else 0)
							
						new_date = new_date + datetime.timedelta(days=days)
						
				elif dow == 'yesterday':
					new_date = new_date - datetime.timedelta(days=1)
				elif dow == 'tomorrow':
					new_date = new_date + datetime.timedelta(days=1)
				elif dow == 'now':
					self.date = datetime.datetime(*time.localtime()[:5])
					
				
			# !year
			year = [date.get(key) for key in ('year','year_2','year_3') if date.get(key)]
			if year: 
				y = int(max(year))
				if len(str(y))!=4:
					y += 2000 if y<=40 else 1900						
				new_date = new_date.replace(year=y)
			
			# !month
			month = [date.get(key) for key in ('month','month_2','month_3') if date.get(key)]
			if month:
				new_date = new_date.replace(day=1)
				new_date = new_date.replace(month=int(max(month)) if re.match('^\d+$',max(month)) else dict(january=1,february=2,march=3,april=4,june=6,july=7,august=8,september=9,october=10,november=11,december=12,jan=1,feb=2,mar=3,apr=4,may=5,jun=6,jul=7,aug=8,sep=9,sept=9,oct=10,nov=11,dec=12).get(max(month).lower(), new_date.month))
			
			# !day
			day = [date.get(key) for key in ('date','date_2','date_3') if date.get(key)]
			if day: 
				new_date = new_date.replace(day=int(max(day)))
			
			# !daytime
			if date.get('daytime'):
				if date['daytime'].find('this time')>-1:
					new_date = new_date.replace(
						hour = 	datetime.datetime(*time.localtime()[:5]).hour,
						minute = datetime.datetime(*time.localtime()[:5]).minute
					)
				else: 
					new_date = new_date.replace(hour=dict(morning=9,noon=12,afternoon=15,evening=18,night=21,nighttime=21,midnight=24).get(date.get('daytime').lower(), 12))
				kwargs['offset'] = False # No offset because the hour was set.
			
			# !hour
			hour = [date.get(key) for key in ('hour','hour_2','hour_3') if date.get(key)] 
			if hour:
				new_date = new_date.replace(hour=int(max(hour)))
				am = [date.get(key) for key in ('am','am_1') if date.get(key)]
				if am and max(am).lower() in ('p','pm'):
					new_date = new_date.replace(hour=int(max(hour))+12)
				kwargs['offset'] = False # No offset because the hour was set.
							
				#minute
				minute = [date.get(key) for key in ('minute','minute_2') if date.get(key)] 
				if minute:
					new_date = new_date.replace(minute=int(max(minute)))
			
			
			self.date = new_date

				
		elif type(date) in (types.IntType, types.LongType, types.FloatType) and re.match('^\d{10}$', date):
			self.date = datetime.datetime.fromtimestamp(int(date))
		
		elif isinstance(date, datetime.datetime):
			self.date = date
		
		elif date is None:
			self.date = datetime.datetime.now()
		
		else:
			# Set to the current date Y, M, D, H0, M0, S0
			self.date = datetime.datetime(*time.localtime()[:3])
		
		# end if type(date) is types.DictType:	
		if kwargs.get('offset') and type(kwargs.get('offset')) is types.DictType:# and self.date.hour == 0:
			self.date = self.date.replace(**kwargs.get('offset'))
	
	def get_date(self):
		return self.date
	
	def get_live(self):
		return self.live
	
	def set_live(self, live):
		self.live = bool(live)
	
	def is_now(self):
		return self.get_live() and self.original == 'now'
	
	def adjust(self, to):
		'''
		Adjusts the time from kwargs to timedelta
		**Will change this object**
		'''
		if type(to) in (types.StringType, types.UnicodeType):
			res = timestring_RE.search(to.lower())
			if res:
				rgroup = res.groupdict()
				if rgroup.get('delta'):
					i = int(string_to_number(rgroup.get('num',1))) * (-1 if to.startswith('-') else 1)
					delta = rgroup.get('delta')
					delta = delta if delta.endswith('s') else delta+'s'
					if delta == 'years':
						try:
							self.date = new_date.replace(year=(self.date.year - i))
						except ValueError: #day is out of range for month
							self.date = self.date - datetime.timedelta(days=(365*i))
					elif delta == 'months':
						try:
							self.date = self.date.replace(month=(self.date.month - i))
						except ValueError: #day is out of range for month
							self.date = self.date - datetime.timedelta(days=(30*i))
					elif delta == 'quarters':
						pass #NP
					else:
						self.date = self.date + datetime.timedelta(**{delta:i})
					return self
		else:
			self.date = self.date + datetime.timedelta(seconds=int(to))
			return self
				
		raise ValueError('Invalid addition request')
		
		self.date = self.date + datetime.timedelta(**kwargs)
	
	def __new__(self):
		return Date(self.get_date())
	
	def __iadd__(self, to):
		return self.adjust(to)
	
	def __isub__(self, to):
		if type(to) in (types.StringType, types.UnicodeType):
			to = to[1:] if to.startswith('-') else ('-'+to)
		elif type(to) in (types.IntType, types.FloatType, types.LongType):
			to = to * -1
		return self.adjust(to)	
	
	def __add__(self, to):
		return self.__new__().adjust(to)
		
	def __sub__(self, to):
		if type(to) in (types.StringType, types.UnicodeType):
			to = to[1:] if to.startswith('-') else ('-'+to)
		elif type(to) in (types.IntType, types.FloatType, types.LongType):
			to = to * -1
		return self.__new__().adjust(to)
	
	
	def __format__(self, _):
		return self.get_date().strftime('%x %X')

	def __str__(self):
		"""Returns date in representation of `%x %X` ie `2013-02-17 00:00:00`"""
		return str(self.date)
	
	def __cmp__(self, to):
		return 1 if self.get_date() > to.get_date() else 0 if self.get_date()==to.get_date() else -1

	def format(self, format_string='%x %X'):
		return self.get_date().strftime(format_string)
		

	def to_unixtime(self):
		return time.mktime(self.date.timetuple())
	

	def to_mysql(self):
		if self.get_live():
			if self.original in (None, 'now'):
				return 'now()'
			#elif self.original in ('today','now','tomorrow'):
			#	return '%s()' % self.original
			
			elif re.match(r'^this\s', self.original, re.I):
				return "now() - interval 1 %s" % re.sub(r'^this\s', '', self.original, re.I).lower()
				
			else:
				return "now() %s interval '%s'" % ( '-' if 'ago' in self.original else '+', self.original.replace(' ago','').lower())
		else:
			return "date '%s'" % str(self.date)

	
	def to_postgresql(self):
		'''
		Returns a well formatted string for postgresql to process.
		'''
# 		TIME = JOIN[tables[0]]['times'] % ("day('%s')"%self.get_range()[0], "day('%s')"%self.get_range()[1])
		if self.get_live():
			if self.original in (None, 'now'):
				return 'now()'
			elif self.original in ('today','now','tomorrow'):
				return '%s()' % self.original
			else:
				return "today() %s '%s'::interval" % ( '-' if 'ago' in self.original else '+', self.original.replace(' ago','').lower())
		else:
			return "'%s'::date" % str(self.date)
	
	
# !Range
class Range:
	'''
	Range objects are like <standards.Date> but contain 2 dates that are ranges to be used.

	* between <date> and <date>
	* (from)? <date> to <date>
	* from <date>
	* greater then date
	* less then date
	* this week
	'''
	def __init__(self, start, end=None, offset=None, live=False, start_of_week=0):
		'''
		#date1 and #date2 can be type <standards.Date> || str || None
		#date1 can be a full string to express the whole range.
			ex. from x to y, between x and y, x to y
		'''
		self.original = (start, end)
		self.live = live
		self.dates = {}
		
		if type(start) in (types.StringType, types.UnicodeType):
			# Remove prefix
			start = start.lower()
			start = re.sub('^(between|from)\s','',start)
			
			# Split the two requests
			if re.search(r'(\s(and|to)\s)', start):
				# Both arguments found in start variable
				r = tuple(re.split(r'(\s(and|to)\s)', start.strip()))
				start, end = r[0], r[-1]

			
			# Parse
			res = timestring_RE.search(start)
			if res:
				group = res.groupdict()
				if group.get('ref')=='this' and group.get('delta'):
					if group.get('delta') == 'week':
						start = today(offset=offset) - (str(today().get_date().weekday())+' days')
						end = start.get_date() + datetime.timedelta(weeks=1)
						
					elif group.get('delta') == 'month':
						start = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1)
						end = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, 1)
						if end.month == 12:
							end = end.replace(year=end.year+1, month=1)
						else:
							end = end.replace(month=end.month+1)
						
					elif group.get('delta') == 'quarter':
						pass
					
					elif group.get('delta') == 'day':
						start = datetime.datetime(*time.localtime()[:3])
						end = datetime.datetime(*time.localtime()[:3]) + datetime.timedelta(days=1)
					
					elif group.get('delta') == 'year':
						start = datetime.datetime(datetime.datetime.now().year, 1, 1)
						end = datetime.datetime(datetime.datetime.now().year+1, 1, 1)
						
					elif group.get('delta') == 'hour':
						start = datetime.datetime(*time.localtime()[:4])
						end = datetime.datetime(*time.localtime()[:4]) + datetime.timedelta(hours=1)
						
					elif group.get('delta') == 'minute':
						start = datetime.datetime(*time.localtime()[:5])
						end = datetime.datetime(*time.localtime()[:5]) + datetime.timedelta(minutes=1)

					else:
						raise ValueError("Invalid timestring request")
				
				else:
					start = Date(group, offset=offset)	
				
			else:
				raise ValueError("Invalid timestring request")
		
		self[0] = start if isinstance(start, Date) else Date(start, offset=offset)
		self[1] = end if isinstance(end, Date) else Date(end, live, offset=offset)
		
	
	def __setitem__(self, index, value):
		self.dates[index] = value
		return True
	
	def __getitem__(self, index):
		return self.dates[index]
			
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
	
	def format(self, format_string='%x %X'):
		return "From %s to %s" % (self[0].format(format_string), self[1].format(format_string))
	
	@property
	def elapse(self, short=False, format=True, min=None, round=None):
		full = [0, 0, 0, 0, 0, 0] # years, months, days, hours, minutes, seconds
		elapse = self[1].get_date() - self[0].get_date()
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
		
		full[3], full[4], full[5] = tuple(map(int,map(float,str(elapse).split(', ')[-1].split(':'))))
		
		if round:
			r = ['years','months','days','hours','minutes', 'seconds']
			assert round in r[:-1], "round value is not allowed. Must be in "+",".join(r)
			if full[r.index(round)+1] > dict(months=6,days=15,hours=12,minutes=30,seconds=30).get(r[r.index(round)+1]):
				full[r.index(round)] += 1 
			
			min = r[r.index(round)+1]
			
		if min:
			m = ['years','months','days','hours','minutes','seconds']
			assert min in m, "min value is not allowed. Must be in "+",".join(m)
			for x in range(6-m.index(min)):
				full[5-x] = 0
		
		if format:
			if short:
				return re.sub('((?<!\d)0\w\s?)','',"%dy %dm %dd %dh %dm %ss" % tuple(full))
			else:
				return re.sub('((?<!\d)0\s\w+\s?)','',"%d years %d months %d days %d hours %d minutes %d seconds" % tuple(full))
		return full
	
	def __len__(self):
		"""Returns how many `seconds` the `Range` lasts.
		"""
		return self[1].to_unixtime() - self[0].to_unixtime()
	
	def get_live(self):
		return self.live
	
	def set_live(self, tf):
		self.live = bool(tf)

	def to_mysql(self):
		'''
		Returns a well formatted string for postgresql to process.
		ex. 
			between x and y
			> x
			>= x
			< y
		'''
		if self[1].get_live() and self[1].is_now():
			return '> %s' % self[0].to_mysql()
		elif self[0] is None:
			return '< %s' % self[1].to_mysql()
		else:
			return 'between %s and %s' % (self[0].to_mysql(), self[1].to_mysql())
	
	def to_postgresql(self):
		'''
		Returns a well formatted string for postgresql to process.
		'''
		if self[1].get_live() and self[1].is_now():
			return '> %s' % self[0].to_postgresql()
		elif self[0] is None:
			return '< %s' % self[1].to_postgresql()
		else:
			return 'between %s and %s' % (self[0].to_postgresql(), self[1].to_postgresql())
	
	def cut(self, by, from_start=True):
		""" Cuts this object from_start to the number requestd
		"""
		if from_start:
			self[1] = self[0] + by
		else:
			self[0] = self[1] - by
		return self
	
	def adjust(self, to):
		self[0].adjust(to)
		self[1].adjust(to)
		return self
	
	def __new__(self):
		return Range(self[0], self[1])
		
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
