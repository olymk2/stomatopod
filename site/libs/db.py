import os
import sys
import MySQLdb
sys.path.append(os.path.abspath('../'))
import settings
import MySQLdb.cursors

import psycopg2 as pgdb

class query_builder:
    query_path = os.path.abspath('./sql/')
    
    def __init__(self, filename=None, query=None):
        if query:
            self.query = query
        else:
            self.query = ''
            file_path = self.query_path + os.sep + filename
            if os.path.exists(file_path):
                if not os.path.exists(file_path):
                    print 'sql file not found %s' % file_path
                    sys.exit(0)
                with open(file_path) as fp:
                    self.query = fp.read()

    def build_where(self, columns, params):
        """build where conditions dynamically insert the columns to test and invalidate missing params"""
        where_conditions = []
        for c in columns:
            current_column = c.split('.')[-1]
            print current_column
            print params
            if params.get(current_column) is None:
                where_conditions.append(c + '=' + c)
            else:
                where_conditions.append(c+ "=%(" + current_column + ")s")
        if where_conditions:
            self.query += ' where ' + ' AND '.join(where_conditions)
        print self.query
        return self
    
    def build_group(self, grouping):
        """build grouping"""
        if not grouping:
            return self
        self.query += ' GROUP BY ' + ', '.join(grouping)
        return self
    
    def build_limit(self, page=0, limit=25, enabled = False):
        if not enabled:
            return self
        start = (int(page) - 1) * int(limit)
        if start < 0:
            start = 0
        """build where conditions dynamically insert the columns to test and invalidate missing params"""
        self.query += ' LIMIT %s, %s' % (start, limit)
        return self

    def __str__(self):
        return self.query

    def finish(self):
        return self.query

class mydb:
    name = None
    connection = None
    cursor = None
    debug = False

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        connection_details = settings.database[self.name].copy()
        dbtype = connection_details['type']
        del(connection_details['type'])
        if dbtype == 'mysql':
            self.connection = MySQLdb.connect(**connection_details)
            self.cursor = self.connection.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            return self

        if dbtype == 'pgsql':
            self.connection = pgdb.connect(**connection_details)
            self.cursor = self.connection.cursor(cursorclass=pgdb.extras.DictCursor)
        return self

    def commit(self):
        self.connection.commit()

    def __exit__(self, type, value, traceback):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def build_where(self, columns, params, query=''):
        """build where conditions dynamically insert the columns to test and invalidate missing params"""
        where_conditions = []
        for c in columns:
            current_column = c.split('.')[-1]
            if params.get(current_column, ''):
                where_conditions.append(c+ "=%(" + current_column + ")s")
            else:
                where_conditions.append(c + '=' + c)
        return query + ' where ' + ' AND '.join(where_conditions)

    def clean_field_names(self, values):
        fields = []
        for item in xrange(0, len(values)):
            if values[item].endswith('_id'):
                v = values[item][0:len(values[item]) - 3].replace('_', ' ')
            else:
                v = values[item].replace('_', ' ')
            fields.append(v)
        return fields

    def escape(self, value):
        if int == type(value) or long == type(value):
            value = str(value)
        return self.connection.escape_string(value)

    def columns(self, table):
        self.cursor.execute('show columns from ' + table)
        fieldnames = []
        for column in self.cursor.fetchall():
            if column['Field'] != 'id':
                fieldnames.append(column['Field'].strip())
        return fieldnames

    def fetchone(self, sql, values=None):
        if not values:
            values = []
        if self.debug:
            print(sql.format(values))
        self.cursor.execute(sql, values)
        return self.cursor.fetchone()

    def fetchall(self, sql, values=None):
        if not values:
            values = []
        if self.debug:
            print(sql.format(values))
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def last_id(self):
        return self.cursor.lastrowid

    def execute(self, sql, values=None):
        if not values:
            values = []
        if self.debug:
            print(sql.format(values))
        self.cursor.execute(sql, values)
        return self.commit()

    def insert(self, table, fieldnames=(), values=()):
        value_placeholder = ''
        for v in values:
            value_placeholder += u'%s,'
        sql = u'insert into ' + table + u' (`' + u'`,`'.join(fieldnames) + u'`) VALUES (' + value_placeholder.rstrip(',') + u');'
        if self.debug:
            print(sql.format(values))
        result = self.cursor.execute(sql, values)
        #self.cursor.commit()
        return result

    def insert_paginated(self, table, fieldnames, rows=100):
        values = []
        item = yield
        while item:
            if len(values) == rows:
                self.mass_insert(table, fieldnames, values)
                print(values)
                item = yield
                values = [item]
            item = yield
            if item:
                values.append(item)
        self.mass_insert(table, fieldnames, values)

    def mass_insert(self, table, fieldnames, values):
        value_placeholder = ''
        for v in fieldnames:
            value_placeholder += u'%s,'
        sql = u'insert into ' + table + u' (`' + u'`,`'.join(fieldnames) + u'`) VALUES (' + value_placeholder.rstrip(',') + u')'
        if self.debug:
            print(sql.format(values))
        #passing parameters in this way auto escapes them and supports unicode better
        return self.cursor.executemany(sql, values)

    def insert_duplicate(self, table, fieldnames, values):
        escape_values = []
        for v in values:
            escape_values.append(self.connection.escape_string(str(v).strip('"')))

        update = ''
        for item in xrange(1, len(fieldnames)):
            value = values[item]
            if value is None:
                value = ''
            update += fieldnames[item] + '=' + self.connection.escape_string(unicode(value, encoding='UTF-8').strip('"'))

        sql = u'insert into ' + table + u' (`' + '`,`'.join(fieldnames) + u'`) VALUES (' + u'","'.join(escape_values) + u') ON DUPLICATE KEY UPDATE ' + update + u';'
        return self.cursor.execute(sql)

    def update(self, table, where=(), fieldnames=(), values=()):
        update = []
        for item in xrange(0, len(fieldnames)):
            value = values[item]
            if value is None:
                value = ''
            update.append('`' + fieldnames[item] + '`="' + self.connection.escape_string(str(value).strip('"')) + '"')
        sql = 'update ' + table + ' set ' + ', '.join(update) + ' where ' + ' and '.join(where) + ';'
        if self.debug:
            print(sql.format(values))
        return self.cursor.execute(sql)

    def exists(self, table, where):
        conditions = []
        field_list = []
        for field, value in where.iteritems():
            field_list.append(value)
            conditions.append('`' + field + '`=%s')
        sql = 'select count(*) as `count` from `' + table + '` where ' + ' and '.join(conditions) + ';'
        self.cursor.execute(sql, field_list)
        total = self.cursor.fetchone()['count']
        return total
