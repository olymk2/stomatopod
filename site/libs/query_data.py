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

class query_data(object):
    required = {'id'}
    query_str = None
    limit_rows = True
    query_file = None
    count_rows = True
    columns = ['ticket_relations.user_id', 'milestone_id', 'ticket.status_id']
    grouping = []

    def __init__(self, data, page=0):
        self.page = page
        self.total_rows = 0
        self.data = data
        required_values(self.data, required=self.required)

    def update_values(self, data):
        self.data = data
        required_values(self.data, required=self.required)

    def query(self):
        query = query_builder(self.query_file, self.query_str) \
            .build_where(columns=self.columns, params=self.data) \
            .build_group(self.grouping) \
            .build_limit(page=self.page, limit=PAGINATION_ROWS, enabled=self.limit_rows)
        return query.finish()

    def get(self):
        with dataset(selected_database) as database:
            print self.query()
            return database.fetchone(self.query(), values=self.data)

    def __iter__(self):
        with dataset(selected_database) as database:
            for row in database.fetchall(self.query(), values=self.data):
                yield row
            if self.count_rows is True:
                self.total_rows = database.fetchone('SELECT FOUND_ROWS();').get('FOUND_ROWS()', 0)
    
    def get_total(self):
        return self.total_rows
