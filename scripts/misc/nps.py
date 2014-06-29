#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os, re, string
import urllib, urllib2, simplejson, string
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

def getFiles(pathname):
	fileList = [('%s' % (os.path.normcase(f)))
			for f in os.listdir(pathname)]
	return fileList

class Image:
	
	def __init__(self, f, p):
		self.filename = f
		self.filepath = p
		self.metadata = {
			'filename' : None,					                        
			'pubdate' : None,
			'description' : None,
                        'author' : None
		}
		self.setMetadata()

	def setMetadata(self):
 		if self.metadata['description'] == None:
			self.metadata['description'] = wikipedia.input("Enter description: ")

		self.metadata['template'] = '== {{int:filedesc}} ==\n{{Information\n|description={{en|1=%s}}\n|date=23 August 2011\n|source=http://www.nps.gov/wamo/photosmultimedia/index.htm \n|author=National Park Service\n|permission=See below}}\n\n== {{int:license}} ==\n{{PD-USGov-NPS}}\n\n[[Category:2011 Virginia earthquake]]\n[[Category:Washington Monument]]' % (self.metadata['description'])

		print self.metadata['template']

	def upload(self):
		print 'Uploading %s' % (self.filename)
		bot = upload.UploadRobot(url='%s%s' % (self.filepath, self.filename), description=self.metadata['template'], useFilename = string.replace(self.filename, ' ', '_'), keepFilename = True, verifyDescription=False)
		bot.run()

def main(args):
	p = '/home/aude/bots/images/'
	for f in getFiles(p):
		im = Image(f,p)
		im.upload()

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
