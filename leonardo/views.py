from flask import request, render_template, flash, g, session, redirect, url_for, make_response, redirect
import os
import urllib
import json
import re
from time import strftime, localtime
import copy
import config
from . import app
import leonardo
from graph import GraphiteGraph

class View:
    def __init__(self):
        self.options = config.YAML_CONFIG.get('options')

        # where graphite lives
        self.graphite_base = config.YAML_CONFIG.get('graphite')

        # where the graphite renderer is
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

        # Time filters in interface
        self.interval_filters = self.options.get('interval_filters', [])

        self.intervals = self.options.get('intervals', [])

        self.top_level = {}

        for category in [ name for name in os.listdir(self.graph_templates) 
                                        if not name.startswith('.') and os.path.isdir(os.path.join(self.graph_templates, name)) ]:
            
            if os.listdir( os.path.join(self.graph_templates,category) ) != []:                
                
                self.top_level[category] = leonardo.Leonardo( self.graphite_base, 
                                                              "/render/", 
                                                              self.graph_templates, 
                                                              category, 
                                                              { "width" : self.graph_width, 
                                                                "height" : self.graph_height
                                                              }
                                                            )

        self.search_elements = [ "%s/%s" % (d['category'], d['name'])   for dash in self.top_level  for d in self.top_level[dash].dashboards() ]

        elements_string = ""
        for item in self.search_elements:
            elements_string += '"%s",' % item
        self.search_elements = "[%s]" % elements_string[:-1]



    def uri_to_interval(self, options, category, dash):
        parameters = urllib.urlencode( {'from': options['from'], 'to': options['to']} )
        uri = "%s/%s/%s/?" % (self.prefix, category, dash)
        # uri.query = request.query_string unless request.query_string.empty? 
        return uri + parameters

    def link_to_interval(self, options, category, dash):
        if not options.get('to'):
            options['to'] = "now"
        uti = self.uri_to_interval(options, category, dash)
        return """<a href="%s">%s</a>""" % ( uti, options['label'] )

    def fmt_for_select_date(self, date, default):
        result = ""        
        try:
            date = int(date)
        except: 
            result = default
        else:
            result = strftime("%Y-%m-%d %H:%M", localtime(date) )
        return result


        
view = View()


@app.route('/')
def index():
    if view.top_level == {}:
        print "No dashboards found in the templates directory"
    dashboards_to_display = {}
    for k in view.top_level:
        dashboards_to_display[k] = [ d for d in view.top_level[k].dashboards() ]

    return render_template("index.html", view = view, dashboards = dashboards_to_display)


@app.route('/<category>/<dash>/', methods=['GET', 'POST'])
def dash(category, dash):

    options = { 'graph_columns': view.graph_columns }
    t_from = t_until = None

    # remember the time interval
    if request.cookies.get('interval'):
        cookie_date = json.loads(request.cookies["interval"])
        t_from = request.args.get( 'from', cookie_date['from'] ) or "-1hour"
        t_until = request.args.get( 'to', cookie_date['until'] ) or "now"

    options['from'] = t_from
    options['until'] = t_until


    # Build Dashboard
    if view.top_level.get(category):
        dashboard = view.top_level[category].dashboard(dash, options)

    else:
        raise Exception('Category %s does not exist' % category )

    args_string = '&'.join( [ "%s=%s" % (k,v) for k,v in request.args.items() ] )


    # ZOOM 
    zoom = request.form.get('zoom')

    if request.cookies.get('graph_topo'):
        cookie_size = json.loads(request.cookies["graph_topo"])

        if zoom == "zoom-in":
            dashboard.properties['graph_width']   = cookie_size['width'] * 1.5
            dashboard.properties['graph_height']  = cookie_size['height'] * 1.5
            if dashboard.properties['graph_columns'] > 1:
                dashboard.properties['graph_columns'] = cookie_size['graph_columns'] - 1 
        if zoom == "zoom-out":
            dashboard.properties['graph_width']   = cookie_size['width'] / 1.5
            dashboard.properties['graph_height']  = cookie_size['height'] / 1.5
            dashboard.properties['graph_columns'] = cookie_size['graph_columns'] + 1

    # Build dashboard's graphs
    graphs = dashboard.graphs()


    if request.args.get('full'):
        resp = make_response( render_template("full.html", view = view, dashboard = dashboard.properties, graphs = graphs, args = args_string ) )
    else:
        resp = make_response( render_template("dashboard.html", view = view, dashboard = dashboard.properties, graphs = graphs, args = args_string ) )

    resp.set_cookie( 'interval', json.dumps( { 'from': t_from, 'until': t_until } ) )
    resp.set_cookie( 'graph_topo', json.dumps( { 'width': dashboard.properties['graph_width'], 
                                                 'height': dashboard.properties['graph_height'], 
                                                 'graph_columns' : dashboard.properties['graph_columns'] 
                                                } 
                                            ) 
    )

    return resp


@app.route('/<category>/<dash>/details/<path:name>/', methods=['GET', 'POST'])
def detail(category, dash, name):

    options = { 'graph_columns': view.graph_columns }
    cookie_size = {}

    if view.top_level.get(category):
        dashboard = view.top_level[category].dashboard(dash, options)
    else:
        raise Exception('Category %s does not exist' % category )

    if request.cookies.get('graph_topo'):
        cookie_size = json.loads(request.cookies["graph_topo"])

    # ZOOM 
    zoomed_width, zoomed_height = dashboard.properties['graph_width'], dashboard.properties['graph_height']
    zoom = request.form.get('zoom')
    if zoom == "zoom-in":
        zoomed_width = cookie_size['width'] * 1.5
        zoomed_height = cookie_size['height'] * 1.5
        if dashboard.properties['graph_columns'] > 1:
            dashboard.properties['graph_columns'] = cookie_size['graph_columns'] - 1             
    if zoom == "zoom-out":
        zoomed_width  = cookie_size['width'] / 1.5
        zoomed_height = cookie_size['height'] / 1.5
        dashboard.properties['graph_columns'] = cookie_size['graph_columns'] + 1 

    graphs = []
    for e in view.intervals:
        graph = dashboard.graph_by_name(name, options)
        title = "%s - %s" % ( graph['graphite'].properties['title'] , e[1] )
        new_props = { 'from': e[0] , 'title': title, 'width': zoomed_width, 'height': zoomed_height }
        graph['graphite'].properties.update( new_props )
        graph['graphite'] = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
        graphs.append(graph)

    
    resp = make_response( render_template("detail.html", view = view, dashboard = dashboard.properties, graphs = graphs, omit_link = True) )

    resp.set_cookie( 'graph_topo', json.dumps( { 'width': zoomed_width, 
                                                 'height': zoomed_height, 
                                                 'graph_columns' : dashboard.properties['graph_columns'] 
                                                } 
                                            ) 
    )

    return resp





@app.route('/search/')
def search():
    search_string = request.args.get('dashboard', '')
    compare_with  = request.args.get('compare_with')

    try:
        category, dashboard = search_string.split('/', 1)
    except ValueError:
        category = None
        dashboard = search_string
    
    # try to expand search regexp
    dashboard_list = []
    if compare_with:
        dashboard_list = [compare_with]
    for k in view.top_level:
        for d in view.top_level[k].dashboards():
            category_and_name = '%s/%s' % (d['category'], d['name'])
            if re.match(search_string, category_and_name, re.IGNORECASE):
                dashboard_list.append(category_and_name)

    if len(dashboard_list) == 1:
        category, name = dashboard_list[0].split('/')
        return redirect("/%s/%s" % (category, name))
    else:
        return multiple(dashboard_list)


@app.route('/multiple/')
def multiple(asked_dashboards = None):
    options = {}
    t_from = t_until = None

    if request.cookies.get('interval'):
        cookie_date = json.loads(request.cookies["interval"])
        t_from = request.args.get( 'from', cookie_date['from'] ) or "-1hour"
        t_until = request.args.get( 'to', cookie_date['until'] ) or "now"


    options['from'] = t_from
    options['until'] = t_until

    dashboard_list = []
    for db in asked_dashboards:
        category, name = db.split('/')
        if view.top_level.get(category):
            dashboard = view.top_level[category].dashboard(name, options)
            dashboard.no_resize = True
            dashboard.graphs = dashboard.graphs()
            dashboard_list.append(dashboard)

    args_string = '&'.join( [ "%s=%s" % (k,v) for k,v in request.args.items() ] )

    resp = make_response( render_template("multiple.html", view = view, dashboard_list = dashboard_list, args = args_string ) )
    resp.set_cookie( 'interval', json.dumps( { 'from': t_from, 'until': t_until } ) )
    return resp





@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404

