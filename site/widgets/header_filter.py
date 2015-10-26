from scaffold.core.widget import base_widget
from settings import web

class control(base_widget):
    def create(self, params):
        self.params = params
        return self

    def render(self):
        if self.params.get('hide_top_bar'):
            return ''

        htm = '<div id="navbar">'
        htm += '<div id="nav-contain">'
        htm += '<div id="nav-middle"><ul><li><span>STOMATOPOD</span></li></ul></div>'
        htm += '<div id="formticket">show form here</div>'

        htm += '<ul id="nav-right">'
        htm += '<li><a href="/view-queue">My Queue</a></li>'
        htm += '<li><a href="/view-teams">My Teams</a></li>'
        htm += '<li><a href="/view-projects">My Projects</a></li>'
        htm += '</ul>'

        htm += '<ul id="nav-left">'
        htm += '<li><a id="showfilter" href="/show-filter"><div class="icon-action-white icon-action-white-ic_reorder_white_24dp"></div></a></li>'
        htm += '<li><a id="newticket" href="/view-my-tickets">%s</a></li>' % (self.params.get('ticket_count', '0'))
        htm += '<li><a href="/view-users">U</a></li>' 
        htm += '<li><a href="/view-projects">P</a></li>' 
        htm += '<li><a id="newmilestone" href="/new-milestone">M</a></li>'
        htm += '<li><a id="username" href="/view-profile">%s</a></li>' % (self.params.get('username', 'Anonymous'))
        htm += '</ul>'

        htm += web.action_bar.create('/new-project', 'New Project', 'add-project', 'icon-action-white icon-action-white-ic_assignment_white_24dp') \
            .append('/new-milestone', 'New Team', 'add-team', 'icon-action-white icon-action-white-ic_note_add_white_24dp') \
            .append('/new-milestone', 'New Milestone', 'add-milestone', 'icon-action-white icon-action-white-ic_note_add_white_24dp') \
            .append('/new-ticket', 'New Ticket', 'add-ticket', 'icon-content-white icon-content-white-ic_add_white_24dp').render()
        #~ htm+= '<a id="nav-plus" href="/project/1"><div class="icon-content-white icon-content-white-ic_add_white_24dp"></div></a>'
        
        htm += '</div>'
        htm += '</div>'
        htm += '<div class="form-popout" style="display:none;"></div>'
        return htm
