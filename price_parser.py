#!/usr/bin/python
import sys
import json
import time, datetime
import csv
import random
import statistics
from dateutil import parser
from datetime import datetime, timedelta


def getmins(start_date, td):
	timediff = td - start_date
	min_tuple = divmod(timediff.days * 86400 + timediff.seconds, 60)
	mins = min_tuple[0]
	
	if min_tuple[1] > 0:
		mins = mins + min_tuple[1]/60
		
	return mins	


def parse(aws_spot_history, bid):
	#aws_spot_history = sys.argv[1]
	#bid = float(sys.argv[2])

	with open(aws_spot_history) as infile:
		data = json.load(infile)

	datalist = data["SpotPriceHistory"]	
	length = len(datalist)

	prices = []
	timestamps = []
	for record in datalist:
		mytime = record["Timestamp"].replace('T', ' ')
		mytime = mytime.replace('Z', '')
		mytime = mytime.split("2016-")[1]
		mytime = mytime.split(".000")[0]
		timestamps.append(mytime)
		prices.append(float(record["SpotPrice"]))

	#SORT FROM OLD TO RECENT DATES
	timestamps = list(reversed(timestamps))
	prices = list(reversed(prices))

	#LIST OF (TIMESTAMP, PRICE)
	return prices, timestamps


def calculate(prices, timestamps):
        ordered = []

        x = len(timestamps)
        for i in range(0, x):
                ordered.append((timestamps[i],prices[i]))

        avg_lifetime = 0
        start_date = 0
        lifetime_list = []

        for itr1 in range(0, len(ordered)):
                current_date = parser.parse(ordered[itr1][0])
                current_bid = ordered[itr1][1]

                #start_date = 0 MEANS 1st ITERATION OR SEARCH FOR INITIALIZATION VALUE
                if start_date == 0 and current_bid <= bid:
                        start_date = parser.parse(ordered[itr1][0])
                        continue

                #CALCULATE IF CONDITION IS VIOLATED OR YOU REACHED EOF
                if ((start_date != 0) and current_bid > bid) or itr1 == len(ordered)-1:
                        if itr1 == len(ordered)-1 and start_date == 0:
                                lifetime = 0
                        else:
                                lifetime = getmins(start_date, current_date)
                                #t_range.append((str(bid) + "=="+ str(lifetime) +" = "+ str(start_date), str(current_date)))
                                lifetime_list.append(lifetime)
                                start_date = 0


        if len(lifetime_list) != 0:
                avg_lifetime = sum(lifetime_list)/len(lifetime_list)
        else:
                avg_lifetime = 0

        return avg_lifetime

