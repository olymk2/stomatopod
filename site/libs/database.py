import os
import sys
import MySQLdb

sys.path.append(os.path.abspath('../'))
import settings

database_name = None
connection = None
cursor = None
debug = None


class db:
    def __init__(self, name):
        open(name)

    def __enter__(self, name):
        pass

    def __exit__(self, type, value, traceback):
        close()


def open(database):
    global connection, cursor, database_name, debug
    database_name = database
    connection = MySQLdb.connect(**settings.database[database_name])
    cursor = connection.cursor()


def escape(value):
    global connection
    return connection.escape_string(value)


def clean_field_names(values):
    fields = []
    for item in xrange(0, len(values)):
        if values[item].endswith('_id'):
            v = values[item][0:len(values[item])-3].replace('_', ' ')
        else:
            v = values[item].replace('_', ' ')
        fields.append(v)
    return fields


def columns(table):
    global connection, cursor, debug
    cursor.execute('show columns from ' + table)
    fieldnames = []
    for column in cursor.fetchall():
        if column[0] != 'id':
            fieldnames.append(column[0].strip())
    return fieldnames


def select(sql, values):
    global connection, cursor, debug
    cursor.execute(sql, values)
    return cursor.fetchall()


def fetchall(sql, values):
    global connection, cursor, debug
    cursor.execute(sql)
    return cursor.fetchall()

def fetchone(sql, values):
    global connection, cursor, debug
    cursor.execute(sql, values)
    return cursor.fetchone()

def insert(table, fieldnames=(), values=()):
    global connection, cursor, debug
    escape_values = []
    for v in values:
        escape_values.append(connection.escape_string(str(v).strip('"')))
    sql = 'insert into ' + table + ' (`' + '`,`'.join(fieldnames) + '`) VALUES ("' + '","'.join(escape_values) + '");'
    print sql
    return cursor.execute(sql)

def insert_duplicate(table, fieldnames, values):
    global connection, cursor, debug
    escape_values = []
    for v in values:
        escape_values.append(connection.escape_string(str(v).strip('"')))
    
    update = ''
    for item in xrange(1, len(fieldnames)):
        update += fieldnames[item]+'='+  connection.escape_string(str(values[item]).strip('"'))
        
    sql = 'insert into ' + table + ' (`' + '`,`'.join(fieldnames) + '`) VALUES ("' + '","'.join(escape_values) + '") ON DUPLICATE KEY UPDATE '+update+';'
    return cursor.execute(sql)

def update(table, where=(), fieldnames=(), values=()):
    global connection, cursor, debug
    update = []
    for item in xrange(0, len(fieldnames)):
        update.append( '`'+fieldnames[item]+'`="' + connection.escape_string(str(values[item]).strip('"')) + '"' )
    sql = 'update ' + table + ' set ' + ', '.join(update) + ' where '+' and '.join(where)+';'
    print sql
    cursor.execute(sql)


def exists(table, where):
    global connection, cursor, debug
    conditions = []
    for field, value in where.iteritems():
        conditions.append('`' + field + '`="' + connection.escape_string(value.strip('"')) + '"')
    sql = 'select count(*) from ' + table + ' where ' + ' and '.join(conditions) + ';'
    cursor.execute(sql)
    return cursor.fetchone()[0]


def close():
    global connection, cursor, debug
    connection.commit()
    cursor.close()
    connection.close()
