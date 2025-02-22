from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages, auth
from django.contrib.auth.models import User
from authentication.models import Coordinator, Volunteer, Activity, GuardianFaculty, currentData, Attendance, Event
from authentication.commonPasswords import common_passwords
from itertools import chain
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import os
from PyPDF2 import PdfWriter, PdfReader
import io
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A3, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import Transformation
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import geopy.distance
from django.utils.timezone import localtime
import json
import requests
from django.conf import settings
from dotenv import load_dotenv




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def my_activity(request):
    volunteer = Volunteer.objects.get(email=request.user.email)
    current = currentData.objects.get(index = 'Current')
    return render (request, 'my_activity.html', {'volunteer': volunteer, 'current': current})





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def view_attendance(request):
    volunteer = Volunteer.objects.get(email=request.user.email)
    current = currentData.objects.get(index = 'Current')
    return render (request, 'view_attendance.html', {'volunteer': volunteer, 'current': current})





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def fetch_attendance(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email=request.user.email)
        attendance_data = volunteer.attendance

        attendance_list = attendance_data.split(", ")
        parsed_attendance = []

        for entry in attendance_list:
            if entry:
                # status = 'Present' if entry.startswith('$') else 'Absent'
                if entry.startswith('$'):
                    status = 'Present'
                elif entry.startswith('?'):
                    status = 'In-Attendance Marked'
                else:
                    status = 'Absent'
                date = entry[1:]
                parsed_attendance.append({'date': date, 'status': status})

        return JsonResponse({'attendance': parsed_attendance})






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def v_contact_us(request):
    return render(request, 'contactus.html')



def update_env_variable(key, value):
    """ Updates a key-value pair in the .env file and reloads the environment. """
    ENV_FILE_PATH = "/home/swdc/SWDCWebsite/all_passwords.env"

    with open(ENV_FILE_PATH, "r") as file:
        lines = file.readlines()

    with open(ENV_FILE_PATH, "w") as file:
        found = False
        for line in lines:
            if line.startswith(f"export {key}="):  # Updating if key exists
                file.write(f"export {key}={value}\n")
                found = True
            else:
                file.write(line)

        if not found:  # Adding key if it doesn't exist
            file.write(f"\nexport {key}={value}\n")

    load_dotenv(ENV_FILE_PATH)


def refresh_access_token():
    data = {
        "client_id": os.getenv('CLIENT_ID'),
        "client_secret": os.getenv('CLIENT_SECRET'),
        "refresh_token": os.getenv('REFRESH_TOKEN'),
        "grant_type": "refresh_token"
    }

    response = requests.post("https://oauth2.googleapis.com/token", data=data)
    response_data = response.json()

    if "access_token" in response_data:
        return response_data["access_token"]
    else:
        print("Failed to refresh access token:", response_data)
        raise Exception("Token refresh failed")


def upload_to_google_drive(file_path, file_name, folder_id):
    ACCESS_TOKEN = os.getenv('GDRIVE_ACCESS_TOKEN')
    # folder_id = os.getenv('GDRIVE_FOLDER_ID')

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    para = {
        "name": file_name,
        "parents": [folder_id]
    }
    files = {
        "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
        "file": open(file_path, "rb")
    }

    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files
    )

    if r.status_code == 401:  # Unauthorized
        # print("Access token expired, refreshing...")
        ACCESS_TOKEN = refresh_access_token()
        update_env_variable('GDRIVE_ACCESS_TOKEN',ACCESS_TOKEN)

        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        para = {
            "name": file_name,
            "parents": [folder_id]
        }
        files = {
            "data": ("metadata", json.dumps(para), "application/json; charset=UTF-8"),
            "file": open(file_path, "rb")
        }
        # print("Renewed access token:", ACCESS_TOKEN)
        r = requests.post(
            "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
            headers=headers,
            files=files
        )

    if r.status_code == 200:
        # print("File uploaded successfully!")
        file_id = r.json().get('id')
        return f"https://drive.google.com/file/d/{file_id}/view"
    else:
        return "error"



def calculate_distance(lat1, lon1, lat2, lon2):
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geopy.distance.geodesic(coords_1, coords_2).km





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def MarkAttendanceView(request):
    if request.method=='GET':
        volunteer = Volunteer.objects.get(email=request.user.email)
        current = currentData.objects.get(index = 'Current')
        today = datetime.now().date()
        events = Event.objects.filter(activity=volunteer.activity, date=today, divisions__icontains=volunteer.div)
        return render (request, 'mark_attendance.html', {'volunteer': volunteer, 'current': current, 'events': events})

    if request.method == 'POST':
        try:
            coord_prn = request.POST.get('coord_prn')
            coord_name = request.POST.get('coord_name')
            coord_activity = request.POST.get('coord_activity')
            volunteer = Volunteer.objects.get(email=request.user.email)
            vol_name = volunteer.vname
            vol_prn = volunteer.prn
            actual_latitude = float(request.POST.get('actual_latitude'))
            actual_longitude = float(request.POST.get('actual_longitude'))
            geo_photo = request.FILES.get('geo_photo')
            venue = request.POST.get('venue')

            volunteer = Volunteer.objects.get(email=request.user.email)

            if geo_photo:
                temp_photo_path = os.path.join(settings.BASE_DIR, 'tmp_photo_{}.png'.format(volunteer.prn))

                with open(temp_photo_path, 'wb+') as destination:
                    for chunk in geo_photo.chunks():
                        destination.write(chunk)


                file_url = upload_to_google_drive(temp_photo_path, geo_photo.name, os.getenv('GDRIVE_FOLDER_ID'))
                os.remove(temp_photo_path)
            else:
                return JsonResponse({'error': 'Geo photo is required.'}, status=400)

            # current_time = datetime.now().time()
            # today = datetime.now().date()
            current_time = localtime().time()
            today = localtime().date()

            activity_name = volunteer.activity

            if activity_name != coord_activity:
                return JsonResponse({'error': 'The activity of coordinator and volunteer do not match.'}, status=400)

            activities = Event.objects.filter(activity=activity_name, date=today, venue=venue)
            count = activities.count()

            error = ''

            if count == 0:
                return JsonResponse({'error': 'No active activity present to mark attendance.'}, status=400)

            for activity in activities:
                # Time window checks
                in_time_window_start = (datetime.combine(today, activity.start_time) - timedelta(minutes=10)).time()
                in_time_window_end = (datetime.combine(today, activity.start_time) + timedelta(minutes=40)).time()

                out_time_window_start = (datetime.combine(today, activity.end_time) - timedelta(minutes=10)).time()
                out_time_window_end = (datetime.combine(today, activity.end_time) + timedelta(minutes=40)).time()

                if not activity.isOnline:
                    # Calculate distance
                    distance = calculate_distance(
                        actual_latitude, actual_longitude,
                        activity.latitude, activity.longitude
                    )

                    # Ensure volunteer is within 1 km range
                    if distance > 3:
                        error = "You are too far from the activity location to mark attendance."
                        continue
                        # return JsonResponse({'error': 'You are too far from the activity location to mark attendance.'}, status=400)

                # In-Time Attendance
                if not volunteer.marked_IN_attendance:
                    if in_time_window_start <= current_time and current_time <= in_time_window_end:
                        # Mark in-time attendance
                        idx = volunteer.attendance.find(today.strftime("%d-%m-%Y"))

                        if volunteer.attendance[idx-1] == "$":
                            return JsonResponse({'message': 'Your attendance has already been marked!'}, status=200)

                        volunteer.attendance = volunteer.attendance[:idx-1] + '?' + volunteer.attendance[idx:]
                        # volunteer.attendance += f"{attendance}, "
                        volunteer.marked_IN_attendance = True
                        volunteer.save()

                        if file_url == "error":
                            Attendance.objects.create(
                                coord_prn=coord_prn,
                                coord_name=coord_name,
                                activity=activity_name,
                                vol_name=vol_name,
                                vol_prn=vol_prn,
                                actual_latitude=actual_latitude,
                                actual_longitude=actual_longitude,
                                geo_photo=geo_photo,
                                time=datetime.now()
                            )
                        else:
                            Attendance.objects.create(
                                coord_prn=coord_prn,
                                coord_name=coord_name,
                                activity=activity_name,
                                vol_name=vol_name,
                                vol_prn=vol_prn,
                                actual_latitude=actual_latitude,
                                actual_longitude=actual_longitude,
                                geo_photo=file_url,
                                time=datetime.now()
                            )
                        return JsonResponse({'message': 'In-time attendance marked successfully!'}, status=200)
                    else:
                        error = f'Current time is outside the in-time attendance window. {in_time_window_start} - {in_time_window_end} - {activity.venue} - {current_time}'
                        continue
                else:
                    # Out-Time Attendance
                    if current_time >= out_time_window_start and current_time <= out_time_window_end:
                        idx = volunteer.attendance.find(today.strftime("%d-%m-%Y"))
                        volunteer.attendance = volunteer.attendance[:idx-1] + "$" + volunteer.attendance[idx:]
                        volunteer.marked_IN_attendance = False
                        volunteer.save()

                        # attendance_record = Attendance.objects.get(vol_prn=vol_prn, activity=activity_name)
                        # # attendance_record.marked_IN_attendance = False
                        # attendance_record.save()

                        return JsonResponse({'message': 'Out-time attendance marked successfully!'}, status=200)
                    else:
                        error = 'Current time is outside the out-time attendance window.'
                        continue

            return JsonResponse({'error': error}, status=400)

        except Event.DoesNotExist:
            return JsonResponse({'error': 'Activity does not exist.'}, status=404)
        except Volunteer.DoesNotExist:
            return JsonResponse({'error': 'Volunteer does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def VDashboardView(request):
    if request.method == "GET":
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        current = currentData.objects.get(index = 'Current')
        return render(request, 'vdashboard.html', {'volunteer': volunteer, 'activity': activity, 'current' : current, 'CURR_YEAR': current.AcademicYear, 'CURR_SEM': current.Semester})
    else:
        return redirect('vdashboard')



def checkUrl(url):
    if url == 'http://' or url == 'https://':
        return 'Your URL should be a valid URL. It has only http:// or https:// in it. You have to fill report again because of doing malpractice.'
    if ' ' in url or ',' in url:
        return 'Your URL cannot have a blank space or a comma. You have to fill report again because of doing malpractice.'
    if not ('http://' in url or 'https://' in url):
        return 'Your URL must contain a http:// or https:// You have to fill report again because of doing malpractice.'
    return 'True'



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def home_reportfilling(request):
    if request.method == 'GET':
        guardian_faculties = GuardianFaculty.objects.filter(active=True)
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        current = currentData.objects.get(index = 'Current')
        return render (request, 'report-filling-home.html', {'volunteer':volunteer, 'activity':activity, 'current':current, 'guardian_faculties': guardian_faculties})
    else:
        volunteer = Volunteer.objects.get(email=request.user.email)
        url = request.POST['url']
        if checkUrl(url.strip()) != 'True':
            messages.error(request, checkUrl(url))
            return redirect('home_reportfilling')

        volunteer.guardian_faculty = request.POST['guardian_faculty']
        volunteer.url = url
        volunteer.save()
        return redirect('report-filling')







@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
@csrf_exempt
def rejectedReportFillingView(request):
    if request.method == 'GET':
        browser = str(request.user_agent.browser.family) + ' (Version ' + str(request.user_agent.browser.version_string) + ')'
        os = str(request.user_agent.os.family)
        device = request.user_agent.is_pc

        if not device:
            return render(request, 'report-filling-blocked.html', {'browser':browser, 'os':os})
        guardian_faculties = GuardianFaculty.objects.filter(active=True)
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        current = currentData.objects.get(index = 'Current')
        user = User.objects.get(email = request.user.email)
        hours = str(user.last_login)[11:13]
        minutes = str(user.last_login)[14:16]
        return render (request, 'report-filling-for-rejected.html', {'volunteer': volunteer, 'activity': activity, 'current' : current, 'hours':hours, 'minutes':minutes, 'guardian_faculties':guardian_faculties})
    else:
        return redirect('vdashboard')


def checkAnswerLength(string):
    c = 0
    for char in string:
        if char.isalpha():
            c += 1
    if c >= 650:
        return False
    return True




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
@csrf_exempt
def reportFillingView(request):
    if request.method == 'GET':
        browser = str(request.user_agent.browser.family) + ' (Version ' + str(request.user_agent.browser.version_string) + ')'
        os = str(request.user_agent.os.family)
        device = request.user_agent.is_pc

        if not device:
            messages.error(request, 'Oops! Seems like you are accessing this page from your mobile phone.')
            return render(request, 'report-filling-blocked.html', {'browser':browser, 'os':os})

        os_check = str(request.user_agent.os)

        backup_check = request.META.get('HTTP_USER_AGENT', '')
        os_check += backup_check

        # Below check is important. Some students might open report filling page inside a VirtualBox VM running Ubuntu/Linux & enter answers into it without exiting the full screen mode
        # Below check blocks someone accessing the page from a mobile device in 'desktop mode'
        # When most mobile devices try to mimic being a desktop device when in 'desktop mode', they end up telling in their HTTP request that they are using linux/ubuntu OS
        if 'linux' in os_check or 'Linux' in os_check or 'ubuntu' in os_check or 'Ubuntu' in os_check:
            messages.error(request, 'Oops! Your device failed some of our security checks. Please contact your coordinator!')
            return render(request, 'report-filling-blocked.html', {'browser':browser, 'os':os})

        guardian_faculties = GuardianFaculty.objects.filter(active=True)
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        user = User.objects.get(email = request.user.email)
        # hours = str(user.last_login)[11:13]
        # minutes = str(user.last_login)[14:16]
        hours = user.last_login.strftime("%H")
        minutes = user.last_login.strftime("%M")
        return render(request, 'report-filling-main.html', {'guardian_faculties':guardian_faculties, 'activity':activity, 'volunteer':volunteer, 'hours':hours, 'minutes':minutes, 'browser':browser, 'os':os})

    if request.method == 'POST':
        ans1 = request.POST['quest1']
        ans2 = request.POST['quest2']
        ans3 = request.POST['quest3']
        ans4 = request.POST['quest4']
        ans5 = request.POST['quest5']
        ans6 = request.POST['quest6']

        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name = volunteer.activity)

        if checkAnswerLength(ans1)  or checkAnswerLength(ans2) or checkAnswerLength(ans3) or checkAnswerLength(ans4) or checkAnswerLength(ans5) or checkAnswerLength(ans6):
            messages.error(request, 'You have submitted the report without writing 700 characters for each question. You will have to write the report again. Your report is not submitted to us.')
            return redirect('home_reportfilling')



        if not activity.report_filling:
            messages.error(request, 'Now report filling is closed for ' + activity.name + '. Hence, even though you started writing your report on time, your report is not submitted to us because report filling is currently closed.')
            return redirect('home_reportfilling')

        volunteer.ans1 = ans1
        volunteer.ans2 = ans2
        volunteer.ans3 = ans3
        volunteer.ans4 = ans4
        volunteer.ans5 = ans5
        volunteer.ans6 = ans6
        volunteer.submitted = 1
        volunteer.verified = 0
        volunteer.save()
        return redirect('home_reportfilling')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def ChooseCoordinatorView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email=request.user.email)

        coordinators_doing_GP2_activities = Coordinator.objects.filter(activity=volunteer.activity, registered_academic_year = volunteer.registered_academic_year, registered_semester = volunteer.registered_semester)

        coordinators_doing_flagship_events = Coordinator.objects.filter(flagshipEvent=volunteer.activity, registered_academic_year = volunteer.registered_academic_year, registered_semester = volunteer.registered_semester)

        coordinators = list(chain(coordinators_doing_GP2_activities, coordinators_doing_flagship_events))
        return render(request, 'choose-coordinator.html', {'coordinators': coordinators, 'volunteer' :volunteer})
    else:
        coord = request.POST['coordinator']
        volunteer = Volunteer.objects.get(email=request.user.email)
        volunteer.Cordinator = coord
        volunteer.save()
        return redirect('choose-coordinator')



def Format_Name_Function(name):
    formatted_name = name[0].upper()
    i = 1
    while i < len(name):
        if name[i] == ' ':
            if name[i + 1] == ' ':
                i += 1
                continue
            formatted_name += ' ' + name[i + 1].upper()
            i += 1
        else:
            formatted_name += name[i].lower()
        i += 1
    return formatted_name


def checkName(name):
    for c in name:
        if not c.isalpha() and c != ' ':
            return False
    return True


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def VProfileView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email=request.user.email)
        return render(request, 'VProfile.html', {'volunteer':volunteer})
    else:
        vname = Format_Name_Function(request.POST['vname'].strip())
        prn = request.POST['prn']
        contact_num = request.POST['contact_num']
        parent_num = request.POST['parent_num']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        div = request.POST['div']
        current_add = request.POST['current_add']

        if not checkName(vname):
            messages.error(request, 'You entered your name as ' + vname + '. But it cannot contain special characters or numbers.')
            return redirect('vprofile')

        if ' ' not in vname:
            messages.error(request, 'Please enter both your firstname and lastname')
            return redirect('vprofile')

        vols_with_same_name = Volunteer.objects.filter(vname = vname)
        users_with_same_name = User.objects.filter(username = vname)

        if len(vols_with_same_name) > 1 or len(users_with_same_name) > 1: # >1 because, the same volunteer will have his/her name. If two vols have same name then the if condition should be executed
            messages.error(request, 'A user with the name ' + vname + ' has already registered on the website. So please enter your full name or your name with your initial so that we can distinguish both of you!')
            return redirect('vprofile')

        vols_with_same_prn = Volunteer.objects.filter(prn = prn)
        if len(vols_with_same_prn) > 1:
            messages.error(request, 'Oops! Seems like the PRN ' + str(prn) + ' belongs to someone else, or, someone else has entered your PRN. Please mail to us at vitswd@vit.edu')
            messages.info(request, 'Do not enter an incorrect PRN, which is not yours, to just bypass this check. Please contact us!')
            return redirect('vprofile')



        try:
            volunteer = Volunteer.objects.get(email = request.user.email)

            volunteer.vname = vname
            volunteer.prn = prn
            volunteer.contact_num = contact_num
            volunteer.parent_num = parent_num
            volunteer.gender = gender
            volunteer.blood_group = blood_group
            volunteer.div = div
            volunteer.current_add = current_add
            volunteer.profile_edited = datetime.now().strftime("%d-%m-%Y")
            volunteer.save()
            user = User.objects.get(email = request.user.email)
            user.username = vname
            user.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('vprofile')

        except Exception as e:
            messages.error(request, e)
            return redirect('vprofile')






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def SetpasswordPageView(request):
    if request.method == 'POST':
        password = request.POST["password"]
        password = password.strip()
        if len(password) <=6:
            messages.error(request, 'Please enter a password with more than 6 characters')
            return redirect('vprofile')
        if password in common_passwords:
            messages.error(request, 'This password is too common. Choose a safer one.')
            return redirect('vprofile')
        user = User.objects.get(username=request.user.username)
        user.set_password(password)
        user.save()
        volunteer = Volunteer.objects.get(email=user.email)
        volunteer.password_changed = True
        volunteer.save()
        auth.logout(request)
        messages.success(request, 'Your password has been changed successfully! Please login again!')
        return redirect('login')
    else:
        messages.info(request, 'Not allowed')
        return redirect('vdashboard')






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def VRequestToUpdateEmailView(request):
    if request.method == 'POST':
        emailaddress = request.POST['email'].strip().lower()
        volunteer = Volunteer.objects.get(email = request.user.email)
        if emailaddress == volunteer.email:
            messages.error(request, 'Your email address is already ' + emailaddress + '. Enter a different email address.')
            return redirect('vprofile')
        if User.objects.filter(email = emailaddress).exists() or Volunteer.objects.filter(email = emailaddress).exists():
            messages.error(request, "This email is in use by another user. Please enter your email ID and not someone else's")
            return redirect('vprofile')
        try:
            current_site = get_current_site(request)
            link = reverse('v-update-email', args=[urlsafe_base64_encode(force_bytes(emailaddress)), urlsafe_base64_encode(force_bytes(volunteer.email))])
            email_subject = 'Update your email address'
            url = 'https://' + current_site.domain + link
            email = EmailMessage(
                email_subject,
                'Hi ' + volunteer.vname + ',\nPlease click the below link to update your email address:\n\n' + url + ' \n\nRegards,\nThe Social Welfare Development Committee',
                'noreply@semycolon.com',
                [emailaddress],)
            email.send(fail_silently=False)
        except Exception as error_while_sendng_mail:
            messages.error(request, 'There was an unexpected error. Please try again.')
            return redirect('vprofile')
        messages.success(request, 'A mail with a link has been sent to ' + emailaddress + ', please click on that link to update your email address.')
        return redirect('vprofile')
    else:
        messages.info(request, 'Not allowed')
        return redirect('vdashboard')







def VUpdateEmailView(request, new_email, current_email):
    if request.method == 'GET':
        try:
            new_email = force_str(urlsafe_base64_decode(new_email))
            current_email = force_str(urlsafe_base64_decode(current_email))
            volunteer = Volunteer.objects.get(email = current_email)
            volunteer.email = new_email
            volunteer.save()
            user = User.objects.get(email = current_email)
            user.email = new_email
            user.save()
            messages.success(request, 'Your email address was updated to ' + new_email + '. You can login with the new mail address now.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'The link you clicked is invalid or has been used earlier. Please login and request a new link.')
            return redirect('login')
    else:
        messages.info(request, 'Not allowed')
        return redirect('login')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def downloadCertificateView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email = request.user.email)
        if volunteer.verified != 1:
            messages.error(request, 'Oops! Your report is not yet verified. You can\'t download your certificate!!!')
            return redirect('home_reportfilling')

        activity = (volunteer.activity).replace(" ", "_")

        packet = io.BytesIO()
        canvasObj = canvas.Canvas(packet, pagesize=landscape(A3))
        canvasObj.setFont("Times-Bold", 27)
        width, height = A3
        text_width = canvasObj.stringWidth(volunteer.vname, "Times-Bold", 27)
        x_center = (width - text_width) / 2
        canvasObj.drawString(x_center, settings.COORDINATE[activity], volunteer.vname)
        canvasObj.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)

        # Use this template_path if every activity has its own certificate template
        template_path = os.path.join(settings.BASE_DIR, "certificateTemplates") + "/" + activity + "/" + activity + "_" + volunteer.registered_academic_year + "_" + str(volunteer.registered_semester) + ".pdf"
        # template_path = os.path.join(settings.BASE_DIR, "certificateTemplates") + "/certificateTemplate.pdf"

        certificate_template = PdfReader(open(template_path, "rb"))
        output = PdfWriter()
        page = certificate_template.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        pdf_file_path = "Certificate.pdf"
        output_stream = open(pdf_file_path, "wb")
        output.write(output_stream)
        output_stream.close()
        with open(pdf_file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Certificate.pdf"'
        os.remove(pdf_file_path)
        return response
    else:
        pass






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def downloadReportView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email = request.user.email)
        if volunteer.verified != 1:
            messages.error(request, 'Oops! Your report is not yet verified. You can\'t download your report!!!')
            return redirect('home_reportfilling')
        volDetails = [
                [
                    volunteer.vname,
                    volunteer.dept,
                    volunteer.div,
                    volunteer.email,
                    str(volunteer.prn),
                    volunteer.gender,
                    volunteer.guardian_faculty,
                    volunteer.Cordinator,
                    volunteer.registered_academic_year,
                    str(volunteer.registered_semester),
                    volunteer.activity,
                    volunteer.ans1,
                    volunteer.ans2,
                ],
                [
                    volunteer.ans3,
                    volunteer.ans4,
                    volunteer.ans5,
                ],
                [volunteer.ans6, volunteer.url],
            ]
        coordinates = [
                [45, 12, -18, -45, -72, -100, -130, -155, -185, -215, -270, -295, -470],
                [50, -165, -385],
                [50, -170],
            ]
        template_pdf = PdfReader(open(os.path.join(settings.BASE_DIR, "certificateTemplates/ReportTemplate.pdf"), "rb"))

        custom_style = ParagraphStyle(
                name="CustomStyle",
                parent=getSampleStyleSheet()["Normal"],
                wordWrap="CJK",
            )
        custom_style.leading = 12
        custom_style.alignment = 0
        custom_style.leftIndent = 0
        custom_style.rightIndent = 125
        custom_style.spaceAfter = 6
        custom_style.fontSize = 9
        # PAGE1
        for i in range(len(coordinates[0])):
            packet = io.BytesIO()
            doc = SimpleDocTemplate(packet, pagesize=A4)
            story = []
            story.append(Spacer(1, 50))
            volunteer_name_paragraph = Paragraph(volDetails[0][i], custom_style)
            story.append(volunteer_name_paragraph)
            doc.build(story)
            packet.seek(0)
            generated_pdf = PdfReader(packet)
            output_pdf = PdfWriter()
            template_page = template_pdf.pages[0]
            generated_page = generated_pdf.pages[0]
            translation = Transformation().translate(130, coordinates[0][i])
            generated_page.add_transformation(translation)
            template_page.merge_page(generated_page)
            output_pdf.add_page(template_page)
        with open("page1.pdf", "wb") as output_file:
            output_pdf.write(output_file)
        # PAGE2
        for i in range(len(coordinates[1])):
            packet = io.BytesIO()
            doc = SimpleDocTemplate(packet, pagesize=A4)
            story = []
            story.append(Spacer(1, 50))
            volunteer_name_paragraph = Paragraph(volDetails[1][i], custom_style)
            story.append(volunteer_name_paragraph)
            doc.build(story)
            packet.seek(0)
            generated_pdf = PdfReader(packet)
            output_pdf = PdfWriter()
            template_page = template_pdf.pages[1]
            generated_page = generated_pdf.pages[0]
            translation = Transformation().translate(130, coordinates[1][i])
            generated_page.add_transformation(translation)
            template_page.merge_page(generated_page)
            output_pdf.add_page(template_page)
        with open("page2.pdf", "wb") as output_file:
            output_pdf.write(output_file)
        # PAGE3
        for i in range(len(coordinates[2])):
            packet = io.BytesIO()
            doc = SimpleDocTemplate(packet, pagesize=A4)
            story = []
            story.append(Spacer(1, 50))
            volunteer_name_paragraph = Paragraph(volDetails[2][i], custom_style)
            story.append(volunteer_name_paragraph)
            doc.build(story)
            packet.seek(0)
            generated_pdf = PdfReader(packet)
            output_pdf = PdfWriter()
            template_page = template_pdf.pages[2]
            generated_page = generated_pdf.pages[0]
            translation = Transformation().translate(130, coordinates[2][i])
            generated_page.add_transformation(translation)
            template_page.merge_page(generated_page)
            output_pdf.add_page(template_page)

        with open("page3.pdf", "wb") as output_file:
            output_pdf.write(output_file)

        # MERGE PAGE1 & PAGE2 & PAGE3

        pdf1 = open("page1.pdf", "rb")
        pdf2 = open("page2.pdf", "rb")
        pdf3 = open("page3.pdf", "rb")
        pdf_reader1 = PdfReader(pdf1)
        pdf_reader2 = PdfReader(pdf2)
        pdf_reader3 = PdfReader(pdf3)
        pdf_writer = PdfWriter()
        for page_num in range(len(pdf_reader1.pages)):
            page = pdf_reader1.pages[page_num]
            pdf_writer.add_page(page)
        for page_num in range(len(pdf_reader2.pages)):
            page = pdf_reader2.pages[page_num]
            pdf_writer.add_page(page)
        for page_num in range(len(pdf_reader3.pages)):
            page = pdf_reader3.pages[page_num]
            pdf_writer.add_page(page)
        output = "Report.pdf"
        output_pdf = open(output, "wb")
        pdf_writer.write(output_pdf)
        pdf1.close()
        pdf2.close()
        pdf3.close()
        output_pdf.close()
        with open(output, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Report.pdf"'
        os.remove("Report.pdf")
        os.remove("page1.pdf")
        os.remove("page2.pdf")
        os.remove("page3.pdf")
        return response
    else:
        pass