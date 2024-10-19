from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages, auth
from django.contrib.auth.models import User
from authentication.models import Coordinator, Volunteer, Activity, GuardianFaculty, currentData
from authentication.commonPasswords import common_passwords
from itertools import chain
from datetime import datetime
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


def check(string):
    c = 0
    for char in string:
        if char.isalpha():
            c += 1
    if c >= 650:
        return False
    return True

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
def VDashboardView(request):
    if request.method == "GET":
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        current = currentData.objects.get(index = 'Current')
        return render(request, 'vdashboard.html', {'volunteer': volunteer, 'activity': activity, 'current' : current})
    else:
        return redirect('vdashboard')


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
        return render (request, 'rejectedReportFilling.html', {'volunteer': volunteer, 'activity': activity, 'current' : current, 'hours':hours, 'minutes':minutes, 'guardian_faculties':guardian_faculties})
    else:
        return redirect('vdashboard')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
@csrf_exempt
def reportFillingView(request):
    if request.method == 'GET':
        browser = str(request.user_agent.browser.family) + ' (Version ' + str(request.user_agent.browser.version_string) + ')'
        os = str(request.user_agent.os.family)
        device = request.user_agent.is_pc

        if not device:
            return render(request, 'report-filling-blocked.html', {'browser':browser, 'os':os})

        guardian_faculties = GuardianFaculty.objects.filter(active=True)
        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name=volunteer.activity)
        user = User.objects.get(email = request.user.email)
        hours = str(user.last_login)[11:13]
        minutes = str(user.last_login)[14:16]
        return render(request, 'reportFilling.html', {'guardian_faculties':guardian_faculties, 'activity':activity, 'volunteer':volunteer, 'hours':hours, 'minutes':minutes, 'browser':browser, 'os':os})

    if request.method == 'POST':
        q1 = request.POST['quest1']
        q2 = request.POST['quest2']
        q3 = request.POST['quest3']
        q4 = request.POST['quest4']
        q5 = request.POST['quest5']
        q6 = request.POST['quest6']
        q7 = request.POST['quest7']

        volunteer = Volunteer.objects.get(email=request.user.email)
        activity = Activity.objects.get(name = volunteer.activity)

        if check(q1)  or check(q2) or check(q3) or check(q4) or check(q5) or check(q6):
            messages.error(request, 'You have submitted the report without writing 700 characters for each question. You will have to write the report again. Your report is not submitted to us.')
            return redirect('vdashboard')

        if checkUrl(q7.strip()) != 'True':
            messages.error(request, checkUrl(q7))
            return redirect('vdashboard')

        if not activity.report_filling:
            messages.error(request, 'Now report filling is closed for ' + activity.name + '. Hence, even though you started writing your report on time, your report is not submitted to us because report filling is currently closed.')
            return redirect('vdashboard')

        volunteer.Objective_of_the_Activity = q1
        volunteer.Description_of_the_Activity = q2
        volunteer.Benefits_to_Society = q3
        volunteer.Benefits_to_Self = q4
        volunteer.Learning_Experiences_challenges = q5
        volunteer.How_did_it_help_you_to_shape_your_Empathy = q6
        volunteer.url = q7.strip()
        volunteer.submitted = 1
        volunteer.verified = 0
        volunteer.guardian_faculty = request.POST['guardian_faculty']
        volunteer.save()
        return redirect('vdashboard')


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
        messages.success(request, 'Your coordinator has been choosen as ' + str(coord))
        return redirect('vdashboard')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def VProfileView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email=request.user.email)
        return render(request, 'VProfile.html', {'volunteer':volunteer})
    else:
        volunteer = Volunteer.objects.get(email = request.user.email)
        volunteer.vname = request.POST['vname']
        volunteer.prn = request.POST['prn']
        volunteer.contact_num = request.POST['contact_num']
        volunteer.parent_num = request.POST['parent_num']
        volunteer.gender = request.POST['gender']
        volunteer.blood_group = request.POST['blood_group']
        volunteer.div = request.POST['div']
        volunteer.current_add = request.POST['current_add']
        volunteer.profile_edited = datetime.now().strftime("%d-%m-%Y")
        volunteer.save()
        user = User.objects.get(email = request.user.email)
        user.username = request.POST['vname']
        user.save()
        messages.success(request, 'Your profile was updated successfully!')
        return redirect('vdashboard')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def SetpasswordPageView(request):
    if request.method == 'POST':
        password = request.POST["password"]
        password = password.strip()
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
            messages.error(request, 'This email is in use by another user.')
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
def attendanceView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email=request.user.email)
        attendance = (Volunteer.objects.get(email=request.user.email)).attendance
        if '.' in attendance:
            attendance = attendance[1:]
            volunteer.attendance = attendance
            volunteer.save()
        att = {}
        present = 0
        total = 0
        for i in range(0,len(attendance), 11):
            date = attendance[i+1:i+11]
            total += 1
            if (attendance[i] == '$'):
                att[date] = 'Present'
                present += 1
            else:
                att[date] = 'Absent'
        if total == 0:
            return render(request, 'viewattendance.html', {'att':att, 'volunteer': volunteer, 'percentage' : total})
        percentage = round((present/total)*100)

        sorted_keys = sorted(att.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
        sorted_date_dict = {key: att[key] for key in sorted_keys}
        att.clear()
        att.update(sorted_date_dict)
        return render(request, 'viewattendance.html', {'att':att, 'volunteer': volunteer, 'percentage' : percentage})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/a/login-restricted')
def downloadCertificateView(request):
    if request.method == 'GET':
        volunteer = Volunteer.objects.get(email = request.user.email)
        if volunteer.verified != 1:
            messages.error(request, 'Report not verified.')
            return redirect('vdashboard')

        packet = io.BytesIO()
        canvasObj = canvas.Canvas(packet, pagesize=landscape(A3))
        canvasObj.setFont("Times-Bold", 27)
        width, height = A3
        text_width = canvasObj.stringWidth(volunteer.vname, "Times-Bold", 27)
        x_center = (width - text_width) / 2
        canvasObj.drawString(x_center, 330, volunteer.vname)
        canvasObj.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        activity = (volunteer.activity).replace(" ", "_")
        template_path = "/home/swdc/SWDCWebsite/certificateTemplates/" + activity + "/" + activity + "_" + volunteer.registered_academic_year + "_" + str(volunteer.registered_semester) + ".pdf"
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
            messages.error(request, 'Report not verified.')
            return redirect('vdashboard')
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
                    volunteer.Objective_of_the_Activity,
                    volunteer.Description_of_the_Activity,
                ],
                [
                    volunteer.Benefits_to_Society,
                    volunteer.Benefits_to_Self,
                    volunteer.Learning_Experiences_challenges,
                ],
                [volunteer.How_did_it_help_you_to_shape_your_Empathy, volunteer.url],
            ]
        coordinates = [
                [45, 12, -18, -45, -72, -100, -130, -155, -185, -215, -270, -295, -470],
                [50, -165, -385],
                [50, -170],
            ]
        base_path = '/home/swdc/SWDCWebsite/'
        template_pdf = PdfReader(open( base_path +"certificateTemplates/ReportTemplate.pdf", "rb"))

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