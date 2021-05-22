#!/usr/bin/env python

import yaml
from flask import Flask
from leonardo import app

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0')

