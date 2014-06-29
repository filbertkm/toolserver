#!/usr/bin/python
# -*- coding: utf-8  -*-
import sys, os
sys.path.append("/home/aude/src/pywikipedia")
import datetime
import wikipedia, query, userlib

Site = wikipedia.getSite()

def numEdits(user):
  return true

def lastEdit(user):
  predata = {
    'action' : 'query',
    'list': 'usercontribs',
    'uclimit': '1',
    'ucuser': user,
  }
  data = query.GetData(predata, Site)
  print datetime.datetime.now()
  return data

def getRecipients():
  users = []
#  invitelist = wikipedia.Page(Site, 'Wikipedia:Meetup/Baltimore/Invite/List')
  invitelist = wikipedia.Page(Site, 'User:Aude/Invitelist')
  for userpage in invitelist.linkedPages():
    if (userpage.namespace() == 2):
      username = userpage.titleWithoutNamespace()
      if (userpage.isRedirectPage()):	    
        target = userpage.getRedirectTarget()
	userpage = wikipedia.Page(Site, target)
	username = username = userpage.titleWithoutNamespace()
      try:
        user = userlib.User(Site, username)
	edit = lastEdit(username)
	editTime = edit['query']['usercontribs'][0]['timestamp']
	users.append(  { 'user' : user , 'username' : username, 'last' : editTime } )
      except:
        print u'error on %s' % (username)
  return users

def deliver(user):
  print u'Deliver'

def main(args):
  newsletter = wikipedia.Page(Site, 'User:Aude/Invite').get()
  recipients = sorted(getRecipients(), key=lambda k: k['last'], reverse=True)
  for user in recipients:
    print '%s - %s' % (user['username'], user['last'])

if __name__ == "__main__":
  try:
    main(sys.argv[1:])
  finally:		       
    print u'All done'
