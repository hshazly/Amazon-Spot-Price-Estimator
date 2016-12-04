#!/usr/bin/python
import config
import os, MySQLdb, subprocess, random, json
from mod_python import util,Cookie,apache


def connectToDB():
	#Host=config.DBHost
	Host=config.usersDBhost
	#Port=int(config.DBPort)
	Port=int(config.usersDBport)
	#Database=config.DB
	Database=config.usersDB
	#Username=config.DBUserName
	Username=config.usersDBun
	#Password=config.DBPassword
	Password=config.usersDBpwd
	#raise Exception(Host, Port, Database, Username, Password)
	db = MySQLdb.connect(host=Host, port=Port, user=Username, passwd=Password,db=Database)
	return db	

def _insert(st):
	db = connectToDB()
	cursor = db.cursor()
	cursor.execute(st)
	db.commit()
	cursor.close()
	db.close()

#Use to get ID of registered users only
def getUserUid(req):
	c = Cookie.get_cookies(req).get("mart.Login",None)
	global uid
	if (c):
		uid = c.value
		return uid
	else:
		return None
	
	
