from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import logging
import json

from models.model import *
import util


periods = ('SM', 'TW', 'RF')

########################################################################################################################
class ReportCabinReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1 order by cabin', session)
        camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(
                camperAchievement.cabin, 
                camperAchievement.camper.firstName.upper(),
                camperAchievement.camper.lastName.upper(),
                periods.index(camperAchievement.period)))
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

########################################################################################################################
class ReportAlphabeticalReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1', session)
        camperAchievements = sorted(camperAchievements,
                key=lambda camperAchievement:(
                        camperAchievement.camper.lastName.upper(),
                        camperAchievement.camper.firstName.upper(),
                        periods.index(camperAchievement.period)))
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

########################################################################################################################
class ReportScheduleAdjust(webapp.RequestHandler):
    def get(self):
        session = Session.get(self.request.get('session'))
        path = os.path.join(os.path.dirname(__file__), '../html/report/schedule_adjust.html')
        template_values = {'session': session}
        self.response.out.write(template.render(path, template_values))

class ReportScheduleAdjustCompletedAchievements(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        camperKeys = self.request.get_all('camperKeys[]')
        completedAchievements = []
        for camperKey in camperKeys:
            completedAchievements.extend(CamperAchievement.gql('where camper = KEY(:1)', camperKey))
        template_values = {
                'completedAchievements': [ca.toJson() for ca in completedAchievements],
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(template_values))

class ReportScheduleAdjustCheck(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        camperKey = self.request.get('camperKey')
        achievementKey = self.request.get('achievementKey')
        sessionKey = self.request.get('sessionKey')
        period = self.request.get('period')
        cabin = self.request.get('cabin')
        scheduled = self.request.get('scheduled').lower() == 'true'

        deleteList = CamperAchievement.gql('where camper = KEY(:1) and session = KEY(:2) and period = :3', camperKey, sessionKey, period)

        foundCaToDelete = False
        caToDelete = None
        for deleteCa in deleteList:
            if foundCaToDelete:
                raise AssertionError('Too many achievements in a period for camper ' + camperKey);
            caToDelete = deleteCa
            foundCaToDelete = True

        if foundCaToDelete:
            caToDelete.delete()

        camperAchievement = None
        if not scheduled:
            camperAchievement = CamperAchievement()
            camperAchievement.camper = Camper.get(self.request.get('camperKey'))
            camperAchievement.achievement = Achievement.get(self.request.get('achievementKey'))
            camperAchievement.session = Session.get(self.request.get('sessionKey'))
            camperAchievement.period = self.request.get('period')
            camperAchievement.group = 'A'
            camperAchievement.cabin = self.request.get('cabin')
            camperAchievement.passed = True
            camperAchievement.put()

        template_values = {
            'camperAchievement': camperAchievement.toJson() if camperAchievement else None,
            'deletedCa': caToDelete.toJson() if caToDelete else None,
        }
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.out.write(json.dumps(template_values))

class ReportScheduleAdjustJson(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        session = Session.get(self.request.get('session'))
        achievements = Achievement.gql('ORDER BY level')
        camperAchievements = CamperAchievement.gql('where session = :1', session)
        camperAchievements = sorted(camperAchievements,
                key=lambda camperAchievement:(
                        camperAchievement.camper.lastName.upper(),
                        camperAchievement.camper.firstName.upper(),
                        periods.index(camperAchievement.period)))
        scheduleAdjustRoot = ScheduleAdjustRoot()
        for camperAchievement in camperAchievements:
            scheduleAdjustRoot.addCamperAchievement(camperAchievement)

        template_values = {
                #'sessionList': [s.toJson() for s in Session.all()],
                'session': session.toJson(),
                #'camperAchievements': [ca.toJson() for ca in camperAchievements],
                'scheduleCampers': [c.toJson() for c in scheduleAdjustRoot.campers],
                'badges': [b.toJson() for b in Badge.all()],
                'achievements': [a.toJson() for a in achievements],
                'periods':periods
        }
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.out.write(json.dumps(template_values))

class ScheduleAdjustRoot:
    def __init__(self):
        self.campers = []

    def addCamperAchievement(self, camperAchievement):
        # if self.campers is empty or the last camper is not the same as the current camper.
        # incoming campers should be in order of camper
        if not self.campers or camperAchievement.camper.key() != self.campers[-1].camper.key():
            self.campers.append(ScheduleAdjustCamper(camperAchievement.camper))
        self.campers[-1].addCamperAchievement(camperAchievement)

class ScheduleAdjustCamper:
    def __init__(self, camper):
        self.camper = camper
        self.camperAchievements = []
        #self.completedAchievements = []
        #for camperAchievement in CamperAchievement.gql('where passed = True and camper = :1', camper):
            #self.completedAchievements.append(camperAchievement.achievement)

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)

    def toJson(self):
        return {
                'camper': self.camper.toJson(),
                #'completedAchievements': [a.toJson() for a in self.completedAchievements],
                'sessionAchievements': [ca.toJson() for ca in self.camperAchievements],
        }

########################################################################################################################
class ReportGroupReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        session = Session.get(self.request.get('session'))
        camperAchievements = CamperAchievement.gql('where session = :1', session)
        camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(
                camperAchievement.achievement.level,
                periods.index(camperAchievement.period),
                camperAchievement.camper.firstName.upper(),
                camperAchievement.camper.lastName.upper()))

        groupReportRoot = GroupReportRoot()
        for camperAchievement in camperAchievements:
            groupReportRoot.addCamperAchievement(camperAchievement)
        for groupReportAchievement in groupReportRoot.achievements:
            for i in xrange(max([len(period.camperAchievements) for period in groupReportAchievement.periods])):
                groupReportAchievement.rows.append(
                        [None if i >= len(period.camperAchievements) else period.camperAchievements[i]
                                for period in groupReportAchievement.periods])


        template_values = {'groupReportRoot': groupReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/group_report.html')
        self.response.out.write(template.render(path, template_values))

class GroupReportRoot:
    def __init__(self):
        self.achievements = []

    def addCamperAchievement(self, camperAchievement):
        # If this camperAchievement has a differenet achievement than the last we need to start a new achievement
        if not self.achievements or camperAchievement.achievement.level != self.achievements[-1].achievement.level:
            self.achievements.append(GroupReportAchievement(camperAchievement.achievement))
        self.achievements[-1].addCamperAchievement(camperAchievement)
            
class GroupReportAchievement:
    def __init__(self, achievement):
        self.achievement = achievement
        self.periods = []
        self.rows = []
        for period in periods:
            self.periods.append(GroupReportPeriod(period))

    def addCamperAchievement(self, camperAchievement):
        self.periods[periods.index(camperAchievement.period)].addCamperAchievement(camperAchievement)

class GroupReportPeriod:
    def __init__(self, period):
        self.period = period
        self.camperAchievements = []

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)

########################################################################################################################
class ReportMedalReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        session = Session.get(self.request.get('session'))
        sessionCamperAchievements = CamperAchievement.gql('where session = :1', session)
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

########################################################################################################################
class ReportSizeReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        # Reuse criteria report classes and there generation
        criteriaReportRoot = generateCriteriaReportRoot(self.request.get('session'))
        template_values = {'criteriaReportRoot': criteriaReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/size_report.html')
        self.response.out.write(template.render(path, template_values))
        
########################################################################################################################
class ReportCriteriaReport(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        criteriaReportRoot = generateCriteriaReportRoot(self.request.get('session'))
        template_values = {'criteriaReportRoot': criteriaReportRoot, 'periods':periods}
        path = os.path.join(os.path.dirname(__file__), '../html/report/criteria_report.html')
        self.response.out.write(template.render(path, template_values))

########################################################################################################################
def generateCriteriaReportRoot(sessionParam):
    session = Session.get(sessionParam)
    camperAchievements = CamperAchievement.gql('where session = :1', session)
    camperAchievements = sorted(camperAchievements, key=lambda camperAchievement:(
            camperAchievement.achievement.level,
            periods.index(camperAchievement.period),
            camperAchievement.camper.firstName.upper(),
            camperAchievement.camper.lastName.upper()))

    criteriaReportRoot = CriteriaReportRoot()
    for camperAchievement in camperAchievements:
        criteriaReportRoot.addCamperAchievement(camperAchievement)
    return criteriaReportRoot

class CriteriaReportRoot:
    def __init__(self):
        self.achievements = []

    def addCamperAchievement(self, camperAchievement):
        # If this camperAchievement has a differenet achievement than the last we need to start a new achievement
        if not self.achievements or camperAchievement.achievement.level != self.achievements[-1].achievement.level:
            self.achievements.append(CriteriaReportAchievement(camperAchievement.achievement))
        self.achievements[-1].addCamperAchievement(camperAchievement)
            
class CriteriaReportAchievement:
    def __init__(self, achievement):
        self.achievement = achievement
        self.periods = []
        self.criteriaLines = achievement.criteria.splitlines() if achievement.criteria else []


    def addCamperAchievement(self, camperAchievement):
        if not self.periods or camperAchievement.period != self.periods[-1].period:
            self.periods.append(GroupReportPeriod(camperAchievement.period))
        self.periods[-1].addCamperAchievement(camperAchievement)

class CriteriaReportPeriod:
    def __init__(self, period):
        self.period = period
        self.camperAchievements = []

    def addCamperAchievement(self, camperAchievement):
        self.camperAchievements.append(camperAchievement)
