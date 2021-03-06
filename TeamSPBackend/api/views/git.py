# -*- coding: utf-8 -*-
import time
from django.views.decorators.http import require_http_methods
from TeamSPBackend.git.views import update_individual_commits, get_metrics
from TeamSPBackend.common.github_util import get_commits, get_pull_request, get_und_metrics
from TeamSPBackend.api.dto.dto import GitDTO
from TeamSPBackend.common.choices import RespCode
from TeamSPBackend.common.utils import make_json_response, body_extract, init_http_response_my_enum, transformTimestamp
from TeamSPBackend.git.models import StudentCommitCounts, GitCommitCounts, GitMetrics
from TeamSPBackend.project.models import ProjectCoordinatorRelation
from TeamSPBackend.git.views import construct_url
import collections

@require_http_methods(['GET'])
def get_git_individual_commits(request, space_key):
    data = []
    if StudentCommitCounts.objects.filter(space_key=space_key).exists():
        for item in StudentCommitCounts.objects.filter(space_key=space_key):
            temp = {
                "student": str(item.student_name),
                "commit_count": int(item.commit_counts),
                 "version": str(item.version)
            }
            data.append(temp)
    else:
        # if we know its github url
        if ProjectCoordinatorRelation.objects.filter(space_key=space_key).exists():
            update_individual_commits()
            temp = {}
            for item in StudentCommitCounts.objects.filter(space_key=space_key):
                temp = {
                    "student": str(item.student_name),
                    "commit_count": int(item.commit_counts),
                    "version": str(item.version)
                }
                data.append(temp)
        else:
            resp = init_http_response_my_enum(RespCode.invalid_parameter)
            return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['GET'])
def get_git_commits(request, space_key):
    # Case 1: if git_commit table contains this space_key, get it directly from db
    data = []
    if GitCommitCounts.objects.filter(space_key=space_key).exists() and not GitCommitCounts.objects.filter(space_key=space_key,version ="").exists():

        query_set = GitCommitCounts.objects.filter(space_key=space_key)
        start = 0
        if len(query_set) >= 30:
            start = len(query_set) - 30
        for i in query_set[start:]:
            tmp = {
                "time": int(i.query_date),
                "commit_count": int(i.commit_counts),
                "version": str(i.version)
            }
            data.append(tmp)
    else:
        # Case 2: if git_commit table doesn't contain while relation table contains,
        # get it from git web (the first crawler)

        coordinator_id = request.session['coordinator_id']
        if ProjectCoordinatorRelation.objects.filter(space_key=space_key, coordinator_id=coordinator_id).exists():
            relation_data = ProjectCoordinatorRelation.objects.filter(space_key=space_key, coordinator_id=coordinator_id)[0]
            git_dto = construct_url(relation_data)
            if not git_dto.valid_url:
                resp = init_http_response_my_enum(RespCode.no_repository)
                return make_json_response(resp=resp)
            commits = get_commits(relation_data.git_url, space_key, None, None, None, None)
            if commits is None:
                resp = init_http_response_my_enum(RespCode.invalid_authentication)
                return make_json_response(resp=resp)
            if commits == -1:
                resp = init_http_response_my_enum(RespCode.user_not_found)
                return make_json_response(resp=resp)
            if commits == -2:
                resp = init_http_response_my_enum(RespCode.git_config_not_found)
                return make_json_response(resp=resp)

            delta_commit_count = {}  # To store every day commit count
            days = []  # For a month loop
            today = transformTimestamp(time.time())
            for i in range(30):
                days.append(today - i * 24 * 60 * 60)

            delta_version =  collections.defaultdict(lambda: "Not Present")  # To store every day lastest description
            for commit in commits:
                ts = commit['date']
                for i in days:
                    if ts > i:
                        break
                    else:
                        if delta_version[i] =="Not Present":
                            delta_version[i] = commit['description']
                        if i in delta_commit_count:
                            delta_commit_count[i] += 1
                        else:
                            delta_commit_count[i] = 1

            days = [i for i in reversed(days)]  # sort days
            for day in days:
                count = 0
                version = ''
                if day in delta_commit_count:
                    count = delta_commit_count[day]
                    version = delta_version[day]
                # data which are returned to front end
                tmp = {
                    "time": int(day),
                    "commit_count": int(count),
                    "version": str(version)
                }
                data.append(tmp)
                # store data into db by date
                git_data = GitCommitCounts(
                    space_key=space_key,
                    commit_counts=count,
                    query_date=day,
                    version = version
                )
                git_data.save()
            # for i in commits:
            #     ts = transformTimestamp(i['date'])
            #     if ts in delta_commit_count:
            #         delta_commit_count[ts] += 1
            #     else:
            #         delta_commit_count[ts] = 1
            #         days.append(ts)

            # for day in days:
            #     count = 0
            #     for k, v in delta_commit_count.items():
            #         if k <= day:
            #             count += v
            #     # data which are returned to front end
            #     tmp = {
            #         "time": int(day),
            #         "commit_count": int(count)
            #
            #     }
            #     data.append(tmp)
            #     # store data into db by date
            #     git_data = GitCommitCounts(
            #         space_key=space_key,
            #         commit_counts=count,
            #         query_date=day
            #     )
            #     git_data.save()


        # Case 3: Neither contains, invalid space_key, return None
        else:
            resp = init_http_response_my_enum(RespCode.invalid_parameter)
            return make_json_response(resp=resp)

    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


# pull request
@require_http_methods(['POST'])
def get_git_pr(request, body, *args, **kwargs):
    git_dto = GitDTO()
    body_extract(body, git_dto)

    if not git_dto.valid_url:
        resp = init_http_response_my_enum(RespCode.no_repository)
        return make_json_response(resp=resp)
    git_dto.url = git_dto.url.lstrip('$')

    commits = get_pull_request(git_dto.url, git_dto.author, git_dto.branch, git_dto.second_after, git_dto.second_before)
    total = len(commits)
    author = set()
    for commit in commits:
        author.add(commit['author'])
    # ???????????????????????????????????????????????????{author1: [commits...], author2: [cmits...], ...}
    data = dict(
        total=total,
        author=list(author),
        commits=commits,
    )
    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)


@require_http_methods(['GET'])
def get_git_metrics(request, space_key):
    # Case 1: if git_metrics table contains this space_key, get it directly from db
    if GitMetrics.objects.filter(space_key=space_key).exists():

        metrics_data = GitMetrics.objects.filter(space_key=space_key)
    # Case 2: if git_metrics table does not contain this space_key, get it using get_metrics()
    else:

        coordinator_id = request.session['coordinator_id']
        if ProjectCoordinatorRelation.objects.filter(space_key=space_key, coordinator_id=coordinator_id).exists():
            relation_data = ProjectCoordinatorRelation.objects.filter(space_key=space_key, coordinator_id=coordinator_id)[0]
            get_metrics(relation_data)

            if GitMetrics.objects.filter(space_key=space_key).exists():

                metrics_data = GitMetrics.objects.filter(space_key=space_key)
            else:

                resp = init_http_response_my_enum(RespCode.invalid_parameter)
                return make_json_response(resp=resp)
            # Case 3: if space_key is invalid, return None
        else:
            resp = init_http_response_my_enum(RespCode.invalid_parameter)
            return make_json_response(resp=resp)
    data = []

    for elem in metrics_data:
        tmp = {
            "file_count": int(elem.file_count),
            "class_count": int(elem.class_count),
            "function_count": int(elem.function_count),
            "code_lines_count": int(elem.code_lines_count),
            "declarative_lines_count": int(elem.declarative_lines_count),
            "executable_lines_count": int(elem.executable_lines_count),
            "comment_lines_count": int(elem.comment_lines_count),
            "comment_to_code_ratio": float(elem.comment_to_code_ratio),
            "release": str(elem.release),
            "sum_cyclomatic_complexity": int(elem.sum_cyclomatic_complexity),
            "all_methods": int(elem.all_methods)

        }

        data.append(tmp)

    resp = init_http_response_my_enum(RespCode.success, data)
    return make_json_response(resp=resp)