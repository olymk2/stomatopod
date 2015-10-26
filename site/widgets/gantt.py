from scaffold.web import web
from scaffold.web import www

class control(www.default.html_ui):  
    title = ''

    page = ''
    subpage = ''
    db = ''
    
    data_total = 0.0
    data_max = 0
    data_min = 0
    data = []

    show_open_id = False

    def create(self, text=None, data_max=100):
        self.data_min = None
        self.data = []
        if text:
            self.title = text

    def append(self, start, end, title=''):
        self.data_total = float(max(end, self.data_total))
        if self.data_min is None:
            self.data_min = start
        self.data_min = min(self.data_min, start)
        print 'append' + str(start)
        self.data.append((start, end, title))
        
    def render(self, html=""):
        htmout = '<div style="background-color:#fff;width:100%;height:200px;position:relative;">'
        count = 0
        print self.data_total
        print self.data_min
        if self.data_total and self.data_min:
            total = self.data_total - self.data_min
            for start, end, title in self.data:
                print self.data_min 
                print start
                print end
                data_range_start = start - self.data_min
                data_range_end = end - self.data_min
                data_total = self.data_total - self.data_min
                print data_range_start
                print data_range_end
                print data_total
                print '----'
                
                left = (data_range_start / (data_total)) * 100.0
                end = ((data_range_end / (data_total)) * 100.0) - left
                htmout += '<div style="background-color:#000;position:absolute;top:%spx;left:%s%%;height:20px;width:%s%%;" title="%s"></div>' % (count, left, end, title)
                count += 25
        
        htmout+='</div>'    

        return htmout
     

