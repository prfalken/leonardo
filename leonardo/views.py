from flask import request, render_template, make_response, redirect, Response
import os
import json
import re
from time import strftime, localtime, time
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


def get_dashboard_from_category(category, dash, options):
    if view.top_level.get(category):
        dashboard = view.top_level[category].dashboard(dash, options)
    else:
        raise Exception('Category %s does not exist' % category )

    return dashboard


def zoom(request, dashboard):
    cookie_size = {}

    if request.cookies.get('graph_topo'):
        cookie_size = json.loads(request.cookies["graph_topo"])

    zoomed_width, zoomed_height = dashboard.properties['graph_width'], dashboard.properties['graph_height']
    zoom = request.form.get('zoom')
    if zoom == "zoom-in":
        dashboard.properties['graph_width'] = cookie_size['width'] * 1.5
        dashboard.properties['graph_height'] = cookie_size['height'] * 1.5
        if cookie_size['graph_columns'] > 1:
            dashboard.properties['graph_columns'] = cookie_size['graph_columns'] - 1
        else:
            dashboard.properties['graph_columns'] = cookie_size['graph_columns']

    if zoom == "zoom-out":
        dashboard.properties['graph_width']  = cookie_size['width'] / 1.5
        dashboard.properties['graph_height'] = cookie_size['height'] / 1.5
        dashboard.properties['graph_columns'] = cookie_size['graph_columns'] + 1

    return dashboard



@app.route('/')
def index():
    if view.top_level == {}:
        print "No dashboards found in the templates directory"
    dashboards_to_display = {}
    for k in view.top_level:
        dashboards_to_display[k] = [ d for d in view.top_level[k].dashboards() ]

    return render_template("index.html", view = view, dashboards = dashboards_to_display)


@app.route('/<category>/<dash>/', methods=['GET', 'POST'])
def dash(category, dash, format='standard'):

    options = { 'graph_columns': view.graph_columns }
    # Set a default time range, being -1 hour
    t_until = "now"
    t_from = "-1hour"

    # Get the time range from the navigator. Precedence: Query string > cookie > default.
    options['from'] = request.args.get( 'from', request.cookies.get('from', t_from))
    options['until'] = request.args.get( 'until', request.cookies.get('until', t_until))

    # Build Dashboard
    dashboard = get_dashboard_from_category(category, dash, options)

    args_string = '&'.join( [ "%s=%s" % (k,v) for k,v in request.args.items() ] )

    # Retrieve zoomed values if necessary, and update dashboard with new width and height properties
    dashboard = zoom(request, dashboard)

    # Build dashboard's graphs
    graphs = dashboard.graphs()

    if format == 'json':
        return graphs

    if request.args.get('full'):
        resp = make_response( render_template("full.html", view = view, dashboard = dashboard.properties, graphs = graphs, args = args_string, links_to=None) )
    else:
        resp = make_response( render_template("dashboard.html", view = view, dashboard = dashboard.properties, graphs = graphs, args = args_string, links_to='detail' ) )

    resp.set_cookie("from", str(options['from']))
    resp.set_cookie("until", str(options['until']))
    app.logger.debug("Setting cookies from:%s until:%s" % (str(options['from']), str(options['until'])))

    resp.set_cookie( 'graph_topo', json.dumps( { 'width': dashboard.properties['graph_width'],
                                                 'height': dashboard.properties['graph_height'],
                                                 'graph_columns' : dashboard.properties['graph_columns']
                                                }
                                            )
    )

    return resp



@app.route('/<category>/<dash>/details/<path:name>/', methods=['GET', 'POST'])
def detail(category, dash, name, format='standard'):

    options = { 'graph_columns': view.graph_columns }

    # Build Dashboard
    dashboard = get_dashboard_from_category(category, dash, options)

    # Retrieve zoomed values if necessary, and update dashboard with new width and height properties
    dashboard = zoom(request, dashboard)

    graphs = []
    for e in view.intervals:
        graph = dashboard.graph_by_name(name, options)
        title = "%s - %s" % ( graph['graphite'].properties['title'] , e[1] )
        new_props = { 'from': e[0] , 'nice_from': e[1] ,'title': title }
        graph['graphite'].properties.update( new_props )
        graph['graphite'] = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
        graphs.append(graph)

    if format == 'json':
        return graphs

    resp = make_response( render_template("detail.html", view = view, dashboard = dashboard.properties, graphs = graphs, links_to="single") )

    resp.set_cookie( 'graph_topo', json.dumps( { 'width': dashboard.properties['graph_width'],
                                                 'height': dashboard.properties['graph_height'],
                                                 'graph_columns' : dashboard.properties['graph_columns']
                                                }
                                            )
    )

    return resp



@app.route('/<category>/<dash>/single/<path:name>/', methods=['GET', 'POST'])
def single(category, dash, name):

    # Set default width of a single graph to <default nb columns> times <default width>
    single_width = view.graph_columns * view.graph_width
    # Set default height of a single graph to twice the <default height>
    single_height = 2 * view.graph_height

    # Get the time range from the navigator. Precedence: Query string > cookie > default.
    t_from = request.args.get( 'from', request.cookies.get('from', "-1hour"))
    t_until = request.args.get( 'until', request.cookies.get('until', "now"))

    # Get dashboard where the graph comes from
    dashboard = get_dashboard_from_category(category, dash, options={})

    # Retrieve zoomed values if necessary, and update dashboard with new width and height properties
    dashboard = zoom(request, dashboard)

    # get the graph
    graph = dashboard.graph_by_name(name, options={})
    graph['graphite'] = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
    new_props = { 'from': t_from, 'until': t_until, 'width': single_width, 'height': single_height }
    graph['graphite'].properties.update( new_props )

    resp = make_response( render_template("single.html", view = view, dashboard = dashboard.properties, graph = graph, links_to=None) )
    resp.set_cookie( 'graph_topo', json.dumps( { 'width': dashboard.properties['graph_width'],
                                                 'height': dashboard.properties['graph_height'],
                                                }
                                            )
    )

    return resp



# These routes return graphs Graphite URL + Leonardo properties as a JSON list of dictionaries
# They can be used as a gateway to render graphs with toolkits such as Rickshaw, HighCharts ...
@app.route('/api/<category>/<dash_name>/')
def json_dashboard(category, dash_name):

    graphs = dash(category, dash_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)


@app.route('/api/<category>/<dash_name>/details/<path:graph_name>/')
def json_detailed(category, dash_name, graph_name):

    graphs = detail(category, dash_name, graph_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)



@app.route('/search/')
def search():
    search_string = request.args.get('dashboard')
    compare_with  = request.args.get('compare_with')

    try:
        category, dashboard = search_string.split('/', 1)
    except ValueError:
        category = None

    # try to expand search regexp
    dashboard_list = []
    if compare_with:
        dashboard_list = [compare_with]
    for k in view.top_level:
        for d in view.top_level[k].dashboards():
            category_and_name = '%s/%s' % (d['category'], d['name'])
            if search_string and re.match(search_string, category_and_name, re.IGNORECASE):
                dashboard_list.append(category_and_name)

    if len(dashboard_list) == 1:
        category, name = dashboard_list[0].split('/')
        return redirect("/%s/%s" % (category, name))
    else:
        return multiple(dashboard_list)


@app.route('/multiple/')
def multiple(asked_dashboards = None):
    options = {}
    # Set a default time range, being -1 hour
    t_until = "now"
    t_from = "-1hour"

    # Get the time range from the navigator. Precedence: Query string > cookie > default.
    options['from'] = request.args.get( 'from', request.cookies.get('from', t_from))
    options['until'] = request.args.get( 'until', request.cookies.get('until', t_until))

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

    resp.set_cookie("from", str(options['from']))
    resp.set_cookie("until", str(options['until']))
    app.logger.debug("Setting cookies from:%s until:%s" % (str(options['from']), str(options['until'])))

    return resp





@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
