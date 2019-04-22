from flask import request, redirect, url_for
import re
from .. import app
from ..leonardo import Leonardo
from .multiple import multiple

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
        return redirect(url_for("dash", category=category, dash=name))
    else:
        return multiple(dashboard_list)
