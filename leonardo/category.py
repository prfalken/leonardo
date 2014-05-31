import os
import yaml
from dashboard import Dashboard


class Category:
    def __init__(self, graphite_base, render_url, graph_templates, name,  options={}):
        self.graphite_base = graphite_base
        self.graphite_render = self.graphite_base + "/render/"
        self.graph_templates = graph_templates
        self.name = name
        self.dash_templates = "%s/%s" % (graph_templates, name)
        self.height = options.get('height')
        self.width = options.get('width')
        self.time_from = options.get('from')
        self.until = options.get('until')
        self.options = options

    def dashboard(self, name, options={}):
        if not options.get('width'): options['width'] = self.width
        if not options.get('height'): options['height'] = self.height
        if not options.get('from'): options['from'] = self.time_from
        if not options.get('until'): options['until'] = self.until

        return Dashboard(name, self.graph_templates, self.name, options, self.graphite_render)

    def dashboards(self):
        dashboards = []
        for dash in sorted(os.listdir(self.dash_templates)):
            if not dash.startswith('.'):
                yaml_file = os.path.join(self.dash_templates, dash, "dash.yaml")
                if os.path.exists(yaml_file):
                    with open(yaml_file) as f:
                        yaml_conf = yaml.load(f.read())

                    yaml_conf.update( { 'category' : self.name, 'link' : dash } ) 
                    dashboards.append(yaml_conf)

        return dashboards


