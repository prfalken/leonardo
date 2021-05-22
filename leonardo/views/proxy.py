from flask import request, render_template, Response
from ..leonardo import Leonardo
from .. import app
from urllib.parse import urlparse, urlunparse
import requests

@app.route('/_graphite/', methods=["GET"])
def proxy():
  leonardo = Leonardo()

  graph_render = "%s/render/" % leonardo.graphite_base
  r = make_request(graph_render, request.query_string)

  headers = dict(r.raw.headers)
  def generate():
    for chunk in r.raw.stream(decode_content=False):
      yield chunk

  out = Response(generate(), headers=headers)
  out.status_code=r.status_code

  return out

def make_request(url, params):
  request_url = "%s?%s" %( url, params )
  return requests.get(request_url, stream=True)

