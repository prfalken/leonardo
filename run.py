#!/usr/bin/env python

import yaml
from flask import Flask
from leonardo import app


app.debug = True
app.run(host='0.0.0.0')


