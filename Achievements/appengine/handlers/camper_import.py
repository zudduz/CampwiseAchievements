from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os

from models.model import *
import util

class Import(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), '../html/import/import.html')
        self.response.out.write(template.render(path, template_values))

class ClearImports(webapp.RequestHandler):
    def get(self):
        for incomingCamper in IncomingCamper.all():
            incomingCamper.delete()
        self.redirect('/import')

class ReceiveImport(webapp.RequestHandler):
    def post(self):
        for camperStrings in self.request.get('raw_csv').splitlines():
            camperArr = camperStrings.split('|')
            iCamper = IncomingCamper()
            iCamper.campwiseId = int(camperArr[0])
            iCamper.firstName = camperArr[1]
            iCamper.lastName = camperArr[2]
            iCamper.birthDate = util.string2Date(camperArr[3])
            if camperArr[4] in ('', None):
                iCamper.cabin = None
            else:
                iCamper.cabin = camperArr[4]
            found = Camper.gql('WHERE campwiseId = :1', iCamper.campwiseId).get()
            if found:
                iCamper.existingCamper = found
            incomingFound = IncomingCamper.gql('WHERE campwiseId = :1', iCamper.campwiseId).get()
            if not incomingFound:
                iCamper.put()
        self.redirect('/process_imports')

class FinalizeImport(webapp.RequestHandler):
    def post(self):
        #1. Record incoming campers that are new
        for incomingCamper in IncomingCamper.gql('WHERE existingCamper = NULL'):
            camper = Camper()
            camper.campwiseId = incomingCamper.campwiseId
            camper.firstName = incomingCamper.firstName
            camper.lastName = incomingCamper.lastName
            camper.birthDate = incomingCamper.birthDate
            camper.put()
            for achievementKey in self.request.get_all('camper' + str(incomingCamper.key())):
                camperAchievement = CamperAchievement()
                camperAchievement.camper = camper
                camperAchievement.achievement = Achievement.get(achievementKey)
                camperAchievement.session = None
                camperAchievement.cabin = None
                camperAchievement.period = None
                camperAchievement.group = None
                camperAchievement.put()


        #2 Delete all Incoming Campers
        for incomingCamper in IncomingCamper.all():
            incomingCamper.delete()

        self.redirect('/')

class ProcessImports(webapp.RequestHandler):
    def get(self):
        incomingCampers = IncomingCamper.gql('WHERE existingCamper = NULL');
        incomingCampers = sorted(incomingCampers, key=lambda incomingCamper:(incomingCamper.lastName.upper(), incomingCamper.firstName.upper()))
        existingIncomingCampers = IncomingCamper.gql("WHERE existingCamper != NULL");
        existingIncomingCampers = sorted(existingIncomingCampers, key=lambda incomingCamper:(incomingCamper.lastName.upper(), incomingCamper.firstName.upper()))
        achievementsByBadge = {}
        for badge in Badge.gql('order by level'):
            achievementsByBadge[badge.name] = []
        for achievement in Achievement.gql('order by level'):
            achievementsByBadge[achievement.badge.name].append(achievement)
        template_values = {
            'incomingCampers': incomingCampers,
            'existingIncomingCampers': existingIncomingCampers,
            'achievementsByBadge': achievementsByBadge,
            }
        path = os.path.join(os.path.dirname(__file__), '../html/import/process_imports.html')
        self.response.out.write(template.render(path, template_values))
