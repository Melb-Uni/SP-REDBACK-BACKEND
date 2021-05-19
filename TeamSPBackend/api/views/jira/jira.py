# TODO: space_key is not used in jira, clarification required, currently we use Project in JQL
# TODO: illegal value assignments in legacy code, specifically response only have data field.
# TODO: Re-adapt to fit legacy API documentation, include: variable rename, django app integration
# TODO: Specify except statement to avoid accidental termination
# TODO: django app integration
# TODO: charts output
from django.apps import AppConfig
from atlassian import Jira
import json
import time
import datetime

from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# for file op
import os
import time
from dateutil import parser
from shutil import copyfile

from TeamSPBackend.common.choices import RespCode
from TeamSPBackend.common.utils import init_http_response
from TeamSPBackend.common.utils import init_http_response_withoutdata
from TeamSPBackend.common.utils import start_schedule
from TeamSPBackend.api.views.jira.models import JiraCountByTime
from TeamSPBackend.api.views.jira.models import IndividualContributions
from TeamSPBackend.api.views.jira.models import Urlconfig
from TeamSPBackend.project.models import ProjectCoordinatorRelation
from TeamSPBackend.coordinator.models import Coordinator
from TeamSPBackend.api.config import atl_username, atl_password
from TeamSPBackend.git.views import auto_update_commits


# helper functions
def session_interpreter(request):
    """ Extracts credentials from session"""
    user = request.session.get('user')
    username = user['atl_username']
    password = user['atl_password']
    return username, password

def jira_login(request):
    """ Handles Jira login"""
    # username, password = session_interpreter(request)
    username = atl_username
    password = atl_password
    jira = Jira(
        url='https://jira.cis.unimelb.edu.au:8444',
        username=username,
        password=password,
        verify_ssl=False
    )
    return jira


def get_project_key(project, jira):
    """"Get corresponding project key"""
    jira_resp = jira.projects()
    result = ""
    for d in jira_resp:
        if d['name'].lower() == project:
            result = d['key']
    return result


def get_done_contributor_names(team, jira):
    """Get contributors (name, displayName) list of a project"""
    data = []
    total = jira.jql('project = ' + team + ' AND Status = Done', limit=0)['total']  # get total issue count
    for i in range(ceil(total / 100)):  # recurring query if count > 100
        start = 0 + i * 100
        data.append(jira.jql('project = ' + team + ' AND Status = Done', start=start, limit=100)['issues'])
    data = [issue for subdata in data for issue in subdata]  # flatten
    name_lst = []
    display_name_lst = []
    for i in range(len(data)):
        result = data[i]['fields']['assignee']
        if result is not None:
            if result['name'] not in name_lst:
                name_lst.append(result['name'])
            if result['displayName'] not in display_name_lst:
                display_name_lst.append(result['displayName'])
    return name_lst, display_name_lst


def datetime_truncate(t):
    """returns truncated datetime object that only contains date"""
    t = t.replace(hour=0, minute=0, second=0, microsecond=0)
    t = datetime.date(t.year, t.month, t.day)
    return t


def to_unix_time(day):
    """returns unix timestamp from truncated datetime object """
    return time.mktime(datetime.datetime.strptime(str(day), "%Y-%m-%d").timetuple())


# Legacy APIs
@require_http_methods(['GET'])
def get_issues_individual(request, team, student):
    """ Return a HttpResponse, data contains count of all categories of issues (of an individual)"""
    try:
        jira = jira_login(request)

        total = jira.jql('assignee = ' + student + ' AND project = ' + team)['total']
        todo = jira.jql('assignee = ' + student + ' AND project = ' + team + ' AND status = "To Do"')['total']
        in_progress = jira.jql('assignee = ' + student + ' AND project = '
                               + team + ' AND status = "In Progress"')['total']
        done = jira.jql('assignee = ' + student + ' AND project = '
                        + team + ' AND status = "Done"')['total']
        in_review = jira.jql('assignee = ' + student + ' AND project = '
                             + team + ' AND status = "In Review"')['total']
        review = jira.jql('assignee = ' + student + ' AND project = '
                          + team + ' AND status = "Review"')['total']
        data = {
            'student': student,
            'count_issues_total': total,
            'count_issues_to_do': todo,
            'count_issues_progress': in_progress,
            'count_issues_in_review': in_review,
            'count_issues_done': done,
            'count_issues_review': review
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_issues_team(request, team):
    """ Return a HttpResponse, data contains count of all categories of issues (of a team)"""
    try:
        jira = jira_login(request)

        total = jira.jql('project = ' + team)['total']
        todo = jira.jql('project = ' + team + ' AND status = "To Do"')['total']
        in_progress = jira.jql('project = ' + team + ' AND status = "In Progress"')['total']
        done = jira.jql('project = ' + team + ' AND status = "Done"')['total']
        in_review = jira.jql('project = ' + team + ' AND status = "In Review"')['total']
        review = jira.jql('project = ' + team + ' AND status = "Review"')['total']
        data = {
            'count_issues_total': total,
            'count_issues_to_do': todo,
            'count_issues_progress': in_progress,
            'count_issues_in_review': in_review,
            'count_issues_done': done,
            'count_issues_review': review
        }
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_comment_count_individual(request, team, student):
    """ Return a HttpResponse, with username and comment fields"""
    try:
        jira = jira_login(request)

        issues = json.dumps(jira.get_all_project_issues(team, fields='comment'))
        count = issues.count(student)
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['username'] = student
        resp['comments'] = count / 16
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_sprints_dates(request, team):
    try:
        jira = jira_login(request)
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)

        issues = json.dumps(jira.get_all_project_issues(team, fields='*all'))
        split = issues.split("name=Sprint 1,startDate=", 1)
        split2 = split[1].split("endDate=", 1)
        if split[1][:10].startswith('20'):
            resp['sprint_1_start'] = split[1][:10]
        else:
            resp['sprint_1_start'] = "null"
        if split[1][:10].startswith('20'):
            resp['sprint_1_end'] = split2[1][:10]
        else:
            resp['sprint_1_end'] = "null"

        split = issues.split("name=Sprint 2,startDate=", 1)
        split2 = split[1].split("endDate=", 1)
        if split[1][:10].startswith('20'):
            resp['sprint_2_start'] = split[1][:10]
        else:
            resp['sprint_2_start'] = "null"
        if split[1][:10].startswith('20'):
            resp['sprint_2_end'] = split2[1][:10]
        else:
            resp['sprint_2_end'] = "null"

        split = issues.split("name=Sprint 3,startDate=", 1)
        split2 = split[1].split("endDate=", 1)
        if split[1][:10].startswith('20'):
            resp['sprint_3_start'] = split[1][:10]
        else:
            resp['sprint_3_start'] = "null"
        if split[1][:10].startswith('20'):
            resp['sprint_3_end'] = split2[1][:10]
        else:
            resp['sprint_3_end'] = "null"

        split = issues.split("name=Sprint 4,startDate=", 1)
        split2 = split[1].split("endDate=", 1)
        if split[1][:10].startswith('20'):
            resp['sprint_4_start'] = split[1][:10]
        else:
            resp['sprint_4_start'] = "null"
        if split[1][:10].startswith('20'):
            resp['sprint_4_end'] = split2[1][:10]
        else:
            resp['sprint_4_end'] = "null"
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_issues_per_sprint(request, team):
    try:
        jira = jira_login(request)
        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        issues = json.dumps(jira.get_all_project_issues(team, fields='*all'))
        split = issues.split("[id=")
        sprint_ids = []
        for str in split[1:]:
            split2 = str.split(",")
            id = split2[0]
            if id not in sprint_ids:
                sprint_ids.append(id)
        sprint_ids.sort()
        i = 1
        for id in sprint_ids:
            jql_request = 'Sprint = id'
            jql_request = jql_request.replace('id', id)
            issues = jira.jql(jql_request)
            count_issues_total = issues['total']
            resp[i] = count_issues_total
            i += 1
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


# New APIs
@require_http_methods(['GET'])
def get_ticket_count_team_timestamped(request, team):
     """ Return a HttpResponse, data contains 3 kinds of issues timestamped with unix time of each day"""
     try:
        username, password = session_interpreter(request)
        jira_analytics(username, password, team)
        data = []
        with open('cfd.yaml', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                data.append({
                    'time': to_unix_time(datetime_truncate(parser.parse(row['']))),
                    'to_do': int(float(row['To Do'])),
                    'in_progress': int(float(row['In Progress'])),
                    'done': int(float(row['Done']))
                })

                jira_obj = JiraCountByTime(space_key=team, count_time=time.strftime('%Y-%m-%d', time.localtime(int((to_unix_time(day))))), todo=todo,
                                            in_progress=in_progress, done=done)
                jira_obj.save()

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
     except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['GET'])
def get_contributions(request, team):
    """ Return a HttpResponse, data contains display names and Done Counts
    NOTE:
    jira.get_all_assignable_users_for_project returns assignable users
    jql assignee returns issues assigned to users

    assignable users may have zero records, let alone DONE
    whilst assignees may have been deactivated, thus not gettable with jira methods
    """
    try:
        jira = jira_login(request)

        students, names = get_done_contributor_names(get_project_key(team, jira), jira)
        count = []
        for student in students:
            count.append(jira.jql('assignee = ' + student + ' AND project = '
                                  + team + ' AND status = "Done"')['total'])
        result = dict(zip(names, count))

        data = []
        for name, count in result.items():
            data.append({
                'student': name,
                'done_count': count
            })
            jira_obj = IndividualContributions(space_key=team,student=name, done_count=count)
            jira_obj.save()

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_contributions_from_db(request,team):
    try:

        allExistRecord=list(IndividualContributions.objects.filter(space_key=team).values('student','done_count'))

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = allExistRecord
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_ticket_count_team_timestamped_afterthefirstrun(request, team):
    """ Return a HttpResponse, data contains 3 kinds of issues timestamped with unix time"""
    try:
        jira = jira_login(request)

        todo = jira.jql('project = ' + team + ' AND status = "To Do"', limit=0)['total']
        in_progress = jira.jql('project = ' + team + ' AND status = "In Progress"', limit=0)['total']
        done = jira.jql('project = ' + team + ' AND status = "Done"', limit=0)['total']
        data = {
            'time': time.strftime('%Y-%m-%d', time.localtime(to_unix_time(datetime.date.today()))),
            'to_do': todo,
            'in_progress': in_progress,
            'done': done,
        }

        jira_obj = JiraCountByTime(space_key=team,count_time=data['time'], todo=data['to_do'], in_progress=data['in_progress'], done=data['done'])
        jira_obj.save()

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def get_ticket_count_team_timestamped_from_db(request,team):
    try:
        allExistRecord=list(JiraCountByTime.objects.filter(space_key=team).values('count_time','todo','in_progress','done'))

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = allExistRecord
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


@require_http_methods(['GET'])
def auto_get_ticket_count_team_timestamped(request):
     jira = jira_login(request)
     allProjects = jira.projects()
     for p in allProjects:
        # first run, fetch all the records from the date the project is created
        get_ticket_count_team_timestamped(request, p['name'])

     time.sleep(60 * 60 * 24)
     for p in allProjects:
        start_schedule(get_ticket_count_team_timestamped_afterthefirstrun, 60 * 60 * 24, request, p['name'])

     resp = 'success!'
     return HttpResponse(resp, content_type="application/json")


@require_http_methods(['POST'])
def setGithubJiraUrl(request):
     try:
        coordinator_id = '1'
        coordinator_name = 'peter'
        data = json.loads(request.body)
        space_key = data.get("space_key")
        git_url = data.get("git_url")
        jira_url = data.get("jira_url")
        git_username = data.get("git_username")
        git_password = data.get("git_password")

        existURLRecord = ProjectCoordinatorRelation.objects.get(coordinator_id=coordinator_id,space_key=space_key)
        existURLRecord.git_url=git_url
        existURLRecord.jira_project=jira_url
        existURLRecord.save()

        existCoordinatorRecord = Coordinator.objects.get(coordinator_name=coordinator_name)
        existCoordinatorRecord.git_username = git_username
        existCoordinatorRecord.git_password = git_password
        existCoordinatorRecord.save()

        auto_update_commits(space_key)  # after setting git config, try to update git_commit table at once

        resp = init_http_response_withoutdata(
             RespCode.success.value.key, RespCode.success.value.msg)
        return HttpResponse(json.dumps(resp), content_type="application/json")
     except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['POST'])
def get_url_from_db(request):
    try:
        data = json.loads(request.body)
        coordinator_id = data.get('coordinator_id')
        space_key = data.get('space_key')
        allExistRecord=list(ProjectCoordinatorRelation.objects.filter(coordinator_id=coordinator_id,space_key=space_key).values('git_url','jira_project'))

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = allExistRecord
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")


def jira_analytics(username, password, team):
    """Only queries cfd with jira-agile metrics"""
    copyfile('cfd-template.yaml', 'cfd.yaml')
    with open('cfd.yaml', 'r') as file:
        data = file.read()
        data = data.replace('jirainstance', 'https://jira.cis.unimelb.edu.au:8444')
        data = data.replace('usernameplace', username)
        data = data.replace('passwordplace', password)
        data = data.replace('projectplace', team)
    with open('cfd.yaml', 'w') as file:
        file.write(data)
    os.system("jira-agile-metrics cfd.yaml --output-directory $PWD")
    copyfile('cfd-template.yaml', 'cfd.yaml')
# Legacy APIs, not working


@require_http_methods(['GET'])
def get_jira_cfd(request, team):
    """ Return a HttpResponse, data contains a a png of Cumulative Flow Diagram"""
    jira_analytics(request, team)
    while not os.path.exists('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)

    if os.path.isfile('TeamSPBackend/api/views/jira/cfd.png'):
        time.sleep(1)
        data = open('TeamSPBackend/api/views/jira/cfd.png', 'rb').read()
        return HttpResponse(data, content_type="image/png")


