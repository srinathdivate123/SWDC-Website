from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('d', views.VDashboardView, name = 'vdashboard'),
    path('report-filling', csrf_exempt(views.reportFillingView), name = 'report-filling'),
    path('rejected-report-filling', csrf_exempt(views.rejectedReportFillingView), name = 'rejected-report-filling'),
    path('sp', views.SetpasswordPageView, name = 'vresetpass'),
    path('profile', views.VProfileView, name = 'vprofile'),
    path('c', views.ChooseCoordinatorView, name = 'choose-coordinator'),
    path('a', views.attendanceView, name = 'my-attendance'),
    path('v-download-certificate', views.downloadCertificateView, name = 'v-download-certificate'),
    path('v-download-report', views.downloadReportView, name = 'v-download-report'),
    path('v-request-to-update-email', views.VRequestToUpdateEmailView, name = 'v-request-to-update-email'),
    path('v-update-email/<str:new_email>/<str:current_email>', views.VUpdateEmailView, name = 'v-update-email'),
]