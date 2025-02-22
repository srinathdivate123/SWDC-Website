from django.shortcuts import render, redirect
from django.core.files import File
import os, qrcode, io, PyPDF2, platform, base64
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages, auth
from django.contrib.auth.models import User
from authentication.models import Volunteer, Coordinator, Secretary, Activity, GuardianFaculty, Event, Attendance, currentData
from authentication.commonPasswords import common_passwords
from datetime import datetime
from django.core.mail import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A3, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import Transformation
from django.template.loader import render_to_string
from .captcha import FormWithCaptcha




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ReportVerificationView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        GP2 = Volunteer.objects.filter(submitted=1, verified=0, Cordinator=coordinator.cname, activity=coordinator.activity, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        flagship_event = Volunteer.objects.filter(submitted=1, verified=0, Cordinator=coordinator.cname, activity=coordinator.flagshipEvent, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        verified = Volunteer.objects.filter(submitted=1, verified=1, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        rejected = Volunteer.objects.filter(submitted=0, verified=2, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        failed = Volunteer.objects.filter(verified=3, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        return render(request, "report_verification.html", {"volunteers_done_GP2": GP2, "volunteers_done_flagship_event": flagship_event, "volunteers_verified": verified, "volunteers_rejected": rejected, "volunteers_failed": failed, "coordinator": coordinator})
    else:
        email = request.POST["email"]
        volunteer = Volunteer.objects.get(email=email)
        activity = Activity.objects.get(name=volunteer.activity)
        return render(request, "ViewVolunteer.html", {"volunteer": volunteer, "activity": activity, "form":FormWithCaptcha()})






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ContactUsView(request):
    return render(request, 'contactus.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def activityAttendance(request):
    if request.method == 'POST':
        coord = Coordinator.objects.get(email=request.user.email)
        att_date = request.POST.get('date')
        # att_date = att_date[8:] + att_date[4:8] + att_date[:4]
        vol_attendance = request.POST.getlist('attendance')
        eventType = request.POST.get('eventType')

        for vol in vol_attendance:
            try:
                volunteer = Volunteer.objects.get(email=vol)
                idx = volunteer.attendance.find(att_date)

                if idx != -1:
                    volunteer.attendance = volunteer.attendance[:idx-1] + '$' + volunteer.attendance[idx:]
                else:
                    volunteer.attendance += '$' + att_date + ', '

                volunteer.save()

                Attendance.objects.create(
                    coord_prn=coord.prn,
                    coord_name=coord.cname,
                    activity=volunteer.activity,
                    vol_name=volunteer.vname,
                    vol_prn=volunteer.prn,
                    geo_photo="Manual Attendance",
                    time=datetime.now()
                )

            except Volunteer.DoesNotExist:
                print(f"Volunteer with email {vol} not found.")

        if eventType == 'SS':
            messages.success(request,"Hurray! Attendance for "+ coord.activity + " marked successfully!")
        else:
            messages.success(request,"Hurray! Attendance for "+ coord.flagshipEvent + " marked successfully!")

    return render(request,'activityAttendance.html')


AASHAKIRAN = {
    "CS-L": ["1-16", "17-32", "33-48", "49-64", "65-78"],
    "IT-F": ["1-15", "16-31", "32-47", "48-63", "64-77"]
}


def FetchVolunteers(request):
    if request.method == 'POST':
        coord = Coordinator.objects.get(email=request.user.email)
        activity = coord.activity
        eventDate = request.POST.get('date')

        if not eventDate:
            messages.error(request, "Please select a date to mark attendance!")
            return redirect('activityAttendance')

        events = []
        flagshipEvents = []

        if coord.activity:
            events = Event.objects.filter(date=eventDate, activity=coord.activity)
        if coord.flagshipEvent:
            flagshipEvents = Event.objects.filter(date=eventDate, activity=coord.flagshipEvent)

        eventDate = eventDate[8:] + eventDate[4:8] + eventDate[:4]
        vols = {}
        flagshipVols = {}

        for event in events:
            divisions = event.divisions.split(',')

            #Only for Aashakiran
            if activity == "Aashakiran":
                for div in divisions:
                    temp = []
                    dept, division, group = div.split('-')
                    group = int(group) - 1

                    min_roll, max_roll = AASHAKIRAN[dept + '-' + division][group].split('-')
                    min_roll = int(min_roll)
                    max_roll = int(max_roll)

                    volunteers = Volunteer.objects.filter(activity=activity, div=division, dept=dept, roll__range=(min_roll, max_roll))
                    for volunteer in volunteers:
                        index = volunteer.attendance.find(eventDate)
                        if index == -1 or volunteer.attendance[index-1] != '$':
                            temp.append(volunteer)

                    vols[div] = temp

            else:
                for div in divisions:
                    temp = []
                    if div.count('-') == 1:
                        dept, division = div.split('-')
                        volunteers = Volunteer.objects.filter(activity=activity, div=division, dept=dept)
                        for volunteer in volunteers:
                            index = volunteer.attendance.find(eventDate)
                            if index == -1 or volunteer.attendance[index-1] != '$':
                                temp.append(volunteer)
                    else:
                        dept, division, group = div.split('-')
                        group = int(group) - 1

                        min_roll, max_roll = settings.GROUPS[activity][group].split('-')
                        min_roll = int(min_roll)
                        max_roll = int(max_roll)

                        volunteers = Volunteer.objects.filter(activity=activity, div=division, dept=dept, roll__range=(min_roll, max_roll))
                        for volunteer in volunteers:
                            index = volunteer.attendance.find(eventDate)
                            if index == -1 or volunteer.attendance[index-1] != '$':
                                temp.append(volunteer)

                    vols[div] = temp

        activity = coord.flagshipEvent

        for event in flagshipEvents:
            divisions = event.divisions.split(',')

            for div in divisions:
                temp = []
                if div.count('-') == 1:
                    dept, division = div.split('-')
                    volunteers = Volunteer.objects.filter(activity=activity, div=division, dept=dept)
                    for volunteer in volunteers:
                        index = volunteer.attendance.find(eventDate)
                        if index == -1 or volunteer.attendance[index-1] != '$':
                            temp.append(volunteer)
                else:
                    dept, division, group = div.split('-')
                    group = int(group) - 1
                    print(group)

                    try:
                        min_roll, max_roll = settings.GROUPS[activity][group].split('-')
                        min_roll = int(min_roll)
                        max_roll = int(max_roll)
                    except Exception as e:
                        return render(request,'activityAttendance.html', {'volunteers': activity})

                    volunteers = Volunteer.objects.filter(activity=activity, div=division, dept=dept, roll__range=(min_roll, max_roll))
                    for volunteer in volunteers:
                        index = volunteer.attendance.find(eventDate)
                        if index == -1 or volunteer.attendance[index-1] != '$':
                            temp.append(volunteer)

                flagshipVols[div] = temp

        return render(request,'activityAttendance.html', {'volunteers': vols, 'date': eventDate, 'flagshipVols': flagshipVols})
    return redirect('activityAttendance')




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def CoordDashboardView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        GP2 = Volunteer.objects.filter(submitted=1, verified=0, Cordinator=coordinator.cname, activity=coordinator.activity, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        flagship_event = Volunteer.objects.filter(submitted=1, verified=0, Cordinator=coordinator.cname, activity=coordinator.flagshipEvent, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        verified = Volunteer.objects.filter(submitted=1, verified=1, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        rejected = Volunteer.objects.filter(submitted=0, verified=2, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        failed = Volunteer.objects.filter(verified=3, Cordinator=coordinator.cname, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        return render(request, "cdashboard.html", {"volunteers_done_GP2": GP2, "volunteers_done_flagship_event": flagship_event, "volunteers_verified": verified, "volunteers_rejected": rejected, "volunteers_failed": failed, "coordinator": coordinator})
    else:
        email = request.POST["email"]
        volunteer = Volunteer.objects.get(email=email)
        activity = Activity.objects.get(name=volunteer.activity)
        return render(request, "ViewVolunteer.html", {"volunteer": volunteer, "activity": activity, "form":FormWithCaptcha()})






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def AttendanceView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        volunteers_done_GP2 = Volunteer.objects.filter(Cordinator=coordinator.cname, activity=coordinator.activity, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        volunteers_done_FE = Volunteer.objects.filter(Cordinator=coordinator.cname, activity=coordinator.flagshipEvent, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        date = datetime.now().date().strftime("%d-%m-%Y")
        maxDate = datetime.now().date().strftime("%Y-%m-%d")
        return render(request, "attendance.html", {"coordinator": coordinator, "volunteers_done_GP2": volunteers_done_GP2, "volunteers_done_FE": volunteers_done_FE, "date": date, "coordinator": coordinator, "maxDate": maxDate})
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def markPreviousGP2Attendance(request):
    coordinator = Coordinator.objects.get(email=request.user.email)

    if request.method == "POST":
        date = request.POST["date"]
        date = date[8:] + date[4:8] + date[:4]

        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken" or volunteer_email == "date":
                continue
            volunteer = Volunteer.objects.get(email = volunteer_email)
            if attendance == 'Present':
                volunteer.attendance += "$" + str(date)
            elif attendance == 'Absent':
                volunteer.attendance += "!" + str(date)
            volunteer.save()

        messages.success(request, coordinator.activity + "'s attendence successfully marked for " + date)
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def markPreviousFEAttendance(request):
    coordinator = Coordinator.objects.get(email=request.user.email)

    if request.method == "POST":
        date = request.POST["date"]
        date = date[8:] + date[4:8] + date[:4]

        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken" or volunteer_email == "date":
                continue
            volunteer = Volunteer.objects.get(email = volunteer_email)
            if attendance == 'Present':
                volunteer.attendance += "$" + str(date)
            elif attendance == 'Absent':
                volunteer.attendance += "!" + str(date)
            volunteer.save()

        messages.success(request, coordinator.flagshipEvent + "'s attendence successfully marked for " + date)
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def Mark_GP2_IN_AttendanceView(request):
    coordinator = Coordinator.objects.get(email=request.user.email)
    if request.method == "POST":
        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken":
                continue
            volunteer = Volunteer.objects.get(email=volunteer_email)
            if attendance == 'Present':
                volunteer.marked_IN_attendance = True
            elif attendance == 'Absent':
                volunteer.marked_IN_attendance = False
            else:
                volunteer.marked_IN_attendance = None
            volunteer.save()
        coordinator.marked_IN_GP2 = True
        coordinator.save()
        messages.success(request,"Hurray! IN-Attendance for "+ coordinator.activity+ " marked successfully!")
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def Mark_GP2_OUT_AttendanceView(request):
    coordinator = Coordinator.objects.get(email=request.user.email)
    if request.method == "POST":
        date = datetime.now().date().strftime("%d-%m-%Y")

        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken":
                continue
            volunteer = Volunteer.objects.get(email=volunteer_email)

            if attendance == 'Present':
                if volunteer.marked_IN_attendance == True:
                    volunteer.attendance += "$" + str(date)
                    volunteer.save()
                elif volunteer.marked_IN_attendance == False:
                    volunteer.attendance += "!" + str(date)
                    volunteer.save()
            elif attendance == 'Absent':
                volunteer.attendance += "!" + str(date)
                volunteer.save()
            volunteer.marked_IN_attendance = False
            volunteer.save()
        coordinator.marked_attendance_GP2 = True
        coordinator.save()
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def Mark_FE_IN_AttendanceView(request):
    coordinator = Coordinator.objects.get(email=request.user.email)
    if request.method == "POST":
        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken":
                continue
            volunteer = Volunteer.objects.get(email=volunteer_email)
            if attendance == 'Present':
                volunteer.marked_IN_attendance = True
            elif attendance == 'Absent':
                volunteer.marked_IN_attendance = False
            else:
                volunteer.marked_IN_attendance = None
            volunteer.save()
        coordinator.marked_IN_FE = True
        coordinator.save()
        messages.success(request,"Hurray! IN-Attendance for "+ coordinator.flagshipEvent+ " marked successfully!")
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def Mark_FE_OUT_AttendanceView(request):
    coordinator = Coordinator.objects.get(email=request.user.email)
    if request.method == "POST":
        date = datetime.now().date().strftime("%d-%m-%Y")

        for volunteer_email, attendance in request.POST.items():
            if volunteer_email == "csrfmiddlewaretoken":
                continue
            volunteer = Volunteer.objects.get(email=volunteer_email)
            if attendance == 'Present':
                if volunteer.marked_IN_attendance == True:
                    volunteer.attendance += "$" + str(date)
                    volunteer.save()
                elif volunteer.marked_IN_attendance == False:
                    volunteer.attendance += "!" + str(date)
                    volunteer.save()
            elif attendance == 'Absent':
                volunteer.attendance += "!" + str(date)
                volunteer.save()
            volunteer.marked_IN_attendance = False
            volunteer.save()
        coordinator.marked_attendance_FE = True
        coordinator.save()
        return redirect("attendance")
    else:
        return redirect("attendance")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def viewVolunteerAttendanceView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        volunteers_doing_SS = Volunteer.objects.filter(Cordinator=coordinator.cname, activity=coordinator.activity, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        SS_data = []
        for volunteer in volunteers_doing_SS:
            SS_att = {}
            attendance = volunteer.attendance
            if '.' in attendance:
                attendance = attendance[1:]
                volunteer.attendance = attendance
                volunteer.save()
            for i in range(0, len(attendance), 11):
                date = attendance[i + 1 : i + 11]
                if attendance[i] == "$":
                    SS_att[date] = "Present"
                else:
                    SS_att[date] = "Absent"
            sorted_keys = sorted(SS_att.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
            sorted_date_dict = {key: SS_att[key] for key in sorted_keys}
            SS_att.clear()
            SS_att.update(sorted_date_dict)
            SS_data.append({volunteer.vname: SS_att})

        volunteers_doing_FE = Volunteer.objects.filter(Cordinator=coordinator.cname, activity=coordinator.flagshipEvent, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        FE_data = []
        for volunteer in volunteers_doing_FE:
            FE_att = {}
            attendance = volunteer.attendance
            if '.' in attendance:
                attendance = attendance[1:]
                volunteer.attendance = attendance
                volunteer.save()
            for i in range(0, len(volunteer.attendance), 11):
                date = volunteer.attendance[i + 1 : i + 11]
                if volunteer.attendance[i] == "$":
                    FE_att[date] = "Present"
                else:
                    FE_att[date] = "Absent"
            sorted_keys = sorted(FE_att.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
            sorted_date_dict = {key: FE_att[key] for key in sorted_keys}
            FE_att.clear()
            FE_att.update(sorted_date_dict)
            FE_data.append({volunteer.vname: FE_att})
        return render(request, "volunteerAttendance.html", {"SS_data": SS_data, "FE_data": FE_data, "coordinator": coordinator})





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def FormFillingView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        secretaries = Secretary.objects.filter(domain=coordinator.domain, registered_academic_year=coordinator.registered_academic_year, registered_semester=coordinator.registered_semester)
        return render(request, "cFormFilling.html", {"coordinator": coordinator, "secretaries": secretaries})
    else:
        coordinator = Coordinator.objects.get(email=request.user.email)
        coordinator.ans1 = request.POST["quest1"]
        coordinator.ans2 = request.POST["quest2"]
        coordinator.ans3 = request.POST["quest3"]
        coordinator.ans4 = request.POST["quest4"]
        coordinator.ans5 = request.POST["quest5"]
        coordinator.ans6 = request.POST["quest6"]
        coordinator.url = request.POST["quest7"]
        coordinator.Secretary = request.POST["Secretary"]
        coordinator.submitted = 1
        coordinator.verified = 0
        coordinator.save()
        return redirect("cFormFilling")





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def SetpasswordPageView(request):
    if request.method == "GET":
        coordinator = Coordinator.objects.get(email=request.user.email)
        return render(request, "CPassword.html")
    else:
        password = request.POST["password"]
        password = password.strip()
        if password in common_passwords:
            messages.error(request, "This password is too common. Choose a safer one.")
            return redirect("cresetpass")
        user = User.objects.get(username=request.user.username)
        user.set_password(password)
        user.save()
        coordinator = Coordinator.objects.get(email=request.user.email)
        coordinator.password_changed = True
        coordinator.save()
        auth.logout(request)
        messages.success(request, "Your password was changed successfully! Please login again!")
        return redirect("login")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def EventsView(request):
    if request.method == "GET":
        current = currentData.objects.get(index='Current')
        flagship_events = Activity.objects.filter(registration_enabled=True, flagship_event=True)
        activities = Activity.objects.filter(registration_enabled=True, flagship_event=False)
        coordinator = Coordinator.objects.get(email=request.user.email)

        activity_data = f"PRN: {coordinator.prn}\nName: {coordinator.cname}\nActivity: {coordinator.activity}"
        flagshipEvent_data = f"PRN: {coordinator.prn}\nName: {coordinator.cname}\nActivity: {coordinator.flagshipEvent}"


        activity_qr = qrcode.QRCode(box_size=10, border=5)
        activity_qr.add_data(activity_data)
        activity_qr.make(fit=True)

        flagshipEvent_qr = qrcode.QRCode(box_size=10, border=5)
        flagshipEvent_qr.add_data(flagshipEvent_data)
        flagshipEvent_qr.make(fit=True)

        activity_img = activity_qr.make_image(fill="black", back_color="white")
        flagshipEvent_img = flagshipEvent_qr.make_image(fill="black", back_color="white")


        activity_buffer = io.BytesIO()
        activity_img.save(activity_buffer, format="PNG")
        activity_buffer.seek(0)
        activity_base64 = base64.b64encode(activity_buffer.getvalue()).decode()

        flagshipEvent_buffer = io.BytesIO()
        flagshipEvent_img.save(flagshipEvent_buffer, format="PNG")
        flagshipEvent_buffer.seek(0)
        flagshipevent_base64 = base64.b64encode(flagshipEvent_buffer.getvalue()).decode()



        return render(request, "events.html", {"flagship_events": flagship_events, "activities": activities, "coordinator": coordinator, 'activity_qr': activity_base64, 'flagshipEvent_qr': flagshipevent_base64, "current": current})
    else:
        return redirect("events")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ChooseSocialActivityView(request):
    if request.method == "POST":
        if request.POST['social_activity_chosen'] == 'Choose...':
            messages.error(request, 'Choose an activity.')
            return redirect("events")

        current = currentData.objects.get(index='Current')
        coordinator = Coordinator.objects.get(email=request.user.email)
        coordinator.activity = request.POST["social_activity_chosen"]
        coordinator.registered_academic_year = current.AcademicYear
        coordinator.registered_semester = current.Semester
        coordinator.save()
        return redirect("events")
    else:
        return redirect("events")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ChooseFlagshipEventView(request):
    if request.method == "POST":
        if request.POST['flagship_event_chosen'] == 'Choose...':
            messages.error(request, 'Choose a Flagship Event.')
            return redirect("events")

        current = currentData.objects.get(index='Current')
        coordinator = Coordinator.objects.get(email=request.user.email)
        coordinator.flagshipEvent = request.POST["flagship_event_chosen"]
        coordinator.registered_academic_year = current.AcademicYear
        coordinator.registered_semester = current.Semester
        coordinator.save()
        return redirect("events")
    else:
        return redirect("events")





def formatMessage(message):
    finalMsg = []
    msgPart = ""
    for char in message:
        if char == "$":
            finalMsg.append(msgPart)
            msgPart = ""
            continue
        msgPart += char
    return finalMsg





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ApproveVolunteer(request):
    if request.method == "GET":
        return redirect("report-verification")
    if request.method == "POST":
        # if not FormWithCaptcha(request.POST).is_valid():
        #     messages.error(request, 'Please verify that you are not a robot, only then you can approve the report.')
        #     return redirect('report-verification')
        volunteer = Volunteer.objects.get(email=request.POST["email"])
        if volunteer.verified == 1 and volunteer.submitted == 1:
            return redirect("report-verification")

        # attendance = int(request.POST["attendance"].split("%")[0])

        # if (not attendance) or attendance < 0 or attendance > 100:
        #     messages.error(request, "Enter valid Attendance Percentage (between 0 to 100).")
        #     return redirect("report-verification")

        attendance = request.POST.get("attendance", "No")

        if attendance == "Yes":
            attendance = True
        else:
            attendance = False

        try:
            if (not request.POST["reportMarks"]) or int(request.POST["reportMarks"]) < 0 or int(request.POST["reportMarks"]) > 15:
                messages.error(request, "Enter valid Report Filling marks (between 0 to 15).")
                return redirect("report-verification")
        except:
            messages.error(request, "Enter numeric Report Filling marks (between 0 to 15).")
            return redirect("report-verification")

        try:
            if (not request.POST["dataCollection"]) or int(request.POST["dataCollection"]) < 0 or int(request.POST["dataCollection"]) > 10:
                messages.error(request, "Enter valid Data Collection marks (between 0 to 10).")
                return redirect("report-verification")
        except:
            messages.error(request, "Enter numeric Data Collection marks (between 0 to 10).")
            return redirect("report-verification")

        try:
            activity = (volunteer.activity).replace(" ", "_")
            formatedMsg = formatMessage(Activity.objects.get(name=volunteer.activity).message)

            if attendance:
                formatedMsg.append("You can login and view that you have cleared the course. You can also, anytime in the future, download your Activity Certificate & Report through this login link : https://swdc.pythonanywhere.com/a/login")
            else:
                formatedMsg.append("Although you have successfully completed the course, your attendance is below 50%, so you are not eligible for an official certificate.")
            formatedMsg.append("This mail and the attached documents are important as they will serve as a proof that you have cleared the 'Social Services Course' in your Freshman Year, so we request you to not delete this mail and keep it safe for future reference.")
            context = {"name": volunteer.vname, "messages": formatedMsg}
            email_body = render_to_string("email_template.html", context)
            email_subject = "Hurray! You\'ve cleared the Social Services Course"
            email = EmailMessage(email_subject, email_body, "noreply@semycolon.com", [volunteer.email])
            email.content_subtype = "html"

            if attendance:
                # Code for generating Course Completion Certificate!
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

                # Use this template_path if every activity has its own certificate.
                template_path = os.path.join(settings.BASE_DIR, 'certificateTemplates') + "/" + activity + "/" + activity + "_" + volunteer.registered_academic_year + "_" + str(volunteer.registered_semester) + ".pdf"
                # template_path = os.path.join(settings.BASE_DIR, 'certificateTemplates') + "/certificateTemplate.pdf"

                certificate_template = PdfReader(open(template_path, "rb"))
                output = PdfWriter()
                page = certificate_template.pages[0]
                page.merge_page(new_pdf.pages[0])
                output.add_page(page)
                pdf_file_path = os.path.join(settings.BASE_DIR, "Certificate.pdf")
                output_stream = open(pdf_file_path, "wb")
                output.write(output_stream)
                output_stream.close()
                with open(pdf_file_path, "rb") as pdf_file:
                    completion_certificate = MIMEBase("application", "octet-stream")
                    completion_certificate.set_payload(pdf_file.read())
                encoders.encode_base64(completion_certificate)
                completion_certificate.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(pdf_file_path)}"',
                )
                email.attach(completion_certificate)
                os.remove(pdf_file_path)
                # End

            # Code for generating Activity Report
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
            custom_style.spaceAfter = 8

            max_ans = max(len(volunteer.ans1), max(len(volunteer.ans2), max(len(volunteer.ans3), max(len(volunteer.ans4), max(len(volunteer.ans5), len(volunteer.ans6))))))

            if max_ans > 1100:
                custom_style.fontSize = 7
            elif max_ans > 850:
                custom_style.fontSize = 8
            else:
                custom_style.fontSize = 10

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


            with open(output, "rb") as pdf_file:
                report = MIMEBase("application", "octet-stream")
                report.set_payload(pdf_file.read())
            encoders.encode_base64(report)
            report.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(output)}"',
            )
            email.attach(report)
            email.send(fail_silently=False)
            os.remove("Report.pdf")
            os.remove("page1.pdf")
            os.remove("page2.pdf")
            os.remove("page3.pdf")
            volunteer.verified = 1
            volunteer.reportFillingMarks = int(request.POST["reportMarks"])
            volunteer.dataCollectionMarks = int(request.POST["dataCollection"])
            volunteer.save()
            messages.success(request, "Volunteer " + volunteer.vname + " verified successfully!")
            return redirect("report-verification")

        except Exception as error:
            volunteer.verified = 0
            volunteer.save()
            print("Error while sending certificate - " + str(error))
            messages.error(request, "There was an error, please try again. "+str(error))
            return redirect("report-verification")
        # messages.success(request, "Volunteer " + volunteer.vname + " verified successfully!")
        # return redirect("report-verification")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def rejectVolunteerView(request):
    if request.method == "POST":
        volunteer = Volunteer.objects.get(email=request.POST["email"])
        volunteer.verified = 2
        volunteer.submitted = 0
        volunteer.rejection_count += 1
        volunteer.rejection_reason = request.POST["rejection_reason"]
        volunteer.save()
        email_subject = "Oops! Your " + volunteer.activity + "'s Report Was Rejected "
        formatedMsg = []
        formatedMsg.append("The report you submitted for " + volunteer.activity + " has been rejected. The reason, as stated by " + volunteer.Cordinator + ", is:")
        formatedMsg.append('"' + request.POST["rejection_reason"] + '"')
        formatedMsg.append("Please edit and re-submit your report here as soon as possible: https://swdc.pythonanywhere.com/a/login")
        context = {"name": volunteer.vname, "messages": formatedMsg}
        email_body = render_to_string("email_template.html", context)
        email = EmailMessage(email_subject, email_body, "noreply@semycolon.com", [volunteer.email])
        email.content_subtype = "html"
        email.send(fail_silently=False)
        messages.info(request, "Volunteer " + volunteer.vname + " rejected. They have been mailed to fill the report again.")
        return redirect("report-verification")
    else:
        return redirect("report-verification")






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def failVolunteerView(request):
    if request.method == "POST":
        volunteer = Volunteer.objects.get(email=request.POST["email"])
        volunteer.verified = 3
        volunteer.submitted = 1
        volunteer.rejection_reason = request.POST["fail_reason"]
        volunteer.save()
        email_subject = "Failure in completing the Social Services Course"
        formatedMsg = []
        formatedMsg.append("The 'Social Services' course required active participation, with successful completion of " + volunteer.activity + " being the primary criterion for passing.")
        formatedMsg.append("Regrettably, we are informing you that you have Failed in the 'Social Services' course.")
        formatedMsg.append("The reason, as stated by " + volunteer.Cordinator + ", is:")
        formatedMsg.append('"' + request.POST["fail_reason"] + '"')
        context = {"name": volunteer.vname, "messages": formatedMsg}
        email_body = render_to_string("email_template.html", context)
        email = EmailMessage(email_subject, email_body, "noreply@semycolon.com", [volunteer.email])
        email.content_subtype = "html"
        email.send(fail_silently=False)
        messages.info(request, "Volunteer " + volunteer.vname + " has been marked as failed. They have been mailed about it. They cannot submit the report again")
        return redirect("report-verification")
    if request.method == "GET":
        return redirect("report-verification")





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def CShowSSCertificate(request):
    if request.method == 'GET':
        coordinator = Coordinator.objects.get(email = request.user.email)
        act = coordinator.activity.replace(" ", "_")
        if act == 'not_chosen' or act == '' or act == '.':
            messages.error(request, 'Oops! There was an error')
            return redirect("report-verification")

        # Use this template_path if every activity has its own certificate.
        template_path = os.path.join(settings.BASE_DIR, "certificateTemplates") + "/" + act + "/" + act + "_" + coordinator.registered_academic_year + "_" + str(coordinator.registered_semester) + ".pdf"
        # template_path = os.path.join(settings.BASE_DIR, 'certificateTemplates') + "/certificateTemplate.pdf"

        if not os.path.exists(template_path):
            messages.error(request, coordinator.activity + '\'s certificate is not available on our servers.')
            return redirect("report-verification")

        try:
            certificate_template = PdfReader(open(template_path, "rb"))
            packet = io.BytesIO()
            output_buffer = io.BytesIO()
            canvasObj = canvas.Canvas(packet, pagesize=landscape(A3))
            canvasObj.setFont("Times-Bold", 27)
            width, height = A3
            text_width = canvasObj.stringWidth('Volunteer Name', "Times-Roman", 27)
            x_center = (width - text_width) / 2
            canvasObj.drawString(x_center, settings.COORDINATE[act], 'Volunteer Name')
            canvasObj.save()
            packet.seek(0)
            new_pdf = PdfReader(packet)
            output = PdfWriter()
            page = certificate_template.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            output.write(output_buffer)
            output_buffer.seek(0)
            response = HttpResponse(output_buffer, content_type='application/pdf')
            messages.success(request, 'Certificate found.')
            return response
        except Exception as e:
            messages.error(request, e)
            return None
    else:
        messages.error(request, 'Not allowed.')
        return redirect('report-verification')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def CShowFECertificate(request):
    if request.method == 'GET':
        coordinator = Coordinator.objects.get(email = request.user.email)
        act = coordinator.flagshipEvent.replace(" ", "_")
        if act == 'not_chosen' or act == '' or act == '.':
            messages.error(request, 'Oops! There was an error')
            return redirect("report-verification")

        # Use this template_path if every activity has its own certificate.
        template_path = os.path.join(settings.BASE_DIR, "certificateTemplates") + act + "/" + act + "_" + coordinator.registered_academic_year + "_" + str(coordinator.registered_semester) + ".pdf"
        # template_path = os.path.join(settings.BASE_DIR, 'certificateTemplates') + "/certificateTemplate.pdf"

        if not os.path.exists(template_path):
            messages.error(request, coordinator.flagshipEvent + '\'s certificate is not available on our servers.')
            return redirect("report-verification")
        certificate_template = PdfReader(open(template_path, "rb"))
        packet = io.BytesIO()
        output_buffer = io.BytesIO()
        canvasObj = canvas.Canvas(packet, pagesize=landscape(A3))
        canvasObj.setFont("Times-Bold", 27)
        width, height = A3
        text_width = canvasObj.stringWidth('Volunteer Name', "Times-Roman", 27)
        x_center = (width - text_width) / 2
        canvasObj.drawString(x_center, settings.COORDINATE[act], 'Volunteer Name')
        canvasObj.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        output = PdfWriter()
        page = certificate_template.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        output.write(output_buffer)
        output_buffer.seek(0)
        response = HttpResponse(output_buffer, content_type='application/pdf')
        return response
    else:
        messages.error(request, 'Not allowed.')
        return redirect('report-verification')





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def showReport(request):
    if request.method == 'GET':
        template_path = os.path.join(settings.BASE_DIR, "certificateTemplates/ReportTemplate.pdf")
        with open(template_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pdf_writer = PyPDF2.PdfWriter()
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)
            output_pdf = io.BytesIO()
            pdf_writer.write(output_pdf)
            output_pdf.seek(0)
            response = HttpResponse(output_pdf, content_type='application/pdf')
            return response
    else:
        messages.error(request, 'Not allowed.')
        return redirect('report-verification')






@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ReportFillingSampleView(request):
    if request.method == 'GET':
        guardian_faculties = GuardianFaculty.objects.all()
        user = User.objects.get(email = request.user.email)
        hours = str(user.last_login)[11:13]
        minutes = str(user.last_login)[14:16]
        return render(request, 'c-sample-report-filling.html', {'guardian_faculties':guardian_faculties, 'hours':hours, 'minutes':minutes})
    else:
        messages.error(request, 'Not allowed.')
        return redirect('report-verification')