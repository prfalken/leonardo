import unittest
import urllib.parse

from leonardo import graph

from . import DATA_DIR


class GraphTest(unittest.TestCase):
    
    maxDiff = None
    def setUp(self):
        self.g = graph.GraphiteGraph("%s/graphs/System/server-1/cpu.graph" % DATA_DIR)


    def test_graph_init(self):
        self.assertEqual( self.g.properties.get("title") , "Combined CPU Usage")

    def test_url(self):
        parts = urllib.parse.parse_qs( self.g.url(), keep_blank_values=True)
        self.assertEqual ( parts, 
            {   'from'  : ['-1hour'], 
                'target': ['cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.wait.value),"IO Wait"),"si")', 
                         'cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.system.value),"System"),"si")', 
                         'cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.user.value),"User"),"si")'], 
                'title': ['Combined CPU Usage'], 
                'areaMode': ['stacked'], 
                'height': ['None'], 
                'width': ['None'], 
                'vtitle': ['percent'], 
                'until': ['Now']
            }
        )

    def test_get_graph_spec(self):
        expected_result = {     'url': 'title=Combined CPU Usage&vtitle=percent&from=-1hour&width=None&height=None&until=Now&areaMode=stacked&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.wait.value),"IO Wait"),"si")&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.system.value),"System"),"si")&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.user.value),"User"),"si")&format=json',
                                'properties':
                                {   'ymaxright': None,
                                    'yunit_system': None,
                                    'height': None,
                                    'hide_y_axis': None,
                                    'timezone': None,
                                    'hide_axes': None,
                                    'ymin': None,
                                    'background_color': None,
                                    'vtitle_right': None,
                                    'draw_null_as_zero': False,
                                    'fontbold': False,
                                    'linewidth': None,
                                    'from': '-1hour',
                                    'ymax': None,
                                    'title': 'Combined CPU Usage',
                                    'minor_grid_line_color': None,
                                    'foreground_color': None,
                                    'width': None,
                                    'theme': None,
                                    'area_alpha': None,
                                    'hide_grid': None,
                                    'until': 'Now',
                                    'linemode': None,
                                    'description': 'The combined CPU usage',
                                    'graphtype': None,
                                    'fontsize': None,
                                    'vtitle': 'percent',
                                    'logbase': None,
                                    'placeholders': None,
                                    'surpress': False,
                                    'yminright': None,
                                    'major_grid_line_color': None,
                                    'area': 'stacked',
                                    'unique_legend': None,
                                    'fontname': None,
                                    'xformat': None,
                                    'hide_legend': None,
                                    'margin': None,
                                    'color_list': None
                                },
                                'yaml_file': {'area': 'stacked',
                                                'description': 'The combined CPU usage',
                                                'fields': {'iowait': {'alias': 'IO Wait',
                                                                      'cacti_style': 'si',
                                                                      'data': 'sumSeries(collectd.server-1.cpu.*.cpu.wait.value)'},
                                                           'system': {'alias': 'System',
                                                                      'cacti_style': 'si',
                                                                      'data': 'sumSeries(collectd.server-1.cpu.*.cpu.system.value)'},
                                                           'user': {'alias': 'User',
                                                                    'cacti_style': 'si',
                                                                    'data': 'sumSeries(collectd.server-1.cpu.*.cpu.user.value)'}},
                                                'title': 'Combined CPU Usage',
                                                'vtitle': 'percent'
                                             }
                            }

        self.assertEqual( expected_result, self.g.get_graph_spec()  )

