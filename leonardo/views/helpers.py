import json

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
