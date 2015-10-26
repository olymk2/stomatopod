#~ from settings import web
from libs.html import web
from libs.create_data import *
from libs.modify_data import *
from libs.select_data import *


from plugin.plugins import plugin

class view_profile_template:
    def __call__(self):
        return self

    def render(self, values):
        web.div.set_id('profile').create(
            web.title.create('User Profile').render())
        web.images.create('/static/images/defaults/users/01.jpg', "name").add_attributes('width', '200')
        
        web.div.append(web.images.render())
        
        web.list.create(web.link.set_id('edit-profile').create('Edit Profile', 'Edit Profile', '/edit-profile').set_classes('ajax-form').render())
        web.list.append('test')
        web.list.append('name' + str(get_user_info({'id': values.get('user_id')})))
        web.list.append('teams ' + ','.join([row.get('name') for row in get_user_teams(values)]))
        
        web.div.append(web.list.render())
        return web.div.render()

class edit_profile_template:
    def __call__(self):
        return self

    def render(self, values):

        web.container.create('<div>')
        
        web.container.append(web.title.create('Editing Profile' + web.div.create('').set_classes('close-button icon-content-white icon-content-white-ic_add_white_24dp').render()).render())
        web.form.create('/edit-ticket', node_id='edit_profile_form', node_class='form-horizontal')
        user_info = get_user_info({'id': values.get('user_id')})

        web.form.append('<label for="email">Email</label><input type="text" name="email" value="'+values.get('job_code','')+'">')
        web.form.append('<label for="title">Name</label><input type="text" name="name" value="'+values.get('title','')+'">')
        web.form.append('<label for="csvvalues">Notes</label><textarea style="width:100%;height:100px;" name="note">'+values.get('note','')+'</textarea>')
        web.form.append('<input type="submit" value="Create Ticket" />')

        #web.container.append('')
        web.container.append(web.form.render())
        web.container.append('</div>')
        return web.container.render()
