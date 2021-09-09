from django.db import models
# Create your models here.


class JiraCountByTime(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    time = models.CharField(max_length=256,null=False)
    to_do = models.IntegerField( null=False)
    in_progress = models.IntegerField( null=False)
    done = models.IntegerField(null=False)


    class Meta:
        db_table = 'jira_count_by_time'

class JiraCycleTimeScatter(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    completed = models.CharField(max_length=256,null=False)
    cycle_time = models.IntegerField( null=False)
    summary = models.CharField(max_length=256, null=False)

    class Meta:
        db_table = 'jira_cycle_time_data'

class JiraThroughPut(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    time = models.CharField(max_length=256,null=False)
    count = models.IntegerField( null=False)

    class Meta:
        db_table = 'jira_throughput'

class JiraHistogram(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    day = models.CharField(max_length=256,null=False)
    count = models.IntegerField(null=False)

    class Meta:
        db_table = 'jira_histogram'

class IndividualContributions(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    student = models.CharField(max_length=256, null=False)
    done_count = models.IntegerField(null=False)
    change_log = models.CharField(max_length=10000, default="")


    class Meta:
        db_table = 'individual_contributions'


class Urlconfig(models.Model):
    id = models.AutoField(primary_key=True)
    space_key = models.CharField(max_length=256, null=False)
    jira_url = models.CharField(max_length=256, null=False)
    git_url = models.CharField(max_length=256, null=False)
    git_username = models.CharField(max_length=256, null=False)
    git_password = models.CharField(max_length=256, null=False)


    class Meta:
        db_table = 'url_config'

