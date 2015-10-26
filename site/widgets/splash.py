from scaffold.web import www
from scaffold.loaders import load_resource

class control(www.default.html_ui):
    def create(self, image, link):
        self.image = image
        self.link = link
        return self

    def render(self):
        return '<a href="%s"><img src="%s" /><p>Welcome please add a new project</p></a>' % (self.link, self.image)
