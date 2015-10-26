import os
import sys
import datetime
import time
import api
from flask import Flask, session
from flask import redirect
from flask.ext.login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user, make_secure_token
from requests_oauthlib import OAuth2Session
from werkzeug import secure_filename
from flask import make_response
from flask import request
from flask import Blueprint

from libs.html import web
from libs import data
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *
from plugin.plugins import plugin

#from plugin.mantis import mantis_auth, mantis_populate

from widgets import loginbox
from settings import *
from constants import *

authorize_pages = Blueprint('authorize_pages', __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.login_view = '/login'

def todict(data):
    new_dict = {}
    for key, value in data.items():
        new_dict[key] = value
    return new_dict


class User(UserMixin):
    def __init__(self, user_id, active=True):
        fetch_user = get_user_info({'id': user_id})
        user_details = fetch_user.get()
        self.active = False
        if user_details:
            self.id = user_id
            self.name = user_details.get('username')
            self.team_id = user_details.get('team_id', 1)
            self.active = active

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.active
        
    def get_auth_token(self):
        return make_secure_token(self.name, key='deterministic')

@login_manager.user_loader
def load_user(userid):
    return User(userid)


@login_manager.token_loader
def load_token(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')
     
    if token is not None:
        username, password = token.split(":")  # naive token
        print username
        print password
        user_entry = User.get(username)
    if (user_entry is not None):
        user = User(user_entry[0], user_entry[1])
        
    if (user.password == password):
        return user
    return None 

def auth_required():
    if not session.get('user_id'):
        redirect(domain + '/login', 301)

@authorize_pages.route("/register", methods=['GET'])
def register_form():
    top_bar_params = todict(session)
    web.header.create('', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(web.register_form.create().render())
    web.template.append(web.page.render())
    return make_response(web.render())

@authorize_pages.route("/register", methods=['POST'])
def register_submit():
    data = {}
    data['email'] = request.form.get('email')
    data['username'] = request.form.get('email')
    data['first_name'] = request.form.get('name').strip().split()[0]
    data['last_name'] = request.form.get('name').strip().split()[-1]
    data['password'] = request.form.get('password')
    top_bar_params = todict(session)

    web.container.create('Your account has been registered')
    web.header.create('', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(web.container.render())
    web.page.section(web.register_form.create().render())
    #~ create_new_user()
    print data
    new_user = create_new_user()
    new_user.execute(data)
    return make_response(web.render())

@authorize_pages.route("/oauth", methods=['GET'])
@authorize_pages.route("/oauth/", methods=['GET'])
@authorize_pages.route("/oauth/<provider>", methods=['GET'])
def oauth(provider=None):
    oauth_provider = oauth_conf.get('google')
    if oauth_live is False:
        oauth_verify = False
        oauth_access_type = 'offline'
        oauth_approval_prompt = "force"
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
    if provider:
        oauth_session = OAuth2Session(
            oauth_provider.get('client_id'), 
            scope=oauth_provider.get('scope'), 
            redirect_uri=redirect_uri)

        
        # offline for refresh token
        # force to always make user click authorize
        #generate the google url we will use to authorize and redirect there
        authorization_url, state = oauth_session.authorization_url(
            oauth_provider.get('uri'),
            access_type=oauth_access_type,
            approval_prompt=oauth_approval_prompt)

        session['oauth_state'] = state
        return redirect(authorization_url)

    #allready authorised so lets handle the callback
    print request.args
    print request.url
    oauth_session = OAuth2Session(
        oauth_provider.get('client_id'), 
        state=session['oauth_state'], 
        redirect_uri=redirect_uri)

    token = oauth_session.fetch_token(
        oauth_provider.get('token'),
        client_secret=oauth_provider.get('client_secret_id'),
        authorization_response=request.url,
        verify=oauth_verify)

    # Fetch a protected resource, i.e. user profile
    r = oauth_session.get('https://www.googleapis.com/oauth2/v1/userinfo')

    oauth_user = r.json()
    print oauth_user
    fetch_user = get_by_email({'email': oauth_user.get('email')})
    user_details = fetch_user.get()
    print 'user details'
    print user_details
    #user_details = get_user_info({'username': request.form.get('username'), 'password': request.form.get('password')})
    if not user_details:
        create_new_user().execute({
            'email': oauth_user.get('email'), 
            'password': 'oauth', 
            'username': oauth_user.get('email'),
            'first_name': oauth_user.get('given_name'),
            'last_name': oauth_user.get('family_name')})
        #~ print 'login'
        #~ return login_screen()

    print oauth_user.get('email')
    fetch_user = get_by_email({'email': oauth_user.get('email')})
    user_details = fetch_user.get()
    
    print user_details
    if not user_details:
        redirect('/login')
    print 'user id '
    print user_details.get('user_id')
    user = User(user_details.get('user_id'))
    login_user(user)
    session['username'] = user_details.get('username', 'anonymous')
    session['user_id'] = str(user_details.get('user_id'))
    session['team_id'] = str(user_details.get('team_id'))
    return redirect('/')


@authorize_pages.route("/login", methods=['GET'])
def login_screen():
    print request.args
    top_bar_params = todict(session)
    top_bar_params['hide_top_bar'] = 1

    web.header.create('', top_bar_params)
    web.page.create(web.header.render())

    session['username'] = 'user01'
    test_user = User(session['username'], 1)
    login_user(test_user, remember=True)
    view_data = todict(session)
    web.template.body.append(web.login_box.create().render())
    return make_response(web.render())

def hook_login_auth(username, password):
    return remote_ticket_source.auth(username, password)

@authorize_pages.route("/login", methods=['POST'])
def login_screen_submit():
    print "###### login screen submit"
    # TODO encrypt and handle passwords currently we cheat and use mantis

    user_details = None
    # TODO make this a hook instead of hard coding to mantis
    #~ if request.form.get('username') and request.form.get('password'):
        #~ if not plugin.auth(request.form.get('username'), request.form.get('password')):
            #~ return login_screen()
    
    fetch_user = get_auth_user({'username': request.form.get('username'), 'password': request.form.get('password')})
    user_details = fetch_user.get()
    print 'user details'
    print user_details
    #user_details = get_user_info({'username': request.form.get('username'), 'password': request.form.get('password')})
    if not user_details:
        print 'login'
        return login_screen()

    user = User(user_details.get('id'))
    login_user(user)
    session['username'] = user_details.get('username', 'anonymous')
    session['user_id'] = str(user_details.get('id'))
    session['team_id'] = str(user_details.get('team_id'))
    return index()


def login_oauth_user(username, password):
    user_details = None
    # TODO make this a hook instead of hard coding to mantis
    #~ if request.form.get('username') and request.form.get('password'):
        #~ if not plugin.auth(request.form.get('username'), request.form.get('password')):
            #~ return login_screen()
    
    fetch_user = get_auth_user({'username': request.form.get('username'), 'password': request.form.get('password')})
    user_details = fetch_user.get()
    print 'user details'
    print user_details
    #user_details = get_user_info({'username': request.form.get('username'), 'password': request.form.get('password')})
    if not user_details:
        print 'login'
        return login_screen()

    user = User(user_details.get('id'))
    login_user(user)
