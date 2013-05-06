import timestring

if __name__ == '__main__':
	#
	# Test Ranges
	#
	timestring.Range("this week")
	timestring.Range("13 days")
	timestring.Range("between january 15th and august 5th")

	#
	# Cut
	#
	timestring.Range('from january 10th to february 2nd').cut('10 days')
	timestring.Range('from january 10th to february 2nd').adjust('1 month')