import os
import sys
import time
import datetime

from settings import *
from constants import *

selected_database = 'development'

def required_values(data, required):
    print '########################'
    print data.viewkeys()
    print required
    if not data.viewkeys() >= required:
        print required.difference(data.viewkeys())
        print 'required params = ' + str(required)
        print 'actual params = ' + str(data.viewkeys())
        raise ValueError
    for key in required:
        if data.get(key) is None:
            print '-----------'
            print required
            print data
            print key
            raise ValueError

def optional_values(data, optional):
    if not data.viewkeys() >= {'title', 'owner_user_id', 'milestone_id'}:
        raise ValueError


def load_sql(filename):
    query = ''
    with open(os.path.abspath('./sql/' + filename)) as fp:
        query = fp.read()
    return query
