import os
import sys
from eventlet import db_pool
import MySQLdb
sys.path.append(os.path.abspath('../'))
import settings
import MySQLdb.cursors

import psycopg2 as pgdb


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
        print connection_details
        if dbtype == 'mysql':
            #self.connection = MySQLdb.connect(**connection_details)
            self.cp = MySQLdb.connect(MySQLdb, **connection_details)
            self.connection = cp.get()
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
        self.cp.put(self.connection)

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



    def fetchone(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def fetchall(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insert(self, table, fieldnames=(), values=()):
        value_placeholder = ''
        for v in values:
            value_placeholder += u'%s,'
        sql = u'insert into ' + table + u' (`' + u'`,`'.join(fieldnames) + u'`) VALUES (' +  value_placeholder.rstrip(',') + u');'

        if self.debug:
            print sql
        #passing parameters in this way auto escapes them and supports unicode better
        return self.cursor.execute(sql, values)

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
            print sql
        return self.cursor.execute(sql)

    def exists(self, table, where):
        conditions = []
        field_list = []
        for field, value in where.iteritems():
            field_list.append(value)
            conditions.append('`' + field + '`=%s')
        sql = 'select count(*) as `count` from `' + table + '` where ' + ' and '.join(conditions) + ';'
        print sql
        self.cursor.execute(sql, field_list)
        total = self.cursor.fetchone()['count']
        print total
        return total
