from libs.db import mydb as dataset
from libs.db import query_builder
from libs.data_helper import *
import os
import sys
import time
import datetime

from settings import *
from constants import *

selected_database = 'development'

class select_data(object):
    required = {'id'}
    query_str = None
    limit_rows = True
    query_file = None
    count_rows = True
    columns = ['ticket_relations.user_id', 'milestone_id', 'ticket.status_id']
    grouping = []

    def __call__(self):
        return self

    def __init__(self, data, page=0, limit_rows=True):
        self.page = page
        self.total_rows = 0
        self.data = data
        self.limit_rows = limit_rows
        required_values(self.data, required=self.required)

    def update_values(self, data):
        self.data = data
        required_values(self.data, required=self.required)

    def query(self, one_record=False):
        print '------query start'
        print self.query_file
        print self.query_str
        print self.columns
        print self.data
        
        if one_record:
            self.limit_rows = False
        query = query_builder(self.query_file, self.query_str) \
            .build_where(columns=self.columns, params=self.data) \
            .build_group(self.grouping) \
            .build_limit(page=self.page, limit=PAGINATION_ROWS, enabled=self.limit_rows)
        print '------query end'
        return query.finish()

    def get(self):
        with dataset(selected_database) as database:
            return database.fetchone(self.query(True), values=self.data)

    def __iter__(self):
        with dataset(selected_database) as database:
            for row in database.fetchall(self.query(), values=self.data):
                yield row
            if self.count_rows is True:
                self.total_rows = database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)
    
    def get_total(self):
        return self.total_rows

#~ class select_data(object):
    #~ required = {'id'}
    #~ query_str = None
    #~ query_file = None
    #~ columns = ['ticket_relations.user_id', 'milestone_id', 'ticket.status_id']
#~ 
    #~ def __init__(self, data, page=0):
        #~ self.page = page
        #~ self.total_rows = 0
        #~ self.data = data
        #~ required_values(self.data, required=self.required)
#~ 
    #~ def query(self):
        #~ query = query_builder(self.query_file, self.query_str) \
            #~ .build_where(columns=self.columns, params=self.data) \
            #~ .build_limit(page=self.page, limit=PAGINATION_ROWS)
        #~ return query.finish()
#~ 
    #~ def get(self):
        #~ with dataset(selected_database) as database:
            #~ return database.fetchone(self.query(), values=self.data)
#~ 
    #~ def __iter__(self):
        #~ with dataset(selected_database) as database:
            #~ for row in database.fetchall(self.query(), values=self.data):
                #~ yield row
            #~ self.total_rows = database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)
    #~ 
    #~ def get_total(self):
        #~ return self.total_rows

class select_ticket_data(select_data):
    query_file = 'ticket_list.sql'

    def __iter__(self):
        with dataset(selected_database) as database:
            for row in database.fetchall(self.query(), values=self.data):
                row['status'] = STATUS_LIST.get(row['status_id'])
                yield row
            self.total_rows = database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)

class get_users(select_data):
    required = {}
    query_file = 'get_users.sql'
    columns = []

class get_user_info(select_data):
    required = {'id'}
    query_file = 'get_user_details_by_username.sql'
    columns = ['id']

class get_by_email(select_data):
    required = {'email'}
    query_file = 'get_user_details_by_username.sql'
    columns = ['email']

class get_by_username(select_data):
    required = {'username'}
    query_file = 'get_user_details_by_username.sql'
    columns = ['username']

class get_auth_user(select_data):
    required = {'username', 'password'}
    query_file = 'get_user_details_by_username.sql'
    columns = ['username']
    #columns = ['username', 'password']

def get_user_info_old(data):
    required = {'username', 'password'}
    try:
        if not data.viewkeys() >= {'username', 'password'}:
            raise ValueError
        with dataset(selected_database) as database:
            user_data = database.fetchone(sql = load_sql('get_user_details_by_username.sql'), values=data)
            if not user_data:
                raise ValueError
    except ValueError:
        return None
    return user_data

#~ def get_ticket_count(data):
    #~ if not data.viewkeys() >= {'user_id', 'team_id'}:
        #~ raise ValueError
#~ 
    #~ with dataset(selected_database) as database:
        #~ query = open(os.path.abspath('./sql/ticket_count.sql')).read()        
        #~ return database.fetchone(query, data).get('total')

#~ class select_ticket_data(select_data):
    #~ query_file = 'ticket_list.sql'
    #~ def __iter__(self):
        #~ with dataset(selected_database) as database:
            #~ for row in database.fetchall(self.query(), values=self.data):
                #~ row['status'] = STATUS_LIST.get(row['status_id'])
                #~ yield row
            #~ self.total_rows = database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)


class get_ticket_count(select_ticket_data):
    required = {'user_id', 'team_id'}
    query_file = 'ticket_count.sql'
    columns = ['status_id']

class get_ticket(select_ticket_data):
    required = {'ticket_id'}
    query_file = 'get_ticket.sql'
    columns = ['ticket_id']

class get_mantis_ticket_id(select_ticket_data):
    required = {'ticket_id'}
    query_file = 'get_mantis_ticket_id.sql'
    columns = ['ticket_id']

class get_ticket_notes(select_data):
    required = {'ticket_id'}
    query_file = 'get_ticket_details.sql'
    columns = ['ticket.id']

class get_my_tickets(select_ticket_data):
    required = {'user_id'}
    query_file = 'users_tickets.sql'
    columns = ['ticket_relations.user_id', 'ticket.status_id']#, 'milestone_id', 'ticket.status_id']

class get_milestone_tickets(select_ticket_data):
    required = {'milestone_id'}
    query_file = 'ticket_list.sql'
    columns = ['milestone_id', 'ticket.status_id']

class get_teams_tickets(select_ticket_data):
    required = {'team_id'}
    query_file = 'ticket_list.sql'
    columns = ['team_id', 'milestone_id', 'ticket.status_id']

class get_user_teams(select_data):
    required = {'user_id'}
    query_file = 'get_user_teams.sql'
    columns = ['user_id']

#~ def get_milestone_tickets(data):
    #~ required = {'milestone_id'}
    #~ query_file = 'ticket_list.sql'
    #~ columns = ['team_id', 'milestone_id', 'ticket_relations.project_id', 'ticket.status_id']
    #~ if not data.viewkeys() >= {'milestone_id'}:
        #~ raise ValueError
    #~ with dataset(selected_database) as database:
        #~ query = query_builder('ticket_list.sql').build_where(
            #~ columns=['team_id', 'milestone_id', 'ticket.status_id'], params=data).build_limit()
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row
        #~ yield database.fetchone('SELECT FOUND_ROWS() as row_count;')


class get_project_tickets(select_ticket_data):
    required = {'project_id'}
    query_file = 'ticket_list.sql'
    columns = ['team_id', 'milestone_id', 'ticket_relations.project_id', 'ticket.status_id']

class get_milestone(select_data):
    required = {'milestone_id'}
    query_file = 'milestone.sql'
    columns=['id']

class get_milestones(select_ticket_data):
    required = {'project_id'}
    query_file = 'project_milestones.sql'
    columns=['project_id']

class get_project(select_ticket_data):
    def __init__(self, data, page=0):
        data['id'] = data.get('project_id')
        super(get_project, self).__init__(data, page)

    required = {'project_id'}
    query_file = 'project.sql'
    columns=['project.id']

class get_projects(select_data):
    required = {'user_id'}
    query_file = 'project.sql'
    columns=['user_projects.user_id']

class get_users_projects(select_data):
    required = {'user_id'}
    query_file = 'get_users_projects.sql'
    columns=['user_projects.user_id']

#~ def get_project(data):
    #~ required_values(data, required={'project_id'})
    #~ data['id'] = data.get('project_id')
    #~ query = query_builder('project.sql').build_where(
        #~ columns=['id'], params=data).build_limit()
    #~ with dataset(selected_database) as database:
        #~ return database.fetchone(query.finish(), values=data)

#~ def get_milestones(data):
    #~ required_values(data, required={'project_id'})
    #~ query = query_builder('project_milestones.sql').build_where(
        #~ columns=['project_id'], params=data).build_limit()
    #~ with dataset(selected_database) as database:
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row

#~ def get_project_tickets(data):
    #~ required_values(data, required={'project_id'})
    #~ with dataset(selected_database) as database:
        #~ query = query_builder('ticket_list.sql').build_where(
            #~ columns=['team_id', 'milestone_id', 'ticket_relations.project_id', 'ticket.status_id'], params=data).build_limit()
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row

def get_row_count():
    with dataset(selected_database) as database:
        return database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)

#~ def get_teams_tickets(data):
    #~ required_values(data, required={'team_id'})
    #~ with dataset(selected_database) as database:
        #~ query = query_builder('ticket_list.sql').build_where(
            #~ columns=['team_id', 'milestone_id', 'ticket.status_id'], params=data).build_limit()
        #~ print query
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row

    
#~ def get_milestone_tickets(data):
    #~ if not data.viewkeys() >= {'milestone_id'}:
        #~ raise ValueError
    #~ with dataset(selected_database) as database:
        #~ query = query_builder('ticket_list.sql').build_where(
            #~ columns=['team_id', 'milestone_id', 'ticket.status_id'], params=data).build_limit()
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row
        #~ yield database.fetchone('SELECT FOUND_ROWS() as row_count;')

#~ def get_project_tickets(data):
    #~ required_values(data, required={'project_id'})
    #~ with dataset(selected_database) as database:
        #~ query = query_builder('ticket_list.sql').build_where(
            #~ columns=['team_id', 'milestone_id', 'ticket_relations.project_id', 'ticket.status_id'], params=data).build_limit()
        #~ for row in database.fetchall(query.finish(), values=data):
            #~ row['status'] = STATUS_LIST.get(row['status_id'])
            #~ yield row




