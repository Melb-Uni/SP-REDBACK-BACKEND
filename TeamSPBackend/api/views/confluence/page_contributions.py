import yaml
import json
from django.http.response import HttpResponse
from django.views.decorators.http import require_http_methods
from TeamSPBackend.common.utils import init_http_response, make_json_response
from TeamSPBackend.common.choices import RespCode
from TeamSPBackend.confluence.models import IndividualConfluenceContribution
from TeamSPBackend.confluence.models import IndividualContributionPages
from TeamSPBackend.confluence.models import RecentPages ,RecentComments


@require_http_methods(['GET'])
def get_all_page_contributions(request, space_key):
    """
    Get all the page contributions made by each team member
    Method: GET
    Request: space_key
    Response: list of student name, page count pairs
    """
    try:
        data = []
        for contribution in IndividualConfluenceContribution.objects.filter(space_key=space_key):
            pair = {
                "student": contribution.user_name,
                "page_count": contribution.page_count
            }
            data.append(pair)

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

@require_http_methods(['GET'])
def get_all_contributor_pages(request, space_key):
    """
    Get all the page contributions made by each team member
    Method: GET
    Request: space_key
    Response: list of student name, and the pages they contributed
    """
    try:
        di = dict()

        data = []
        for contribution in IndividualContributionPages.objects.filter(space_key=space_key):
            if contribution.user_id in di:
                di[contribution.user_id].append(contribution.page_name)
            else:
                di[contribution.user_id] = [contribution.page_name]
        for student in di:
            pair = {
                #"student": contribution.user_id,
                #"page_name": contribution.page_name
                "student": student,
                "page_name": str(di[student])
            }
            data.append(pair)

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

require_http_methods(['GET'])
def get_recent_pages(request, space_key):
    """
    Get all the page contributions made by each team member
    Method: GET
    Request: space_key
    Response: list of student name, and the pages they contributed
    """
    try:
        data = []
        for pages in RecentPages.objects.filter(space_key=space_key):
            pair = {
                "action":pages.action,
                "time": pages.updated_time,
                "page_name": pages.page_name,
                "link":pages.link
            }
            data.append(pair)

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")
require_http_methods(['GET'])
def get_comments(request, space_key):
    """
    Get all the page contributions made by each team member
    Method: GET
    Request: space_key
    Response: list of student name, and the pages they contributed
    """
    try:
        data = []
        for pages in RecentComments.objects.filter(space_key=space_key):
            pair = {
                "time": pages.updated_time,
                "page_name": pages.page_name,
                "comment content":pages.content,
                "creator":pages.creator
            }
            data.append(pair)

        resp = init_http_response(
            RespCode.success.value.key, RespCode.success.value.msg)
        resp['data'] = data
        return HttpResponse(json.dumps(resp), content_type="application/json")
    except:
        resp = {'code': -1, 'msg': 'error'}
        return HttpResponse(json.dumps(resp), content_type="application/json")

def read_confluence_config():
    """
    Helper function to read confluence config yaml file
    """
    try:
        confluence_config = open(
            "TeamSPBackend/common/config/confluence_config.yml")
        config_dict = yaml.load(confluence_config, Loader=yaml.FullLoader)
        return config_dict

    except FileNotFoundError as e:
        return -1
