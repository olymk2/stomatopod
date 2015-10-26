from settings import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *

def dict_to_list(data, keys):
    return [data.get(k) for k in keys]


class error_view:
    project = None
    milestones_in_progress = []

    errors = {
        100: 'Missing Data',
        104: 'Permission denied'}

    def render(self, values):
        web.div.create('An Error occured please report the issue')
        web.div.append(self.render_ticket(values))
        web.div.append(self.render_ticket_notes(values))
        web.div.append(self.render_quick_note_form(values))
        return web.div.render()





