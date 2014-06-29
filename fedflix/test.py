#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, re, string
import urllib, urllib2, simplejson
import MySQLdb
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
		self.template = Template(filename='/home/aude/fedflix/templates/index.phtml')
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

	collection = Collection(json)
	output = ''

        for collectionItem in collection.collection:
        	item = Item(collectionItem)
		query = '''
	       		/* fedflix.py SLOW_OK */
			SELECT * FROM fedflix WHERE arcid = %s;''' % (item.arc)
		try:
			cursor.execute(query)
		except:
			pass

		if (cursor.rowcount == 0): 
			query = '''
		        	/* fedflix.py SLOW_OK */
				INSERT INTO fedflix (arcid, title) VALUES(%s, '%s');''' % (item.arc, item.title.replace("'", "''"))
			try:
				cursor.execute(query)
			except:
				pass

			conn.commit()

	query = '''
		/* fedflix.py SLOW_OK */
		SELECT * FROM fedflix ORDER BY arcid;
		'''
	cursor.execute(query)

	output = ''
	for row in cursor.fetchall():
		output += "<tr><td>%s</td><td>%s</td></tr>" % (row[2], row[1])  

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
	output = "<table id='itemlist'>"
	output += "<thead><tr class='rowheader'><td>Title</td><td>ARC</td></tr></thead><tbody>"
	output += query(page)
	output += "</tbody></table>"
	return output

def main(args):
	print generateOutput(1)

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
