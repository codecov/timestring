import re

version = '1.1.0'
__version__ = '1.1.0'

from Date import Date
from Range import Range

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