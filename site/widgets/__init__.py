#~ import os
#~ from scaffold.web import web as html
#~ from scaffold.web import www
#~ 
#~ web = html()
#~ web.load_widgets('widgets')
#~ web.document_root = os.path.abspath('./')
#~ web.template.theme_full_path = os.path.abspath('./') + os.sep + 'template' + os.sep
#~ web.template.enable_cache('cache')

#~ from filterbar import filter_bar
#~ from filterbar import header_filter
#~ from image_selector import image_selector
#~ from loginbox import login_box
#~ from gantt import gantt
#~ from tile import tiles
#~ web.elements['header_filter'] = header_filter()
#~ web.elements['filterbar'] = filter_bar()
#~ web.elements['image_selector'] = image_selector()
#~ web.elements['login_box'] = login_box()
#~ web.elements['gantt'] = gantt()
#~ web.elements['tiles'] = tiles()
