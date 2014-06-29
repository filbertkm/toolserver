#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os, shutil
import re, string, math
import hashlib, base64
import urllib, urllib2, simplejson
from datetime import datetime
import string, StringIO
import xlrd
sys.path.append("/home/filbertkm/src/pywikipedia")
import wikipedia, config, query, upload

class Metadata:
	def __init__(self, xls):
		self.params = {}

class Image:
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
			'caption' : 'ItemCaption',
			'date' : 'DisplayDate',
			'dimensions' : 'ItemSize',
			'medium' : 'ItemSpecificFormat',
			'notes' : 'ItemNote',
			'source' : 'Url',
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

				d = self.parseDate(self.metadata['date'])
				strdate = self.date2Template(d)
				self.metadata['date'] = strdate

				self.parseSize(self.metadata['dimensions'])

				self.filelocation = '/home/sarah/images/%s' % (self.filename)
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
		self.metadata['circa'] = False
	
		formats = ["%Y %b %d", "%Y"]

		match = re.search("ca. (\d+)", d)
		if match:
			self.metadata['circa'] = True
			d = match(1)

		print d

		for f in formats:
			try:
				t = datetime.strptime(d.replace('.',''), f)
				return t
			except ValueError:
				pass

		raise ValueError()

	def date2Template(self, d):
		print type(d)
		if (self.metadata['circa']):
			dateTemplate = '{{other data|ca|%s}}' % (d.strftime("%Y"))
		else:
			dateTemplate = '{{ISOdate|%s}}' % (d.strftime("%Y-%m-%d"))
		return dateTemplate

	def parseSize(self, size):
		match = re.search(r'(\d+) x (\d+) (\w+)', size)

		self.metadata['dimensions-units'] = match.group(3)
		self.metadata['dimensions-height'] = match.group(2)
		self.metadata['dimensions-width'] = match.group(1)
	
	def printCats(self):
		cats = ''
		for i in self.categories:
			cats += '\n[[Category:%s]]' % (i)
		return cats

	def upload(self, logfilename, donedir):
		print self.template
#		p = wikipedia.Page(wikipedia.getSite(u'commons', u'commons'), 'User:Aude/sandbox2')
#		p.put(self.template, 'AAA-image template, tests')

		do_upload = wikipedia.input( u'\nContinue uploading %s ?' % (self.uploadname) )
		if (do_upload == 'y'):
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
		else:   		
			print u'\nUpload of image %s cancelled.\n\n' % (self.filename)

class Template:
	def __init__(self, im):
		self.im = im
		self.template = self.create()

	def create(self):
		template = '''
== {{int:filedesc}} ==
{{AAA-image
|Artist=%s
|Title=%s
|Author=
|Creator=
|Description={{en|
{{Original caption|%s}}
}}
|Date=%s
|Medium=%s
|Dimensions={{size|units=%s|height=%s|width=%s}}
|Location=
|references=
|object history=
|credit line=
|notes={{en|%s}}
|id=%s
|collection={{en|%s}}
|source=%s
|permission=See below
}}

== {{int:license}} ==
{{PD-USGov-WPA}}
{{AAA-cooperation}}
%s
''' % (self.im.metadata['artist'], self.im.metadata['title'], self.im.metadata['caption'], self.im.metadata['date'], self.im.metadata['medium'], self.im.metadata['dimensions-units'], self.im.metadata['dimensions-height'], self.im.metadata['dimensions-width'], self.im.metadata['notes'], self.im.metadata['id'], "[http://www.aaa.si.edu/collections/federal-art-project-photographic-division-collection-5467 Federal Art Project, Photographic Division collection], circa 1920-1965, bulk 1935-1942", self.im.metadata['source'], self.im.printCats())
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
	do_upload = False

	dirname = '/home/sarah/images'
	pattern = 'AAA_fedeartp(\d+)_(\d+).jpg'
	files = readfiles('/home/sarah/images', pattern)
	xlsfilename = '/home/filbertkm/bots/Wikipedia_Contribution_FAP.xls'
	logfilename = '/home/filbertkm/bots/logs/aaa.log'
	donedir = '/home/sarah/uploaded/'

	xls = readxls(xlsfilename)

	for f in files:
		im = Image(f['filename'], xls)
		im.upload(logfilename, donedir)

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
