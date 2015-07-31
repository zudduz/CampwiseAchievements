from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *

#Badge
class BadgeList(webapp.RequestHandler):
    def get(self):
        badges = Badge.all()
        template_values = {
            'badges': badges,
            }
        path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_list.html')
        self.response.out.write(template.render(path, template_values))

class BadgeView(webapp.RequestHandler):
    def get(self):
        badge = Badge.get(self.request.get('key'))
        achievements = Achievement.gql('WHERE badge = :1', badge)
        template_values = {'badge': badge, 'achievements': achievements}
        path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_view.html')
        self.response.out.write(template.render(path, template_values))

class BadgeDelete(webapp.RequestHandler):
    def get(self):
        badge = Badge.get(self.request.get('key'))
        template_values = {'badge': badge}
        path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_delete.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        badge = Badge.get(self.request.get('key'))
        badge.delete()
        self.redirect('/badge_list')

class BadgeEdit(webapp.RequestHandler):
    def get(self):
        badge = Badge.get(self.request.get('key'))
        template_values = {'badge': badge}
        path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_edit.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        badge = Badge.get(self.request.get('key'))
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'level'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('level') not in (None, ''):
            try:
                badge.level = int(self.request.get('level'))
            except:
                validationErrors.extend(['Invalid Number Format for level'])

        incomingName = self.request.get('name')
        if incomingName != badge.name and badge.gql("WHERE name = :1", incomingName).get() is not None:
            validationErrors.extend(['Badge already exists! (Badge Name was found in database)'])
        else:
            badge.name = self.request.get('name')
        
        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            badge.put()
            self.redirect('/badge_view?key=' + str(badge.key()))

class BadgeNew(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        badge = Badge()
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'level'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('level') not in (None, ''):
            try:
                badge.level = int(self.request.get('level'))
            except:
                validationErrors.extend(['Invalid Number Format for level'])

        badge.name = self.request.get('name')
        if badge.name and badge.gql("WHERE name = :1", badge.name).get() is not None:
            validationErrors.extend(['Badge already exists! (Badge Name was found in database)'])
        
        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/badge/badge_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            badge.put()
            self.redirect('/badge_view?key=' + str(badge.key()))
