from flask import Response, Blueprint
import json
from ..leonardo import Leonardo
from ..graph import GraphiteGraph
from ..config import YAML_CONFIG

api = Blueprint('api', __name__, url_prefix='/api')

# These routes return graphs Graphite URL + Leonardo properties as a JSON list of dictionaries
# They can be used as a gateway to render graphs with toolkits such as Rickshaw, HighCharts ...
# You can also use this API to create your own front end.

@api.route('/<category>/<dash_name>/')
def json_dashboard(category, dash_name):

    leonardo = Leonardo()

    options = { 'graph_columns': leonardo.graph_columns }
    dashboard = leonardo.top_level[category].dashboard(dash_name, options)
    graphs = dashboard.graphs()
    graph_list = [ g['graphite'].get_graph_spec() for g in graphs ]

    result = {  'main_config' : YAML_CONFIG ,
                'dashboard_properties' : dashboard.properties,
                'graph_list': graph_list,

    }

    return Response( json.dumps(result) )


@api.route('/<category>/<dash_name>/details/<path:graph_name>/')
def json_detailed(category, dash_name, graph_name):

    leonardo = Leonardo()
    options = { 'graph_columns': leonardo.graph_columns }
    dashboard = leonardo.top_level[category].dashboard(dash_name, options)

    graphs = []
    for e in leonardo.intervals:
        graph = dashboard.graph_by_name(graph_name, options)
        title = "%s - %s" % ( graph['graphite'].properties['title'] , e[1] )
        new_props = { 'from': e[0] , 'nice_from': e[1] ,'title': title }
        graph['graphite'].properties.update( new_props )
        graph['graphite'] = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
        graphs.append(graph)
    graph_list = json.dumps( [ g['graphite'].get_graph_spec() for g in graphs ] )

    return Response(graph_list)


@api.route('/<category>/<dash_name>/single/<path:graph_name>/')
def json_single(category, dash_name, graph_name):

    leonardo = Leonardo()

    dashboard = leonardo.top_level[category].dashboard(dash_name, options={})
    graph = dashboard.graph_by_name(graph_name, options={})
    graphite_graph = GraphiteGraph( graph['graphite'].file, graph['graphite'].properties)
    graph_spec = graphite_graph.get_graph_spec()

    result = { 'main_config' : YAML_CONFIG ,
                    'graph' : graph_spec
            }


    return Response( json.dumps(result) )
