#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os
import re, string
import MySQLdb
from datetime import datetime
import string, StringIO
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

def main(args):
	site = wikipedia.getSite(u'en', u'wikipedia')
	page = wikipedia.Page(site, 'User:Aude/Sandbox17')

	templatename = None

	for arg in wikipedia.handleArgs():
		if arg.startswith('-template'):
			templatename = arg[10:]

	report_template = u'''
{| class="wikitable sortable" 
|-
!Num
!Article
|-
%s
|}
'''

	conn = MySQLdb.connect(
		db = "enwiki_p",
		host = "enwiki-p.rrdb.toolserver.org",
		read_default_file = os.path.expanduser("~/.my.cnf")
	)
	cursor = conn.cursor()
	cursor.execute('''
	/* transclusions.py SLOW_OK */
	SELECT p.page_title 
	FROM templatelinks t 
	JOIN page p ON p.page_id = t.tl_from
	WHERE t.tl_title = 'Featured_article' 
	  AND p.page_namespace = 0 
	  AND t.tl_namespace = 10
	LIMIT 5000;
	''')

	i = 0
	output = []
	for row in cursor.fetchall():
		table_row = u'''||%d||[[%s]] 
|-''' % (i, unicode(row[0].replace('_', ' '), 'utf-8'))
		output.append(table_row)
		i += 1

	body = '\n'.join(output)
	pageText = report_template % (body)
	page.put(pageText, 'list of featured articles')

	cursor.close()
	conn.close()

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
