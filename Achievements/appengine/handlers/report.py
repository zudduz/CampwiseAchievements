from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import logging

from models.model import *
import util


periods = ['SM', 'TW', 'RF']
groups = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
class ReportCabinReport(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(camperAchievement.cabin, camperAchievement.camper.firstName.upper(), camperAchievement.camper.lastName.upper(), periods.index(camperAchievement.period)))
        cabinReportRoot = CabinReportRoot()
        for camperAchievement in camperAchievements:
            cabinReportRoot.addCamperAchievement(camperAchievement)

        template_values = {'cabinReportRoot': cabinReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/cabin_report.html')
        self.response.out.write(template.render(path, template_values))

class CabinReportRoot:
    def __init__(self):
        self.cabins = []

    def addCamperAchievement(self, camperAchievement):
        if not self.cabins or camperAchievement.cabin != self.cabins[-1].cabin:
            self.cabins.append(CabinReportCabin(camperAchievement.cabin))
        self.cabins[-1].addCamperAchievement(camperAchievement)
            
class CabinReportCabin:
    def __init__(self, cabin):
        self.cabin = cabin
        self.campers = []

    def addCamperAchievement(self, camperAchievement):
        if not self.campers or camperAchievement.camper.key() != self.campers[-1].camper.key():
            self.campers.append(CabinReportCamper(camperAchievement.camper))
        self.campers[-1].addCamperAchievement(camperAchievement)

class CabinReportCamper:
    def __init__(self, camper):
        self.camper = camper
        self.camperAchievements = []

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)

class ReportAlphabeticalReport(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1', session)
        camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(camperAchievement.camper.lastName.upper(), camperAchievement.camper.firstName.upper(), periods.index(camperAchievement.period)))
        alphabeticalReportRoot = AlphabeticalReportRoot()
        for camperAchievement in camperAchievements:
            alphabeticalReportRoot.addCamperAchievement(camperAchievement)

        template_values = {'alphabeticalReportRoot': alphabeticalReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/alphabetical_report.html')
        self.response.out.write(template.render(path, template_values))

class AlphabeticalReportRoot:
    def __init__(self):
        self.campers = []

    def addCamperAchievement(self, camperAchievement):
        #if self.campers is empty or the last camper is not the same as the current camper.  incoming campers should be in order of camper
        if not self.campers or camperAchievement.camper.key() != self.campers[-1].camper.key():
            self.campers.append(AlphabeticalReportCamper(camperAchievement.camper))
        self.campers[-1].addCamperAchievement(camperAchievement)

class AlphabeticalReportCamper:
    def __init__(self, camper):
        self.camper = camper
        self.camperAchievements = []

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)

class ReportGroupReport(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(camperAchievement.achievement.level, camperAchievement.group, periods.index(camperAchievement.period), camperAchievement.camper.firstName.upper(), camperAchievement.camper.lastName.upper()))
        groupReportRoot = GroupReportRoot()
        for camperAchievement in camperAchievements:
            groupReportRoot.addCamperAchievement(camperAchievement)

        template_values = {'groupReportRoot': groupReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/group_report.html')
        self.response.out.write(template.render(path, template_values))

class GroupReportRoot:
    def __init__(self):
        self.groups = []

    def addCamperAchievement(self, camperAchievement):
        if not self.groups or camperAchievement.group != self.groups[-1].group or camperAchievement.achievement.key() != self.groups[-1].achievement.key():
            self.groups.append(GroupReportGroup(camperAchievement.group, camperAchievement.achievement))
        self.groups[-1].addCamperAchievement(camperAchievement)
            
class GroupReportGroup:
    def __init__(self, group, achievement):
        self.group = group
        self.achievement = achievement
        self.periods = []

    def addCamperAchievement(self, camperAchievement):
        if not self.periods or camperAchievement.period != self.periods[-1].period:
            self.periods.append(GroupReportPeriod(camperAchievement.period))
        self.periods[-1].addCamperAchievement(camperAchievement)

class GroupReportPeriod:
    def __init__(self, period):
        self.period = period
        self.camperAchievements = []

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)

class ReportMedalReport(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        sessionCamperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        camperListByCampwiseId = {}
        for camperAchievement in sessionCamperAchievements:
            if camperAchievement.camper.campwiseId not in camperListByCampwiseId:
                camperListByCampwiseId[camperAchievement.camper.campwiseId] = camperAchievement.camper
                
        badges = []
        badgesByLevel = {}
        for badge in Badge.all():
            badges.append(badge)
            badgesByLevel[badge.level] = badge

        achievements = []
        for achievement in Achievement.all():
            achievements.append(achievement)

        camperBadges = []
        for camper in camperListByCampwiseId.values():
            previousAchievements = {}
            currentAchievements = {}
            for camperAchievement in CamperAchievement.gql('where camper = :1', camper):
                if (not camperAchievement.session) or camperAchievement.session.startDate < session.startDate:
                    previousAchievements[camperAchievement.achievement.level] = camperAchievement.achievement
                elif session.key() == camperAchievement.session.key():
                    currentAchievements[camperAchievement.achievement.level] = camperAchievement.achievement
            previousNeededAchievements = filter(lambda achievement: achievement.level not in previousAchievements, achievements)
            previousNeededBadges = {}
            for achievement in previousNeededAchievements: 
                previousNeededBadges[achievement.badge.level] = achievement.badge
            currentNeededAchievements = filter(lambda achievement: achievement.level not in currentAchievements, previousNeededAchievements)
            currentNeededBadges = {}
            for achievement in currentNeededAchievements: 
                currentNeededBadges[achievement.badge.level] = achievement.badge
            newBadgeLevels = filter(lambda badgeLevel:badgeLevel not in currentNeededBadges, previousNeededBadges.keys())
            for badgeLevel in newBadgeLevels:
                camperBadges.append(CamperBadge(camper, badgesByLevel[badgeLevel]))

            camperBadges = sorted(camperBadges, key=lambda camperBadge:(camperBadge.badge.level, camperBadge.camper.firstName.upper(), camperBadge.camper.lastName.upper()))
                
        template_values = {'camperBadges': camperBadges, 'session': session}
        path = os.path.join(os.path.dirname(__file__), '../html/report/medal_report.html')
        self.response.out.write(template.render(path, template_values))

class CamperBadge:
    def __init__(self, camper, badge):
        self.camper = camper
        self.badge = badge

