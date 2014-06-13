from .. import app
from flask import render_template

@app.errorhandler(404)
def not_found(error):
  app.logger.debug("404")
  return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
