import sys
from github import Github
import re
from flask import escape
from flask import abort
import json
import requests
import base64
import os

def lookml_parameter_option_generator(request):
    queryStringParameters = validate_queryStringParameters(request)

    if queryStringParameters == '':
        print('filename and project_id query parameters are required')
        return abort(401)

    looker_header_token = check_headers(request)
    if looker_header_token == '':
        print('invalid payload headers')
        return abort(401)

    config = json.loads(os.environ.get('CONFIG'))

    if looker_header_token in config:
        instance = config[looker_header_token]
    else:
        print('invalid project_config (instance webhook signature)')
        return abort(401)

    if not ({'base_url','github_token','projects'} <= instance.keys() ):
        print('instance missing variables (base_url, github_token, projects)')
        return abort(401)

    if not (type(instance['projects']) is list and len(instance['projects']) > 0 ):
        print('project is not list or length is 0')
        return abort(401)
    
    body = request.get_json()
    if body == '':
        print('body missing from event')
        return abort(401)

    if 'scheduled_plan' in body and 'query' in body['scheduled_plan'] and 'fields' in body['scheduled_plan']['query']:
        fields = body['scheduled_plan']['query']['fields']
    else:
        print('selection not correct, check fields')
        return abort(401)

    if 'attachment' in body and 'data' in body['attachment']:
        data = json.loads(body['attachment']['data'])
        if not check_data(data):
            print('No attachment data')
            return abort(401)
    else:
        print('No attachment data')
        return abort(401)

    # Find the projects node in the CONFIG environment variable that matches the value for the 'project_id' querystring parameter
    for project in instance['projects']:
        if queryStringParameters['project_id'] == project['project_id']:
            matched_project = project
    
    if not ( {'repository', 'project_id'} <= matched_project.keys() ):
        print('missing keys from project (X-Looker-Deploy-Secret, repository, project_id)')
        return abort(401)

    # Create new values for parameter options based on the rows returned from the scheduled look
    parameter_values = "" 
    for row in data:
        # The label_field and value_field CONFIG options correspond to the name of fields from the scheduled look
        parameter_values += """
  allowed_value: {
    label: \"""" + str(row[matched_project['label_field']]) + """\"
    value: \"""" + str(row[matched_project['value_field']]) + """\"
  }"""

    git = Github(instance['github_token'])

    # Search for a file in the repository that matches the filename specified in the 'filename' querystring parameter, and retrieve the contents
    fName = queryStringParameters['filename'] + '.view.lkml'
    repo = git.get_repo(matched_project['repository'])
    contents = repo.get_contents("")
    matched_content = None

    for content in contents:
        if content.path == fName:
            matched_content = content
            file_content = repo.get_file_contents(matched_content.path).content
            vw = base64.b64decode(file_content).decode('UTF-8')
            break

    # Replace the text between the special beginning and ending comments with the new parameter values we built on line 69
    vw = re.sub(matched_project['begin_comment'] + "(.*?)" + matched_project['end_comment'], matched_project['begin_comment'] + parameter_values + "\n  # " + matched_project['end_comment'], vw, flags=re.DOTALL)
    
    if matched_content is not None:
        # Update the LookML file in the repository with the new parameter options
        repo.update_file(matched_content.path, "auto-update", str(vw), sha=matched_content.sha, branch="master")
    
    if matched_project['X-Looker-Deploy-Secret'] is None or matched_project['X-Looker-Deploy-Secret'] == '':
        headers = {}
    else:
        headers={"X-Looker-Deploy-Secret": matched_project['X-Looker-Deploy-Secret']}

    # After the LookML file has been updated, hit the post-commit /deploy hook to force Looker to deploy the changes
    r = requests.get(
        instance['base_url'] + '/webhooks/projects/' + matched_project['project_id'] + '/deploy',
        headers=headers)

    return 'success'

def check_headers(event):
    if 'X-Looker-Webhook-Token' in event.headers:
        return event.headers['X-Looker-Webhook-Token']
    else: 
        return ''
    
def check_data(data):
    if data is None:
        return False
    elif len(data) > 0:
        return True
    else:
        return False

def validate_queryStringParameters(event):
    # filename and project_id are required
    if 'filename' in event.args and 'project_id' in event.args:
        return event.args
    else:
        return ''
