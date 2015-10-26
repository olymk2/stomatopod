from scaffold.core.widget import base_widget
from scaffold.loaders import load_resource

    
class control(base_widget):
    script = [load_resource('./widgets/search_filter.js')]

    def create(self, params={}):
        self.params = params
        return self

    def get_script(self):
        return "<script type=\"text/javascript\">%s</script>" % "\n\t".join(self.script)

    def render(self):
        self.count += 1
        htm = '<div ng-controller="ExampleController">'
        htm += '<form method="get"><input id="search_filter" type="text" ng-model="user.name" ng-model-options="{ debounce: 1000 }" ng-ajax-url="/view-projects/search/" placeholder=" - Type project filter here - " name="search_filter"/></form>'        
        htm += '</div>'
        return htm

