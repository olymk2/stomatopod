from werkzeug import secure_filename
from flask import Flask, session
from flask.ext.login import current_user
from flask import make_response
from flask import request
from flask import Blueprint

from itsdangerous import JSONWebSignatureSerializer

from libs.db import mydb as dataset
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *
#~ from pprint import pprint
import pprint
import os
import sys
import datetime
import MySQLdb
import csv
import json

from settings import *
from constants import *

from templates.ticket import ticket_view, create_ticket, create_ticket_note, my_tickets_view

app = Flask(__name__)
#~ lm = LoginManager()
#~ lm.init_app(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'TODO F12Zr47j\3yX R~X@H!jmM]Lwf/,?K-CHANGEME'

#pp = pprint.PrettyPrinter(indent=4)

selected_database = 'development'
mod = Blueprint('api', __name__, url_prefix='/api')

ERROR_INVALID_TOKEN = json.dumps({'status': '1', 'msg': 'invalid token'})


def example_result_format(result):
    return pprint.pformat({'data': next(result, {})}, 4).replace('\n', '<br />').replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

def example_data_format(result):
    return pprint.pformat(result, 4).replace('\n', '<br />').replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')

def create_response(value=0, message=''):
    return {'status': value, 'msg': message}

@mod.route("/", methods=['GET'])
@mod.route("/v1.0", methods=['GET'])
def index_api():
    htm =''

    htm+= '/login<br/>'
    #htm += example_result_format([])

    htm+= '/my-tickets/1<br/>'
    #htm += example_result_format(my_tickets({'user_id': 1}))
    
    htm += '<br/><br/>/team-tickets/1<br>'
    #htm += example_result_format(team_tickets({'team_id': 1}))
    
    htm+= '<br/><br/>/milestone-tickets/1<br>'
    #htm += example_result_format(milestone_tickets({'milestone_id': 1}))
    
    htm+= '<br/><br/>/project-tickets/1<br>'
    #htm += example_result_format(project_tickets({'project_id': 1}))
    
    htm+= '<br/><br/>/new-ticket<br>'
    data = {'title': 'create new ticket', 'owner_user_id': '1', 'milestone_id': '1'}
    htm += example_data_format(data) + '<br />'
    htm += example_data_format(create_response())
    
    htm+= '<br/><br/>/assign-ticket<br>'
    data = {'ticket_id': '1', 'user_id': '2'}
    htm += example_data_format(data) + '<br />'
    htm += example_data_format(create_response())
    #htm += example_data_format(project_tickets({'project_id': 1}))

    return make_response(htm)

def authenticate(data):
    if data.get('authkey'):
        return decode_auth_token(data.get('authkey'))
    return current_user.id

def decode_auth_token(token):
    try:
        s = JSONWebSignatureSerializer(app.secret_key)
        print token 
        return s.loads(token)
    except:
        return None
    
def encode_auth_token(token_data):
    s = JSONWebSignatureSerializer(app.secret_key)
    token = s.dumps(token_data)
    return token.decode('ascii')

@mod.route("/v1.0/login", methods=['GET'])
def login():
    token = encode_auth_token({'status': '0', 'user_id': '1'})
    return make_response(json.dumps({'authkey': token, 'data': []}))

@mod.route("/v1.0/my-tickets", methods=['POST', 'GET'])
@mod.route("/v1.0/my-tickets/<page>", methods=['POST', 'GET'])
def my_tickets(page=0):
    user = authenticate(request.form)
    if user is None: return make_response(ERROR_INVALID_TOKEN)
    #~ data = {'user_id': '1'}
    #values = ordered_dict_to_dict(request.args)
    values = {}
    values['user_id'] = 1 #current_user.id
    tickets = my_tickets_view()
    result = []
    for row in tickets.get_data(values):
        row['updated'] = str(row['updated'])
        result.append(row)
    return make_response(json.dumps({'authkey': request.form.get('authkey'), 'data': result}))

@mod.route("/v1.0/team-tickets", methods=['POST'])
def team_tickets():
    user = authenticate(request.form)
    if user is None: return make_response(ERROR_INVALID_TOKEN)
    data = {'team_id': '1'}
    result = []
    for row in get_teams_tickets(data):
        row['updated'] = str(row['updated'])
        result.append(row)
    print result
    return make_response(json.dumps({'authkey': request.form.get('authkey'), 'data': result}))

@mod.route("/v1.0/milestone-tickets", methods=['GET'])
def milestone_tickets():
    user = decode_auth_token(request.form.get('authkey'))
    if user is None: return make_response(ERROR_INVALID_TOKEN)
    data = {'milestone_id': '1'}
    result = []
    for row in get_milestone_tickets(data):
        row['updated'] = str(row['updated'])
        result.append(row)
    return make_response(json.dumps({'authkey': request.form.get('authkey'), 'data': result}))

@mod.route("/v1.0/project-tickets", methods=['GET'])
def project_tickets():
    user = decode_auth_token(request.form.get('authkey'))
    if user is None: return make_response(ERROR_INVALID_TOKEN)
    data = {'project_id': '1'}
    result = []
    for row in get_project_tickets(data):
        row['updated'] = str(row['updated'])
        result.append(row)
    return make_response(json.dumps({'authkey': request.form.get('authkey'), 'data': result}))


@mod.route("/v1.0/new-ticket", methods=['PUT'])
def new_ticket():
    user = decode_auth_token(request.form.get('authkey'))
    if user is None: return make_response(ERROR_INVALID_TOKEN)
    data = request.form
    print data
    result = create_new_ticket(data)
    if result == 0:
        return create_response(result, 'success')
    return create_response(result, 'An error was encountered creating ticket')

@mod.route("/v1.0/assign-ticket", methods=['PUT'])
def assign_ticket(data):
    result = ticket_assign_to_user(data)
    if result == 0:
        return create_response(result, 'success')
    return create_response(result, 'An error was encountered creating ticket')


@mod.route("/v1.0/create-project", methods=['PUT'])
def new_project(data):
    result = create_new_project(data)
    if result == 0:
        return create_response(result, 'success')
    return create_response(result, 'An error was encountered creating ticket')

@mod.route("/v1.0/create-projects", methods=['PUT'])
def new_projects(data):
    for project in data:
        print project
    if result == 0:
        return create_response(result, 'success')
    return create_response(result, 'An error was encountered creating ticket')

