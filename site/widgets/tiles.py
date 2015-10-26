from scaffold.web import www

class control(www.default.html_ui):
    def create(self):
        self.data = []
        return self

    def append(self, title, link, image='projects.png'):
        if not image:
            image = 'projects.png'
        self.data.append((title, link, image))

    def render(self):
        htm = ''
        for project in self.data:
            htm += '<div class="tile">'
            htm += '<div><img src="/static/images/defaults/projects/%s"/></div>' % project[2]
            htm += '<div style="padding-left:5px;"><a href="%s">%s</a></div>' % (project[1], project[0])
            htm += '</div>'
        return htm
