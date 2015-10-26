import os, sys
from types import MethodType
import database

from flask import request
from flask import make_response


from settings import web
print os.path.abspath('../../../scaffold/')
sys.path.insert(0, os.path.abspath('../../../scaffold/'))
from scaffold.web import www

#paths
web.document_root = os.path.abspath('./')
web.template.theme_full_path = os.path.abspath('./static/') + os.sep
domain = 'http://192.168.21.41:5000/'
image_path = domain + os.sep + 'images' + os.sep
web.template.create('Stomatopod - Simple project tracking')


with web.template as setup:
    setup.persistent_header('<link rel="stylesheet" id="navigationCss" href="/static/css/default.css" media="" type="text/css" />')
    setup.persistent_header('<link rel="stylesheet" id="navigationCss" href="/static/css/main.css" media="" type="text/css" />')
    setup.persistent_header('<link rel="stylesheet" id="navigationCss" href="/static/css/sprite-action-white.css" media="" type="text/css" />')
    setup.persistent_header('<link rel="stylesheet" id="navigationCss" href="/static/css/sprite-content-white.css" media="" type="text/css" />')
    #setup.persistent_header('<link rel="stylesheet" id="navigationCss" href="/static/template/js/jquery-ui/themes/base/jquery-ui.css" media="" type="text/css" />')

    setup.persistent_header('<script type="text/javascript" src="' + web.template.path_javascript + 'jquery/jquery.min.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="' + web.template.path_javascript + 'jquery-ui/ui/jquery-ui.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="' + web.template.path_javascript + 'custom.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="' + web.template.path_javascript + 'lib_validate.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="' + web.template.path_javascript + 'lib_jquery_validate.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.0/angular.js"></script>')
    setup.persistent_header('<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/angularjs/1.4.0/angular-animate.js"></script>')

#todo move this to a widget
class header(www.default.html_ui):
    pagelink = '/'
    pagetitle = ''

    def create(self, title, params):
        self.data = params
        return self

    def render(self):
        servers = []
        db = request.args.get('dbselect', request.cookies.get('db', 'development'))
        
        web.template.body.append(web.header_filter.create(self.data).render())
        web.template.body.append(web.filter_bar.create(self.data).render())

        return web.container.create('').render()


class toolbar_filter(www.default.html_ui):
    def create(self, params):
        self.params = params
        return self

    def render(self):
        print 'header render'
        htm = '<div id="topbar">'
        htm = '<div id="user_info">'
        htm += '<div id="newticket">%s</div>' % (self.params.get('ticket_count', '0'))
        htm += '<div id="username">%s</div>' % (self.params.get('username', 'Anonymous'))
        htm += '</div>'
        htm += '<div id="filters">'
        htm += '<div id="filter_milestone_id" class="filter %s" data-value="%s">Milestone</div>' % tuple([
            self.params.get('milestone_id', ''), 'ticked' if self.params.get('milestone_id') else ''])
        htm += '<div id="filter_status_id" class="filter %s" data-value="%s">Status</div>' % tuple([
            'ticked' if self.params.get('status_id') else '', self.params.get('status_id', '')])
        htm += '<div id="filter_assigned_id" class="filter %s" data-value="%s">User</div>' % tuple([
            self.params.get('user_id', ''), 'ticked' if self.params.get('user_id') else ''])
        htm += '</div>'
        htm += '<div id="formticket">show form here</div>'
        htm += '</div>'
        return htm

def render(html):
    response = make_response(html)
    if request.args.get('dbselect'):
        db = request.args.get('dbselect')
        response.set_cookie('db', db)
    return response

web.elements['header'] = header()
web.elements['toolbar_filter'] = toolbar_filter()

