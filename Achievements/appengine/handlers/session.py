from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *
import util

#Session
class SessionList(webapp.RequestHandler):
    def get(self):
        sessions = Session.all()
        template_values = {
            'sessions': sessions,
            }
        path = os.path.join(os.path.dirname(__file__), '../html/session/session_list.html')
        self.response.out.write(template.render(path, template_values))

class SessionView(webapp.RequestHandler):
    def get(self):
        session = Session.get(self.request.get('key'))
        startDateString = util.date2String(session.startDate)
        template_values = {'session': session, 'startDateString': startDateString}
        path = os.path.join(os.path.dirname(__file__), '../html/session/session_view.html')
        self.response.out.write(template.render(path, template_values))

class SessionDelete(webapp.RequestHandler):
    def get(self):
        session = Session.get(self.request.get('key'))
        startDateString = util.date2String(session.startDate)
        template_values = {'session': session, 'startDateString': startDateString}
        path = os.path.join(os.path.dirname(__file__), '../html/session/session_delete.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        session = Session.get(self.request.get('key'))
        session.delete()
        self.redirect('/session_list')

class SessionEdit(webapp.RequestHandler):
    def get(self):
        session = Session.get(self.request.get('key'))
        startDateString = util.date2String(session.startDate)
        template_values = {'session': session, 'startDateString': startDateString}
        path = os.path.join(os.path.dirname(__file__), '../html/session/session_edit.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        session = Session.get(self.request.get('key'))
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'startDate'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('campwiseId') not in (None, ''):
            incomingCampwiseId = None
            try:
                incomingCampwiseId = int(self.request.get('campwiseId'))
            except:
                validationErrors.extend(['Invalid Number Format for Campwise Id'])

            if incomingCampwiseId not in (None, session.campwiseId) and Session.gql("WHERE campwiseId = :1", incomingCampwiseId).get() is not None:
                validationErrors.extend(['Session already exists! (campwise id was found in database)'])
            else:
                session.campwiseId = incomingCampwiseId
        else:
            session.campwiseId = None

        incomingName = self.request.get('name')
        if incomingName != session.name and session.gql("WHERE name = :1", incomingName).get() is not None:
            validationErrors.extend(['Session already exists! (Session Name was found in database)'])
        else:
            session.name = self.request.get('name')
        
        try:
            session.startDate = util.string2Date(self.request.get('startDate'))
        except:
            validationErrors.extend(['Invalid Date Format for Start Date'])

        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/session/session_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            session.put()
            self.redirect('/session_view?key=' + str(session.key()))

class SessionNew(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../html/session/session_new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        session = Session()
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('name', 'startDate'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        if self.request.get('campwiseId') not in (None, ''):
            try:
                session.campwiseId = int(self.request.get('campwiseId'))
            except:
                validationErrors.extend(['Invalid Number Format for Campwise Id'])
            if session.campwiseId and Session.gql("WHERE campwiseId = :1", session.campwiseId).get() is not None:
                validationErrors.extend(['Session already exists! (campwise id was found in database)'])

        session.name = self.request.get('name')
        if session.name and session.gql("WHERE name = :1", session.name).get() is not None:
            validationErrors.extend(['Session already exists! (Session Name was found in database)'])
        
        try:
            session.startDate = util.string2Date(self.request.get('startDate'))
        except:
            validationErrors.extend(['Invalid Date Format for Start Date'])

        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/session/session_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            session.put()
            self.redirect('/session_view?key=' + str(session.key()))

