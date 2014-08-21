import webapp2
import urllib2
import json
import base64
import cgi

from google.appengine.ext import ndb
from google.appengine.api import users

class TogglCredential(ndb.Model):
	user = ndb.UserProperty()
	api_token = ndb.StringProperty()
	workspace_id = ndb.IntegerProperty()

MAINPAGE_TEMPLATE = """
	<html>
		<body>
			<h2>Enter your details</h2>
			<form action="/store" method="post">
				toggl API token: 
				<input name="toggl_api_token">
				toggl workspace ID: 
				<input name="workspace_id">
				<input type="submit" value="Submit">
				<br>
				Logged in as %s
			</form>
		</body>
	</html>
"""

class MainPage(webapp2.RequestHandler):
	def get(self):
		self.response.headers['content-type'] = 'text/html'
		self.response.write(MAINPAGE_TEMPLATE % str(users.get_current_user()))


class Store(webapp2.RequestHandler):
	def post(self):
		togglCredential = TogglCredential()
		togglCredential.user = users.get_current_user()
		togglCredential.api_token = str(self.request.get('toggl_api_token'))
		togglCredential.workspace_id = int(self.request.get('workspace_id'))
		togglCredential.put()

		self.response.write(str(togglCredential.api_token) + ' ' + str(togglCredential.workspace_id) + ' ' + 'saved for user ' + str(users.get_current_user()))


application = webapp2.WSGIApplication([
	('/', MainPage),
	('/store', Store)
], debug=True)