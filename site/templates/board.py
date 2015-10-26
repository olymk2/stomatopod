from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *
from plugin.plugins import plugin


class board_view:
    project = None

    def render(self, values):
        projects = {}
        for project in get_users_projects({'user_id': values.get('user_id')}, limit_rows=False):
            projects[project.get('id')] = project.get('title'), project.get('id'), project.get('image')

        #get_users_projects
        values['project_id'] = 4
        web.div.create('')
            
        web.board.create('Board view')
        tickets = get_project_tickets({'project_id':4}, page=1)
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        print [i for i in tickets]
        #~ sys.exit(0)
        for ticket in tickets:
            print "test"
            print ticket.get('status')
            print ticket.get('status_id')
            if int(ticket.get('status_id')) is STATUS_NEW:
                web.board.append(ticket.get('title'), '1','description')
            if int(ticket.get('status_id')) is STATUS_IN_PROGRESS:
                web.board.append_progress(ticket.get('title'), '1','description')
            if int(ticket.get('status_id')) is STATUS_COMPLETE:
                web.board.append_completed(ticket.get('title'), '1','description')
            #~ web.board.append_progress(ticket.get('title'), '1','description')
            #~ web.board.append_completed(ticket.get('title'), '1','description')
        web.div.append(web.board.render())
        return web.div.render()

