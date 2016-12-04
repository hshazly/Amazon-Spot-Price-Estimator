#!/usr/bin/python
import sys
from dateutil import parser
from datetime import datetime, timedelta
import json
    
def getmins(start_date, td):
	timediff = td - start_date
	min_tuple = divmod(timediff.days * 86400 + timediff.seconds, 60)
	mins = min_tuple[0]
	
	if min_tuple[1] > 0:
		mins = mins + min_tuple[1]/60
		
	return mins	
	    
in_prefix = sys.argv[1]
price_file = sys.argv[2]

#spot-c4-8xlarge.txt
#0.616, 2, 3, 4, 0.256, 0.338, 0.402, 0.884, 1, 5
#0.256, 0.338, 0.402, 0.616, 0.884, 2, 3, 4, 5

prices = []
timestamps = []

bid_list = []

with open(price_file) as infile:
	lines = infile.readlines()
	
for line in lines:
	bid_list.append(float(line.strip()))

mainf = "spot-"+in_prefix+".txt"
#"sample.txt" #

with open(mainf) as infile:
	data = json.load(infile)

datalist = data["SpotPriceHistory"]	
records = {}

#raise Exception(list(reversed(datalist)))
for record in datalist:
	mytime = record["Timestamp"].replace('T', ' ')
	mytime = mytime.replace('Z', '')
	mytime = mytime.split("2016-")[1]
	mytime = mytime.split(".000")[0]
	timestamps.append(mytime)
	prices.append(float(record["SpotPrice"]))

timestamps = list(reversed(timestamps))
prices = list(reversed(prices))
	
life_time = []

start_date = None
skip_date = ""
#i = len(prices)-1
avg_list = []
for bid in bid_list:
	for i in range(0, len(prices)):
		time, price = timestamps[i], prices[i]
		#print timestamps[i], prices[i]
		td = parser.parse(time)

		if skip_date == str(td).split(" ")[0]:
			#print "here"
			continue

		if start_date == None:
			start_date = td
			#print start_date

		if start_date.day != td.day:
			#print start_date.day, td.day
			mins = getmins(start_date, td)
			#life_time.append(str((str(mins), str(start_date))))
			life_time.append(mins)
			start_date = td
		
		if price > bid or i+1 == len(prices):
			mins = getmins(start_date, td)
			#life_time.append(str((str(mins), str(start_date))))
			life_time.append(mins)
			skip_date = str(start_date).split(" ")[0]
			start_date = None
	
	sumn, avg = sum(life_time), 0
	avg = sumn/len(life_time)
	avg_list.append(str(avg))
	
with open(in_prefix+"_avg_lt", 'w') as outfile:
	outfile.write("\n".join(avg_list))	
