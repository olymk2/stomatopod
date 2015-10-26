from scaffold.core.widget import base_widget

class control(base_widget):
    link = None
    action = ""
    includes = []
    script = []

    def create(self, url, title, node_id='', styles='icon-content-white icon-content-white-ic_add_white_24dp'):
        self.content = []
        self.append(url, title, node_id, styles)
        return self

    def append(self, url, title, node_id='', styles='icon-content-white-ic_add_white_24dp'):
        if node_id:
            node_id = 'id="%s" ' % node_id
        self.content.append(
            '<a class="action-bar-button ajax-form" title="%s" %sdata-ajax-url="%s" href="%s">\n\t\t<div class="%s"></div></a>' % (title, node_id, url, url, styles))
        return self

    def render(self):
        self.count += 1
        return """<div class="action-bar"><div class="container">\n%s</div></div>""" % "\n".join(self.content)
