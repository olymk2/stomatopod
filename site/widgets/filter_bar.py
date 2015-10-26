from scaffold.core.widget import base_widget

class control(base_widget):
    def create(self, params={}):
        self.params = params
        return self

    def render(self):
        if self.params.get('user_teams') is None:
            return ''
        htm = '<div id="leftbar">'        

        htm += '<div id="filters">'

        htm += '<div class="widget-dropdown">'
        htm += '<ul>'
        htm += '<ul><li class="hover"><a href="/view-projects">View projects</a></li>'
        #~ htm += '</li><li class="hover">'.join(['<a href="/view-project/%s">%s</a>' % (project) for project in self.params.get('projects', [])])
        #htm += '<li class="hover"><a href="/project/1">Project 1</a></li>'
        #htm += '<li class="hover selected"><a href="/project/2">Project 2</a></li>'
        htm += '</ul>'
        
        
        htm += '<ul><li class="hover"><a href="/view-teams">View teams</a></li>'
        htm += ''.join(
            ['<li class="hover"><a href="/view-team-tickets/%s">%s</a></li>' % (team.get('team_id'), team.get('name')) for team in self.params.get('user_teams')])
        #htm += '</div>'

        htm += '</ul></div>'
        
        #~ htm += '<div id="filter_projects_id" class="filter %s" data-value="%s">Project</div>' % tuple([
            #~ self.params.get('project_id', ''), 'ticked' if self.params.get('project_id') else ''])
        #~ htm += '<div id="filter_milestone_id" class="filter %s" data-value="%s">Milestone</div>' % tuple([
            #~ self.params.get('milestone_id', ''), 'ticked' if self.params.get('milestone_id') else ''])
        #~ htm += '<div id="filter_status_id" class="filter %s" data-value="%s">Status</div>' % tuple([
            #~ 'ticked' if self.params.get('status_id') else '', self.params.get('status_id', '')])

        htm += '</div>'

        htm += '</div>'
        return htm

