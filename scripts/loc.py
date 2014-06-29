#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, re, string
import urllib, simplejson, Image
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

class Collection:

	def __init__(self, term):
		query = urllib.urlencode({'co' : term})
		url = 'http://www.loc.gov/pictures/search/?sp=1&%s&c=500&fo=json' % (query)
		search_result = urllib.urlopen(url)
		self.json = simplejson.loads(search_result.read())
		self.title = self.json['collection']['title']
		self.link = self.json['collection']['link']

	def getItems(self):
		for item in self.json['results']:
			photo = Photo(item, self)

class Photo:
	
	def __init__(self, item, collection):
		self.item = item
		self.collection = collection
		self.downloadFile = False
		self.saveDir = '/home/aude/data/uploads/'
		self.baseTitle = 'Ansel_Adams_Manzanar'
		self.getMetadata()

		if self.downloadFile:
			print('fetching %s' % (self.tiffName))
			cont = raw_input('Download (y) or (n)? ')
			if cont == 'y':
				print ''
				self.download()
				self.convert()
				self.upload()
			elif cont == 'x':
				sys.exit()

	def photoExists(self, ppprs):
		tiffName = '%su.tif' % (ppprs)
		tiffPath = '%s%s' % (self.saveDir, tiffName)
		return os.path.isfile(tiffPath)

	def getMetadata(self):
		if (re.search('photograph', self.item['medium'])):
			b = os.path.basename(self.item['image']['full'])
			baselink = self.item['image']['full'].split(b)
			parts = b.split('r.')
			self.ppprs = parts[0]
			self.tiffName = '%su.%s' % (parts[0],'tif')
			self.tiffUrl = '%s%s' % (baselink[0],self.tiffName)
			self.caption = self.item['title']
			print self.generateTitle()
			if self.photoExists(self.ppprs):
				print '%s photo exists' % (self.ppprs)
			else:
				self.downloadFile = True

	def download(self):
		tiffDownload = urllib.urlopen(self.tiffUrl)
		self.tiffPath = '%s%s' % (self.saveDir, self.tiffName)
		tiffFile = open(self.tiffPath, 'w')
		print('saving %s' % (self.tiffName))
		tiffFile.write(tiffDownload.read())
		tiffFile.close()
		tiffDownload.close()

	def generateTitle(self):
		desc = self.caption[0 : 50]
		title = '%s_-_%s_-_LOC_ppprs-%s.jpg' % (self.baseTitle, desc, self.ppprs)
		return title

	def convert(self):
		self.jpgName = self.generateTitle()
		self.jpgPath = '%s%s' % (self.saveDir, self.jpgName)
		print 'converting from %s to %s' % (self.tiffName,self.jpgName)
		jpgFile = open(self.jpgPath, 'w')
		try:
			Image.open(self.tiffPath).save(jpgFile)
		except IOError:
			print 'cannot convert file'

	def generateDescription(self):
		desc = "{{subst:User:Aude/Manzanar |collection_link=%s |collection_title=%s |id=%s |caption=%s |date=1943}}" % (self.collection.link, self.collection.title, self.ppprs, self.caption)
		return desc

	def upload(self):
		desc = self.generateDescription()
		bot = upload.UploadRobot(url=self.jpgPath, description=desc, useFilename=self.jpgName, keepFilename=True, verifyDescription=False)
		bot.run()

def main(args):
	collection_term = u''

	for arg in wikipedia.handleArgs(*args):
		if arg.startswith('-collection'):
			collection_term = arg[12:]
		
	if (len(collection_term) < 1):
		print 'no collection term specified'
		sys.exit()

	collection = Collection(collection_term)
	collection.getItems()

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
