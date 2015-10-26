from pprint import pprint
import os
import sys
import time
import datetime


from libs.db import mydb as dataset
from libs.db import query_builder
from libs.data_helper import *
from libs.modify_data import ticket_assign_to_user

from settings import *
from constants import *

selected_database = 'development'


class import_data():
    required = {}
    query = ''
    query_file = ''
    columns = []

    def set(self, data):
        self.data = data
        required_values(self.data, required=self.required)

    def update_query(self, query_file, query_str):
        self.query_file = query_file
        self.query_str = query_str
        
    def query(self):
        query = query_builder(self.query_file, self.query_str) \
            .build_where(columns=self.columns, params=self.data)
        return query.finish()

    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            database.execute(self.query(), self.data)


class import_milestones(import_data):
    required = {'title', 'project_id'}
    query = u"insert into milestones (title, project_id, status_id) VALUES (%(title)s, %(project_id)s, 1);"
    
    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            query = u"select id from milestones where project_id=%(project_id)s and title=%(title)s;"
            result = database.fetchone(query, self.data)
            if result:
                return result['id']
            database.execute(self.query, self.data)
            return database.last_id()
        return None


#~ class import_ticket_relations(import_data):
    #~ required = {'ticket_id', 'project_id', 'milestone_id'}
    #~ query = u"insert into milestones (title, project_id, status_id) VALUES (%(title)s, %(project_id)s, 1);"
    #~ 
    #~ def execute(self, data):
        #~ self.set(data)
        #~ with dataset(selected_database) as database:
            #~ query = u"select id from milestones where project_id=%(project_id)s and title=%(title)s;"
            #~ result = database.fetchone(query, self.data)
            #~ if result is None:
                #~ database.execute(self.query, self.data)
                #~ return database.last_id()
        #~ return None


class import_ticket(import_data):
    required = {'title', 'owner_user_id', 'status_id', 'updated', 'project_id'}
    query = u"insert into tickets (title, owner_user_id, updated) VALUES (%(title)s, %(owner_user_id)s, %(updated)s);"

    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            query = u"select ticket_id from plugin_mantis_tickets where mantis_ticket_id=%(cid)s;"
            result = database.fetchone(query, self.data)
            if result is None:
                query = u"insert into tickets (title, owner_user_id, updated) VALUES (%(title)s, %(owner_user_id)s, %(updated)s);"
                database.execute(query, self.data)
                data['ticket_id'] = database.last_id()

                query = u"insert into ticket_notes (ticket_id, user_id, note) VALUES (%(ticket_id)s, %(user_id)s, %(description)s);"
                database.execute(query, self.data)
                #data['ticket_notes_id'] = database.last_id()

                # add relationship data for new ticket
                self.update_query('insert_ticket.sql')
                #~ query = u"""insert into ticket_relations 
                    #~ (ticket_id, user_id, project_id, milestone_id, status_id) 
                    #~ VALUES 
                    #~ (%(ticket_id)s, %(owner_user_id)s, %(project_id)s, %(milestone_id)s, %(status_id)s)
                    #~ ON DUPLICATE KEY UPDATE
                    #~ user_id=VALUES(user_id), project_id=VALUES(project_id);"""
                self.execute(query, self.data)

                query = u'insert into plugin_mantis_tickets (ticket_id, mantis_ticket_id) VALUES (%(ticket_id)s, %(cid)s);'
                database.execute(query, self.data)
            else:
                print result
                data['ticket_id'] = result['ticket_id']

            for note in data.get('notes', []):
                note_data = {'ticket_id': data['ticket_id'], 'user_id': 1, 'note': note[1], 'mantis_ticket_note_id': note[0]}
                query = "select mantis_ticket_note_id from plugin_mantis_ticket_notes where mantis_ticket_note_id=%(mantis_ticket_note_id)s;"
                result = database.fetchone(query, note_data)
                if result is None:
                    query = u"insert into ticket_notes (ticket_id, user_id, note) VALUES (%(ticket_id)s, %(user_id)s, %(note)s);"
                    database.execute(query, note_data)
                    note_data['mantis_ticket_note_id'] = note[0]
                    note_data['ticket_note_id'] = database.last_id()

                    query = u"insert into plugin_mantis_ticket_notes (ticket_note_id, mantis_ticket_note_id) VALUES (%(ticket_note_id)s, %(mantis_ticket_note_id)s);"
                    database.execute(query, note_data)
        return 0


class import_user(import_data):
    required = {'username', 'email', 'first_name', 'last_name', 'mantis_user_id'}
    query = u"insert into users (username, email, first_name, last_name) VALUES (%(username)s, %(email)s, %(first_name)s, %(last_name)s);"
    
    user_cache = []

    def __init__(self):
        self.populate_user_cache()

    def lookup_id(self, mantis_id):
        # TODO map mantis id to user id
        return 1

    def lookup_username(self, username):
        for user in self.user_cache:
            print user
            if user[-1] == username:
                print user
                print user[-1]
                print username
                print user[0]
                return user[0]
        return 1

    def populate_user_cache(self):
        print 'populating user cache'
        if not self.user_cache:
            self.user_cache = []

            with dataset(selected_database) as database:
                for row in database.fetchall(u"select user_id, mantis_user_id, email, username from plugin_mantis_users join users on plugin_mantis_users.user_id=users.id;", []):
                    self.user_cache.append((row['user_id'], row['mantis_user_id'], row['email'], row['username']))

    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            # check if user exists and add if they do not
            if [user for user in self.user_cache if user[-1] == self.data.get('email')]:
                return

            database.execute(self.query, self.data)
            user = [(database.last_id(), self.data['email'])]
            user_id = database.last_id()
            self.user_cache.append((user_id, self.data['mantis_user_id'], self.data['email'], self.data['username']))
            data['user_id'] = user[0][0]
            database.execute('insert into plugin_mantis_users (user_id, mantis_user_id) VALUES (%(user_id)s, %(mantis_user_id)s);', self.data)

            #~ query = u"select user_id, mantis_user_id from plugin_mantis_users where mantis_user_id=%(mantis_user_id)s;"
            #~ result = database.fetchone(query, self.data)
            #~ if result is None:
                #~ query = "select * from users where email=%(email)s;"
                #~ result = database.fetchone(query, data)
                #~ user = [user for user in self.user_cache if user[1] == self.data.get('email')]
                #~ if not user: 
                    #~ print 'inserting user'
                    #~ database.execute(self.query, self.data)
                    #~ user = [(database.last_id(), self.data['email'])]
                    #~ self.user_cache.append((user[0], self.data['mantis_user_id'], self.data['email']))
                    #~ data['user_id'] = user[0][0]
                    #~ database.execute('insert into plugin_mantis_users (user_id, mantis_user_id) VALUES (%(user_id)s, %(mantis_user_id)s);', self.data)
                #~ else:
                    #~ print 'cahced user'
                    #~ data['user_id'] = user[0][0]
            # add relationship data for new ticket
            print user
            
            #~ query = "select * from user_projects where user_id=%(user_id)s AND project_id=%(project_id)s;"
            #~ print query
            #~ print data
            #~ result = database.fetchone(query, data)
            #~ if result is None:
                #~ query = u"insert into user_projects (user_id, project_id) VALUES (%(user_id)s, %(project_id)s);"
                #~ database.execute(query, self.data)
        return 0


class import_project(import_data):
    required = {'title', 'user_id', 'mantis_project_id'}
    query = u"select mantis_project_id, project_id from plugin_mantis_projects"
    
    project_cache = []

    def __init__(self):
        self.populate_project_cache()

    def populate_project_cache(self):
        with dataset(selected_database) as database:
            for row in database.fetchall(self.query, []):
                self.project_cache.append((row['mantis_project_id'], row['project_id']))

    def fetch_or_insert(self, mantis_project_id):
        mantis_project_id = data.get('mantis_project_id')
        project_id = self.lookup_mantis_project_id(mantis_project_id)
        if not project_id:
             project_id = self.create(data)
        return project_id
        
    def lookup_mantis_project_id(self, mantis_project_id):
        for row in self.project_cache:
            print row
            if row[0] == mantis_project_id:
                return row[1]

    def create(self, data):
        data['status_id'] = data.get('status_id', STATUS_NEW)
        data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        required_values(data, required={'title', 'user_id'})

        with dataset(selected_database) as database:
            query = "select * from projects where title=%(title)s;"
            result = database.fetchone(query, data)
            if result is None:
                query = "insert into projects (title, user_id, status_id) VALUES (%(title)s, %(user_id)s, %(status_id)s);"
                print data
                database.execute(query, data)
                data['project_id'] = database.last_id()
                
                query = "insert into user_projects (user_id, project_id) VALUES (%(user_id)s, %(project_id)s);"
                print query
                print data
                database.execute(query, data)
                data['project_id'] = database.last_id()
                
                query = "insert into plugin_mantis_projects (mantis_project_id, project_id) VALUES (%(mantis_id)s, %(project_id)s);"
                database.execute(query, data)
                return data['project_id']
            return result['id']

def create_new_project(data):
    data['status_id'] = data.get('status_id', STATUS_NEW)
    data['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    required_values(data, required={'title', 'user_id'})

    with dataset(selected_database) as database:
        query = "select * from projects where title=%(title)s;"
        result = database.fetchone(query, data)
        if result is None:
            query = "insert into projects (title, user_id, status_id) VALUES (%(title)s, %(user_id)s, %(status_id)s);"
            print data
            database.execute(query, data)
            data['project_id'] = database.last_id()
            
            query = "insert into user_projects (user_id, project_id) VALUES (%(user_id)s, %(project_id)s);"
            print query
            print data
            database.execute(query, data)
            data['project_id'] = database.last_id()
            
            query = "insert into plugin_mantis_projects (mantis_project_id, project_id) VALUES (%(mantis_id)s, %(project_id)s);"
            database.execute(query, data)
            return data['project_id']
        return result['id']

def lookup_mantis_project_id(data):
    required_values(data, required={'project_id'})
    with dataset(selected_database) as database:
        query = "select * from plugin_mantis_projects where id=%(project_id)s;"
        return database.fetchone(query, data)

def clean():
    with dataset(selected_database) as database:
        database.fetchone("truncate plugin_mantis_users", [])
        database.fetchone("truncate plugin_mantis_projects", [])
        database.fetchone("truncate plugin_mantis_user_projects", [])
        database.fetchone("truncate plugin_mantis_tickets", [])
        database.fetchone("truncate plugin_mantis_ticket_notes", [])
        
        database.fetchone("truncate milestones", [])
        database.fetchone("truncate users", [])
        database.fetchone("truncate users", [])
        database.fetchone("truncate projects", [])
        database.fetchone("truncate user_projects", [])
        database.fetchone("truncate tickets", [])
        database.fetchone("truncate ticket_relations", [])
        database.fetchone("truncate ticket_notes", [])

