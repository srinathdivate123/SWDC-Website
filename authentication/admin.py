from django.contrib import admin
from . models import Coordinator, Volunteer, Secretary, Activity, currentData, Domain, Departments, stats, GuardianFaculty
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'is_active')
    list_filter = ('first_name', 'is_active')
    ordering = ['id']
    search_fields = ('username', 'email')
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Volunteer)
class volunteerInfo(admin.ModelAdmin):
    list_display = ('id', 'vname', 'submitted', 'verified', 'Cordinator','email', 'prn', 'gender', 'activity', 'dept', 'registered_academic_year', 'registered_semester','academic_year', 'div', 'roll', 'contact_num', 'parent_num','blood_group', 'current_add', 'marked_IN_attendance', 'attendance', 'Objective_of_the_Activity', 'Description_of_the_Activity', 'Benefits_to_Society', 'Benefits_to_Self', 'Learning_Experiences_challenges', 'How_did_it_help_you_to_shape_your_Empathy', 'url', 'guardian_faculty', 'rejection_reason', 'profile_edited', 'password_changed')
    list_filter = ( 'registered_academic_year', 'registered_semester', 'activity','submitted', 'verified', 'password_changed', 'gender')
    search_fields = ('vname', 'Cordinator', 'email', 'prn', 'contact_num', 'parent_num')


@admin.register(Coordinator)
class coordinfo(admin.ModelAdmin):
    list_display = ('id', 'cname', 'email', 'prn', 'activity', 'flagshipEvent', 'domain', 'Secretary', 'submitted', 'verified', 'marked_IN_GP2', 'marked_attendance_GP2', 'marked_IN_FE', 'marked_attendance_FE', 'gender', 'dept', 'registered_academic_year', 'registered_semester', 'academic_year', 'div', 'current_add', 'roll', 'parent_num', 'blood_group', 'contact_num', 'Objective_of_the_Activity', 'Description_of_the_Activity', 'Benefits_to_Society', 'Benefits_to_Self', 'Learning_Experiences_challenges',  'url', 'password_changed')
    list_filter = ('registered_academic_year', 'registered_semester', 'activity', 'flagshipEvent', 'domain', 'submitted', 'verified', 'password_changed')
    search_fields = ('cname', 'email', 'prn', 'contact_num', 'parent_num')


@admin.register(Secretary)
class secInfo(admin.ModelAdmin):
    list_display = ('id', 'sname', 'email', 'prn', 'gender', 'activity', 'domain', 'dept', 'registered_academic_year', 'registered_semester', 'academic_year', 'div', 'current_add', 'roll', 'contact_num', 'password_changed')
    list_filter = ('registered_academic_year', 'registered_semester', 'activity', 'domain', 'password_changed')
    search_fields = ('sname', 'email',  'prn', 'contact_num')


@admin.register(Activity)
class activityInfo(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'flagship_event', 'report_filling', 'report_verification', 'current_count', 'max_count', 'allow_failed_volunteers', 'only_males','only_females', 'attendance', 't_and_c', 'message')
    list_filter = ('enabled', 'report_filling', 'report_verification', 'flagship_event')

@admin.register(Domain)
class domainInfo(admin.ModelAdmin):
    list_display = ('name', 'enabled')

@admin.register(currentData)
class currentInfo(admin.ModelAdmin):
    list_display = ('index', 'AcademicYear', 'Semester')


@admin.register(Departments)
class departmentInfo(admin.ModelAdmin):
    list_display = ('name', 'enabled')


@admin.register(stats)
class statsInfo(admin.ModelAdmin):
    list_display = ('index','hits', 'uCount','vCount','cCount','sCount','totalLogins','lastUpdated')


@admin.register(GuardianFaculty)
class GuardianFacultyInfo(admin.ModelAdmin):
    list_display = ('name', 'active')