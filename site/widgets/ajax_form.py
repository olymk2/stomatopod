from scaffold.web import www
from scaffold.loaders import load_resource

class control(www.default.html_ui):
    
    def create(self, html):
        self.content = html
        return self

    def render(self):
        return '<div class="ajax-form-container">%s</div>' % self.content

