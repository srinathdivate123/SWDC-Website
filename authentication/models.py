from django.db import models

class Volunteer(models.Model):
    vname = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    gender = models.CharField(max_length=10)
    activity = models.CharField(max_length=30)
    dept = models.CharField(max_length=60)
    academic_year = models.CharField(max_length=10)
    registered_academic_year = models.CharField(max_length=30)
    registered_semester = models.IntegerField()
    div = models.CharField(max_length=10)
    current_add = models.CharField(max_length=200)
    prn = models.BigIntegerField()
    roll = models.BigIntegerField()
    contact_num = models.CharField(max_length=12)
    parent_num = models.CharField(max_length=12)
    blood_group = models.CharField(max_length=10, default='')
    verified = models.IntegerField(default=0)
    submitted = models.IntegerField(default=0)
    Objective_of_the_Activity = models.CharField(max_length=1000, null=True)
    Description_of_the_Activity = models.CharField(max_length=1000, null=True)
    Benefits_to_Society = models.CharField(max_length=1000, null=True)
    Benefits_to_Self = models.CharField(max_length=1000, null=True)
    Learning_Experiences_challenges = models.CharField(max_length=1000, null=True)
    How_did_it_help_you_to_shape_your_Empathy = models.CharField(max_length=1000, null=True)
    url = models.URLField(max_length=1000, null=True)
    Cordinator = models.CharField(max_length=40, null=True)
    guardian_faculty = models.CharField(max_length=50, default='not_assigned')
    rejection_reason = models.CharField(max_length=200, default='none')
    password_changed = models.BooleanField(default=False)
    attendance = models.CharField(max_length=350, default='')
    marked_IN_attendance = models.BooleanField(default=False, null=True, blank=True)
    profile_edited = models.CharField(max_length=10, default='')
    def _str_(self):
        return self.vname
    class Meta:
        ordering = ['vname']

class Coordinator(models.Model):
    cname = models.CharField(max_length=40)
    email = models.EmailField(max_length=30)
    gender = models.CharField(max_length=10)
    dept = models.CharField(max_length=60)
    academic_year = models.CharField(max_length=10)
    registered_academic_year = models.CharField(max_length=30)
    registered_semester = models.IntegerField()
    div = models.CharField(max_length=10)
    current_add = models.CharField(max_length=100)
    prn = models.BigIntegerField()
    roll = models.BigIntegerField()
    contact_num = models.CharField(max_length=10)
    parent_num = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=10, default='')
    verified = models.IntegerField()
    submitted = models.IntegerField()
    Objective_of_the_Activity = models.CharField(max_length=1000, null=True)
    Description_of_the_Activity = models.CharField(max_length=1000, null=True)
    Benefits_to_Society = models.CharField(max_length=1000, null=True)
    Benefits_to_Self = models.CharField(max_length=1000, null=True)
    Learning_Experiences_challenges = models.CharField(max_length=1000, null=True)
    How_did_it_help_you_to_shape_your_Empathy = models.CharField(max_length=1000, null=True)
    url = models.URLField(max_length=1000, null=True)
    Secretary = models.CharField(max_length=40, null=True)
    activity = models.CharField(max_length=20, null=True)
    flagshipEvent = models.CharField(max_length=30)
    domain = models.CharField(max_length=30, null=True)
    password_changed = models.BooleanField(default=False)
    marked_attendance_GP2 = models.BooleanField(default=False)
    marked_attendance_FE = models.BooleanField(default=False)
    marked_IN_GP2 = models.BooleanField(default=False)
    marked_IN_FE = models.BooleanField(default=False)
    def __str__(self):
        return self.cname
    class Meta:
        verbose_name_plural = 'Coordinators'
        ordering = ['cname']

class Secretary(models.Model):
    sname = models.CharField(max_length=20)
    email = models.EmailField(max_length=30)
    gender = models.CharField(max_length=10)
    dept = models.CharField(max_length=60)
    academic_year = models.CharField(max_length=10)
    registered_academic_year = models.CharField(max_length=30)
    registered_semester = models.IntegerField(default=2)
    domain = models.CharField(max_length=20)
    activity = models.CharField(max_length=20, null = True)
    div = models.CharField(max_length=10)
    current_add = models.CharField(max_length=100)
    prn = models.BigIntegerField()
    roll = models.BigIntegerField()
    contact_num = models.CharField(max_length=10)
    password_changed = models.BooleanField(default=False)
    def __str__(self):
        return self.sname
    class Meta:
        verbose_name_plural = 'Secretaries'
        ordering = ['sname']

class stats(models.Model):
    index = models.IntegerField()
    uCount = models.IntegerField()
    vCount = models.IntegerField()
    cCount = models.IntegerField()
    sCount = models.IntegerField()
    totalLogins = models.IntegerField()
    hits = models.IntegerField()
    lastUpdated = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'Stats'

class Activity(models.Model):
    name = models.CharField(max_length=30)
    enabled = models.BooleanField()
    current_count = models.IntegerField()
    max_count = models.IntegerField()
    flagship_event = models.BooleanField()
    allow_failed_volunteers = models.BooleanField(default=False)
    only_males = models.BooleanField()
    only_females = models.BooleanField()
    report_filling = models.BooleanField(default=False)
    report_verification = models.BooleanField(default=False)
    attendance = models.BooleanField(default=False)
    t_and_c = models.CharField(max_length=1000, null=True)
    message = models.CharField(max_length=1000, default='')
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['name']

class Domain(models.Model):
    name = models.CharField(max_length=40)
    enabled = models.BooleanField()
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Domains'
        ordering =  ['name']

class currentData (models.Model):
    index = models.CharField(max_length=15)
    AcademicYear = models.CharField(max_length=30)
    Semester = models.IntegerField()
    class Meta:
        verbose_name_plural = 'Current-Data'
        ordering = ['index']

class Departments(models.Model):
    name = models.CharField(max_length=70)
    enabled = models.BooleanField()
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Departments'

class GuardianFaculty(models.Model):
    name = models.CharField(max_length=50, default='')
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Guardian Faculties'
        ordering = ['name']