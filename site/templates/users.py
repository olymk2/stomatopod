#~ from settings import web
from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *


from plugin.plugins import plugin

def dict_to_list(data, keys):
    return [data.get(k) for k in keys]

class create_user:
    def create(self, data):
        new_user = create_new_user()
        new_user.execute(data)
        return web.div.render()
    
    def modify(self, data):
        create_new_ticket(data)
        plugin.create_ticket(data)
        return web.div.render()


class users_view:
    project = None
    milestones_in_progress = []

    def render_users(self, data):
        web.user_tiles.create()
        for user in get_users({}, limit_rows=False):
            web.user_tiles.append(user.get('username') + '<br />' + user.get('first_name') + ' ' + user.get('last_name'), user.get('id'), user.get('image'))
        return web.user_tiles.render()

    def render(self, values):
        web.div.create(
            web.title.create('Users').render())
        web.div.append(self.render_users(values))
        return web.div.render()

