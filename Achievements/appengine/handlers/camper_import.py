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
            if camperArr[5] in ('', None):
                iCamper.cabin = None
            else:
                iCamper.cabin = camperArr[5]
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


        #2 Delete all Incoming Campers
        for incomingCamper in IncomingCamper.all():
            incomingCamper.delete()

        self.redirect('/')

class ProcessImports(webapp.RequestHandler):
    def get(self):
        existingCampers = [];
        renamedCampers = [];
        newCampers = [];
        duplicatedCampers = [];
        incomingCampers = sorted(IncomingCamper.all(), key=lambda camper:(camper.lastName.upper(), camper.firstName.upper()))
        for incomingCamper in incomingCampers:
            if incomingCamper.existingCamper:
                if (incomingCamper.firstName != incomingCamper.existingCamper.firstName or
                         incomingCamper.lastName != incomingCamper.existingCamper.lastName or
                         incomingCamper.birthDate != incomingCamper.existingCamper.birthDate):
                    renamedCampers.append(incomingCamper);
                else:
                    existingCampers.append(incomingCamper);
            else:
                newCampers.append(incomingCamper)

        campers = list(Camper.all())
        for incomingCamper in incomingCampers:
            dupes = []
            for camper in campers:
                if (incomingCamper.campwiseId != camper.campwiseId and (
                        (incomingCamper.firstName.upper() == camper.firstName.upper() and incomingCamper.lastName.upper() == camper.lastName.upper()) or
                        (incomingCamper.firstName.upper() == camper.firstName.upper() and incomingCamper.birthDate == camper.birthDate) or
                        (incomingCamper.lastName.upper() == camper.lastName.upper() and incomingCamper.birthDate == camper.birthDate))):
                    dupes.append(camper)
            if len(dupes) > 0:
                duplicatedCampers.append(DuplicatedCamper(incomingCamper, dupes))

        template_values = {
            'newCampers': newCampers,
            'renamedCampers': renamedCampers,
            'existingCampers': existingCampers,
            'duplicatedCampers': duplicatedCampers,
        }
        path = os.path.join(os.path.dirname(__file__), '../html/import/process_imports.html')
        self.response.out.write(template.render(path, template_values))

class DuplicatedCamper:
    def __init__(self, incomingCamper, dupes):
        self.incomingCamper = incomingCamper
        self.dupes = dupes

