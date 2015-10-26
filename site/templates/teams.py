#~ from settings import web
from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *


from plugin.plugins import plugin

def dict_to_list(data, keys):
    return [data.get(k) for k in keys]


class projects_view:
    project = None
    milestones_in_progress = []

    def render_projects(self, data):
        plugin.get_projects()
        web.tiles.create()
        for project in get_users_projects({'user_id': data.get('user_id')}, limit_rows=False):
            print project
            web.tiles.append(project.get('title'), project.get('id'), project.get('image'))
        return web.tiles.render()

    def render(self, values):
        web.div.create(
            web.title.create('Projects assigned to you').render())
        web.div.append(web.search_filter.create().render())
        web.div.append(self.render_projects(values))
        return web.div.render()


class teams_view:
    project = None
    milestones_in_progress = []

    def render(self, values, page=1):
        teams = get_user_teams(values)


        web.div.create(
            web.title.create('Your Teams').render())

        #~ web.div.append(str(project_info.get('image')))
        #~ self.render_milestones(values)
        web.tiles.create()
        if teams:
            
            for team in teams:
                print team
                #~ print team_id
                #~ print team_name
                #~ print team['name']
                web.tiles.append(team.get('name'), '/view-team/%s' % team.get('team_id'))
                #~ web.div.append(team)
                #~ values['milestone_id'] = milestone_id
                #~ web.div.append(self.render_milestone_tickets(milestone_title, values))
                #~ web.div.append(web.pagination.render())
            web.div.append(web.tiles.render())
        else:
            web.div.append('You are not in any teams')
        return web.tiles.render()



class project_teams_view:
    project = None
    milestones_in_progress = []

    def render(self, values, page=1):
        project_info = get_project(values).get()
        print project_info
        plugin.get_project_tickets(values.get('project_id'))

        web.div.create(
            web.title.create(project_info.get('title')).render())
        
        web.div.append(str(project_info.get('image')))
        self.render_milestones(values)
        if self.milestones_in_progress:
            for milestone_title, milestone_id in self.milestones_in_progress:
                values['milestone_id'] = milestone_id
                web.div.append(self.render_milestone_tickets(milestone_title, values))
                web.div.append(web.pagination.render())
        else:
            web.div.append('No milestones in progress')
        return web.div.render()


class team_tickets_view:
    project = None
    milestones_in_progress = []

    def render_project_tickets(self, title, data, page):
        plugin.get_project_tickets(data.get('project_id'))
        web.table.create('Tickets for %s' % title, ('Milestone', 'Status', 'Updated', 'Summary'))
        milestone_tickets = get_project_tickets(data, page=page)
        for row in milestone_tickets:
            values = dict_to_list(row, ('milestone_name', 'status', 'updated', 'title'))
            values[0] = web.link.create(values[0] + '&#10;test', values[0], '/view-milestone/%s' % row.get('milestone_id')).render()
            values[1] = web.link.create(values[1], values[1], '/view-ticket/%s' % row.get('id')).render()
            values[2] = web.link.create(values[2], values[2], '/view-ticket/%s' % row.get('id')).render()
            web.table.append(values)
        web.pagination.create(perpage=5, total=milestone_tickets.get_total(), page=1)
        web.pagination.url(before='/view-project/%s/tickets/' % data.get('project_id'), after=' ')
        return web.table.render()

    def render(self, values, page=1):
        project_info = get_project(values).get()
        plugin.get_project_tickets(values.get('project_id'))
        web.div.create(
            web.title.create(project_info.get('title')).set_id('view-projects').render())
        web.div.append(self.render_project_tickets(project_info.get('title'), values, page))
        web.div.append(web.pagination.render())
        return web.div.render()


class project_create:    
    def render(self):
        web.container.create('<div>')
        web.form.create('/new-project', node_id='csvimport', node_class='form-horizontal')
        web.form.append('<label for="title">Project Name</label><input type="text" name="title" value="">')
        web.form.append(web.image_selector.create().render())
        web.form.append('<input type="submit" value="Create Project" />')
        web.container.append(web.form.render())
        web.container.append('</div>')
        web.container.append(web.image_selector.get_script())
        return web.container.render()
