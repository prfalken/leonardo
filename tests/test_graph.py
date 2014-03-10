import unittest
import urlparse
import json

from leonardo import graph

from . import DATA_DIR


class GraphTest(unittest.TestCase):
    
    maxDiff = None

    def test_graph_init(self):
        g = graph.GraphiteGraph("%s/cpu.graph" % DATA_DIR)
        self.assertEqual( g.properties.get("title") , "Combined CPU Usage")

    def test_url(self):
        g = graph.GraphiteGraph("%s/cpu.graph" % DATA_DIR)
        parts = urlparse.parse_qs( g.url(), keep_blank_values=True)
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
        g = graph.GraphiteGraph("%s/cpu.graph" % DATA_DIR)
        expected_result = {     u'url': u'title=Combined CPU Usage&vtitle=percent&from=-1hour&width=None&height=None&until=Now&areaMode=stacked&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.wait.value),"IO Wait"),"si")&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.system.value),"System"),"si")&target=cactiStyle(alias(sumSeries(collectd.server-1.cpu.*.cpu.user.value),"User"),"si")&format=json',
                                u'properties':
                                {   u'ymaxright': None,
                                    u'yunit_system': None,
                                    u'height': None,
                                    u'hide_y_axis': None,
                                    u'timezone': None,
                                    u'hide_axes': None,
                                    u'ymin': None,
                                    u'background_color': None,
                                    u'vtitle_right': None,
                                    u'draw_null_as_zero': False,
                                    u'fontbold': False,
                                    u'linewidth': None,
                                    u'from': u'-1hour',
                                    u'ymax': None,
                                    u'title': u'Combined CPU Usage',
                                    u'minor_grid_line_color': None,
                                    u'foreground_color': None,
                                    u'width': None,
                                    u'theme': None,
                                    u'area_alpha': None,
                                    u'hide_grid': None,
                                    u'until': u'Now',
                                    u'linemode': None,
                                    u'description': u'The combined CPU usage',
                                    u'graphtype': None,
                                    u'fontsize': None,
                                    u'vtitle': u'percent',
                                    u'logbase': None,
                                    u'placeholders': None,
                                    u'surpress': False,
                                    u'yminright': None,
                                    u'major_grid_line_color': None,
                                    u'area': u'stacked',
                                    u'unique_legend': None,
                                    u'fontname': None,
                                    u'xformat': None,
                                    u'hide_legend': None}}

        self.assertEqual( expected_result, g.get_graph_spec()  )

