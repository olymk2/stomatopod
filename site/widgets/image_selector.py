import os
from scaffold.core.widget import base_widget
from scaffold.loaders import load_resource
    
class control(base_widget):
    includes = []
    script = [load_resource('./widgets/image_selector.js')]
    #~ with open(os.path.abspath('./widgets/image_selector.js')) as fp:
        #~ script = [fp.read()]
        #~ print script

    htm_container = """
        <label for="image_selector">Select project image</label>
        <input type="text" class="image_selector_image" name="selected_image" value="" />
        <ul class="image_selector">%s</ul>"""

    htm_image = """
        <li><img src="/static/images/defaults/projects/%s" data-name="%s"/></li>"""

    def create(self):
        #~ super(control, self).create()
        return self

    def get_script(self):
        print self.script
        return "<script type=\"text/javascript\">%s</script>" % "\n\t".join(self.script)

    def render(self):
        self.count += 1
        images = []
        for image_name in os.listdir(os.path.abspath('./static/images/defaults/projects/')):
            images.append("""<li><img src="/static/images/defaults/projects/%s" data-name="%s" style="width:150px;height:150px;" /></li>""" % (image_name, image_name))
        
        return """<label for="image_selector">Select project image</label><input type="text" class="image_selector_image" name="selected_image" value="" /><ul class="image_selector">%s</ul>""" % ''.join(images)
        

