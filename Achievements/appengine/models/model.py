import os
from google.appengine.ext.webapp import template

import cgi
from datetime import date

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class HistoricalModel(db.Model):
    updated = db.DateTimeProperty(auto_now="true")
    created = db.DateTimeProperty(auto_now_add="true")

class Badge(HistoricalModel):
    name = db.StringProperty()
    level = db.IntegerProperty()

class Session(HistoricalModel):
    campwiseId = db.IntegerProperty()
    name = db.StringProperty()
    startDate = db.DateProperty() #Should be the Sunday that the Camp Session Starts

class Camper(HistoricalModel):
    campwiseId = db.IntegerProperty()
    firstName = db.StringProperty()
    lastName = db.StringProperty()
    birthDate = db.DateProperty()
    note = db.TextProperty()

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

class CamperAchievement(HistoricalModel):
    camper = db.ReferenceProperty(reference_class=Camper)
    achievement = db.ReferenceProperty(reference_class=Achievement)
    session = db.ReferenceProperty(reference_class=Session)
    period = db.StringProperty()
    passed = db.BooleanProperty(default=True)
    cabin = db.StringProperty()
    group = db.StringProperty()

class Cabin(HistoricalModel):
    name = db.StringProperty()
    level = db.IntegerProperty()
    badge = db.ReferenceProperty(reference_class=Badge)
    cabin = db.StringProperty()
