from flask import Flask, render_template

app = Flask(__name__)

from . import log
from . import views

app.register_blueprint(views.api.api)