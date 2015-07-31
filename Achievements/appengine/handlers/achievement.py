from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *

#Achievement
class AchievementList(webapp.RequestHandler):
    def get(self):
        achievements = Achievement.all()
        template_values = {
            'achievements': achievements,
            }
        path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_list.html')
        self.response.out.write(template.render(path, template_values))

class AchievementView(webapp.RequestHandler):
    def get(self):
        achievement = Achievement.get(self.request.get('key'))
        template_values = {'achievement': achievement}
        path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_view.html')
        self.response.out.write(template.render(path, template_values))

class AchievementDelete(webapp.RequestHandler):
    def get(self):
        achievement = Achievement.get(self.request.get('key'))
        template_values = {'achievement': achievement}
        path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_delete.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        achievement = Achievement.get(self.request.get('key'))
        achievement.delete()
        self.redirect('/achievement_list')

class AchievementEdit(webapp.RequestHandler):
    def get(self):
        badges = Badge.all()
        achievement = Achievement.get(self.request.get('key'))
        template_values = {'achievement': achievement, 'badges': badges}
        path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_edit.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        achievement = Achievement.get(self.request.get('key'))
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'level'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('level') not in (None, ''):
            try:
                achievement.level = int(self.request.get('level'))
            except:
                validationErrors.extend(['Invalid Number Format for level'])

        if self.request.get('size') not in (None, ''):
            try:
                achievement.size = int(self.request.get('size'))
            except:
                validationErrors.extend(['Invalid Number Format for size'])

        achievement.badge = Badge.get(self.request.get('badge'))
        incomingName = self.request.get('name')
        if incomingName != achievement.name and achievement.gql("WHERE name = :1", incomingName).get() is not None:
            validationErrors.extend(['Achievement already exists! (Achievement Name was found in database)'])
        else:
            achievement.name = self.request.get('name')
        
        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            achievement.put()
            self.redirect('/achievement_view?key=' + str(achievement.key()))

class AchievementNew(webapp.RequestHandler):
    def get(self):
        badges = Badge.all()
        template_values = {'badges':badges}
        path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        achievement = Achievement()
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'level'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('level') not in (None, ''):
            try:
                achievement.level = int(self.request.get('level'))
            except:
                validationErrors.extend(['Invalid Number Format for level'])
        
        if self.request.get('size') not in (None, ''):
            try:
                achievement.size = int(self.request.get('size'))
            except:
                validationErrors.extend(['Invalid Number Format for size'])

        achievement.badge = Badge.get(self.request.get('badge'))
        achievement.name = self.request.get('name')
        if achievement.name and achievement.gql("WHERE name = :1", achievement.name).get() is not None:
            validationErrors.extend(['Achievement already exists! (Achievement Name was found in database)'])
        
        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/achievement/achievement_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            achievement.put()
            self.redirect('/achievement_view?key=' + str(achievement.key()))
