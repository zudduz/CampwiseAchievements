from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import logging

from models.model import *
import util


periods = ['SM', 'TW', 'RF']
class DebugNullCA(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        template_values = {'camperAchievements': camperAchievements, 'periods': periods}
        path = os.path.join(os.path.dirname(__file__), '../html/debug/null_ca.html')
        self.response.out.write(template.render(path, template_values))

class DebugNullCAWithNames(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        template_values = {'camperAchievements': camperAchievements, 'periods': periods}
        path = os.path.join(os.path.dirname(__file__), '../html/debug/null_ca_with_names.html')
        self.response.out.write(template.render(path, template_values))

class DebugNullCANullPeriods(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        camperAchievements = [ca for ca in camperAchievements if ca.period is None]
        template_values = {'camperAchievements': camperAchievements, 'periods': periods}
        path = os.path.join(os.path.dirname(__file__), '../html/debug/null_ca_with_names.html')
        self.response.out.write(template.render(path, template_values))

