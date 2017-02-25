import os
from google.appengine.ext.webapp import template

import cgi
from datetime import date

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class HistoricalModel(db.Model):
    updated = db.DateTimeProperty(auto_now='true')
    created = db.DateTimeProperty(auto_now_add='true')

class Badge(HistoricalModel):
    name = db.StringProperty()
    level = db.IntegerProperty()

    def toJson(self):
        return {
                'key': str(self.key()),
                'name': self.name,
                'level': self.level,
        }

class Session(HistoricalModel):
    campwiseId = db.IntegerProperty()
    name = db.StringProperty()
    startDate = db.DateProperty() #Should be the Sunday that the Camp Session Starts

    def toJson(self):
        return {
                'key': str(self.key()),
                'campwiseId': self.campwiseId,
                'startDate': str(self.startDate),
        }

class Camper(HistoricalModel):
    campwiseId = db.IntegerProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    birthDate = db.DateProperty()
    note = db.TextProperty()

    def toJson(self):
        return {
                'key': str(self.key()),
                'campwiseId': self.campwiseId,
                'firstName': self.firstName,
                'lastName': self.lastName,
                'birthDate': str(self.birthDate),
        }

class IncomingCamper(HistoricalModel):
    campwiseId = db.IntegerProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    birthDate = db.DateProperty()
    cabin = db.StringProperty()
    existingCamper = db.ReferenceProperty(reference_class=Camper, default=None)

class Achievement(HistoricalModel):
    name = db.StringProperty()
    criteria = db.TextProperty()
    level = db.IntegerProperty()
    badge = db.ReferenceProperty(reference_class=Badge)
    size = db.IntegerProperty(default=10)

    def toJson(self):
        return {
                'key': str(self.key()),
                'name': self.name,
                'level': self.level,
                'badgeKey': str(self.badge.key()),
                'badgeLevel': self.badge.level,
                'size': self.size,
        }

class CamperAchievement(HistoricalModel):
    camper = db.ReferenceProperty(reference_class=Camper)
    achievement = db.ReferenceProperty(reference_class=Achievement)
    session = db.ReferenceProperty(reference_class=Session)
    period = db.StringProperty()
    passed = db.BooleanProperty(default=True)
    cabin = db.StringProperty()
    group = db.StringProperty()

    def toJson(self):
        return {
                'key': str(self.key()),
                'camperKey': str(self.camper.key()),
                'achievementKey': str(self.achievement.key()),
                'sessionKey': str(self.session.key()),
                'period': self.period,
                'passed': self.passed,
                'cabin': self.cabin,
                'group': self.group,
        };
