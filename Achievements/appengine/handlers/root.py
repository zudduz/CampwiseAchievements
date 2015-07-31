from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *

class MainPage(webapp.RequestHandler):
    def get(self):
        sessions = Session.gql('order by startDate')
        template_values = {'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), '../html/index.html')
        self.response.out.write(template.render(path, template_values))
