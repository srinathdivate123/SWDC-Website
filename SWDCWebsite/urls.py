from django.contrib import admin
from django.urls import path, include, re_path
from . import views
urlpatterns = [
    path('FAQs', views.FAQsView, name='faqs'),
    path('home', views.homeView, name='home'),
    path('user-manual', views.showLinksView, name='user-manual'),
    path('admin/', admin.site.urls),
    path('action/', include('action.urls')),
    path('a/', include('authentication.urls')),
    path('v/', include('dashboard.urls')),
    path('c/', include('CoordDashboard.urls')),
    path('s/', include('SecDashboard.urls')),
    re_path(r'^500/$', views.custom_500_error_view, name='custom_500_error'),
]
handler404 = 'SWDCWebsite.views.custom_404'