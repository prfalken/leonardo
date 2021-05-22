import os
import yaml

basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY', 'MY_SECRET_KEY')
config_filename = os.environ.get('CONFIG_FILE',
                                 basedir + "/../config/leonardo.yaml")

with open(config_filename) as config_file:
     YAML_CONFIG = yaml.load( config_file.read(), Loader=yaml.FullLoader )


# Handles env variable for the graphite server
YAML_CONFIG['graphite'] = os.environ.get('GRAPHITE_SERVER', YAML_CONFIG['graphite'])

