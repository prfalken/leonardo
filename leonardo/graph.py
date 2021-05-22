import yaml
from .log import LoggingException

class Parser:
    def parse(self, input_string):
        return yaml.load(input_string, Loader=yaml.FullLoader)



class GraphiteGraph:
    def __init__(self, file, overrides={}):
        self.file = file
        self.overrides = overrides
        self.defaults()
        self.load_graph()

    def defaults(self):
        self.properties = {
                    "title" : None,
                    "vtitle" : None,
                    "vtitle_right" : None,
                    "width" : None,
                    "height" : None,
                    "graphtype" : None,
                    "from" : "-1hour",
                    "until" : "Now",
                    "surpress" : False,
                    "description" : None,
                    "hide_axes" : None,
                    "hide_legend" : None,
                    "hide_grid" : None,
                    "hide_y_axis" : None,
                    "ymin" : None,
                    "yminright" : None,
                    "ymax" : None,
                    "ymaxright" : None,
                    "yunit_system" : None,
                    "linewidth" : None,
                    "linemode" : None,
                    "fontsize" : None,
                    "fontbold" : False,
                    "fontname" : None,
                    "timezone" : None,
                    "xformat" : None,
                    "background_color" : None,
                    "foreground_color" : None,
                    "draw_null_as_zero" : False,
                    "major_grid_line_color" : None,
                    "minor_grid_line_color" : None,
                    "area" : None,
                    "logbase" : None,
                    "placeholders" : None,
                    "area_alpha" : None,
                    "theme" : None,
                    "unique_legend" : None,
                    "margin" : None,
                    "color_list" : None,
                }

        self.properties.update(self.overrides)


    def load_graph(self):
        self.targets = {}
        self.target_order = []
        self.yaml_spec = {}
        with open(self.file, 'r') as graph_file:
            p = Parser()
            try:
                self.yaml_spec = p.parse(graph_file.read())
            except Exception as e:
                raise LoggingException('Could not parse yaml file %s. Error was : %s' % (self.file, e) )



        for key in self.yaml_spec:
            if key != 'fields':
                self.properties[key] = self.yaml_spec[key]

        for field in self.yaml_spec['fields']:
            self.targets[field] = self.yaml_spec['fields'][field]
            self.target_order.append(field)

        if 'field_order' in self.yaml_spec:
            self.target_order = self.yaml_spec['field_order']


    def get_graph_spec(self):
        return { 'url': self.url() + '&format=json' , 'properties': self.properties, 'yaml_file' : self.yaml_spec }


    def url(self):
        properties = self.properties
        dual_axis = False
        for target in self.targets:
            if "second_y_axis" in self.targets[target]:
                dual_axis = True

        url_parts = [ "%s=%s" % (item, properties[item]) for item in ["title", "vtitle", "from", "width", "height", "until"] ]


        if properties.get("area"): url_parts.append( "areaMode=%s" % properties["area"] )
        if properties.get("hide_axes"): url_parts.append( "hideAxes=%s" % properties["hide_axes"] )
        hide_legend = properties.get("hide_legend")
        if hide_legend is not None: 
            if type(hide_legend) == int:
                if properties.get('height') > hide_legend:
                    url_parts.append( "hideLegend=False" )

            else:
                url_parts.append( "hideLegend=%s" % properties["hide_legend"] )

        if properties.get("hide_grid"): url_parts.append( "hideGrid=%s" % properties["hide_grid"] )
        if properties.get("hide_y_axis"): url_parts.append( "hideYAxis=%s" % properties["hide_y_axis"] )

        if dual_axis:
            if properties.get("ymin") is not None: url_parts.append( "yMinLeft=%s" % properties["ymin"] )
            if properties.get("ymax") is not None: url_parts.append( "yMaxLeft=%s" % properties["ymax"] )
        else:
            if properties.get("ymin") is not None: url_parts.append( "yMin=%s" % properties["ymin"] )
            if properties.get("ymax") is not None: url_parts.append( "yMax=%s" % properties["ymax"] )

        if properties.get("yminright") is not None: url_parts.append( "yMinRight=%s" % properties["yminright"] )
        if properties.get("ymaxright") is not None: url_parts.append( "yMaxRight=%s" % properties["ymaxright"] )
        if properties.get("yunit_system"): url_parts.append( "yUnitSystem=%s" % properties["yunit_system"] )
        if properties.get("linewidth"): url_parts.append( "lineWidth=%s" % properties["linewidth"] )
        if properties.get("linemode"): url_parts.append( "lineMode=%s" % properties["linemode"] )
        if properties.get("fontsize"): url_parts.append( "fontSize=%s" % properties["fontsize"] )
        if properties.get("fontbold"): url_parts.append( "fontBold=%s" % properties["fontbold"] )
        if properties.get("fontname"): url_parts.append( "fontName=%s" % properties["fontname"] )
        if properties.get("draw_null_as_zero"): url_parts.append( "drawNullAsZero=%s" % properties["draw_null_as_zero"] )
        if properties.get("timezone"): url_parts.append( "tz=%s" % properties["timezone"] )
        if properties.get("xformat"): url_parts.append( "xFormat=%s" % properties["xformat"] )
        if properties.get("major_grid_line_color"): url_parts.append( "majorGridLineColor=%s" % properties["major_grid_line_color"] )
        if properties.get("minor_grid_line_color"): url_parts.append( "minorGridLineColor=%s" % properties["minor_grid_line_color"] )
        if properties.get("graphtype"): url_parts.append( "graphType=%s" % properties["graphtype"] )
        if properties.get("background_color"): url_parts.append( "bgcolor=%s" % properties["background_color"] )
        if properties.get("foreground_color"): url_parts.append( "fgcolor=%s" % properties["foreground_color"] )
        if properties.get("vtitle_right"): url_parts.append( "vtitleRight=%s" % properties["vtitle_right"] )
        if properties.get("logbase"): url_parts.append( "logBase=%s" % properties["logbase"] )
        if properties.get("area_alpha"): url_parts.append( "areaAlpha=%s" % properties["area_alpha"] )
        if properties.get("min_x_step"): url_parts.append( "minXStep=%s" % properties["min_x_step"] )
        if properties.get("unique_legend"): url_parts.append( "uniqueLegend=%s" % properties["unique_legend"] )
        if properties.get("theme"): url_parts.append( "template=%s" % properties["theme"] )
        if properties.get("margin"): url_parts.append( "margin=%s" % properties["margin"] )
        if properties.get("color_list"): url_parts.append( "colorList=%s" % ','.join(properties["color_list"]) )

        # target is a graph specification 
        for target in self.target_order:

            graphite_target = self.targets[target]["data"]
            target_props = self.targets[target]

            if "exclude"                 in target_props: graphite_target = 'exclude(%s, "%s")' % ( graphite_target, target_props['exclude'] )
            if "remove_above_percentile" in target_props: graphite_target = "removeAbovePercentile(%s)" % graphite_target 
            if "remove_above_value"      in target_props: graphite_target = "removeAboveValue(%s,%s)" % (graphite_target, target_props['remove_above_value'] ) 
            if "remove_below_percentile" in target_props: graphite_target = "removeBelowPercentile(%s,%s)" % ( graphite_target, target_props['remove_below_percentile'] )
            if "remove_below_value"      in target_props: graphite_target = "removeBelowValue(%s,%s)" % ( graphite_target, target_props['remove_below_value'])
            if "field_linewidth"         in target_props: graphite_target = "lineWidth(%s,%s)" % ( graphite_target, target_props['field_linewidth'] )
            if "keep_last_value"         in target_props: graphite_target = "keepLastValue(%s)" % graphite_target
            
            if "derivative" in target_props:
              graphite_target = "derivative(%s)" % graphite_target
            elif "non_negative_derivative" in target_props:
              graphite_target = "nonNegativeDerivative(%s)" % graphite_target

            if "sum"                    in target_props: graphite_target = "sum(%s)" % graphite_target        
            if "sum_with_wildcard"      in target_props: graphite_target = "sumSeriesWithWildcard(%s,%s)" % ( graphite_target, target_props['sum_with_wildcard'] )
            if "highest_average"        in target_props: graphite_target = "highestAverage(%s,%s)" % ( graphite_target, target_props['highest_average'] )
            if "scale"                  in target_props: graphite_target = "scale(%s,%s)" % ( graphite_target, target_props['scale'] )
            if "scale_to_seconds"       in target_props: graphite_target = "scaleToSeconds(%s,%s)" % (target_props['scale_to_seconds'] )
            if "as_percent" in target_props:
                if target_props['as_percent'] == True:
                    graphite_target = "asPercent(%s)" % graphite_target
                else:
                    graphite_target = "asPercent(%s,%s)" % ( graphite_target, target_props['as_percent'] )

            if "summarize" in target_props: graphite_target = "summarize(%s,%s)" % ( graphite_target, target_props["summarize"])
            if "line"      in target_props: graphite_target = "drawAsInfinite(%s)" % graphite_target
            if "smoothing" in target_props: graphite_target = "movingAverage(%s,%s)" % ( graphite_target, target_props['smoothing'])

            if "color"         in target_props: graphite_target = "color(%s,\"%s\")" % ( graphite_target, target_props['color'] )
            if "dashed"        in target_props: graphite_target = "dashed(%s)" % graphite_target
            if "second_y_axis" in target_props: graphite_target = "secondYAxis(%s)" % graphite_target

            if 'alias_by_node' in target_props: 
                graphite_target = "aliasByNode(%s,%s)" % ( graphite_target, target_props['alias_by_node'])
            elif 'alias_sub_search' in target_props:
                graphite_target = """aliasSub(%s,"%s","%s")""" % ( graphite_target, target_props['alias_sub_search'], target_props['alias_sub_replace'] )
            elif 'substr' in target_props:
                graphite_target = "substr(%s,%s)" % ( graphite_target, target_props['substr'])
            elif 'alias' in target_props:
                graphite_target = """alias(%s,"%s")""" % ( graphite_target, target_props['alias'])

            if 'cacti_style' in target_props: 
                graphite_target = 'cactiStyle(%s,"%s")' % ( graphite_target, target_props['cacti_style'] )
            elif 'legend_value' in target_props:
                graphite_target = """legendValue(%s, %s)""" % (graphite_target, target_props['legend_value'])


            url_parts.append("target=%s" % graphite_target)

            url = "&".join(url_parts)

        return url
