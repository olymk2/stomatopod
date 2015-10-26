from scaffold.web import www
from scaffold.loaders import load_resource

class control(www.default.html_ui):
    html = load_resource('./widgets/check_list.htm')

    def create(self):
        self.data = []
        return self

    def append(self, text, status):
        self.data.append((title, project_id, image))

    def render(self):
        return self.html.format(**self.defaults)
