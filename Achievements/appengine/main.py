import webapp2

import models.model
import handlers.achievement
import handlers.badge
import handlers.camper
import handlers.camper_achievement
import handlers.camper_import
import handlers.debug_report
import handlers.report
import handlers.schedule
import handlers.session
import handlers.root

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Hello, WebApp World!')

app = webapp2.WSGIApplication(
     [('/', handlers.root.MainPage),
      ('/ben', handlers.root.BenPage),
      ('/import', handlers.camper_import.Import),
      ('/clear_imports', handlers.camper_import.ClearImports),
      ('/receive_import', handlers.camper_import.ReceiveImport),
      ('/finalize_import', handlers.camper_import.FinalizeImport),
      ('/process_imports', handlers.camper_import.ProcessImports),
      ('/schedule_start', handlers.schedule.ScheduleStart),
      ('/schedule_clear', handlers.schedule.ScheduleClear),
      ('/schedule_review', handlers.schedule.ScheduleReview),
      ('/schedule_finalize', handlers.schedule.ScheduleFinalize),
      ('/schedule_cabin_update', handlers.schedule.ScheduleCabinUpdate),
      ('/report_cabin_report', handlers.report.ReportCabinReport),
      ('/report_group_report', handlers.report.ReportGroupReport),
      ('/report_medal_report', handlers.report.ReportMedalReport),
      ('/report_alphabetical_report', handlers.report.ReportAlphabeticalReport),
      ('/report_criteria_report', handlers.report.ReportCriteriaReport),
      ('/report_size_report', handlers.report.ReportSizeReport),
      ('/report_schedule_adjust', handlers.report.ReportScheduleAdjust),
      ('/report_schedule_adjust_json', handlers.report.ReportScheduleAdjustJson),
      ('/report_schedule_adjust_completed_achievements',
          handlers.report.ReportScheduleAdjustCompletedAchievements),
      ('/debug_null_ca', handlers.debug_report.DebugNullCA),
      ('/debug_null_ca_with_names', handlers.debug_report.DebugNullCAWithNames),
      ('/debug_null_ca_null_periods', handlers.debug_report.DebugNullCANullPeriods),
      ('/camper_list', handlers.camper.CamperList),
      ('/camper_view', handlers.camper.CamperView),
      ('/camper_delete', handlers.camper.CamperDelete),
      ('/camper_edit', handlers.camper.CamperEdit),
      ('/camper_new', handlers.camper.CamperNew),
      ('/session_list', handlers.session.SessionList),
      ('/session_view', handlers.session.SessionView),
      ('/session_delete', handlers.session.SessionDelete),
      ('/session_edit', handlers.session.SessionEdit),
      ('/session_new', handlers.session.SessionNew),
      ('/badge_list', handlers.badge.BadgeList),
      ('/badge_view', handlers.badge.BadgeView),
      ('/badge_delete', handlers.badge.BadgeDelete),
      ('/badge_edit', handlers.badge.BadgeEdit),
      ('/badge_new', handlers.badge.BadgeNew),
      ('/achievement_list', handlers.achievement.AchievementList),
      ('/achievement_view', handlers.achievement.AchievementView),
      ('/achievement_delete', handlers.achievement.AchievementDelete),
      ('/achievement_edit', handlers.achievement.AchievementEdit),
      ('/achievement_new', handlers.achievement.AchievementNew),
      ('/camper_achievement_view', handlers.camper_achievement.CamperAchievementView),
      ('/camper_achievement_delete', handlers.camper_achievement.CamperAchievementDelete),
      ('/camper_achievement_edit', handlers.camper_achievement.CamperAchievementEdit),
      ('/camper_achievement_new', handlers.camper_achievement.CamperAchievementNew),
      ],
     debug=True)

