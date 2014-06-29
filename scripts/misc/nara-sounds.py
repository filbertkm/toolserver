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

class Metadata:
	def __init__(self, xls):
		self.params = {}

class Image:
	def __init__(self, filename):
		self.filename = filename
		self.filelocation = '/home/aude/data/uploads/nara/%s' % (filename)
		self.metadata = {}
		self.template = ''
		self.uploadname = ''

	def upload(self, logfilename, donedir):
		t = Template(self)
		self.template = t.create()
		try:
			print self.template
			print self.filelocation
			uploadname = 'Uncle Sam Calling, Counting the Jobless.ogg'
			self.uploadname = uploadname.replace(' ', '_')
		
			do_upload = wikipedia.input( u'\nContinue uploading %s as %s ?' % (self.filename, self.uploadname) )
			if (do_upload == 'y'):
				time.sleep(120)
				print 'Uploading %s' % (self.uploadname)
				site = wikipedia.getSite(u'commons', u'commons')
				wikipedia.setSite(site)
				bot = upload.UploadRobot(url=self.filelocation, description=self.template, useFilename = self.uploadname, keepFilename = True, verifyDescription=False)
				bot.run()
#				logfile = open(logfilename, 'a')
#				logfile.write('%s,uploaded,%s\n' % (self.filename, datetime.today()))
#				logfile.close()
#     		                dst = '%s%s' % (donedir, self.filename)
				dst = '/home/aude/data/uploads/done'
				shutil.move(self.filelocation, dst)
			else:   		
				print u'\nUpload of file %s cancelled.\n\n' % (self.filename)
		except:
			pass

class Template:
	def __init__(self, im):
		self.im = im
		self.template = self.create()

	def create(self):
		template = '''
== {{int:filedesc}} ==
{{NARA-image-full
| Title                   = Uncle Sam Calling: Counting the Jobless, 1937?
| Scope and content       = Subject summary is available. explains and urges response to the National Unemployment Census of 1937, conducted by the Works Progress Administration. Replies from unemployed persons are mechanically sorted and counted at the Bureau.
| General notes           = 
| ARC                     = 7010
| Local identifier        = 29.5
| Creator                 = Department of Commerce. Bureau of the Census. Public Information Office.
| Author                  = 
| Place                   = 
| Location                = Motion Picture, Sound, and Video Records Section, Special Media Archives Services Division (NWCS-M), National Archives at College Park 
| Date                    = 1940
| Record group            = Record Group 29: Records of the Bureau of the Census, 1790 - 2007
| Record group ARC        = 358
| Series                  = Moving Images Relating to the Taking of the Census, 1937 - 1980
| Series ARC              = 7005
| File unit               = 
| File unit ARC           = 
| Variant control numbers = NAIL Control Number: NWDNM(m)-29.5
| TIFF                    = 
| Other versions          = 
}}

== {{int:license}} ==
{{NARA-cooperation}}
{{PD-USGov}}
[[Category:1940 United States Census]]
[[Category:NARA ExtravaSCANza]]
''' 
		return template

def readfiles(dirname, pattern):
 	files = []
	filelist = os.listdir(dirname)
	for i in filelist:
		match = re.search(r'%s' % (pattern), i)
		f = { 'filename' : i }
		files.append(f)
	return files

def main(args):
	dirname = '/home/aude/data/uploads/nara'
	pattern = '(\S+).ogg'
	files = readfiles(dirname, pattern)
	logfilename = '/home/aude/bots/logs/nara.log'
	donedir = '/home/aude/data/uploads/done'

	for f in files:
		print f['filename']
		im = Image(f['filename'])
		try:
			im.upload(logfilename, donedir)
		except:
			pass

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
