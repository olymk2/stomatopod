from libs.db import mydb as dataset
from libs.db import query_builder
from libs.data_helper import *
import os
import sys
import time
import datetime
import MySQLdb
import csv

from settings import *
from constants import *

selected_database = 'development'


class modify_data():
    required = {}
    query = ''
    query_str = None
    query_file = None
    columns = []

    def __call__(self):
        return self

    def calculated_data(self):
        return {}

    def set(self, data):
        self.data = data
        required_values(self.data, required=self.required)
        for key, value in self.calculated_data().items():
            self.data[key] = value

    def query(self):
        query = query_builder(self.query_file, self.query_str) \
            .build_where(columns=self.columns, params=self.data)
        return query.finish()

    def execute(self, data):
        self.set(data)
        with dataset(selected_database) as database:
            print self.query()
            print self.data
            database.execute(self.query(), self.data)
            return database.last_id()

def ticket_assign_to_user(data):
    if not data.viewkeys() >= {'ticket_id', 'user_id'}:
        raise ValueError

    with dataset(selected_database) as database:
        query = open(os.path.abspath('./sql/user_details.sql')).read()
        user_data = database.fetchone(query, values=data)
        if not user_data:
            raise ValueError

        data['team_id'] = user_data.get('team_id')
        print data
        query = "update ticket_relations  set user_id=%(user_id)s, team_id=%(team_id)s where ticket_id=%(ticket_id)s;"
        return database.execute(query, data)


class update_ticket_status(modify_data):
    required = {'user_id', 'ticket_id', 'status_id'}
    query_str = "insert into tickets (ticket_id, user_id, status_id) VALUES (%(ticket_id)s, %(user_id)s, %(status_id)s);"

