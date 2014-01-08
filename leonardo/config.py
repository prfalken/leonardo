
import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = True
SECRET_KEY = 'JevyogiludalnieshuskVeakheewov'

with open("config/leonardo.yaml" ) as config_file:
     YAML_CONFIG = yaml.load( config_file.read() )

