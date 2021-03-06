from django.db import models
# from TeamSPBackend.account.models import Account
# Create your models here.


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    # student_number = models.IntegerField()
    fullname = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    git_name = models.CharField(max_length=32, unique=True)
    slack_email = models.EmailField(max_length=128, unique=True)
    atl_account = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'student'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)
    # description = models.CharField(max_length=512)
    subject_code = models.CharField(max_length=128)
    supervisor_id = models.IntegerField()
    secondary_supervisor_id = models.IntegerField()
    year = models.IntegerField()
    create_date = models.BigIntegerField(blank=False, null=False)
    project_name = models.CharField(max_length=64)
    slack_oauth_token = models.CharField(max_length=100)
    sprint_start_0 = models.BigIntegerField()
    sprint_end_0 = models.BigIntegerField()
    sprint_start_1 = models.BigIntegerField()
    sprint_end_1 = models.BigIntegerField()
    sprint_start_2 = models.BigIntegerField()
    sprint_end_2 = models.BigIntegerField()
    sprint_start_3 = models.BigIntegerField()
    sprint_end_3 = models.BigIntegerField()
    sprint_start_4 = models.BigIntegerField()
    sprint_end_4 = models.BigIntegerField()

    class Meta:
        db_table = 'team'


class TeamMember(models.Model):
    member_id = models.AutoField(primary_key=True)
    student_id = models.IntegerField()
    team_id = models.IntegerField()

    class Meta:
        db_table = 'team_member'


class TeamConfiguration(models.Model):
    id = models.AutoField(primary_key=True)
    team_id = models.IntegerField()
    slack_access = models.IntegerField()
    slack_workspace = models.CharField(max_length=128)
    slack_token = models.CharField(max_length=128)
    # TODO: add more configuration attributes when needed
    confluence_workspace = models.CharField(max_length=128)
    jira_workspace = models.CharField(max_length=128)
    git_repository = models.CharField(max_length=128)

    class Meta:
        db_table = 'team_configuration'