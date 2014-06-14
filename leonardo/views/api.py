from flask import Response, Blueprint
import json
from frontend import dash, detail, single

api = Blueprint('api', __name__, url_prefix='/api')

# These routes return graphs Graphite URL + Leonardo properties as a JSON list of dictionaries
# They can be used as a gateway to render graphs with toolkits such as Rickshaw, HighCharts ...

@api.route('/<category>/<dash_name>/')
def json_dashboard(category, dash_name):

    graphs = dash(category, dash_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)


@api.route('/<category>/<dash_name>/details/<path:graph_name>/')
def json_detailed(category, dash_name, graph_name):

    graphs = detail(category, dash_name, graph_name, format='json')
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )
    return Response(graph_list)


@api.route('/<category>/<dash_name>/single/<path:graph_name>/')
def json_single(category, dash_name, graph_name):

    graph = single(category, dash_name, graph_name, format='json')
    graph_spec = json.dumps( graph['graphite'].get_graph_spec() )
    return Response(graph_spec)
