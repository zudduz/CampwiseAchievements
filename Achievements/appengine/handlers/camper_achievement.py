from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *

#Camper Achievement
class CamperAchievementView(webapp.RequestHandler):
    def get(self):
        camperAchievement = CamperAchievement.get(self.request.get('key'))
        template_values = {'camperAchievement': camperAchievement}
        path = os.path.join(os.path.dirname(__file__), '../html/camper_achievement/camper_achievement_view.html')
        self.response.out.write(template.render(path, template_values))

class CamperAchievementDelete(webapp.RequestHandler):
    def get(self):
        camperAchievement = CamperAchievement.get(self.request.get('key'))
        template_values = {'camperAchievement': camperAchievement}
        path = os.path.join(os.path.dirname(__file__), '../html/camper_achievement/camper_achievement_delete.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camperAchievement = CamperAchievement.get(self.request.get('key'))
        camper = camperAchievement.camper
        camperAchievement.delete()
        self.redirect('/camper_view?key=' + str(camper.key()))

class CamperAchievementEdit(webapp.RequestHandler):
    def get(self):
        camperAchievement = CamperAchievement.get(self.request.get('key'))
        achievements = Achievement.gql("order by level")
        sessions = Session.gql("order by startDate")
        template_values = {'camperAchievement': camperAchievement, 'achievements': achievements, 'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), '../html/camper_achievement/camper_achievement_edit.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camperAchievement = CamperAchievement.get(self.request.get('key'))
        camperAchievement.achievement = Achievement.get(self.request.get('achievement'))

        if self.request.get('session') == '':
            camperAchievement.session = None
        else:
            camperAchievement.session = Session.get(self.request.get('session'))

        if self.request.get('period') == '':
             camperAchievement.period = None
        else:
            camperAchievement.period = self.request.get('period')

        if self.request.get('group') == '':
             camperAchievement.group = None
        else:
            camperAchievement.group = self.request.get('group')

        if self.request.get('cabin') == '':
             camperAchievement.cabin = None
        else:
            camperAchievement.cabin = self.request.get('cabin')

        if self.request.get('failed') in ('', None):
            camperAchievement.passed = True
        else:
            camperAchievement.passed = False
        camperAchievement.put()
        self.redirect('/camper_achievement_view?key=' + str(camperAchievement.key()))

class CamperAchievementNew(webapp.RequestHandler):
    def get(self):
        camper = Camper.get(self.request.get('camper_key'))
        achievements = Achievement.gql("order by level")
        sessions = Session.gql("order by startDate")
        template_values = {'camper': camper, 'achievements': achievements, 'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), '../html/camper_achievement/camper_achievement_new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camperAchievement = CamperAchievement()
        camperAchievement.camper = Camper.get(self.request.get('camper_key'))
        camperAchievement.achievement = Achievement.get(self.request.get('achievement'))

        if self.request.get('session') == '':
            camperAchievement.session = None
        else:
            camperAchievement.session = Session.get(self.request.get('session'))

        if self.request.get('period') == '':
             camperAchievement.period = None
        else:
            camperAchievement.period = self.request.get('period')

        if self.request.get('group') == '':
             camperAchievement.group = None
        else:
            camperAchievement.group = self.request.get('group')

        if self.request.get('cabin') == '':
             camperAchievement.cabin = None
        else:
            camperAchievement.cabin = self.request.get('cabin')

        if self.request.get('failed') in ('', None):
            camperAchievement.passed = True
        else:
            camperAchievement.passed = False
        camperAchievement.put()
        self.redirect('/camper_view?key=' + str(camperAchievement.camper.key()))



