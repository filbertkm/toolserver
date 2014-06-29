#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os
import re, string
import hashlib, base64
import urllib, urllib2, simplejson
from datetime import datetime
import string, StringIO
sys.path.append("/home/aude/src/pywikipedia")
from BeautifulSoup import BeautifulSoup
import wikipedia, config, query, upload

class Site:
	def __init__(self):
		self.name = u'Visual Information Gallery'
		self.publisher = u'United States Coast Guard'
		self.url = u'http://cgvi.uscg.mil/media/'
		self.license = u'PD-USGov-DHS-CG'

class Gallery: 
	def __init__(self, id):
		self.id = id 
		self.site = Site()
		self.maxPages = self.maxPages()
		self.page = 1
#		self.images = self.getAll()
		self.images = self.getPage(1)

	def maxPages(self):
		base_url = 'http://cgvi.uscg.mil/media/main.php?g2_itemId=%s' % (self.id)
		self.soup = BeautifulSoup(urllib.urlopen(base_url))
		lastlink = self.soup.findAll('div', { 'class' : 'next-and-last no-previous' })[0].findAll('a', { 'class' : 'last'})
		last = re.search(r'main.php\?g2_itemId=(\d+)&g2_page=(\d+)', lastlink[0]['href']).group(2)
		return int(last)

	def getPage(self, page):
		images = []
		keywords = []
		url = 'http://cgvi.uscg.mil/media/main.php?g2_itemId=%s&g2_page=%s' % (self.id, page)
		galleryPage = urllib.urlopen(url)
		self.soup = BeautifulSoup(galleryPage)
		items = self.soup.find('table', id='gsThumbMatrix').findAll('td')
		for i in items:
			if ( i.find('div', { 'class' : 'summary-keyalbum summary' }) is not None ):
				keywords = self.getKeywords(i)
			link = i.find('a')['href']
			images.append(Image(re.search(r'main.php\?g2_itemId=(\d+)', link).group(1), keywords))
		return images

	def getKeywords(self, item):
		keywords = []
		keywordLinks = item.find('div', { 'class' : 'summary-keyalbum summary' }).findAll('a')
		for k in keywordLinks:
			keywords.append(k.contents)
		return keywords

	def getAll(self):
		self.images = []
		for i in range(1, self.maxPages):
			self.images += self.getPage(i)

		print len(self.images)
		return self.images

class Image:
	def __init__(self, id, keywords=None):
		self.id = id
		self.site = Site()
		self.keywords = keywords
		self.categories = []
		self.metadata = {
			'filename' : None,					                        
			'date' : None,
			'description' : None,
                        'author' : None
		}
		self.isDuplicate = False

	def findDuplicateImages(self, photo = None, site = wikipedia.getSite(u'commons', u'commons')):
	        '''
	            Takes the photo, calculates the SHA1 hash and asks the mediawiki api for a list of duplicates.
	            TODO: Add exception handling, fix site thing
	        '''
	        hashObject = hashlib.sha1()
	        hashObject.update(photo.getvalue())
	        return site.getFilesFromAnHash(base64.b16encode(hashObject.digest()))

	def download(self):
		self.photoPageUrl = 'http://cgvi.uscg.mil/media/main.php?g2_itemId=' + str(self.id)
		photoPage = urllib.urlopen(self.photoPageUrl)
		self.parse(photoPage.read())
		self.downloadUrl = 'http://cgvi.uscg.mil/media/main.php?g2_view=core.DownloadItem&g2_itemId=' + str(self.id)
		photo = StringIO.StringIO(urllib.urlopen(self.downloadUrl))
		# TODO
		self.findDuplicateImages(photo)

	def parse(self, html):
		soup = BeautifulSoup(html)

		# description
		self.metadata['description'] = soup.find('p', { 'class' : 'giDescription' }).contents[0]

		# date
		pubdate = soup.find('div', { 'class' : 'date summary' }).contents[0]
		match = re.search(r'(\d+)/(\d+)/(\d+)', pubdate)
		self.metadata['date'] = '%s-%s-%s' % (match.group(3), match.group(1), match.group(2))

		# upload filename
		self.filename = 'US_Coast_Guard_-_%s_-_%s.jpg' % (self.id, string.replace(soup.find('h2').contents[0].strip(), ' ', '_'))
		self.categorize()

	def categorize(self):
		self.categories = ['Files created by the United States Coast Guard with known IDs', 'Hurricane Irene (2011)']
	
	def printCats(self):
		cats = ''
		for i in self.categories:
			cats += '\n[[Category:%s]]' % (i)
		return cats

	def upload(self):
	        t = Template(self, self.site)
	        print t.template

		do_upload = wikipedia.input( u'\nContinue uploading %s ?' % (self.filename) )
		if (do_upload == 'y'):
			print 'Uploading %s' % (self.filename)
			bot = upload.UploadRobot(url=self.downloadUrl, description=t.template, useFilename = string.replace(self.filename, ' ', '_'), keepFilename = True, verifyDescription=False)
			bot.run()
			logfile = open('/home/aude/bots/logs/coastguard.log', 'a')
			logfile.write('%s,%s,uploaded,%s\n' % (self.id, self.filename, datetime.today()))
			logfile.close()
                else:   		
			print u'\nUpload of image %s cancelled.\n\n' % (self.id)

class Template:
	def __init__(self, im, site):
		self.im = im
		self.site = site
		self.template = self.create()

	def create(self):
		if self.im.metadata['description'] == None:
			self.im.metadata['description'] = wikipedia.input("Enter description: ")

		template = '== {{int:filedesc}} ==\n{{Information\n|description={{en|1=%s}}\n|date=%s\n|source=[%s Hurricane Irene Response Efforts] - United States Coast Guard, Visual Information Gallery \n|author=%s\n|permission=See below}}\n\n== {{int:license}} ==\n{{PD-USGov-DHS-CG}}\n%s' % (self.im.metadata['description'], self.im.metadata['date'], self.im.photoPageUrl, self.site.publisher, self.im.printCats())
		return template

def main(args):
	do_upload = False

	for arg in wikipedia.handleArgs():
		if arg.startswith('-photo_id'):
			photo_id = arg[10:]
		if arg.startswith('-gallery'):
		        gallery_id = arg[9:]

	gallery = Gallery(gallery_id)
	for im in gallery.images:
		im.download()
		im.upload()

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
