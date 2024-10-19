from django.shortcuts import render
from authentication.models import stats
from .captcha import FormWithCaptcha
import os


def homeView(request):
    s = stats.objects.get(index=1)
    return render (request, 'homepage.html', {'uCount': s.uCount,'vCount': s.vCount,'cCount': s.cCount,'sCount': s.sCount,'totalLogins': s.totalLogins,'lastUpdated':s.lastUpdated})

def custom_404(request, exception):
    return render(request, '404.html')

def custom_500_error_view(request):
    return render(request, '500.html', status=500)

def csrf_error_handler(request, reason=""):
    return render(request, '403.html')

def showLinksView(request):
    if request.method == 'GET':
        return render(request, 'user-manual.html', {"form":FormWithCaptcha()})
    else:
        if not FormWithCaptcha(request.POST).is_valid():
            return render(request, 'user-manual.html', {'error' : 'Please confirm that you are not a robot.', "form":FormWithCaptcha()})
        if request.POST['password'] != os.getenv('USER_MANUAL_PWD'):
            return render(request, 'user-manual.html', {'error' : 'Password incorrect.', "form":FormWithCaptcha()})

        params = {
            'pwd0' : os.getenv('PYTHONANYWHERE_HOSTING_PWD'),
            'pwd1' : os.getenv('ADMIN_LOGIN_PWD'),
            'pwd2' : os.getenv('ALLOT_COORDS_SEQUENTIAL_PWD'),
            'pwd3' : os.getenv('ALLOT_COORDS_SHEET_PWD'),
            'pwd4' : os.getenv('DOWNLOAD_VOL_DATA_PWD'),
            'pwd5' : os.getenv('DOWNLOAD_COORD_DATA_PWD'),
            'pwd6' : os.getenv('TEST_CERTIFICATE_PWD'),
            'pwd7' : os.getenv('DOWNLOAD_VOL_CERTIFICATES_ZIP_PWD'),
            'pwd8' : os.getenv('GENERATE_INDV_CERTIFICATE_PWD'),
            'pwd9' : os.getenv('FAIL_VOL_PWD'),
            'pwd10': os.getenv('SEND_EMAIL_PWD'),
            'pwd11': os.getenv('INFO_PWD1')

            }
        return render(request, 'show-user-manual.html', params)

def FAQsView(request):
    return render(request, 'faqs.html')