from django.urls import path
from . import views
urlpatterns = [
    path('d', views.SecDashboardView, name='SDashboard'),
    path('sp', views.SetpasswordPageView, name='sresetpass'),
    path('ac', views.ApproveCoord, name='ApproveCoord'),
    path('rc', views.rejectCoordView, name='rejectCoord'),
    path('cd', views.coordDetailsView, name='coord-details'),
    path('va', views.viewVolunteerAttendanceView, name='view-volunteer-attendance'),
    path('a', views.volunteersDataDownloadView, name='volunteers-data-download'),
    path('fv', views.failVolunteersView, name='fail-volunteers'),
    path('Certificate', views.showCertificate, name='s-show-certificate'),
    path('Report', views.showReport, name='s-show-report'),
    path('s-rf', views.ReportFillingSampleView, name='s-rf'),
]
