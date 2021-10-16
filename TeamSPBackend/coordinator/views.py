from django.shortcuts import render
import json
from TeamSPBackend.api.views.jira.models import IndividualContributions
from TeamSPBackend.project.models import ProjectCoordinatorRelation
from TeamSPBackend.confluence.models import IndividualConfluenceContribution
from TeamSPBackend.api.views.jira.jira import key_extracter
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponse
from TeamSPBackend.common.utils import init_http_response
from TeamSPBackend.common.choices import RespCode



# Create your views here.
@require_http_methods(['GET'])
def get_individual_contributions_from_db(request, team):
    try:
        existRecord = list(
            ProjectCoordinatorRelation.objects.filter(space_key=team).values(
                'jira_project'))
        url = key_extracter(existRecord[0])
        jira_url = url.get('jira_project')

        confluence_data = []
        data = []
        for contribution in IndividualConfluenceContribution.objects.filter(space_key=team):
            pair = {
                'student': contribution.user_id,
                'page_count': contribution.page_count,
                'student_name': contribution.user_name
            }
            confluence_data.append(pair)
        for item in confluence_data:
            for record in IndividualContributions.objects.filter(space_key=jira_url, student_id=item['student']):
                pair = {
                    'student': record.student,
                    'confluence_page_count': item['page_count'],
                    'jira_done_count': record.done_count
                }
            data.append(pair)
        resp = init_http_response(RespCode.success.value.key, RespCode.success.value.msg)
        if not IndividualContributions.objects.filter(space_key=jira_url, student_id=confluence_data[0]['student']):
            new_data = []
            for item in confluence_data:
                pair = {
                    'student': item['student_name'],
                    'confluence_page_count': item['page_count'],
                    'jira_done_count': 0
                }
                new_data.append(pair)
            resp['data'] = new_data
        else:
            resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except Exception:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")