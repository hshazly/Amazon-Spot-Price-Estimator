#! /usr/bin/python
import os, MySQLdb,subprocess,random,simplejson,time
import json
#from mod_python import util,Cookie,apache
from datetime import datetime, timedelta
#from price_parser import parse_and_calculate
import price_parser
import scipy.interpolate

def index():
	return "Hello"

def redirect(url,req):
	  util.redirect(req,  url)

def execute(command, silent=False, wait=True, stdout=False):
	PIPE = subprocess.PIPE
	p = subprocess.Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
	if wait:
		p.wait()

	if(not silent):
		st = p.stderr.read()
		if(len(st) > 0):
		   return "ERROR: " + st
		   #raise Exception("ERR: " + st)
	
        if(stdout):
		return p.stdout.read()

def interpolate(instance_type, bid):
	#avg_file = "/var/www/mcgk/tmp/calculator/{0}".format(instance_type+"_avg_lt")
	#bid_file = "/var/www/mcgk/tmp/calculator/{0}".format(instance_type+".price")
	avg_file = instance_type+"_avg_lt"
	bid_file = instance_type+".price"
	yvalue = 0.0
	avg_list = []
	bid_list = []
	bid = float(bid)
	index = 0
		
	with open(avg_file) as fh:
		lines1 = fh.readlines()

	with open(bid_file) as fh:
		lines2 = fh.readlines()
	
	for line in lines1:
		avg_list.append(float(line.strip()))
	for line in lines2:
		bid_list.append(float(line.strip()))

	if bid < min(bid_list):
		for bid_entry in bid_list:
			if bid_entry == min(bid_list):
				index = bid_list.index(bid_entry)
				break
		
		yvalue = (bid * avg_list[index])/bid_list[index]
	elif bid > max(bid_list):
		for bid_entry in bid_list:
			if bid_entry == max(bid_list):
				index = bid_list.index(bid_entry)
				break

		yvalue = (bid * avg_list[index])/bid_list[index]
	else:
		y_interp = scipy.interpolate.interp1d(bid_list, avg_list)
		yvalue = y_interp(bid)


	#raise Exception(yvalue)
	sec = yvalue * 60
	sec = timedelta(seconds=int(sec))
	d = datetime(1,1,1) + sec
	
	#ondemand_price = get_ondemand_price(instance_type)
	#result = {"exp_lt":"%d day, %d hour, %d minute, %d second" % (d.day-1, d.hour, d.minute, d.second), "ondemand_price":ondemand_price}
	result = "%d day, %d hour, %d minute, %d second" % (d.day-1, d.hour, d.minute, d.second)
	return result
	#return round(yvalue, 2)


def get_ondemand_price(instance_type):
	price_file = "/var/www/mcgk/templates/instances_prices"

	prices = {}

	with open(price_file) as fh:
		prices = json.load(fh)

	return prices[instance_type]

def calc(req):
    instance_type = req["instance"]
    bid = float(req["bid"])
    zone = req["zone"]

    import random
    rand=random.randint(1,1000000000000)
   
    working_dir = os.path.join("calculator", str(rand))
    cmd = "mkdir -p {0}".format(working_dir)
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    #raise Exception(out, err)	

    os.chdir(working_dir)
    #os.system("rm spot-* *.price")

    #price_history_file = "spot-{0}.txt".format(instance_type) #AUTOMATIC
    price_history_file = "history_db/{0}".format(instance_type+"-"+zone)

    #aws_cmd = "aws ec2 describe-spot-price-history --instance-types \"{0}\" --product-descriptions \"Linux/UNIX\" --availability-zone \"{1}\" > {2}".format(instance_type, zone, price_history_prefix)
    #raise Exception(aws_cmd)
    #print aws_cmd
    #st = execute(aws_cmd)
    #if type(st) == "string" and "ERROR" in st:
	#return st

    lines_num = execute("wc -l {0}".format(price_history_file), stdout=True)
    #raise Exception(lines_num)
    if int(lines_num.split()[0]) <= 3 or int(lines_num.split()[0]) == 0:
       return "NA"	

    #prepare_bid_list = "python /var/www/mcgk/py/price_parser.py {0} {1}".format(price_history_prefix, instance_type)
    #execute(prepare_bid_list)

    #cal_avg_lt = "python /var/www/mcgk/py/spot_life_time.py {0} {1}.price".format(instance_type, instance_type)
    #raise Exception(cal_avg_lt)
    #print cal_avg_lt
    #execute(cal_avg_lt)
    #avg_lt = parse_and_calculate(price_history_file, bid)
    prices, timestamps = parse(price_history_file, bid)
    avg_lt = calculate(price_history_file)

    sec = avg_lt * 60
    sec = timedelta(seconds=int(sec))
    d = datetime(1,1,1) + sec

    #ondemand_price = get_ondemand_price(instance_type)
    #result = {"exp_lt":"%d day, %d hour, %d minute, %d second" % (d.day-1, d.hour, d.minute, d.second), "ondemand_price":ondemand_price}
    result = "%d day, %d hour, %d minute, %d second" % (d.day-1, d.hour, d.minute, d.second)
    #exp_lt = interpolate(instance_type, bid)
    return result

def fetch_instances():
        files = ["/var/www/mcgk/templates/instances_database", "/var/www/mcgk/templates/avail_zones_database"]
        instances = ""
        zones = ""

        for data_file in files:
            lines = []
            with open(data_file) as fh:
                 lines = fh.readlines()

            if "avail_zones" in data_file:
                for line in lines:
                    zones += line.strip()+","
            else:
                for line in lines:
                    instances += line.strip()+","

        #data = {"instances":instances, "zones":zones}  
        #raise Exception(data)
	#raise Exception(instances+"+"+zones)
        return instances+"+"+zones


def fetch_zones(req):
        instances_db = "/var/www/mcgk/templates/avail_zones_database"
        lines = []
        instances = ""
        with open(instances_db) as fh:
                lines = fh.readlines()

        for line in lines:
                instances += line.strip()+","

        #raise Exception(instances)
        return instances

