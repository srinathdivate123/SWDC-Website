from django.urls import path
from . import views
urlpatterns = [
    path('d', views.CoordDashboardView, name='CDashboard'),
    path('a', views.AttendanceView, name='attendance'),
    path('aa', views.activityAttendance, name='activityAttendance'),
    path('fav', views.FetchVolunteers, name='fetchAbsentVolunteers'),
    path('GP2-in', views.Mark_GP2_IN_AttendanceView, name='mark-GP2-in-attendance'),
    path('GP2-out', views.Mark_GP2_OUT_AttendanceView, name='mark-GP2-out-attendance'),
    path('FE-in', views.Mark_FE_IN_AttendanceView, name='mark-FE-in-attendance'),
    path('FE-out', views.Mark_FE_OUT_AttendanceView, name='mark-FE-out-attendance'),
    path('p-GP2', views.markPreviousGP2Attendance, name='prev-social-attendance'),
    path('p-FE', views.markPreviousFEAttendance, name='prev-FE-attendance'),
    path('sp', views.SetpasswordPageView, name='cresetpass'),
    path('rf', views.FormFillingView, name='cFormFilling'),
    path('vv', views.ApproveVolunteer, name='ApproveVolunteer'),
    path('rv', views.rejectVolunteerView, name='rejectVolunteer'),
    path('fv', views.failVolunteerView, name='fail-volunteer'),
    path('e', views.EventsView, name='events'),
    path('csa', views.ChooseSocialActivityView, name='choose-social-activity'),
    path('cfe', views.ChooseFlagshipEventView, name='choose-flagship-event'),
    path('va', views.viewVolunteerAttendanceView, name='volunteers-attendance'),
    path('c-ss-certificate', views.CShowSSCertificate, name='c-ss-certificate'),
    path('c-fe-certificate', views.CShowFECertificate, name='c-fe-certificate'),
    path('c-report', views.showReport, name='c-report'),
    path('c-rf', views.ReportFillingSampleView, name='c-rf'),
    path('coord-contact-us', views.ContactUsView, name='coord-contact-us'),
    path('report-verification', views.ReportVerificationView, name='report-verification'),
]