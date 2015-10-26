from scaffold.web import www

class control(www.default.html_ui):
    def create(self, title='Title Here'):
        self.title = title
        self.data = []
        self.data_in_progress = []
        self.data_completed = []
        return self

    def append_progress(self, view_id, title, description):
        self.data_in_progress.append((view_id, title, description))

    def append_completed(self, view_id, title, description):
        self.data_completed.append((view_id, title, description))

    def append(self, view_id, title, description):
        self.data.append((view_id, title, description))

    def render(self):
        htm = '<div class="board">'
        htm += '<div><h2>%s</h2></div>' % self.title
        htm += '<div class="left column">'
        for project in self.data:
            htm += '<div class="tile">'
            htm += '<div class="title"><a href="/view-project/%s">%s</a></div>' % (project[1], project[0])
            htm += '<div>%s</div>' % project[2]
            
            htm += '</div>'
        htm += '</div>'

        htm += '<div class="middle column">'
        for project in self.data_in_progress:
            htm += '<div class="tile">'
            htm += '<div class="title"><a href="/view-project/%s">%s</a></div>' % (project[1], project[0])
            htm += '<div>%s</div>' % project[2]
            
            htm += '</div>'
        htm += '</div>'

        htm += '<div class="right column">'
        for project in self.data_completed:
            htm += '<div class="tile">'
            htm += '<div class="title"><a href="/view-project/%s">%s</a></div>' % (project[1], project[0])
            htm += '<div>%s</div>' % project[2]
            
            htm += '</div>'
        htm += '</div>'
        htm += '</div>'
        return htm
