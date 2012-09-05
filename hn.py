import sys
import urllib2
import re
import pymongo
import datetime
import time
DB_SERVER = 'localhost'
DB_PORT = 27017
DB = 'hnusers'
PAGES_BACK = 5 # How many pages back to search by default for each user
THROTTLE = 10

_last_fetch = None
def loadpage(user,more_link=None):
	#return open(user + '.html').read()
	if _last_fetch:
		td = datetime.datetime.now() - _last_fetch	
		if td.total_seconds() < THROTTLE:
			delta = THROTTLE - td.total_seconds()
			print 'sleeping for',delta
			time.sleep(delta)

	url = 'http://news.ycombinator.com/threads?id=' + user
	if more_link:
		url = 'http://news.ycombinator.com/' + more_link.lstrip('/')
	print 'opening',url
	stream = urllib2.urlopen(url)
	txt = stream.read()
	print 'read data'
	stream.close()
	with open(user + '.html','w') as stream:
		stream.write(txt)
	return txt

#exp = re.compile(r'href="user\?.*?<a href="item\?id=(.*?)">link</a>.*?on:\s*<a\s*href="item\?id=(.*?)">(.*?)</a>.*?<span class="comment">(.*?)</span>',re.DOTALL)	
exp = re.compile(r'">link</a>.*?on:\s*<a\s*href="item\?id=(.*?)">(.*?)</a>.*?<span class="comment">(.*?)</span>',re.DOTALL)	
fse = re.compile(r'<font.*?>(.*)</font>')
more_exp = re.compile(r'href="(/x\?fnid=.*?)" rel="nofollow">More<',re.DOTALL)
def parsepage(content):
	print 'parsing 1',len(content)
	all = exp.finditer(content)
	print 'parsing 2'
	more_links = more_exp.findall(content)
	more_link = None
	print 'parsing 3'
	if more_links: more_link = more_links[0]
	print 'done parsing'
	comments = []
	for m in all:
		url,title,comment = m.groups()
		start_pos = m.start()
		comment_link = content[start_pos-7:start_pos]
		x = fse.findall(comment)
		if x:
			comment = x[0]

		comments.append((url,title,comment,comment_link))
	return comments,more_link

def usercomments(user):
	content = loadpage(user)
	return parsepage(content)

def connection():
	return pymongo.Connection(DB_SERVER,DB_PORT)[DB]


def updateuser(user):
	db = connection()
	more_link = None
	for i in range(PAGES_BACK):
		print 'fetching page',i
		content = loadpage(user,more_link)
		comments,more_link = parsepage(content)
		print 'found',len(comments),'comments'
		can_stop = False
		for url,title,comment,comment_link in comments:
			uc = {'comment_link':comment_link,'title_link':url,'title':title,'comment':comment,'user':user}
			uc['date'] = datetime.datetime.now()
			existing =db.users.find_one({'user':user,'comment_link':comment_link})
			if existing: 
				print 'exists',comment[:10]
				can_stop = True
				continue
			db.users.insert(uc)
		if can_stop or not more_link: break
#commentmap = {}
#def loaduser(user):
	#content = loadpage(user)
	#for url,title,comment,comment_link in parsepage(content):
		#x = commentmap.setdefault(url,{})
		#x['title'] = title
		#x.setdefault('comments',[]).append( (user,comment,comment_link))
	#
#loaduser('tptacek')
#loaduser('patio11')
#loaduser('pg')
#loaduser('anigbrowl')
#loaduser('raganwald')
#
#for url,data in commentmap.items():
	#print url,data['title']
	#for user,comment,comment_link in data['comments']:
		#print user,':','http://news.ycombinator.com/' + comment_link,comment
	#print ' '
#
#