from scaffold.web import www

class control(www.default.html_ui):
    def create(self):
        self.data = []
        return self

    def append(self, title, project_id, image='projects.png'):
        if not image:
            image = 'projects.png'
        self.data.append((title, project_id, image))

    def render(self):
        htm = ''
        for project in self.data:
            htm += '<div class="tile">'
            htm += '<div><img src="/static/images/defaults/users/%s"/></div>' % project[2]
            htm += '<div style="padding-left:5px;"><a href="/view-project/%s">%s</a></div>' % (project[1], project[0])
            #~ htm += ['<div>%s</div>'title, project_id for project in self.data]
            htm += '</div>'
        return htm
