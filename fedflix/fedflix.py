#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, re, string
import urllib, urllib2, simplejson
import MySQLdb
import csv
from cgi import escape, parse_qs, FieldStorage
from flup.server.fcgi import WSGIServer
from mako.template import Template

class Item:
	def __init__(self,json):
		self.identifier = json['identifier']
		self.title = json['title'].title()
		self.creator = json['creator']
		self.arc = self.identifier.lstrip('gov.archives.arc.')

class Collection:
	def __init__(self,json):
		self.title = u'FedFlix'
		self.collection = json['response']['docs']

class Handler:
	def __init__(self, env, start_response):
		self.env = env
		self.start_response = start_response
		self.params = parse_qs(self.env['QUERY_STRING'])

	def render(self):
		self.template = Template(filename='/home/aude/fedflix/templates/csv.phtml')
		if (self.params.get('p')):
			page = int(self.params.get('p')[0])

		else:
			page = 1
		output = self.template.render_unicode( env=self.env, content=generateOutput(page) )
		return output.encode( "utf-8" )

def cacheResults(json):
        conn = MySQLdb.connect(
                db = "u_aude",
                host = "sql.toolserver.org",
                read_default_file = os.path.expanduser("~/.my.cnf")
        )
        cursor = conn.cursor()

	output = ''

	query = '''
		/* fedflix.py SLOW_OK */
		SELECT DISTINCT arcid FROM fedflix ORDER BY arcid;
		'''
	cursor.execute(query)

	output = ''
	for row in cursor.fetchall():
		output += "http://www.archive.org/details/gov.archives.arc.%s,%s\n" % (row[0], row[0])  

	cursor.close()
	conn.close()

	return output

def query(page):
	#url = 'http://www.archive.org/advancedsearch.php'
	#params = { 'q' : 'collection:FedFlix',
#		   'fl' : 'identifier,creator',
#		   'rows' : 2500,
#		   'page' : page,
#		   'callback' : 'callback',
#		   'output' : 'json'
#		   }
	#data = urllib.urlencode(params)
	#req = urllib2.Request(url, data)
	#response = urllib2.urlopen(req)
	f = open('/home/aude/fedflix/results.json')
	json = simplejson.loads(f.read())
	#response.read().lstrip('callback(').rstrip(')'))
	results = cacheResults(json)
	return results

def generateOutput(page, format='html'):
	output = ''
	output += query(page)
	return output

def main(args):
	print generateOutput(1)

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
