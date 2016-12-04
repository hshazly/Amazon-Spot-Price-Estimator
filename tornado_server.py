#!/usr/bin/python
import json, os, sys, ast, ssh
import tornado.httpserver
import tornado.escape
import tornado.ioloop
import tornado.web
import simulator

###
#http://stackoverflow.com/questions/2099728/how-do-i-send-an-ajax-request-on-a-different-port-with-jquery
###

class GetAWSopts(tornado.web.RequestHandler):
	def get(self):
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

		self.add_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
		self.write(instances+"+"+zones)

class EstimateBid(tornado.web.RequestHandler):
	def get(self):
		req = self.request.uri
		
		#/calc?bid=0.001&instance=t1.micro&zone=us-east-1a
		bid = req.split('&')[0].split("=")[-1]
		instance = req.split('&')[1].split("=")[-1]
		zone = req.split('&')[2].split("=")[-1]
		
		data = {}
		data["bid"] = bid
		data["instance"] = instance
		data["zone"] = zone
		
		response = simulator.calc(data)
		
		self.add_header('Access-Control-Allow-Origin', self.request.headers.get('Origin', '*'))
		self.write(response)
	

application = tornado.web.Application([
	(r"/fetch_instances", GetAWSopts), 
	(r"/calc", EstimateBid)
])

if __name__ == "__main__":
	port = 9000
	application.listen(port)
	tornado.ioloop.IOLoop.instance().start()
