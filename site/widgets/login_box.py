from scaffold.web import www

class control(www.default.html_ui):
    oauth_enabled = False
    
    def create(self):
        return self

    def enable_oauth(self):
        self.oauth_enabled = True

    def render(self):
        htm = '<img id="login_img" src="/static/template/images/mantis-shrimp.png" />'
        htm += '<div id="login_box">'
        htm += '<form id="user_info" method="post" action="/login" >'
        htm += '<label>username</label><input id="username" name="username" type="text"/>'
        htm += '<label>password</label><input id="password" name="password" type="password"/>'
        htm += '<input type="submit" value="Login"/>'
        htm += '</form>'
        htm += '<a href="/register">Register for an account</a>'

        htm += '<div class="providers">'
        htm += '<a title="Login with Google" href="/oauth/google"><img src="/static/images/oauth/google.png" /></a><br />'
        #htm += '<a title="Login with facebook" href="/oauth/github">Facebook</a>.<br />'
        #htm += '<a title="Login with twitter" href="/oauth/teitter">Twitter</a>.<br />'
        htm += '</div>'

        htm += '</div>'



        return htm

