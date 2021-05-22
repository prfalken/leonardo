
import os
from . import category
from . import config
from time import strftime, localtime

class Leonardo(object):
    ''' 
    Top level Class that defines the initial configuration of Leonard
    '''

    __instance = None
    def __new__(cls):
        '''
        Create a Singleton so that all views can call an unique instance of Leonardo
        '''

        if cls.__instance is None:
            cls.__instance = super(Leonardo,cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance


    def __init__(self):
        if(self.__initialized): return
        self.__initialized = True

        self.options = config.YAML_CONFIG.get('options')

        # where graphite lives
        self.graphite_base = config.YAML_CONFIG.get('graphite')

        # proxy graphite or go directly?
        self.proxy_graphite = config.YAML_CONFIG.get('proxy_graphite', False)

        # where the graphite renderer is
        if self.proxy_graphite:
          self.graphite_render = "/_graphite/" 
        else:
          self.graphite_render = "%s/render/" % self.graphite_base

        # where to find graph, dash etc templates
        self.graph_templates = config.YAML_CONFIG.get('templatedir')

        # the dash site might have a prefix for its css etc
        self.prefix = self.options.get('prefix', "")

        # the page refresh rate
        self.refresh_rate = self.options.get('refresh_rate', 60)

        # how many columns of graphs do you want on a page
        self.graph_columns = self.options.get('graph_columns', 2)

        # how wide each graph should be
        self.graph_width = self.options.get('graph_width')

        # how hight each graph sould be
        self.graph_height = self.options.get('graph_height')

        # Dashboard title
        self.dash_title = self.options.get('title', 'Graphite Dashboard')

        # Dashboard logo
        self.dash_logo = self.options.get('logo')

        # Time filters in interface
        self.interval_filters = self.options.get('interval_filters', [])

        self.intervals = self.options.get('intervals', [])

        self.top_level = {}

        for category_name in [ name for name in os.listdir(self.graph_templates)
                                        if not name.startswith('.') and os.path.isdir(os.path.join(self.graph_templates, name)) ]:

            if os.listdir( os.path.join(self.graph_templates,category_name) ) != []:

                self.top_level[category_name] = category.Category( self.graphite_render,
                                                              self.graph_templates,
                                                              category_name,
                                                              { "width" : self.graph_width,
                                                                "height" : self.graph_height
                                                              }
                                                            )

        self.search_elements = [ "%s/%s" % (d['category'], d['name'])   for dash in self.top_level  for d in self.top_level[dash].dashboards() ]

        elements_string = ""
        for item in self.search_elements:
            elements_string += '"%s",' % item
        self.search_elements = "[%s]" % elements_string[:-1]

    def fmt_for_select_date(self, date, default):
        result = ""
        try:
            date = int(date)
        except:
            result = default
        else:
            result = strftime("%Y-%m-%d %H:%M", localtime(date) )
        return result

