from libs.db import mydb as dataset
from libs.db import query_builder
from libs.data_helper import *
import os
import sys
import time
import datetime
import MySQLdb
import csv

from libs.modify_data import *

from settings import *
from constants import *

selected_database = 'development'


class create_data(object):
    required = {}
    query_offset = 0
    query = ''
    query_str = [None,]
    query_file = [None,]
    columns = []

    def __init__(self):
        self.query_offset = 0

    def __call__(self):
        self.query_offset = 0
        return self

    def calculated_data(self):
        return {}

    def set(self, data):
        self.data = data
        required_values(self.data, required=self.required)
        for key, value in self.calculated_data().items():
            self.data[key] = value

    def clean_data(self):
        #convert missing values to null automatically
        print self.data
        for key, value in self.data.items():
            if not value:
                self.data[key] = None

    def query(self):
        print 'generate query'
        print self.query_offset
        print self.query_file[self.query_offset]
        print self.query_str[self.query_offset]
        query = query_builder(self.query_file[self.query_offset], self.query_str[self.query_offset]) \
            .build_where(columns=self.columns, params=self.data)
        
        return query.finish()

    def execute(self, data):
        self.set(data)
        self.clean_data()
        with dataset(selected_database) as database:
            print self.query()
            print self.data
            database.execute(self.query(), self.data)
            self.query_offset += 1

class create_ticket_status_change(modify_data):
    required = {'user_id', 'ticket_id', 'status_id'}
    query_str = "insert into tickets_status_change (ticket_id, user_id, status_id) VALUES (%(ticket_id)s, %(user_id)s, %(status_id)s);"



class import_ticket(create_data):
    required = {'title', 'cid', 'owner_user_id', 'status_id', 'updated', 'project_id'}
    query = u"insert into tickets (title, owner_user_id, updated) VALUES (%(title)s, %(owner_user_id)s, %(updated)s);"
    
    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            query = u"select cid from tickets where cid=%(cid)s;"
            result = database.fetchone(query, self.data)
            if result is None:
                query = u"insert into tickets (title, owner_user_id, updated, cid) VALUES (%(title)s, %(owner_user_id)s, %(updated)s, %(cid)s);"
                database.execute(query, self.data)
                data['ticket_id'] = database.last_id()

                # add relationship data for new ticket
                query = u"insert into ticket_relations (ticket_id, user_id, project_id) VALUES (%(ticket_id)s, %(owner_user_id)s, %(project_id)s);"
                database.execute(query, self.data)
        return 0

class create_ticket(create_data):
    query_str = [
        u"insert into tickets (title, owner_user_id, updated) VALUES (%(title)s, %(owner_user_id)s, %(updated)s);",
        u"insert into ticket_relations (ticket_id, user_id, milestone_id, project_id) VALUES (%(ticket_id)s, %(owner_user_id)s, %(milestone_id)s, %(project_id)s);"
    ]

    def execute(self):
        data['status_id'] = data.get('status_id', STATUS_NEW)
        data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        required_values(data, required={'title', 'owner_user_id', 'milestone_id', 'status_id', 'updated'})

        with dataset(selected_database) as database:
            database.execute(self.query(), data)
            data['ticket_id'] = database.last_id()

            # add relationship data for new ticket
            database.execute(self.query(), data)

        if data.get('user_id'):
            ticket_assign_to_user(data)

        if data.get('notes'):
            create_ticket_note(data)
        return 0

def create_new_ticket(data):
    data['status_id'] = data.get('status_id', STATUS_NEW)
    data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    required_values(data, required={'title', 'owner_user_id', 'milestone_id', 'status_id', 'updated'})

    with dataset(selected_database) as database:
        query = u"insert into tickets (title, owner_user_id, updated) VALUES (%(title)s, %(owner_user_id)s, %(updated)s);"
        print query
        database.execute(query, data)
        data['ticket_id'] = database.last_id()

        # add relationship data for new ticket
        query = u"insert into ticket_relations (ticket_id, user_id, milestone_id, project_id) VALUES (%(ticket_id)s, %(owner_user_id)s, %(milestone_id)s, %(project_id)s);"
        database.execute(query, data)

    if data.get('user_id'):
        ticket_assign_to_user(data)

    if data.get('notes'):
        create_ticket_note(data)
    return 0


class create_new_user(create_data):
    required = {'email', 'password', 'username', 'first_name', 'last_name'}
    query_str = [u"insert into users (username, first_name, last_name, email, password, created) VALUES (%(username)s, %(first_name)s, %(last_name)s, %(email)s, %(password)s, %(created)s);"]

    def calculated_data(self):
        return {'created': time.strftime('%Y-%m-%d %H:%M:%S')}

    def set(self, data):
        data['created'] = time.strftime('%Y-%m-%d %H:%M:%S')
        super(create_new_user, self).set(data)
        

def new_ticket_note_delme(data):
    data['status_id'] = data.get('status_id', STATUS_NEW)
    data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    required_values(data, required={'ticket_id', 'user_id', 'note'})

    with dataset(selected_database) as database:
        query = "insert into ticket_notes (ticket_id, user_id, note) VALUES (%(ticket_id)s, %(user_id)s, %(note)s);"
        database.execute(query, data)
        data['ticket_note_id'] = database.last_id()

class new_ticket_note(create_data):
    required = {'user_id', 'ticket_id', 'note'}
    query = "insert into ticket_notes (ticket_id, user_id, note) VALUES (%(ticket_id)s, %(user_id)s, %(note)s);"

    def execute(self, data):
        if not data.get('note'):
            return 
        data['status_id'] = data.get('status_id', STATUS_NEW)
        data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        with dataset(selected_database) as database:
            query = "insert into ticket_notes (ticket_id, user_id, note) VALUES (%(ticket_id)s, %(user_id)s, %(note)s);"
            database.execute(query, data)
            return database.last_id()

class create_new_project(create_data):
    required = {'user_id', 'title'}
    query = u"insert into projects (title, user_id, status_id, image) VALUES (%(title)s, %(user_id)s, %(status_id)s, %(selected_image)s);"

    def execute(self, data):
        print 'execute new'
        self.set(data)
        data['status_id'] = data.get('status_id', STATUS_NEW)
        data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        data['selected_image'] = data.get('selected_image', '')
        with dataset(selected_database) as database:
            query = "select * from projects where title=%(title)s;"
            result = database.fetchone(query, data)
            if result is None:
                print self.query
                database.execute(self.query, data)
                return database.last_id()
        return result['id']

class assign_project_to_user(create_data):
    required = {'user_id', 'project_id'}
    query = u"insert into user_projects (user_id, project_id) VALUES (%(user_id)s, %(project_id)s);"

    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            query = u"select id from user_projects where user_id=%(user_id)s and project_id=%(project_id)s;"
            result = database.fetchone(query, self.data)
            if result is None:
                database.execute(self.query, self.data)
                return database.last_id()
            return result['id']



def create_new_milestone(data):
    data['status_id'] = data.get('status_id', STATUS_NEW)
    data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    required_values(data, required={'title', 'user_id', 'project_id'})

    with dataset(selected_database) as database:
        query = "insert into milestones (title, project_id, status_id, user_id) VALUES (%(title)s, %(project_id)s, %(status_id)s, %(user_id)s );"
        database.execute(query, data)
