#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os.path, re, string
import urllib, simplejson, Image
sys.path.append("/home/aude/src/pywikipedia")
import wikipedia, config, query, upload

def main(args):
	file_path = "/home/aude/data/uploads/nara/The_Wapiti_of_Jackson_Hole_1939_ARC-11729.ogv"
	file_name = "The_Wapiti_of_Jackson_Hole_1939_ARC-11729.ogv"
	desc = "{{subst:User:Aude/NARA}}"
	bot = upload.UploadRobot(url=file_path, description=desc, useFilename=file_name, keepFilename=True, verifyDescription=False)
	bot.run()

if __name__ == "__main__":
	try:
		main(sys.argv[1:])
	finally:
		print "All done!"
