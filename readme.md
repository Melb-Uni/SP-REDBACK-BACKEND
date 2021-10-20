# unimelb-COMP90082-SP-Backend
This is the backend for COMP90082 SP project.
It provides REST apis for students activities data on Confluence, Jira, and Git.


## Management of branches and releases

In Semester 2, 2021, in order to make it easier to distinguish from the previous work, there is an instruction of branch and release management.

Branch management is composed of the following parts:

sm2-demo is a demo for running in local environments. It is updated by Yixiao Zhang.

sm2-jira is the branch of new features on Jira part. It is updated by Yixiao Zhang.

sm2-git is the branch of new features on Git part. It is updated by Shisheng Liu.

sm2_confluence is the branch of new features on Confluence part. It is updated by Yalan Zhao.

## Deploy methods

**require python3.7 or higher and MySQL**

1. Install all packages needed `pip install -r requirements.txt` (if python2 and python3 are both installed, use pip3 and python3)
2. start MySQL server on localhost:3306, and create a database named "sp90013" `CREATE DATABASE sp90013`
3. modify the MySQL username and password config in TeamSPBackend/Settings/dev.py and TeamSPBackend/Settings/prod.py (don't forget to modify 'DATABASES/default/TEST/PASSWORD' in prod.py)
4. create MySQL tables: first `python manage.py makemigrations`, then `python manage.py migrate`
5. start server `python manage.py runserver`
6. api web server is now running on: http://127.0.0.1:8000/api/v1
7. This project uses Understand for analyze Metrics.Please install Understand and change UND_PATH in github_util.py


### Structuring files

To create new APIs or extend existing ones, kindly put the API endpoints (URLs) in "TeamSPBackend/api/urls_vX.py" (for version X) with their corresponding API functions. Kindly refer to "TeamSPBackend/api/urls_v1.py" for more info.

The functions called by the API endpoints are created and reside in "TeamSPBackend/api/views". For example, the functions related to any Team APIs reside in "TeamSpBackendd/api/views/team.py". The functions for Confluence and JIRA APIs reside in their own sub-folders ("TeamSPBackend/api/views/confluence" & "TeamSPBackend/api/views/jira") as they are comprised of multiple files.

The database models for the objects used in our APIs are written as modules of their own in "TeamSPBackend".

To create new models and/or APIs utilizing them, kindly follow the current directory structure and format:

- Database models in its own module. E.g. "TeamSPBackend/newModel/" containing the files "app.py" and "models.py"
- Functions for new APIs under "TeamSPBackend/api/views/". E.g. "TeamSPBackend/api/views/newModel.py"
- API endpoints (URLs) in "TeamSPBackend/api/urls_vX.py" for version X
- For any API functions that require multiple files, put those files under a sub-folder in "TeamSPBackend/api/views/". E.g. "TeamSPBackend/api/views/newModel/"

### Some solution for the problems
1. When you first run the system or add a project, it would take a few minutes for the system to get information from API, store these API into the database and show these information on the browser. So please wait until the back-end part do not jump out new log. Then you can add new project or do other operations.
2. Sometimes the system may do not respond for a long time, you can try some solutions in the following order:
    - Go back to the home page and click into the project again
    - Go back to the home page and delete the project that do not respond. Then search for the same project and add it again.
    - Log out and try to login again.
    - Close the back-end and front-end and try to run again from the beginning.
    - Close the back-end and front-end, clearing the cache of the browser you use to open the system and try to run back-end and front-end again from the beginning.
    - If all the solutions listed above could not work, please leave a comment on this git page.
3. There are some team members from previous semester are graduated and their information is not stored in the confluence system. So you could just ignore the log information which tells you the user do not exist. 
4. Not all the project have JIRA or confluence comment information, so some table could be blank.

## Change Log
### Version 1 (September 19th, 2021)

2021.9.6
- Fix the SSLError

2021.9.9
- Update the code of Jira process part and get three new metric data
- Obtain the summary of Jira issue in the individual contribution 
- fix git config

2021.9.14

- Fix one bug about cannot open git in process
- Update the confluence part and could get the confluence pages updated by each user

2021.9.15

- Fix one bug on obtaining histogram data of Jira
- Fix Jira API bugs
- Finish the get_git_commits function
- Update the confluence part and could get the recently updated pages of the project
- Fix a bug in indivadual contribution relative function

2021.9.16

- Update the confluence part and could get all the comments in a project.

2021.9.19

- Create a new release, comp90082_2021_s2_sp_v1.

### Version 2 (October 20th, 2021)

2021.9.27

- Fix bugs and add issues urls

2021.9.28

- Add a new table to store url and summary of Jira
- Add a new url to get summary and urls

2021.9.29

- Change the format of time in confluence page
- Modify the way of displaying indivadual contribution information about confluence
- Add a column in process quality page to show the page change state

2021.9.30

- Fix bugs on obtaining the urls of summaries on Jira
- Add some apis for confluence page count to show information in different time periods

2021.10.03

- Add a new url to get Confluence and Jira data to build a new chart
- Add a new function to obtain Confluence and Jira data to build a new chart

2021.10.08

- Add a new function that shows the metrics of each release of the project

2021.10.10

- Add encryption and decryption functions for bot and git account passwords
