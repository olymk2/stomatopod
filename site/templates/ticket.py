from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *
from settings import *

from plugin.plugins import plugin


def dict_to_list(data, keys):
    return [data.get(k) for k in keys]

class create_ticket:
    def create(self, data):
        create_new_ticket(data)
        plugin.create_ticket(data)
        return web.div.render()
    
    def modify(self, data):
        create_new_ticket(data)
        plugin.create_ticket(data)
        return web.div.render()

class create_ticket_note:
    def create(self, data):
        new_ticket_note().execute(data)
        plugin.create_ticket_note(data)
        return web.div.render()
    
    def modify(self, data):
        modify_ticket_note(data)
        plugin.modify_ticket_note(data)
        return web.div.render()

class update_ticket_view:
    def __call__(self):
        return self
    #~ def check_authorised(self):

    def add_ticket_notes(self, note):
        if not note:
            return 
        new_ticket_note().execute(self.new_values)
        

    def change_ticket_status(self, ticket_status, new_status):
        if self.ticket.get('status_id') == None:
            return None
        if self.ticket.get('status_id') == self.new_values.get('status_id'):
            return None
        create_ticket_status_change().execute(self.new_values)
        self.new_values['status_id'] = self.ticket.get('status_id')
        update_ticket_status().execute(self.ticket)

    def render(self, data):
        self.new_values = data
        view_ticket = get_ticket(data)
        values = view_ticket.get()
        self.ticket = view_ticket.get()
        if data.get('user_id') == self.ticket.get('owner_user_id'):
            print 'not owner'
        if data.get('team_id') == self.ticket.get('team_id'):
            print 'not in team'
        self.change_ticket_status(self.ticket.get('status_id'), self.new_values.get('status_id'))
        self.add_ticket_notes(self.new_values.get('notes'))
        return web.template.render()


class ticket_view:
    project = None
    milestones_in_progress = []

    def render_ticket(self, values):
        project_info = get_project(values).get()        
        web.title.create(values.get('title'))

        web.container.create(web.title.render())
        web.container.append(
            web.images.create('/static/images/defaults/projects/%s' % project_info.get('image')).add_attributes('width', '300').render())
        
        
        print values
        web.table.create('title', ('', ''))
        web.table.append(('milestone', web.link.create(
            values.get('milestone_name'),
            values.get('milestone_name'),
            '/view-project/%s/view-milestone/%s' % (values.get('project_id'), values.get('milestone_id'))).render()))
        web.table.append(('Last updated', '' if not values.get('updated') else values.get('updated').strftime(DATE_FORMAT)))
        web.table.append(('status', STATUS_LIST[values.get('status_id')]))
        web.table.append(('Reported By', str(values.get('owner_user_id'))))

        #TODO make this a hook into the plugin system
        #~ view_mantis_ticket = get_mantis_ticket_id({'ticket_id': data['id']})
        #~ mantis_ticket_id = view_mantis_ticket.get().get('mantis_ticket_id')
        #~ web.table.append((
            #~ 'Mantis ticket id',
            #~ web.link.create(
                #~ '#' + str(mantis_ticket_id),
                #~ '#' + str(mantis_ticket_id),
                #~ 'https://tracker.tangentlabs.co.uk/view.php?id=%s' % mantis_ticket_id).render()))

        web.container.append(web.table.render())
        #~ web.container.append(str(values))

        web.container.append(web.div.create('notes can go here').render())
        web.container.append(web.div.create('').set_id('ticket-history').render())
        return web.container.render()

        def render_milestone_tickets(self, title, data):
            web.table.create('Tickets for %s milestone' % title, ('Milestone', 'Status', 'Updated', 'Summary'))
            milestone_tickets = get_milestone_tickets(data)
            for row in milestone_tickets:
                values = dict_to_list(row, ('milestone_name', 'status', 'updated', 'title'))
                values[0] = web.link.create(values[0], values[0], '/view-milestone/%s' % row.get('milestone_id')).render()
                values[1] = web.link.create(values[1], values[1], '/view-ticket/%s' % row.get('id')).render()
                values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
                web.table.append(values)
            web.pagination.create(perpage=5, total=milestone_tickets.get_total(), page=1)
            return web.table.render()

    def render_ticket_notes(self, data):
        web.paragraph.create('')
        ticket_notes = get_ticket_notes(data)
        for note in ticket_notes:
            web.paragraph.add(note.get('note').replace('\n', '<br />'))
        return web.paragraph.render()

    def render_quick_note_form(self, data):
        web.form.create('/update-ticket/%s' % data.get('id'), node_id='add-ticket-notes', node_class='form-horizontal')
        web.form.append('<input type="hidden" name="project_id" value="%s" />' % data.get('project_id', ''))
        web.form.append('<input type="text" name="time_spent" value="%s" />' % data.get('time_spent', ''))
        web.form.append(web.select_ticket_status.create(data.get('status_id')).render())
        web.form.append('<label for="note">Notes</label><textarea style="width:100%;height:100px;" name="note">' + data.get('note', '') + '</textarea>')
        web.form.append('<input type="submit" value="Add Notes" />')
        return web.form.render()

    def render(self, data):
        view_ticket = get_ticket(data)
        values = view_ticket.get()
        print values
        #project_info = get_milestone(values).get()
        web.div.create(
            web.title.create('Ticket').render())
        web.div.append(self.render_ticket(values))
        web.div.append(self.render_ticket_notes(values))
        web.div.append(self.render_quick_note_form(values))
        return web.div.render()



class tickets_default_view:
    table_title = 'My Tickets'
    project = None
    milestones_in_progress = []

    def get_data(self, values, page=0):
        return get_my_tickets(values, page=0)

    def render(self, values):
        web.table.create(self.table_title, ('Summary', 'Milestone', 'Status', 'Updated'))
        values['status_id'] = STATUS_IN_PROGRESS
        my_tickets = self.get_data(values, page=0)
        for row in my_tickets:
            values = dict_to_list(row, ('title', 'milestone_name', 'status', 'updated'))
            values[0] = web.link.create(values[0], values[0], '/view-ticket/%s' % row.get('id')).render()
            values[1] = web.link.create(values[1], values[1], '/view-project/%s/milestone/%s' % (row.get('project_id'), row.get('milestone_id'))).render()
            values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
            values[3] = '' if row.get('updated') is None else row.get('updated')
            if row.get('updated'):
                values[3] = row.get('updated').strftime(DATE_FORMAT)
            web.table.append(values)
        web.pagination.create(perpage=PAGINATION_ROWS, total=my_tickets.get_total(), page=1)
        web.pagination.url(before='/my-tickets/', after=' ')
        web.div.create(web.table.render() + web.pagination.render())

        return web.div.render()

class my_tickets_view(tickets_default_view):
   pass

class team_tickets_view(tickets_default_view):
    table_title = 'Teams Tickets'
    project = None
    milestones_in_progress = []

    def get_data(self, values, page=0):
        return get_teams_tickets(values, page=0)


class milestone_tickets_view(tickets_default_view):
    table_title = 'Milestone Tickets'
    project = None
    milestones_in_progress = []

    def get_data(self, values, page=0):
        return get_milestone_tickets(values, page=0)

    #~ def render_milestone_tickets(self, title, data):
        #~ print data
        #~ data.get('project_id')
        #~ plugin.get_project_tickets(data.get('project_id'))
        #~ 
        #~ web.table.create('Tickets for %s milestone' % title, ('Milestone', 'Status', 'Title', 'Updated'))
        #~ milestone_tickets = get_milestone_tickets(data)
        #~ for row in milestone_tickets:
            #~ values = dict_to_list(row, ('milestone_name', 'status', 'title', 'updated'))
            #~ values[0] = web.link.create(values[0], values[0], '/view-milestone/%s' % row.get('milestone_id')).render()
            #~ values[1] = web.link.create(values[1], values[1], '/view-ticket/%s' % row.get('id')).render()
            #~ values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
            #~ values[3] = web.link.create(values[3], values[3], '/view-ticket/%s' % row.get('id')).render()
            #~ web.table.append(values)
        #~ web.pagination.create(perpage=5, total=milestone_tickets.get_total(), page=1)
        #~ return web.table.render()
#~ 
    #~ def render(self, values):
        #~ project_info = get_milestone(values).get()
        #~ web.div.create(
            #~ web.title.create(project_info.get('title')).render())
        #~ web.div.append(self.render_milestone_tickets(project_info.get('title'), values))
        #~ return web.div.render()

