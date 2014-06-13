from flask import request, make_response, render_template
from .. import app
from ..leonardo import Leonardo


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


