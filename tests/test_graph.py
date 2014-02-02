import unittest
import urlparse
import urllib

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

