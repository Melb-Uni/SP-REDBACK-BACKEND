# -*- coding: utf-8 -*-
import json
import os
import logging
import re
import sys
import time
import subprocess
from TeamSPBackend.settings.base_setting import BASE_DIR
from TeamSPBackend.project.models import ProjectCoordinatorRelation

logger = logging.getLogger('django')

GITHUB = 'https://github.com/'
REPO_PATH = BASE_DIR + '/resource/repo/'
RELEASE_PATH = BASE_DIR + '/resource/release/'
COMMIT_DIR = BASE_DIR + '/resource/commit_log'

GIT_CLONE_COMMAND = 'git clone {} {}'
GIT_CHECKOUT_COMMAND = 'git -C {} checkout {}'
GIT_UPDATE_COMMAND = 'git -C {} pull origin HEAD'
GIT_LOG_COMMAND = 'git -C {} log --pretty=format:%H%n%an%n%at%n%s --shortstat --no-merges'
GIT_LOG_PR_COMMAND = 'git -C {} log --pretty=format:%H%n%an%n%at%n%s --shortstat --merges'
GIT_LOG_AUTHOR = ' --author={}'
GIT_LOG_AFTER = ' --after={}'
GIT_LOG_BEFORE = ' --before={}'
GIT_LOG_PATH = ' --> {}'

# using Understand for analyze Metrics
# For Mac
UND_PATH = '/Applications/Understand.app/Contents/MacOS/'
# For Linux Server
#UND_PATH = BASE_DIR+'/Understand-6.0.1077-Linux-64bit/scitools/bin/linux64/'

# set Understand License
UND_LICENSE = UND_PATH+'und -setlicensecode bgZynGqTlJCYDj5Z'
os.system(UND_LICENSE)

# understand und command line for loading a git repo and generate metrics
UND_METRICS = UND_PATH + 'und create -db {} -languages python C++ Java add {} {} analyze'

# Using Python API for get metrics
GET_METRICS_PY_PATH = os.path.dirname(os.path.abspath(__file__)) + '/get_und_metrics.py'
GET_METRICS_PY = 'python3 ' + GET_METRICS_PY_PATH + ' {} {}'
# storage metrics.json
METRICS_FILE_PATH = BASE_DIR + '/resource/understand/'


def construct_certification(repo, space_key):
    # filter null username and password
    user_info = ProjectCoordinatorRelation.objects.filter(space_key=space_key).exclude(
        git_username__isnull=True, git_password__isnull=True)
    if len(user_info) == 0:
        return -1  # -1 means there is no user data
    username = user_info[0].git_username  # 'chengzsh3'
    password = user_info[0].git_password  # 'Czs0707+'
    if len(username) == 0 or len(password) == 0:
        return -2  # -2 means there doesn't exist git username and pwd

    return repo[0:5] + r':' + repo[6:8] + username + r':' + password + '@' + repo[8:]


def init_git():
    if not os.path.exists(REPO_PATH):
        os.mkdir(REPO_PATH)
    if not os.path.exists(COMMIT_DIR):
        os.mkdir(COMMIT_DIR)


def convert(repo: str):
    return '-'.join(repo.replace(GITHUB, '').split('/'))


def check_path_exist(path):
    return os.path.exists(path)


def process_changed(changed):
    file_pattern = re.findall('\d+ file', changed)
    insert_pattern = re.findall('\d+ insert', changed)
    delete_pattern = re.findall('\d+ delet', changed)

    file = 0 if not file_pattern else int(file_pattern[0].strip(' file'))
    insert = 0 if not insert_pattern else int(insert_pattern[0].strip(' insert'))
    delete = 0 if not delete_pattern else int(delete_pattern[0].strip(' delet'))
    return file, insert, delete



def pull_repo(repo, space_key):
    repo = construct_certification(repo, space_key)
    if repo == -1 or repo == -2:
        return repo
    path = REPO_PATH + convert(repo)

    if check_path_exist(path):
        git_update = GIT_UPDATE_COMMAND.format(path)
        logger.info('[GIT] Path: {} Executing: {}'.format(path, git_update))

        os.system(git_update)
        return 1  # 1 means valid

    git_clone = GIT_CLONE_COMMAND.format(repo, path)
    logger.info('[GIT] Path: {} Executing: {}'.format(path, git_clone))
    os.system(git_clone)
    return 1


def pull_release(repo, space_key):
    repo = construct_certification(repo, space_key)
    if repo == -1 or repo == -2:
        return repo
    repo_path = REPO_PATH + convert(repo)

    git_get_tag =' git -C '+repo_path+' tag'
    tags = subprocess.getoutput(git_get_tag).split()

    for tag in tags:
        path = RELEASE_PATH + '/'+str(tag)+'/' + convert(repo)
        git_clone = GIT_CLONE_COMMAND.format(repo, path)+' --branch '+str(tag)
        logger.info('[GIT]pull_release Path: {} Executing: {}'.format(path, git_clone))
        os.system(git_clone)
    return tags




def get_commits(repo, space_key, author=None, branch=None, after=None, before=None):
    state = pull_repo(repo, space_key)
    if state == -1 or state == -2:
        return state
    repo = construct_certification(repo, space_key)
    repo_path = REPO_PATH + convert(repo)
    path = COMMIT_DIR + '/' + convert(repo) + '.log'

    git_log = GIT_LOG_COMMAND.format(repo_path)

    if author:
        git_log += GIT_LOG_AUTHOR.format(author)
    if after:
        git_log += GIT_LOG_AFTER.format(after)
    if before:
        git_log += GIT_LOG_BEFORE.format(before)

    # if version:
    #     git_log += GIT_LOG_DATE.format(version)

    git_log += GIT_LOG_PATH.format(path)

    if not branch:
        branch = 'master'

    os.system(GIT_CHECKOUT_COMMAND.format(repo_path, branch))

    logger.info('get_commits[GIT] Path: {} Executing: {}'.format(path, git_log))
    os.system(git_log)

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return None

    commits = list()
    for i in range(0, len(lines), 6):
        # hash_code = lines[i].strip()
        author = lines[i + 1].strip()
        date = int(lines[i + 2].strip())
        description = lines[i + 3].strip()

        commit = dict(

            author=author,
            date=date,
            description=description,
        )

        # commit = dict(
        #     # hash=hash_code,
        #     author=author,
        #     date=date,
        # )
        commits.append(commit)
    return commits


def get_pull_request(repo, author=None, branch=None, after=None, before=None):
    pull_repo(repo)

    repo_path = REPO_PATH + convert(repo)
    path = COMMIT_DIR + '/' + convert(repo)+ '.log'

    git_log = GIT_LOG_PR_COMMAND.format(repo_path)
    if author:
        git_log += GIT_LOG_AUTHOR.format(author)
    if after:
        git_log += GIT_LOG_AFTER.format(after)
    if before:
        git_log += GIT_LOG_BEFORE.format(before)
    git_log += GIT_LOG_PATH.format(path)

    if not branch:
        branch = 'master'

    os.system(GIT_CHECKOUT_COMMAND.format(repo_path, branch))

    logger.info('[GIT] Path: {} Executing: {}'.format(path, git_log))
    os.system(git_log)

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        raise Exception('git log error')

    commits = list()
    for i in range(0, len(lines), 4):
        hash_code = lines[i].strip()
        author = lines[i + 1].strip()
        date = int(lines[i + 2].strip()) * 1000
        description = lines[i + 3].strip()

        commit = dict(
            hash=hash_code,
            author=author,
            date=date,
            description=description,
        )
        commits.append(commit)
    return commits


def get_und_metrics(repo, space_key):
    state = pull_repo(repo, space_key)
    if state == -1 or state == -2:
        return state
    tags = pull_release(repo, space_key)
    metrics = []
    repo = construct_certification(repo, space_key)
    for i in range(len(tags)):


        # bug-fixed: keep the same with  pull_repo()

        und_file = str(tags[i]) + convert(repo) + '.und'
        metrics_file = str(tags[i]) + convert(repo) + '.json'
        path = RELEASE_PATH + str(tags[i]) + '/' + convert(repo)
        st_time = time.time()
        # Get .und , add files and analyze them
        und_metrics = UND_METRICS.format(und_file, path, und_file)
        logger.info('[Understand] File {} Executing: {}'.format(und_file, und_metrics))
        os.system(und_metrics)

        # Get metrics.json by using another .py script
        get_metrics_by_py = GET_METRICS_PY.format(und_file, metrics_file)
        logger.info('[Understand Python API Get Metrics] get_metrics_by_py: {} '.format(get_metrics_by_py))
        os.system(get_metrics_by_py)

        metrics_file = METRICS_FILE_PATH + metrics_file
        with open(metrics_file, 'r') as fp:
            tmp_dict = json.load(fp)
        if tmp_dict:
            tmp_dict["release"] = str(tags[i])

            metrics.append(tmp_dict)
        end_time = time.time()
        cost_time = round(end_time - st_time, 2)
        logger.info('[Understand] File {} Get Metrics: {} , cost : {} seconds'.format(und_file, metrics, cost_time))
        logger.info('[Understand] metrics {} '.format(metrics))
    return metrics

# if __name__ == '__main__':
#     init_git()
#     pull_repo('https://github.com/LikwunCheung/TeamSPBackend')
#     get_commits('https://github.com/LikwunCheung/TeamSPBackend')
