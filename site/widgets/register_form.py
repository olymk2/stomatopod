from scaffold.web import www
from scaffold.loaders import load_resource

class control(www.default.html_ui):
    html = load_resource('./widgets/register_form.htm')

    def __init__(self):
        self.defaults = {
            'name':'',
            'email':''}
    
    def create(self):
        return self

    def default_values(self, *defaults):
        self.defaults = defaults

    def render(self):
        return self.html.format(**self.defaults)

