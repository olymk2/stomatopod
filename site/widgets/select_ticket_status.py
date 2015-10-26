from constants import STATUS_LIST
from scaffold.web import www
from scaffold.scaffold import web 
#~ from scaffold.loaders import load_resource

class control(www.default.html_ui):
    
    def create(self, selected=None):
        self.selected = selected
        return self

    def render(self):
        web.select.create('status_id', label='').append('', ' -- Select Status -- ')
        for status_id, status_name in STATUS_LIST.items():
            print status_id
            print self.selected
            web.select.append(status_id, status_name, self.selected)
        return web.select.render()
