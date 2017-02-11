from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *
import util

#Camper
class CamperList(webapp.RequestHandler):
    def get(self):
        campers = Camper.all()
        campers = sorted(campers, key=lambda camper:(camper.lastName.upper(), camper.firstName.upper()))
        template_values = {'campers': campers}
        path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_list.html')
        self.response.out.write(template.render(path, template_values))

class CamperView(webapp.RequestHandler):
    def get(self):
        camper = Camper.get(self.request.get('key'))
        birthDateString = util.date2String(camper.birthDate)
        achievements = CamperAchievement.gql('WHERE camper = :1', camper) 
        achievements = sorted(achievements, key=lambda camperAchievement:(camperAchievement.achievement.level))
        template_values = {'camper': camper, 'birthDateString': birthDateString, 'achievements': achievements}
        path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_view.html')
        self.response.out.write(template.render(path, template_values))

class CamperDelete(webapp.RequestHandler):
    def get(self):
        camper = Camper.get(self.request.get('key'))
        birthDateString = util.date2String(camper.birthDate)
        template_values = {'camper': camper, 'birthDateString': birthDateString}
        path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_delete.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camper = Camper.get(self.request.get('key'))
        for camperAchievement in CamperAchievement.gql('where camper = :1', camper):
            camperAchievement.delete()
        camper.delete()
        self.redirect('/camper_list')

class CamperEdit(webapp.RequestHandler):
    def get(self):
        camper = Camper.get(self.request.get('key'))
        birthDateString = util.date2String(camper.birthDate)
        template_values = {'camper': camper, 'birthDateString': birthDateString}
        path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_edit.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camper = Camper.get(self.request.get('key'))
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('firstName', 'lastName', 'birthDate'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        camper.firstName = self.request.get('firstName')
        camper.lastName = self.request.get('lastName')
        camper.note = self.request.get('note')
        try:
            camper.birthDate = util.string2Date(self.request.get('birthDate'))
        except:
            validationErrors.extend(['Invalid Date Format for Birthday'])
                
        if self.request.get('campwiseId') not in (None, ''):
            try:
                camper.campwiseId = int(self.request.get('campwiseId'))
            except:
                validationErrors.extend(['Invalid Number Format for Campwise Id'])

        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_edit.html')
            self.response.out.write(template.render(path, template_values))
        else:
            camper.put()
            self.redirect('/camper_view?key=' + str(camper.key()))

class CamperNew(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        camper = Camper()
        validationErrors=[]
        template_values = {'validationErrors': validationErrors}
        for name in ('campwiseId', 'firstName', 'lastName', 'birthDate'):
            if self.request.get(name) in (None, ''):
                validationErrors.extend([name + ' cannot be empty'])
                
        try:
            camper.campwiseId = int(self.request.get('campwiseId'))
        except:
            validationErrors.extend(['Invalid Number Format for Campwise Id'])
        camper.firstName = self.request.get('firstName')
        camper.lastName = self.request.get('lastName')
        camper.note = self.request.get('note')
        try:
            camper.birthDate = util.string2Date(self.request.get('birthDate'))
        except:
            validationErrors.extend(['Invalid Date Format for Birthday'])
        if Camper.gql("WHERE campwiseId = :1", camper.campwiseId).get() is not None:
            validationErrors.extend(['Camper already exists! (campwise id was found in database)'])

        if validationErrors:
            path = os.path.join(os.path.dirname(__file__), '../html/camper/camper_new.html')
            self.response.out.write(template.render(path, template_values))
        else:
            camper.put()
            self.redirect('/camper_view?key=' + str(camper.key()))
