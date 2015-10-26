import os
import sys
import datetime
import time
import api
from flask import Flask, session
from flask.ext.login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user, make_secure_token
from werkzeug import secure_filename
from flask import make_response
from flask import request

#~ sys.path.insert(0, os.path.abspath('../../scaffold/scaffold/'))

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

from templates.profile import view_profile_template, edit_profile_template
from templates.users import users_view
from templates.teams import teams_view
from templates.board import board_view
from templates.projects import project_view, projects_view, project_tickets_view, project_create
from templates.ticket import milestone_tickets_view
from templates.ticket import ticket_view, create_ticket, create_ticket_note, my_tickets_view, team_tickets_view, update_ticket_view


from authorize import authorize_pages, login_manager


app = Flask(__name__, static_url_path='/static')
login_manager.init_app(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'TODO F12Zr47j\3yX R~X@H!jmM]Lwf/,?K-CHANGEME'


app.register_blueprint(authorize_pages)

def todict(data):
    new_dict = {}
    for key, value in data.items():
        new_dict[key] = value
    return new_dict

def dict_to_list(data, keys):
    return [data.get(k) for k in keys]

def get_default_values():
    user_id = session.get('user_id')
    template_params = todict(session)          
    template_params.update(ordered_dict_to_dict(request.args))            
    template_params['ticket_count'] = get_ticket_count({'user_id': user_id, 'team_id': '1', 'status_id': STATUS_IN_PROGRESS}).get().get('total')
    template_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': user_id})]
    template_params['user_id'] = session.get('user_id')
    template_params['team_id'] = session.get('team_id', 1)
    template_params['user_teams'] = [team for team in get_user_teams({'user_id': session.get('user_id')})]
    print template_params['user_teams']
    return template_params


#TODO preload these we can triger an update if needed
def get_projects_select(data):
    web.select.create('project_id', label='Select Project').append('', ' -- Select Project -- ')
    for row in get_users_projects(data):
        web.select.append(str(row.get('id')), str(row.get('title')), 'test')
    return web.select.render()

def get_milestones_select(data):
    web.select.create('milestone_id', label='Select Milestone').append('', ' -- Select milestone -- ')
    for row in get_milestones(data):
        web.select.append(str(row.get('id')), str(row.get('title')), 'test')
    return web.select.render()

def get_status_select():
    web.select.create('ticket_status', label='').append('', ' -- Select Status -- ')
    for status_id, status_name in STATUS_LIST.items():
        web.select.append(str(status_id), status_name, 'test2')
    return web.select.render()

def ordered_dict_to_dict(odict): 
    return dict((key, value) for (key, value) in odict.items())

def render_project_header(data):
    return web.div.create(get_project(data).get('title')).render()

def render_milestones(data):
    web.table.create('Milestone Tickets', ('Milestone', 'Status'))
    for row in get_milestones(data):
        values = dict_to_list(row, ('title', 'status'))
        values[0] = web.link.create(values[0], values[0], '/view-milestone/%s' % row.get('id')).render()
        web.table.append(values)
    return web.table.render()

def render_project_tickets(data):
    web.table.create('Project Tickets', ('Milestone', 'Status', 'Updated', 'Summary'))
    for row in get_project_tickets(data):
        values = dict_to_list(row, ('milestone_name', 'status', 'updated', 'title'))
        values[0] = web.link.create(values[0], values[0], '/view-milestone/%s' % row.get('project_id')).render()
        values[1] = web.link.create(values[1], values[1], '/view-ticket/%s' % row.get('id')).render()
        values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
        web.table.append(values)
    return web.table.render()


def page_header(title=''):
    top_bar_params = get_default_values()
    web.header.create(title, top_bar_params)
    web.page.create(web.header.render())
    #web.template.body.append(web.header_filter.create(top_bar_params).render())
    return top_bar_params

@app.route("/milestone-tickets/<milestone_id>", methods=['GET'])
def milestone_tickets(milestone_id):
    values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['milestone_id'] = milestone_id
    tickets = milestone_tickets_view()
    #return make_response(render_milestone_tickets(values))
    return make_response(tickets.render(values))


@app.route("/view-my-queue", methods=['GET'])
@app.route("/view-my-queue/<page>", methods=['GET'])
def view_my_queue(page=1):
    top_bar_params = get_default_values()
    
    values = ordered_dict_to_dict(request.args)
    values['user_id'] = current_user.id
    tickets = my_tickets_view()

    web.header.create('My Tickets', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(tickets.render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/view-profile", methods=['GET'])
def view_my_profile(page=1):
    values = get_default_values()
    web.header.create('My Profile', values)
    web.page.create(web.header.render())
    web.page.section(view_profile_template().render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())



@app.route("/view-my-tickets", methods=['GET'])
@app.route("/view-my-tickets/<page>", methods=['GET'])
def view_my_ticket(page=1):
    top_bar_params = get_default_values()

    values = ordered_dict_to_dict(request.args)
    values['user_id'] = current_user.id
    tickets = my_tickets_view()

    web.header.create('My Tickets', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(tickets.render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/my-tickets", methods=['GET'])
@app.route("/my-tickets/<page>", methods=['GET'])
def my_ticket(page=1):
    values = get_default_values()
    #~ values = ordered_dict_to_dict(request.args)
    #~ values['user_id'] = current_user.id
    values['status_id'] = STATUS_IN_PROGRESS
    values['ticket.status_id'] = STATUS_IN_PROGRESS
    tickets = my_tickets_view()
    
    return make_response(tickets.render(values))


@app.route("/project/<project_id>", methods=['GET'])
@app.route("/view-project/<project_id>", methods=['GET'])
def view_project(project_id):
    values = get_default_values() 
    values['project_id'] = project_id
    values['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id':'1'})]
    
    pview = project_view()
    web.header.create('Project View', values)
    web.page.create(web.header.render())
    web.page.section(pview.render(values))

    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/view-ticket/<ticket_id>", methods=['GET'])
def view_ticket(ticket_id):
    data = {}
    top_bar_params = todict(session)
    top_bar_params.update(request.args)            
    top_bar_params['ticket_count'] = get_ticket_count({'user_id': current_user.id, 'team_id': '1'}).get().get('total')
    top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': session.get('user_id')})]

    ticket = ticket_view()
    web.header.create('Project View', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(ticket.render({'ticket_id': ticket_id}))
    #~ web.page.section(render_ticket({'id': ticket_id}))
    #~ web.page.section(render_ticket_notes({'id': ticket_id}))
    #web.page.section(web.container.create().set_id('ticketnotes').render())

    web.template.body.append(web.page.render())
    return make_response(web.render())

@login_required
@app.route("/view-project/<project_id>/tickets", methods=['GET'])
@app.route("/view-project/<project_id>/tickets/<page>", methods=['GET'])
def view_project_tickets(project_id, page=1):
    values = get_default_values()
    values['project_id'] = project_id
    
    web.header.create('Project View', values)
    web.page.create(web.header.render())

    view = project_tickets_view()
    web.page.section(view.render({'project_id': project_id}, page))
    web.template.body.append(web.page.render())
    return make_response(web.render())

@login_required
@app.route("/view-teams/", methods=['GET'])
@app.route("/view-teams/<page>", methods=['GET'])
def view_team(page=1):
    values = get_default_values()    
    web.header.create('Team View', values)
    web.page.create(web.header.render())

    view = teams_view()
    #view = team_tickets_view()
    web.page.section(view.render(values, page))
    web.template.body.append(web.page.render())
    return make_response(web.render())

@login_required
@app.route("/view-board/", methods=['GET'])
@app.route("/view-board/<project_id>", methods=['GET'])
def view_board(project_id=0):
    values = get_default_values()
    
    web.header.create('Board View', values)
    web.page.create(web.header.render())

    view = board_view()
    values['project_id'] = project_id
    web.page.section(view.render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())

@login_required
@app.route("/json-project/<project_id>/json-milestones", methods=['GET'])
def json_milestones(project_id):
    top_bar_params = todict(session)
    top_bar_params.update(request.args)
    top_bar_params['ticket_count'] = get_ticket_count({'user_id': current_user.id, 'team_id': '1'}).get().get('total')
    top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': session.get('user_id')})]

    web.header.create('', top_bar_params)
    web.page.create(web.header.render())

    values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['milestone_id'] = milestone_id
    values['project_id'] = project_id
    milestone_tickets = milestone_tickets_view()
    web.page.section(milestone_tickets.render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())


@login_required
@app.route("/view-project/<project_id>/milestone/<milestone_id>", methods=['GET'])
@app.route("/view-project/<project_id>/view-milestone/<milestone_id>", methods=['GET'])
def view_milestone_tickets(project_id, milestone_id):
    values = get_default_values()
    #top_bar_params = todict(session)
    #top_bar_params.update(request.args)
    #top_bar_params['ticket_count'] = get_ticket_count({'user_id': current_user.id, 'team_id': '1'}).get().get('total')
    #top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': session.get('user_id')})]

    web.header.create('', values)
    web.page.create(web.header.render())

    #~ values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['milestone_id'] = milestone_id
    values['project_id'] = project_id
    milestone_tickets = milestone_tickets_view()
    web.page.section(milestone_tickets.render(values))
    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/view-users", methods=['GET'])
@login_required
def users():
    top_bar_params = get_default_values()

    user_view = users_view()
    web.header.create('Users View', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(user_view.render(top_bar_params))

    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/view-projects/search", methods=['GET'])
@login_required
def projects_search():
    top_bar_params = get_default_values()
    pview = projects_view()
    return make_response(pview.render(top_bar_params))


@app.route("/view-projects", methods=['GET'])
@login_required
def projects():
    top_bar_params = get_default_values()

    pview = projects_view()
    web.header.create('Project View', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(pview.render(top_bar_params))

    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/", methods=['GET'])
@app.route("/view-queue", methods=['GET'])
@login_required
def index():
    top_bar_params = get_default_values()
    #~ top_bar_params = todict(session)
    #~ top_bar_params.update(request.args)
    #~ top_bar_params['ticket_count'] = get_ticket_count({'user_id':current_user.id, 'team_id':'1'}).get().get('total')
    #~ top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id':'1'})]
    #~ 
    web.header.create('', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(web.container.create('<img align="centre" src="/static/images/defaults/loading.gif" />').set_id('mytickets').render())
    #~ web.page.section(web.container.create('<img align="middle" src="/static/images/defaults/loading.gif" />').set_id('teamstickets').render())

    web.template.body.append(web.page.render())
    return make_response(web.render())


@app.route("/view-teams-tickets", methods=['GET'])
@app.route("/view-teams-tickets/<page>", methods=['GET'])
def view_team_tickets(page=1):
    #~ data = {}
    top_bar_params = get_default_values()
    #~ top_bar_params = todict(session)
    #~ top_bar_params.update(request.args)            
    #~ top_bar_params['ticket_count'] = get_ticket_count({'user_id': current_user.id, 'team_id': '1'}).get().get('total')
    #~ top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': session.get('user_id')})]

    values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['team_id'] = session.get('team_id')
    values['team_id'] = current_user.team_id
    team_tickets = team_tickets_view()    
    return make_response(team_tickets.render(values))


@app.route("/teams-tickets", methods=['GET'])
@app.route("/teams-tickets/<page>", methods=['GET'])
def team_tickets(page=1):
    data = {}
    top_bar_params = todict(session)
    top_bar_params.update(request.args)            
    top_bar_params['ticket_count'] = get_ticket_count({'user_id': current_user.id, 'team_id': '1'}).get().get('total')
    top_bar_params['projects'] = [(project.get('id'), project.get('title')) for project in get_users_projects({'user_id': session.get('user_id')})]


    values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['team_id'] = session.get('team_id')
    values['team_id'] = current_user.team_id
    team_tickets = team_tickets_view()    
    return make_response(team_tickets.render(values))

@app.route("/project-tickets/<project_id>", methods=['GET'])
def project_tickets(project_id):
    values = ordered_dict_to_dict(request.args)
    values['user_id'] = session.get('user_id')
    values['project_id'] = project_id
    return make_response(render_project_tickets(values))

@app.route("/register", methods=['GET'])
def register_form():
    top_bar_params = get_default_values() #todict(session)
    web.header.create('', top_bar_params)
    web.page.create(web.header.render())
    web.page.section(web.register_form.create().render())
    web.template.append(web.page.render())
    return make_response(web.render())

@app.route("/register", methods=['POST'])
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

    
    #~ data = todict(request.form)
    #~ data['owner_user_id'] = session.get('user_id')
    #~ print data
    #~ new_ticket = create_ticket()
    #~ new_ticket.create(data)
    #~ sys.exit(1)
    create_new_ticket(data)
    #~ return index()



@app.route("/login", methods=['GET'])
def login_screen():
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


@app.route("/login", methods=['POST'])
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

@app.route("/update-ticket/<ticket_id>", methods=['POST', 'GET'])
def update_ticket_form_submit(ticket_id):
    data = get_default_values() #todict(request.form)
    data['user_id'] = session.get('user_id')
    data['ticket_id'] = ticket_id
    #view = update_ticket_view()
    return update_ticket_view().render(data)

@app.route("/new-ticket-note/<ticket_id>", methods=['POST'])
def new_ticket_note_form_submit(ticket_id):
    print  'new_ticket_note_form_submit'
    web.container.create('success submit')
    data = todict(request.form)
    data['user_id'] = session.get('user_id')
    data['ticket_id'] = ticket_id
    print ticket_id
    print data
    #~ create_ticket_note(data)
    create_notes = create_ticket_note()
    create_notes.create(data)
    return view_ticket(ticket_id)

@app.route("/new-ticket", methods=['POST'])
def new_ticket_form_submit():
    web.container.create('success submit')
    data = todict(request.form)
    data['owner_user_id'] = session.get('user_id')
    print data
    new_ticket = create_ticket()
    new_ticket.create(data)
    #~ sys.exit(1)
    #~ create_new_ticket(data)
    return index()


@app.route("/new-project", methods=['GET'])
def new_project_form():
    #~ data = {}
    form_view = project_create()
    #~ web.container.create('<div>')
    #~ web.form.create('/new-project', node_id='csvimport', node_class='form-horizontal')
    #~ web.form.append('<label for="title">Project Name</label><input type="text" name="title" value="' + data.get('title', '') + '">')
    #~ web.form.append(web.image_selector.create().render())
    #~ web.form.append('<input type="submit" value="Create Project" />')
    #~ web.container.append(web.form.render())
    #~ web.container.append('</div>')
    #~ web.container.append(web.image_selector.get_script())
    return make_response(form_view.render())


@app.route("/new-project", methods=['POST'])
def new_project_submit():
    print 'new_project_submit'
    data = todict(request.form)
    data['user_id'] = session.get('user_id')

    project = create_new_project()
    data['project_id'] = project.execute(data)

    project_assign = assign_project_to_user()
    project_assign.execute(data)
    
    return projects()


@app.route("/new-milestone", methods=['GET'])
def new_milestone_form():
    data = get_default_values()
    web.container.create('<div>')
    web.form.create('/new-milestone', node_id='csvimport', node_class='form-horizontal')
    web.form.append(get_projects_select({'project_id': 1, 'user_id': data.get('user_id')}))
    web.form.append('<label for="title">Milestone Name</label><input type="text" name="title" value="'+data.get('title','')+'">')
    web.form.append('<input type="submit" value="Create Milestone" />')
    web.container.append(web.form.render())
    web.container.append('</div>')
    return make_response(web.container.render())


@app.route("/new-milestone", methods=['POST'])
def new_milestone_submit():    
    data = todict(request.form)
    data['user_id'] = session.get('user_id')
    create_new_milestone(data)
    return index()



@app.route("/edit-profile", methods=['GET'])
def edit_profile_form():
    values = get_default_values()
    return make_response(edit_profile_template().render(values))

@app.route("/new-ticket", methods=['GET'])
def new_ticket_form():
    data = get_default_values()
    #TODO check user has permission to project
    web.container.create('<div>')
    
    web.container.append(web.title.create('Form Title' + web.div.create('').set_classes('close-button icon-content-white icon-content-white-ic_add_white_24dp').render()).render())
    #~ web.image.create('close.png').render()
    #~ <div class="form-popout-title">Title - close button here</div><div class="form-popout-content">
    
    web.form.create('/new-ticket', node_id='csvimport', node_class='form-horizontal')
    
    web.form.append(get_projects_select({'project_id': 1, 'user_id': data.get('user_id')}))
    web.form.append(get_milestones_select({'project_id': 1}))

    web.form.append('<label for="title">Job Code</label><input type="text" name="job_code" value="'+data.get('job_code','')+'">')
    web.form.append('<label for="title">Subject</label><input type="text" name="title" value="'+data.get('title','')+'">')
    web.form.append('<label for="csvdata">Notes</label><textarea style="width:100%;height:100px;" name="note">'+data.get('note','')+'</textarea>')
    web.form.append('<input type="submit" value="Create Ticket" />')

    #web.container.append('')
    web.container.append(web.form.render())
    web.container.append('</div>')

    return make_response(web.container.render())

#~ @app.route("/api/v1.0/my-ticket", methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
