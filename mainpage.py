import webapp2
import urllib2
import json
import base64
import cgi
import dateutil.parser

from google.appengine.ext import ndb
from google.appengine.api import users

class TogglCredential(ndb.Model):
    api_token = ndb.StringProperty()
    workspace_id = ndb.IntegerProperty()

class TogglTask(ndb.Model):
    toggl_id = ndb.IntegerProperty()
    toggl_description = ndb.StringProperty()
    toggl_pid = ndb.IntegerProperty()
    toggl_project = ndb.StringProperty()
    toggl_updated = ndb.DateTimeProperty()
    toggl_dur = ndb.IntegerProperty()

MAINPAGE_TEMPLATE = """
    <html>
        <body>
            <a href="%s">%s</a>
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
            <br>
            <a href="/toggldata">Data here!</a>
        </body>
    </html>
"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        """ Create credential entry page using the template """
        self.response.headers['content-type'] = 'text/html'
        url = users.create_logout_url(self.request.url)
        url_text = 'Logout'        
        self.response.write(MAINPAGE_TEMPLATE % (url, url_text, str(users.get_current_user())))


class Store(webapp2.RequestHandler):
    def post(self):
        """ Store credentials in the DataStore """        
        # togglCredential.key_name = users.get_current_user() # trying out putting by key
        togglCredential = TogglCredential(id=str(users.get_current_user())) #another option - but it needs 'id' not 'key_name'
        togglCredential.api_token = str(self.request.get('toggl_api_token'))
        togglCredential.workspace_id = int(self.request.get('workspace_id'))
        togglCredential.put()

        self.response.write(str(togglCredential.api_token) + ' ' + str(togglCredential.workspace_id) + ' ' + 'saved for user ' + str(users.get_current_user()))


class TogglData(webapp2.RequestHandler):
    def get(self):
        """ Get data from toggl """
        user = users.get_current_user()
        togglCredential = TogglCredential.get_by_id(str(users.get_current_user()))
        workspace_id = togglCredential.workspace_id
        request = urllib2.Request("https://toggl.com/reports/api/v2/details?user_agent=TogglToEvernote&workspace_id=%s" % workspace_id)
        api_token = togglCredential.api_token
        base64string = base64.encodestring('%s:%s' % (api_token, 'api_token')).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        data = json.load(urllib2.urlopen(request))
        for task in data['data']:
            qry = TogglTask.query(TogglTask.toggl_id == task['id'])
            if qry.get() == None:
                self.response.write(str(task['id']) + ' does not exist in DataStore<br>')
                newTask = TogglTask()
                newTask.toggl_id = task['id']
                newTask.toggl_description = task['description']
                newTask.toggl_pid = task['pid']
                newTask.toggl_project = task['project']
                newTask.toggl_updated = dateutil.parser.parse(task['updated'])
                newTask.toggl_dur = task['dur']
                newTask.put()         
                self.response.write(str(task['id']) + ' created in DataStore<br>')
        #self.response.headers['content-type'] = 'application/json'
        #self.response.write(json.dumps(data, indent=4, sort_keys=True))        


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/store', Store),
    ('/toggldata', TogglData)
], debug=True)