# unimelb-COMP90082-SP-Backend
This is the backend for COMP90082 SP project.
It provides REST apis for students activities data on Confluence, Jira, and Git.


## Management of branches and releases

In Semester 2, 2021, in order to make it easier to distinguish from the previous work, there is an instruction of branch and release management.

Branch management is composed of the following parts:

sm2-demo is a demo for running in local environments. It is updated by Yixiao Zhang.

sm2-jira is the branch of new features on Jira part. It is updated by Yixiao Zhang.

sm2-git is the branch of new features on Git part. It is updated by Shisheng Liu.

sm2-confluence is the branch of new features on Confluence part. It is updated by Yalan Zhao.

## Deploy methods

**require python3.7 or higher and MySQL**

1. Install all packages needed `pip install -r requirements.txt` (if python2 and python3 are both installed, use pip3 and python3)
2. start MySQL server on localhost:3306, and create a database named "sp90013" `CREATE DATABASE sp90013`
3. modify the MySQL username and password config in TeamSPBackend/Settings/dev.py and TeamSPBackend/Settings/prod.py (don't forget to modify 'DATABASES/default/TEST/PASSWORD' in prod.py)
4. create MySQL tables `python manage.py migrate`
5. start server `python manage.py runserver`
6. api web server is now running on: http://127.0.0.1:8000/api/v1


### Structuring files

To create new APIs or extend existing ones, kindly put the API endpoints (URLs) in "TeamSPBackend/api/urls_vX.py" (for version X) with their corresponding API functions. Kindly refer to "TeamSPBackend/api/urls_v1.py" for more info.

The functions called by the API endpoints are created and reside in "TeamSPBackend/api/views". For example, the functions related to any Team APIs reside in "TeamSpBackendd/api/views/team.py". The functions for Confluence and JIRA APIs reside in their own sub-folders ("TeamSPBackend/api/views/confluence" & "TeamSPBackend/api/views/jira") as they are comprised of multiple files.

The database models for the objects used in our APIs are written as modules of their own in "TeamSPBackend".

To create new models and/or APIs utilizing them, kindly follow the current directory structure and format:

- Database models in its own module. E.g. "TeamSPBackend/newModel/" containing the files "app.py" and "models.py"
- Functions for new APIs under "TeamSPBackend/api/views/". E.g. "TeamSPBackend/api/views/newModel.py"
- API endpoints (URLs) in "TeamSPBackend/api/urls_vX.py" for version X
- For any API functions that require multiple files, put those files under a sub-folder in "TeamSPBackend/api/views/". E.g. "TeamSPBackend/api/views/newModel/"


## Change Log
### Version 1 (September 19th, 2021)

2021.9.6
- Fixed the SSLError

2021.9.9
- Update the code of Jira process part and get three new metric data
- Get the summary of Jira issue in the individual contribution 

2021.9.15
- Fixed one bug on obtaining histogram data of Jira
- Fixed Jira API bugs

2021.9.19
- Create a new release, comp90082_2021_s2_sp_v1.

