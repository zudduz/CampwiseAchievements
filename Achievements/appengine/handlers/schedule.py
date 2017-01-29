from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import os
import logging
import random

from models.model import *
import util


class ScheduleCabinUpdate(webapp.RequestHandler):
    def get(self):
        sessions = Session.gql('order by startDate')
        template_values = {'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), '../html/schedule/schedule_cabin_update.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        session = Session.get(self.request.get('session'))
        for camperLine in self.request.get('raw_csv').splitlines():
            camperArr = camperLine.split('|')
            if len(camperArr) != 5:
                self.response.out.write('error')
            campwiseId = int(camperArr[0])
            cabin = camperArr[4]
            if camperArr[4] == '':
                cabin = None
            camper = Camper.gql('WHERE campwiseId = :1', campwiseId).get()
            for camperAchievement in CamperAchievement.gql('where camper = :1', camper):
                camperAchievement.cabin = cabin
                camperAchievement.put()

        self.redirect('/')

class ScheduleStart(webapp.RequestHandler):
    def get(self):
        sessions = Session.gql('order by startDate')
        template_values = {'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), '../html/schedule/schedule_start.html')
        self.response.out.write(template.render(path, template_values))

class ScheduleClear(webapp.RequestHandler):
    def get(self):
        session = Session.get(self.request.get('session_key'))
        camperAchievements = CamperAchievement.gql('where session = :1', session)
        template_values = {'session': session, 'camperAchievements': camperAchievements}
        path = os.path.join(os.path.dirname(__file__), '../html/schedule/schedule_clear.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        session = Session.get(self.request.get('session'))
        for camperAchievement in CamperAchievement.gql('where session = :1', session):
            camperAchievement.delete()
        self.redirect('/schedule_start')

periods = ('SM', 'TW', 'RF')
groups = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
class ScheduleReview(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))
        
        #Detect existing Achievements in session and redirect
        for camperAchievement in CamperAchievement.gql('where session = :1', session):
            self.redirect('/schedule_clear?session_key=' + str(session.key()))
            return
        classCampers = []
        camperLines = self.request.get('raw_csv').splitlines()
        random.shuffle(camperLines)
        for camperLine in camperLines:
            camperArr = camperLine.split('|')
            if len(camperArr) != 5:
                raise ValueError('Imported line \'' + str(camperLine) + '\' doesn\'t contain 4 |\'s')
            campwiseId = int(camperArr[0])
            cabin = camperArr[4]
            if camperArr[4] == '':
                cabin = None
            camper = Camper.gql('WHERE campwiseId = :1', campwiseId).get()
            if not camper:
                raise AssertionError('campwiseId ' + str(campwiseId) + ' not found in DB. Be sure to run Import before scheduling.')

            classCampers.append(ClassCamper(camper, session, cabin))

        classesByPeriodIndex = {}
        lastPeriodMax = {}
        for achievement in Achievement.gql('order by level'):
            lastPeriodMax[achievement.level] = -1

        for periodIndex in xrange(len(periods)):
            availableClassesByLevel = {}
            unavailableClasses = []
            classCampers=sorted(classCampers, key=lambda classCamper: len(classCamper.neededForBadge()))
            for classCamper in classCampers:
                
                #perform a join on currently available classes and the classe that the camper needs for the next badge
                if classCamper.neededForBadge() and not classCamper.periodScheduled(periodIndex):
                    availableClassesForCamper = []
                    for neededClass in classCamper.neededForBadge():
                        if neededClass.level in availableClassesByLevel:
                            availableClassesForCamper.append(availableClassesByLevel[neededClass.level])
                    chosenClass = None
                    if len(availableClassesForCamper):
                        #place camper in emptiest compatible class
                        chosenClass = sorted(availableClassesForCamper, key=lambda availableClass: len(availableClass.campers))[0]
                        chosenClass.addCamper(classCamper)
                        classCamper.addClass(chosenClass)
                        if chosenClass.isFull():
                            unavailableClasses.append(availableClassesByLevel[chosenClass.achievement.level])
                            del availableClassesByLevel[chosenClass.achievement.level]

                    else:
                        # No Available Classes found
                        # Create available class
                        classInfos = []
                        for neededClass in classCamper.neededForBadge():
                            classInfo = ClassInfo(neededClass, lastPeriodMax[achievement.level])
                            for unavailableClass in unavailableClasses:
                                if unavailableClass.achievement == neededClass:
                                    classInfo.noteClass(unavailableClass)
                            classInfos.append(classInfo)

                        chosenClassInfo = sorted(classInfos, key=lambda classInfo: (classInfo.maxGroup >= classInfo.lastPeriodMax, '!' if classInfo.maxGroup is None else classInfo.maxGroup, classInfo.achievement.level))[0]
                        chosenClass = ClassInstance.fromClassInfo(chosenClassInfo, periodIndex)
                        chosenClass.addCamper(classCamper)
                        classCamper.addClass(chosenClass)
                        availableClassesByLevel[chosenClass.achievement.level] = chosenClass

            unavailableClasses.extend(availableClassesByLevel.values())
            classesByPeriodIndex[periodIndex] = unavailableClasses
            for currClass in classesByPeriodIndex[periodIndex]:
                oldMax = lastPeriodMax[currClass.achievement.level]
                if oldMax < currClass.groupIndex:
                    lastPeriodMax[currClass.achievement.level] = currClass.groupIndex

        sortedClasses = []
        for periodIndex in xrange(len(periods)):
            sortedClasses.extend(classesByPeriodIndex[periodIndex])    
        sortedClasses = sorted(sortedClasses, key=lambda classInstance: (classInstance.periodIndex, classInstance.achievement.level, classInstance.groupIndex))

        #even out groups
        classesByPeriodAndGroup = {}
        for classInstance in sortedClasses:
            if (classInstance.periodIndex, classInstance.achievement.level) not in classesByPeriodAndGroup:
                classesByPeriodAndGroup[(classInstance.periodIndex, classInstance.achievement.level)] = []
            classesByPeriodAndGroup[(classInstance.periodIndex, classInstance.achievement.level)].append(classInstance)

        for classGroup in classesByPeriodAndGroup.values():
            if len(classGroup) > 1:
                roster = []
                for classInstance in classGroup:
                    roster.extend(classInstance.campers)
                    classInstance.campers = []
                for camperIndex in xrange(len(roster)):
                    chosenClass = classGroup[camperIndex % len(classGroup)]
                    chosenClass.addCamper(roster[camperIndex])
                    roster[camperIndex].overwriteClass(chosenClass)

        achievements = []
        for achievement in Achievement.gql('order by level'):
            achievements.append(achievement)
        classCampers=sorted(classCampers, key=lambda classCamper: (classCamper.camper.lastName.upper(), classCamper.camper.firstName.upper()))
        template_values = {'achievements': achievements, 'sortedClasses': sortedClasses, 'classCampers': classCampers, 'classesByPeriodIndex': classesByPeriodIndex, 'session': session, 'achievementLevels': ClassCamper.achievementLevels}
        path = os.path.join(os.path.dirname(__file__), '../html/schedule/schedule_review.html')
        self.response.out.write(template.render(path, template_values))

class ClassInfo:
    def __init__(self, achievement, lastPeriodMax):
        self.achievement = achievement
        self.maxGroup = -1
        self.lastPeriodMax = lastPeriodMax

    def noteClass(self, classInstance):
        if self.maxGroup < classInstance.groupIndex:
            self.maxGroup = classInstance.groupIndex

class ClassInstance:
    @classmethod
    def fromClassInfo(cls, classInfo, periodIndex):
        return cls(achievement=classInfo.achievement, groupIndex=classInfo.maxGroup + 1, campers=[], periodIndex=periodIndex)

    def __init__(self, achievement, groupIndex, campers, periodIndex):
        self.achievement = achievement
        self.groupIndex = groupIndex
        self.campers = campers
        self.periodIndex = periodIndex

    def getPeriod(self):
        return periods[self.periodIndex]

    def getGroup(self):
        return groups[self.groupIndex]

    def getSize(self):
        return len(self.campers)

    def isFull(self):
        return len(self.campers) >= self.achievement.size

    def addCamper(self, classCamper):
        self.campers.append(classCamper)

class ClassCamper:
    achievementsByBadgeLevel = {}
    achievementLevels = []
    for badge in Badge.gql('order by level'):
        achievementsByBadgeLevel[badge.level] = []
    for achievement in Achievement.gql('order by level'):
        achievementsByBadgeLevel[achievement.badge.level].append(achievement)
        achievementLevels.append(achievement.level)

    def __init__(self, camper, session, cabin):
        self.camper = camper
        self.cabin = cabin
        self.achievementsNeededByBadgeLevel = {}
        self.scheduledClasses = {}
        self.completedAchievementLevels = []
        for camperAchievement in CamperAchievement.gql('where passed = True and camper = :1', camper):
            self.completedAchievementLevels.append(camperAchievement.achievement.level)
        for badgeLevel in ClassCamper.achievementsByBadgeLevel.keys():
            self.achievementsNeededByBadgeLevel[badgeLevel] = filter(lambda item: item.level not in self.completedAchievementLevels, ClassCamper.achievementsByBadgeLevel[badgeLevel])

    def periodScheduled(self, periodIndex):
        return periodIndex in self.scheduledClasses

    def overwriteClass(self, classInstance):
        self.scheduledClasses[classInstance.periodIndex] = classInstance

    def addClass(self, classInstance):
        self.scheduledClasses[classInstance.periodIndex] = classInstance
        self.achievementsNeededByBadgeLevel[classInstance.achievement.badge.level] = filter(lambda item: item.level != classInstance.achievement.level, self.achievementsNeededByBadgeLevel[classInstance.achievement.badge.level])

    def neededForBadge(self):
        for level in sorted(self.achievementsNeededByBadgeLevel.keys()):
            if len(self.achievementsNeededByBadgeLevel[level]) > 0:
                return self.achievementsNeededByBadgeLevel[level]
        return []

class ScheduleFinalize(webapp.RequestHandler):
    def post(self):
        session = Session.get(self.request.get('session'))

        achievementsByLevel = {}
        for achievement in Achievement.gql('order by level'):
            achievementsByLevel[achievement.level] = achievement

        camperReqStrings = []
        campersByCampwiseId = {}
        for arg in self.request.arguments():
            if arg.startswith('camper'):
                camperReqStrings.append(arg[6:])
                campwiseId = int(self.request.get(arg))
                if campwiseId not in campersByCampwiseId:
                    campersByCampwiseId[campwiseId] = Camper.gql('where campwiseId = :1', campwiseId).get()

        for suffix in camperReqStrings:
            camperAchievement = CamperAchievement()
            camperAchievement.camper = campersByCampwiseId[int(self.request.get('camper' + suffix))]
            camperAchievement.achievement = achievementsByLevel[int(self.request.get('achievement' + suffix))]
            camperAchievement.session = session
            camperAchievement.period = self.request.get('period' + suffix)
            camperAchievement.cabin = self.request.get('cabin' + suffix)
            if camperAchievement.cabin == '':
                camperAchievement.cabin = None
            camperAchievement.group = self.request.get('group' + suffix)
            camperAchievement.put()

        self.redirect('/')
