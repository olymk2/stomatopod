from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *

from plugin.plugins import plugin

def dict_to_list(data, keys):
    return [data.get(k) for k in keys]


class milestone_tickets_view_old:
    project = None
    milestones_in_progress = []

    def render_milestone_tickets(self, title, data):
        print data
        data.get('project_id')
        plugin.get_project_tickets(data.get('project_id'))
        
        web.table.create('Tickets for %s milestone' % title, ('Milestone', 'Status', 'Title', 'Updated'))
        milestone_tickets = get_milestone_tickets(data)
        for row in milestone_tickets:
            values = dict_to_list(row, ('milestone_name', 'status', 'title', 'updated'))
            values[0] = web.link.create(values[0], values[0], '/view-milestone/%s' % row.get('milestone_id')).render()
            values[1] = web.link.create(values[1], values[1], '/view-ticket/%s' % row.get('id')).render()
            values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
            values[3] = web.link.create(values[3], values[3], '/view-ticket/%s' % row.get('id')).render()
            web.table.append(values)
        web.pagination.create(perpage=5, total=milestone_tickets.get_total(), page=1)
        return web.table.render()

    def render(self, values):
        project_info = get_milestone(values).get()
        web.div.create(
            web.title.create(project_info.get('title')).render())
        web.div.append(self.render_milestone_tickets(project_info.get('title'), values))
        return web.div.render()
