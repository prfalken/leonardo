from flask import request, render_template, make_response, redirect, Response, url_for
import json
import re
from . import app
from graph import GraphiteGraph
from log import LoggingException
import urllib
from leonardo import Leonardo



def get_dashboard_from_category(category, dash, options):

    leonardo = Leonardo()

    if leonardo.top_level.get(category):
        dashboard = leonardo.top_level[category].dashboard(dash, options)
    else:
        raise LoggingException('Category %s does not exist' % category )

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

    leonardo = Leonardo()

    app.logger.debug(
        "responing to %s method on %s route" %
        (request.method, request.url)
    )

    favorite_dashboard = request.cookies.get('favorite')
    if favorite_dashboard is not None:
        category, dash = filter(None, urllib.unquote(favorite_dashboard).split('/'))
        app.logger.debug('Redirect to favorite dashboard /%s/%s' % (category, dash) )
        return redirect( url_for('dash', category = category, dash = dash) )


    if leonardo.top_level == {}:
        app.logger.warning("No dashboards found in the templates directory")
    dashboards_to_display = {}
    for k in leonardo.top_level:
        dashboards_to_display[k] = [ d for d in leonardo.top_level[k].dashboards() ]

    return render_template("index.html", leonardo = leonardo, dashboards = dashboards_to_display)


@app.route('/<category>/<dash>/', methods=['GET', 'POST'])
def dash(category, dash, format='standard'):

    leonardo = Leonardo()

    app.logger.debug(
        "responing to %s method on %s route" %
        (request.method, request.url)
    )

    options = { 'graph_columns': leonardo.graph_columns }
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

    # check if dashboard is set as favorite
    favorite_dashboard = request.cookies.get('favorite', '')
    if urllib.unquote( favorite_dashboard ) == request.path:
        dashboard.properties['favorite'] = True

    if request.args.get('full'):
        resp = make_response( render_template("full.html", leonardo = leonardo, dashboard = dashboard.properties, graphs = graphs, args = args_string, links_to=None) )
    else:
        resp = make_response( render_template("dashboard.html", leonardo = leonardo, dashboard = dashboard.properties, graphs = graphs, args = args_string, links_to='detail' ) )

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

    leonardo = Leonardo()

    app.logger.debug(
        "responing to %s %s" %
        (request.method, request.url)
    )

    options = { 'graph_columns': leonardo.graph_columns }

    # Build Dashboard
    dashboard = get_dashboard_from_category(category, dash, options)

    # Retrieve zoomed values if necessary, and update dashboard with new width and height properties
    dashboard = zoom(request, dashboard)

    graphs = []
    for e in leonardo.intervals:
        graph = dashboard.graph_by_name(name, options)
        title = "%s - %s" % ( graph['graphite'].properties['title'] , e[1] )
        new_props = { 'from': e[0] , 'nice_from': e[1] ,'title': title }
        graph['graphite'].properties.update( new_props )
        graph['graphite'] = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
        graphs.append(graph)

    if format == 'json':
        return graphs

    resp = make_response( render_template("graphs_all_periods.html", leonardo = leonardo, dashboard = dashboard.properties, graphs = graphs, links_to="single") )

    resp.set_cookie( 'graph_topo', json.dumps( { 'width': dashboard.properties['graph_width'],
                                                 'height': dashboard.properties['graph_height'],
                                                 'graph_columns' : dashboard.properties['graph_columns']
                                                }
                                            )
    )

    return resp



@app.route('/<category>/<dash>/single/<path:name>/', methods=['GET', 'POST'])
def single(category, dash, name, format='standard'):

    leonardo = Leonardo()

    # Set default width of a single graph to <default nb columns> times <default width>
    single_width = leonardo.graph_columns * leonardo.graph_width
    # Set default height of a single graph to twice the <default height>
    single_height = 2 * leonardo.graph_height

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

    if format == 'json':
        return graph

    resp = make_response( render_template("single.html", leonardo = leonardo, dashboard = dashboard.properties, graph = graph, links_to=None) )
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

    leonardo = Leonardo()

    graphs = dash(category, dash_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)


@app.route('/api/<category>/<dash_name>/details/<path:graph_name>/')
def json_detailed(category, dash_name, graph_name):

    leonardo = Leonardo()

    graphs = detail(category, dash_name, graph_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)

@app.route('/api/<category>/<dash_name>/single/<path:graph_name>/')
def json_single(category, dash_name, graph_name):

    leonardo = Leonardo()

    graph = single(category, dash_name, graph_name, format='json')
    graph_spec = json.dumps( graph['graphite'].get_graph_spec() )
    return Response(graph_spec)



@app.route('/search/')
def search():

    leonardo = Leonardo()

    app.logger.debug(
        "responing to %s %s" %
        (request.method, request.url)
    )

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
    for k in leonardo.top_level:
        for d in leonardo.top_level[k].dashboards():
            category_and_name = '%s/%s' % (d['category'], d['name'])
            if search_string and re.match(search_string, category_and_name, re.IGNORECASE):
                dashboard_list.append(category_and_name)

    if len(dashboard_list) == 1:
        category, name = dashboard_list[0].split('/')
        app.logger.debug("redirecting to /%s/%s"  % (category, name))
        return redirect("/%s/%s" % (category, name))
    else:
        return multiple(dashboard_list)


@app.route('/multiple/')
def multiple(asked_dashboards = None):

    leonardo = Leonardo()

    app.logger.debug(
        "responing to %s %s" %
        (request.method, request.url)
    )

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
        if leonardo.top_level.get(category):
            dashboard = leonardo.top_level[category].dashboard(name, options)
            dashboard.no_resize = True
            dashboard.graphs = dashboard.graphs()
            dashboard_list.append(dashboard)

    args_string = '&'.join( [ "%s=%s" % (k,v) for k,v in request.args.items() ] )

    resp = make_response( render_template("multiple.html", leonardo = leonardo, dashboard_list = dashboard_list, args = args_string ) )

    resp.set_cookie("from", str(options['from']))
    resp.set_cookie("until", str(options['until']))
    app.logger.debug("Setting cookies from:%s until:%s" % (str(options['from']), str(options['until'])))

    return resp





@app.errorhandler(404)
def not_found(error):
  app.logger.debug("404")
  return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
