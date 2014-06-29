#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os, shutil
import re, string, math
import hashlib, base64
import urllib, urllib2, simplejson
import time
from datetime import datetime
import string, StringIO
import xlrd
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

class Client:
	def __init__(self):
		self.apikey = 'wEzaWG7JtF'

	def request(self):
		requrl = 'http://www.brooklynmuseum.org/opencollection/api/?'
		params = { 
			'method' : 'collection.getCollections',
			'version' : '1',
			'api_key' : self.apikey
		}
		res = urllib.urlopen('%s%s' % (requrl, urllib.urlencode(params)))
		return res.read()

def main(args):
	client = Client()
	page = client.request()
	print page

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
