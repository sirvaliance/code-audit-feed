#!/usr/bin/python

import tornado.ioloop
import tornado.web
import tornado.options
import logging

import MySQLdb, argparse, datetime, unicodedata
from PyRSS2Gen import RSS2
from jinja2 import Environment, FileSystemLoader

from common import *
from config import Config
from database import DB
from databaseQueries import DBQ
from repo import Repo
from commit import Commit
from keywordsfilter import *

class RSSHandler(tornado.web.RequestHandler):
	def get(self, keywords):
		commits = DBQ.findByKeywords(keywords)
		
		feed = RSS2(
			title = "Crypto.is Code Audit Feed",
			description = "Just a thing, right?",
			link = "https://crypto.is",
			lastBuildDate = datetime.datetime.utcnow()
			)
			

		for c in commits:
			feed.items.append(c.toRSSItem())
		
		self.set_header('Content-Type', 'application/rss+xml')
		
		xml = feed.to_xml()
		self.write(xml)
		return

env = Environment(loader=FileSystemLoader(Config.fsdir + 'templates'))
class CommitHandler(tornado.web.RequestHandler):
	def get(self, project, uniqueid):
		commit = DBQ.findByIDs(project, uniqueid)
		if len(commit) > 1:
			raise "More than one commit returned?"
		if not commit:
			self.write("Could not find commit")
			return
		commit = commit[0]		

		template = env.get_template('commit.html')
		html = template.render(commit=commit)	
		
		self.write(html)
		return

application = tornado.web.Application([
    (r"/rss/(.*)", RSSHandler),
    (r"/commit/(.*)/(.*)", CommitHandler),
])
tornado.options.parse_command_line() 

if __name__ == "__main__":
	tlog = logging.FileHandler(Config.logfile)
	logging.getLogger().addHandler(tlog)
	logging.debug('Starting up...')
	
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()

		
		
