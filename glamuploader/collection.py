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

class Collection:
	def __init__(self, filename, xls):
		self.filename = filename
		self.categories = []
		self.original = None
		self.metadata = {}
		self.transformMetadata(xls)

	def transformMetadata(self, xls):
		translation = {
			'id' : 'id',
			'artist' : 'CreatorPersonName',
			'description' : 'ItemNote',
			'date' : 'DisplayDate',
			'dimensions' : 'ItemSize',
			'medium' : 'ItemSpecificFormat',
			'source' : 'ItemCaption',
			'url' : 'Url',
			'title' : 'ItemTitle'
		}

		for i in xls:
			if (i['RepresentativeImageFile'] == self.filename):
				self.original = i

				for k,v in translation.items():
					self.metadata[k] = self.original[v]

				if (isinstance(self.metadata['id'], float)):
					self.metadata['id'] = int(self.metadata['id'])
	
				if (self.metadata['artist'] == "(null)"):
					self.metadata['artist'] = ''

				self.metadata['dateformat'] = 'plain'
				print self.metadata['date']
				d = self.parseDate(self.metadata['date'])
				strdate = self.date2Template(d)
				self.metadata['date'] = strdate

				self.parseSize(self.metadata['dimensions'])

				self.metadata['technique'] = self.parseMedium(self.metadata['medium'])
				self.metadata['source'] = self.parseSource(self.metadata['source'])
			
				self.filelocation = '/home/aude/data/aaa/%s' % (self.filename)
				self.uploadname = 'Archives_of_American_Art_-_%s_-_%s.jpg' % (self.metadata['title'], self.metadata['id'])
				self.categorize()
				self.isDuplicate = False

				# template
				t = Template(self)
				self.template = t.template

	def findDuplicateImages(self, photo = None, site = wikipedia.getSite(u'commons', u'commons')):
	        '''
	            Takes the photo, calculates the SHA1 hash and asks the mediawiki api for a list of duplicates.
	            TODO: Add exception handling, fix site thing
	        '''
	        hashObject = hashlib.sha1()
	        hashObject.update(photo.getvalue())
	        return site.getFilesFromAnHash(base64.b16encode(hashObject.digest()))

	def categorize(self):
		self.categories = ['Federal Art Project, Photographic Division']

	def parseDate(self, d):
		print d
		d = d.replace('Apr.', 'Apr')
		d = d.replace('July', 'Jul')
		d = d.replace('June', 'Jun')
		d = d.replace('Sept', 'Sep')

		self.metadata['circa'] = False
	
		formats = ["%Y %b %d", "%Y", "%d %b %Y", "%Y %b"]

		match = re.search("ca. (\d+)", d)
		if match:
			self.metadata['circa'] = True
			self.metadata['dateformat'] = 'circa'
			d = match.group(1)

		for f in formats:
			try:
				t = datetime.strptime(d.replace('.',''), f)
				self.metadata['dateformat'] = 'iso'
				return t
			except ValueError:
				pass

		return d

	def date2Template(self, d):
		if (self.metadata['dateformat'] == 'circa'):
			dateTemplate = '{{other date|ca|%s}}' % (d.strftime("%Y"))
		elif (self.metadata['dateformat'] == 'iso'):
			dateTemplate = '{{ISOdate|%s}}' % (d.strftime("%Y-%m-%d"))
		else:
			dateTemplate = d

		return dateTemplate

	def parseMedium(self, m):
		formats = [{'photographic print' : 'photograph'}]

		for f in formats:
			for k,v in f.iteritems():
				if (k == m):
					return '{{technique|%s}}' % (v)
					
		return m

	def parseSize(self, size):
                self.metadata['dimensions-units'] = None
                self.metadata['dimensions-height'] = None
		self.metadata['dimensions-width'] = None
		
		try: 
			if ( (size is not None) and (size.__len__() > 0) ):
				print size
				match = re.search(r'(\d+)\s+x\s+(\d+)\s+([\w]+)', size)
	
				self.metadata['dimensions-units'] = match.group(3)
				self.metadata['dimensions-height'] = match.group(2)
				self.metadata['dimensions-width'] = match.group(1)
		except:
			pass

	def parseSource(self, s):
		source = s.replace('Federal Art Project', '[http://www.aaa.si.edu/collections/federal-art-project-photographic-division-collection-5467 Federal Art Project]')
		source = source.replace('Archives of American Art', '[http://www.aaa.si.edu Archives of American Art]')
		return source
	
	def printCats(self):
		cats = ''
		for i in self.categories:
			cats += '\n[[Category:%s]]' % (i)
		return cats

	def upload(self, logfilename, donedir):
		try:
			print self.template
	#		p = wikipedia.Page(wikipedia.getSite(u'commons', u'commons'), 'User:Aude/sandbox2')
	#		p.put(self.template, 'AAA-image template, tests')
		
#			do_upload = wikipedia.input( u'\nContinue uploading %s ?' % (self.uploadname) )
#			if (do_upload == 'y'):
			time.sleep(120)
			print 'Uploading %s' % (self.uploadname)
			site = wikipedia.getSite(u'commons', u'commons')
			wikipedia.setSite(site)
			bot = upload.UploadRobot(url=self.filelocation, description=self.template, useFilename = self.uploadname, keepFilename = True, verifyDescription=False)
			bot.run()
			logfile = open(logfilename, 'a')
			logfile.write('%s,uploaded,%s\n' % (self.filename, datetime.today()))
			logfile.close()
       	                dst = '%s%s' % (donedir, self.filename)
			shutil.move(self.filelocation, dst)
#			else:   		
#				print u'\nUpload of image %s cancelled.\n\n' % (self.filename)
		except:
			pass

class Template:
	def __init__(self, im):
		self.im = im
		self.template = self.create()

	def create(self):
		template = '''
== {{int:filedesc}} ==
{{AAA-image
|Photographer=%s
|Title=%s
|Description={{en|%s}}
|Date=%s
|Medium=%s
|Dimensions={{size|units=%s|height=%s|width=%s}}
|id=[%s %s]
|source={{en|%s}}
|permission=See below
}}

== {{int:license}} ==
{{PD-USGov-WPA}}
{{AAA-cooperation}}
%s
''' % (self.im.metadata['artist'], self.im.metadata['title'], self.im.metadata['description'], self.im.metadata['date'], self.im.metadata['technique'], self.im.metadata['dimensions-units'], self.im.metadata['dimensions-height'], self.im.metadata['dimensions-width'], self.im.metadata['url'], self.im.metadata['id'], self.im.metadata['source'], self.im.printCats())
		return template

def readxls(filename):
	wb = xlrd.open_workbook(filename)
	sh = wb.sheet_by_index(0)
	rows = []
	row = {}
	colnames = []
	for col in sh.row_values(0):
		colnames.append(col)
	for rownum in range(sh.nrows):
		row = {}
		if (rownum > 0):
			count = 0
			for i in sh.row_values(rownum):
				row[colnames[count]] = i
				count += 1
			rows.append(row)
	return rows

def readfiles(dirname, pattern):
 	files = []
	filelist = os.listdir(dirname)
	for i in filelist:
		match = re.search(r'%s' % (pattern), i)
		f = { 'id' : match.group(2), 'filename' : i }
		files.append(f)
	return files

def main(args):
	dirname = '/home/aude/data/aaa'
	pattern = 'AAA_fedeartp(\d+)_(\d+).jpg'
	files = readfiles('/home/aude/data/aaa', pattern)
	xlsfilename = '/home/aude/bots/Wikipedia_Contribution_FAP.xls'
	logfilename = '/home/aude/bots/logs/aaa.log'
	donedir = '/home/aude/data/uploaded/'

	xls = readxls(xlsfilename)

	for f in files:
		print f['filename']
		im = Image(f['filename'], xls)
#		try:
		im.upload(logfilename, donedir)
#		except:
#			pass

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
