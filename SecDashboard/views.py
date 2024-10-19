from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib import messages, auth
from django.contrib.auth.models import User
from authentication.models import Coordinator, Secretary, Volunteer, Activity, GuardianFaculty
from authentication.commonPasswords import common_passwords
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import os
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A3
import PyPDF2
from datetime import datetime
from openpyxl import Workbook

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def SecDashboardView(request):
    if request.method == "GET":
        secretary = Secretary.objects.get(email=request.user.email)
        coordinators = Coordinator.objects.filter(
            submitted=1,
            Secretary=request.user.username,
            verified=0,
            registered_academic_year=secretary.registered_academic_year,
            registered_semester=secretary.registered_semester,
        )
        return render(
            request,
            "sdashboard.html",
            {"coordinators": coordinators, "secretary": secretary},
        )
    else:
        email = request.POST["email"]
        coordinator = Coordinator.objects.get(email=email)
        return render(request, "ViewCoord.html", {"coordinator": coordinator})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def viewVolunteerAttendanceView(request):
    if request.method == "POST":
        email = request.POST["email"]
        secretary = Secretary.objects.get(email=request.user.email)
        coordinator = Coordinator.objects.get(email=email)
        volunteers = Volunteer.objects.filter(
            Cordinator=coordinator.cname,
            activity=secretary.activity,
            registered_academic_year=secretary.registered_academic_year,
            registered_semester=secretary.registered_semester,
        )
        data = []
        for volunteer in volunteers:
            att = {}
            attendance = volunteer.attendance
            if "." in attendance:
                attendance = attendance[1:]
                volunteer.attendance = attendance
                volunteer.save()
            for i in range(0, len(attendance), 11):
                date = attendance[i + 1 : i + 11]
                if attendance[i] == "$":
                    att[date] = "Present"
                else:
                    att[date] = "Absent"
            sorted_keys = sorted(att.keys(), key=lambda x: datetime.strptime(x, '%d-%m-%Y'))
            sorted_date_dict = {key: att[key] for key in sorted_keys}
            att.clear()
            att.update(sorted_date_dict)
            data.append({volunteer.vname: att})
        return render(
            request,
            "view_volunteer_attendance.html",
            {"data": data, "coordinator": coordinator, "secretary": secretary},
        )
    else:
        return redirect("coord-details")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/auth/login-restricted")
def volunteersDataDownloadView(request):
    secretary = Secretary.objects.get(email=request.user.email)
    activity = Activity.objects.get(name = secretary.activity)
    volunteers = Volunteer.objects.filter(activity = secretary.activity, registered_academic_year = secretary.registered_academic_year,registered_semester = secretary.registered_semester)

    if request.method == "GET":
        not_yet_submitted = 0
        submitted_yet_to_be_verified = 0
        verified = 0
        rejected = 0
        failed_by_coords = 0
        total = 0
        failed_for_not_submitting_report = 0
        for v in volunteers:
            total += 1
            if v.submitted == 0 and v.verified == 0:
                not_yet_submitted += 1
            elif v.submitted == 1 and v.verified == 0:
                submitted_yet_to_be_verified += 1
            elif v.submitted == 1 and v.verified == 1:
                verified += 1
            elif v.submitted == 0 and v.verified == 2:
                rejected += 1
            elif v.submitted == 1 and v.verified == 3:
                failed_by_coords += 1
            elif v.submitted == 0 and v.verified == 3:
                failed_for_not_submitting_report += 1
        v_yet_to_verified = Volunteer.objects.filter(activity = secretary.activity, registered_academic_year = secretary.registered_academic_year,registered_semester = secretary.registered_semester, submitted = 1, verified = 0)
        c_yet_to_verify = {}

        for v in v_yet_to_verified:
            if c_yet_to_verify.get(v.Cordinator) is not None:
                c_yet_to_verify[v.Cordinator] += 1
            else:
                c_yet_to_verify[v.Cordinator] = 1
        c_yet_to_verify = dict(sorted(c_yet_to_verify.items()))

        context = {
            'activity' : activity,
            'secretary' : secretary,
            'not_yet_submitted' : not_yet_submitted,
            'submitted_yet_to_be_verified' : submitted_yet_to_be_verified,
            'verified' : verified,
            'rejected' : rejected,
            'failed_by_coords' : failed_by_coords,
            'failed_for_not_submitting_report' : failed_for_not_submitting_report,
            'total' : total,
            'c_yet_to_verify' : c_yet_to_verify,
            'len' : len(c_yet_to_verify),
            'academic_year': secretary.registered_academic_year,
            'sem':secretary.registered_semester
        }
        return render(request,"download_volunteers_data.html",context)
    if request.method == "POST":
        wb = Workbook()
        ws = wb.active
        ws.title = secretary.activity
        ws.append([
            "Name",
            "Submitted",
            "Verified",
            "Email",
            "Gender",
            "Cordinator",
            "Guardian Faculty",
            "Activity",
            "Department",
            "Registered Academic Year",
            "Semester",
            "Academic Year",
            "Division",
            "Phone Number",
            "Parent's Phone Number",
            "Blood Group",
            "PRN",
            "Roll No.",
            "Current Address",
            "Objective Of The Activity",
            "Description Of The Activity",
            "Benefits To The Society",
            "Benefits To Self",
            "Learning Experiences & Challenges",
            "How Did It Shape Your Empathy",
            "URL",
            "Rejection Reason",
            "Attendance",
        ])

        rows = Volunteer.objects.filter(activity=activity, registered_academic_year=secretary.registered_academic_year, registered_semester=secretary.registered_semester)
        if  len(rows) == 0:
            messages.info(request, "No volunteers are registered for " + activity.name + " currently.")
            return redirect("volunteers-data-download")
        for v in rows:
            ws.append([v.vname, v.submitted, v.verified, v.email, v.gender, v.Cordinator, v.guardian_faculty, v.activity, v.dept, v.registered_academic_year, v.registered_semester, v.academic_year, v.div, v.contact_num, v.parent_num, v.blood_group, v.prn, v.roll, v.current_add, v.Objective_of_the_Activity, v.Description_of_the_Activity, v.Benefits_to_Society, v.Benefits_to_Self, v.Learning_Experiences_challenges, v.How_did_it_help_you_to_shape_your_Empathy, v.url, v.rejection_reason, v.attendance])

        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        fname = secretary.activity + ' - Data.xlsx'
        response['Content-Disposition'] = f'attachment; filename={fname}'
        return response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def coordDetailsView(request):
    if request.method == "GET":
        secretary = Secretary.objects.get(email=request.user.email)
        flagship_coordinators = Coordinator.objects.filter(flagshipEvent=secretary.activity, registered_academic_year=secretary.registered_academic_year, registered_semester=secretary.registered_semester)
        social_coordinators = Coordinator.objects.filter(activity=secretary.activity, registered_academic_year=secretary.registered_academic_year, registered_semester=secretary.registered_semester)
        secretaries = Secretary.objects.filter(activity = secretary.activity, registered_academic_year=secretary.registered_academic_year, registered_semester=secretary.registered_semester)
        s = []
        countRegistered = 0
        countAttendance = 0

        for coord in flagship_coordinators:
            countRegistered += 1
            if coord.marked_attendance_FE:
                countAttendance += 1
        for coord in social_coordinators:
            countRegistered += 1
            if coord.marked_attendance_GP2:
                countAttendance += 1
        for sec in secretaries:
            if sec.sname != secretary.sname:
                s.append(sec.sname)
        return render(request,"coordDetails.html",{"flagship_coordinators": flagship_coordinators,"social_coordinators": social_coordinators, "secretary": secretary, "secretaries" : s, "countRegistered":countRegistered, "countAttendance":countAttendance})
    else:
        return redirect("SDashboard")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def SetpasswordPageView(request):
    if request.method == "GET":
        return render(request, "SPassword.html")
    else:
        password = request.POST["password"]
        password = password.strip()
        if password in common_passwords:
            messages.error(request, "This password is too common. Choose a safer one.")
            return redirect("sresetpass")
        user = User.objects.get(username=request.user.username)
        user.set_password(password)
        user.save()
        secretary = Secretary.objects.get(email=user.email)
        secretary.password_changed = True
        secretary.save()
        auth.logout(request)
        messages.success(
            request, "Your password has been changed successfully! Please login again!"
        )
        return redirect("login")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ApproveCoord(request):
    if request.method == "POST":
        coord = Coordinator.objects.get(email=request.POST["email"])
        coord.verified = 1
        coord.save()
        messages.success(
            request, "Coordinator " + coord.cname + " verified successfully!"
        )
        return redirect("SDashboard")
    else:
        return redirect("SDashboard")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def rejectCoordView(request):
    if request.method == "POST":
        coordinator = Coordinator.objects.get(email=request.POST["email"])
        coordinator.verified = 2
        coordinator.submitted = 0
        coordinator.save()
        messages.error(request, "Coordinator " + coordinator.cname + " rejected.")
        return redirect("SDashboard")
    else:
        return redirect("SDashboard")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def failVolunteersView(request):
    if request.method == 'GET':
        secretary = Secretary.objects.get(email = request.user.email)
        volunteers = Volunteer.objects.filter(activity = secretary.activity, registered_semester = secretary.registered_semester, registered_academic_year = secretary.registered_academic_year, verified = 0)
        return render(request, 'failVolunteers.html', {'volunteers': volunteers, 'secretary':secretary})
    else:
        name = request.POST['name']
        reason = request.POST['reason']
        secretary = Secretary.objects.get(email = request.user.email)
        volunteer = Volunteer.objects.get(vname = name)
        volunteer.verified = 3
        volunteer.submitted = 1
        volunteer.rejection_reason = reason
        volunteer.save()
        email_subject = "Social Services Course: Update"
        formatedMsg = []
        formatedMsg.append("The 'Social Services' course required active participation, with successful completion of " + volunteer.activity + " being the primary criterion for passing.")
        formatedMsg.append("Regrettably, we are informing you that you have Failed in the 'Social Services' course.")
        formatedMsg.append("The reason, as stated by " + secretary.sname + ", is:")
        formatedMsg.append('"' + reason + '"')
        context = {"name": volunteer.vname, "messages": formatedMsg}
        email_body = render_to_string("email_template.html", context)
        email = EmailMessage(email_subject, email_body, "noreply@semycolon.com", [volunteer.email])
        email.content_subtype = "html"
        email.send(fail_silently = False)
        messages.info(request,"Volunteer " + volunteer.vname + " has been marked as failed. They have been mailed about it. They cannot submit the report again")
        return redirect('fail-volunteers')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def showCertificate(request):
    if request.method == 'GET':
        secretary = Secretary.objects.get(email = request.user.email)
        act = secretary.activity.replace(" ", "_")
        template_path = "/home/swdc/SWDCWebsite/certificateTemplates/" + act + "/" + act + "_" + secretary.registered_academic_year + "_" + str(secretary.registered_semester) + ".pdf"
        if not os.path.exists(template_path):
            messages.error(request, secretary.activity + '\'s certificate is not available on our servers.')
            return redirect("volunteers-data-download")
        certificate_template = PdfReader(open(template_path, "rb"))
        packet = io.BytesIO()
        output_buffer = io.BytesIO()
        canvasObj = canvas.Canvas(packet, pagesize=landscape(A3))
        canvasObj.setFont("Times-Bold", 27)
        width, height = A3
        text_width = canvasObj.stringWidth('Volunteer Name', "Times-Roman", 27)
        x_center = (width - text_width) / 2
        canvasObj.drawString(x_center, 330, 'Volunteer Name')
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
        return redirect('volunteers-data-download')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def showReport(request):
    if request.method == 'GET':
        template_path = "/home/swdc/SWDCWebsite/certificateTemplates/ReportTemplate.pdf"
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
        return redirect('volunteers-data-download')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/a/login-restricted")
def ReportFillingSampleView(request):
    if request.method == 'GET':
        guardian_faculties = GuardianFaculty.objects.all()
        user = User.objects.get(email = request.user.email)
        hours = str(user.last_login)[11:13]
        minutes = str(user.last_login)[14:16]
        return render(request, 'report-filling.html', {'guardian_faculties':guardian_faculties, 'hours':hours, 'minutes':minutes})
    else:
        messages.error(request, 'Not allowed.')
        return redirect('volunteers-data-download')