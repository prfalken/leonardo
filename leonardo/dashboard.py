import os, fnmatch
import glob
import yaml
from .graph import GraphiteGraph
from .log import LoggingException

class Dashboard:
    def __init__(self, short_name, graph_templates, category, options={}, graphite_render=""):
        self.properties = {
             'graph_width' : None,
             'graph_height' : None,
             'graph_from' : None,
             'graph_until' : None 
        }

        self.properties['short_name'] = short_name
        self.properties['graph_templates'] = graph_templates
        self.properties['category'] = category
        self.properties['directory'] = directory = os.path.join( graph_templates, category, short_name )
        self.properties['graphite_render'] = graphite_render

        # set options from main config
        self.properties.update(options)
        if options.get('width'): self.properties['graph_width'] = options['width']
        if options.get('height'): self.properties['graph_height'] = options['height']
        if options.get('from'): self.properties['graph_from'] = options['from']
        if options.get('until'): self.properties['graph_until'] = options['until']

        if not os.path.isdir(directory):
            raise LoggingException("Cannot find dashboard directory %s" % directory)

        self.properties['yaml'] = yaml_file = os.path.join(directory, "dash.yaml")

        if not os.path.isfile(yaml_file):
            raise LoggingException("Cannot find YAML file %s" % yaml_file)

        with open(yaml_file) as yaml_conf:
            self.properties.update( yaml.load(yaml_conf, Loader=yaml.FullLoader ) )

        # Include external properties
        properties_include = []
        if self.properties.get('include_properties'):
            properties_include = self.properties['include_properties']
            if type(properties_include) is str:
                properties_include = set( [ self.properties['include_properties'] ] )
            elif type(properties_include) is list:
                properties_include = set( self.properties['include_properties'] )

        if options.get('include_properties'):
            properties_include |= set( options['include_properties'] )

        for property_file in properties_include:
            yaml_file = os.path.join(graph_templates, property_file)
            if os.path.isfile(yaml_file):
                with open(yaml_file) as yaml_conf:
                    self.properties.update( yaml.load(yaml_conf, Loader=yaml.FullLoader ) )

        # Graph inclusion
        include_option = self.properties.get('include_graphs')
        if not include_option or include_option == "" :
            graph_includes = []
        elif type(include_option) is list:
            graph_includes = include_option
        elif type(include_option) is str:
            graph_includes = [include_option]
        else:
            raise LoggingException("Invalid value for include in %s/dash.yaml" % (directory))

        # Expand wildcards with glob, creates list of lists
        self.graph_includes = [ glob.glob( os.path.join(graph_templates, d) ) for d in graph_includes ]
        # merge into one big list
        self.graph_includes = [ item for sublist in self.graph_includes for item in sublist ]



    def list_graphs(self):
        graphs = {}
        directory = self.properties['directory']
        current_graphs = [ f for f in os.listdir(directory) if fnmatch.fnmatch(f, '*.graph') ]

        # if there is less graphs than columns, override graph_columns
        # to the number of graphs        
        graph_columns = self.properties.get('graph_columns')
        if graph_columns:
            if len(current_graphs) < graph_columns:
                self.properties['graph_columns'] = len(current_graphs)
        
        for graph_filename in current_graphs:
            graph_name = os.path.splitext(graph_filename)[0]
            graphs[graph_name] = os.path.join(directory, graph_filename)

        for graph_filepath in self.graph_includes:
            graph_name = os.path.splitext(graph_filepath)[0]
            graphs[graph_name] = graph_filepath

        return graphs


    def graphs(self, options={}):
        options['width']  = self.properties['graph_width']
        options['height'] = self.properties['graph_height']
        options['from']   = self.properties['graph_from']
        options['until']   = self.properties['graph_until']

        overrides = { k : v for k,v in list(options.items()) if v }
        if self.properties.get('graph_properties'):
            overrides.update(self.properties['graph_properties'])
        if options.get('placeholder'):
            overrides.update(options['placeholder'])

        graphs = self.list_graphs()
        graphite_graphs = []
        
        for gname, gfile in list(graphs.items()):
            gg = GraphiteGraph( gfile, overrides )
            graphite_graphs.append( { 'name': gname , 'graphite' : gg  } )

        return graphite_graphs


    def graph_by_name(self, name, options={}):
        options['width']  = self.properties['graph_width']
        options['height'] = self.properties['graph_height']
        options['from']   = self.properties['graph_from']
        options['until']   = self.properties['graph_until']

        overrides = { k : v for k,v in list(options.items()) if v }
        if self.properties.get('graph_properties'):
            overrides.update(self.properties['graph_properties'])
        if options.get('placeholder'):
            overrides.update(options['placeholder'])


        graphs = self.list_graphs()
        gg = GraphiteGraph( graphs[name], overrides )
        
        return { 'name': name, 'graphite': gg }




