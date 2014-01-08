from flask_wtf import Form
from wtforms import *
 
class TemplateForm(Form):
    metric = TextField("metric")

class NodeForm(Form):
    nodes = SelectMultipleField('Pick Nodes',
                widget = widgets.Select(multiple=True),
            )