#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, os, re, string
import urllib, urllib2, simplejson
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

def download(identifier):
        download_dir = '/home/aude/data/uploads/fedflix/'
	download_link = 'http://www.archive.org/download/gov.archives.arc.%s/gov.archives.arc.%s.ogv' % (identifier, identifier)
	file_save = '%sgov.archives.arc.%s.ogv' % (download_dir, identifier)
	video_file = urllib2.urlopen(download_link)
	output = open(file_save, 'wb')
	output.write(video_file.read())
	output.close()

def main(args):
	filename = identifier = pubdate = description = author = None
	
	for arg in wikipedia.handleArgs(*args):
		if arg.startswith('-id'):
			identifier = arg[4:]
		if arg.startswith('-filename'):
			filename = arg[10:]
		if arg.startswith('-desc'):
			description = arg[6:]
		if arg.startswith('-author'):
			author = arg[8:]
		if arg.startswith('-date'):
			pubdate = arg[6:]

	if identifier == None:
		identifier = wikipedia.input("Enter identifier: ")
		identifier = "gov.archives.arc.%s" %s (identifier)

	if pubdate == None:
		year = wikipedia.input("Enter year: ")
		day = wikipedia.input("Enter day: ")
		date = "%s, %s" % (day, year)

	if description == None:
		description = wikipedia.input("Enter description: ")

        if filename == None:
                interviewee = wikipedia.input("Enter filename: ")
                filename = "Longines_Chronicles_with_%s_%s_ARC-%s.ogv" % (interviewee, year, identifier)
		filename = filename.replace(" ", "_")
	
	if author == None:
		author = "Longines Wittnauer Watch Company, Inc."

	download(identifier)
	filepath = '/home/aude/data/uploads/fedflix/gov.archives.arc.%s.ogv' % (identifier)
	
	desc = '== {{int:filedesc}} ==\n{{Information\n|description={{en|1=%s}}\n|date=%s\n|source={{FedFlix-source|%s}}\n|author=%s\n|permission=See below}}\n\n== {{int:license}} ==\n{{PD-US-Longines}}' % (description, pubdate, identifier, author)
	print 'Uploading %s as %s' % (filepath, filename)
#	bot = upload.UploadRobot(url=filepath, description=desc, useFilename=filename, keepFilename=True, verifyDescription=False)
#	bot.run()
	os.remove(filepath)

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
