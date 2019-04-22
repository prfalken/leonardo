"""  
Leonardo comes with a variety of logging options. Logging is
configurable via the YAML config file. Each heading under `logging`
specifies the type of the logging option to enable. Heading under those
specify the options.

The following logging types are available [stdout, file, syslog, email].

Below is an example of configuration which will email error to
error@example.com, save info to /var/log/leonardo, and dump debug to the
screen.

logging:
    - email:
        level: error
        to: error@example.com
    - file:
        level: info
        path: /var/log/leonardo
    - stdout:
        level: debug

"""

from . import app
from . import config
import logging
import logging.handlers

log_format = \
    '%(asctime)s %(levelname)s: %(message)s ' \
    '[in %(pathname)s:%(lineno)d]'

email_log_format='''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''

def level_from_str(s):
    """ Given a string return the corresponding runlevel code or None 
    
    The function returns non None values when given the following input
    strings ['notset', 'debug', 'info', 'warning', 'error', 'critical'].
    """
    try:
        return { 
            'notset': logging.NOTSET,
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
        }[s.lower()]
    except KeyError:
        return None


if 'logging' in config.YAML_CONFIG:
    for i in config.YAML_CONFIG.get('logging'):

        key = list(i.keys())[0] # Get the key 
        level = level_from_str(i[key].get('level', None))

        def get_option(key, option, default=None, required=False):
            value = i[key].get(option, default)
            if required and value == default == None:
                raise Exception(
                    "logging type `{}` requires option `{}`".format(key, option))
            return value

        if key == 'file':

            """
            logging:
                - file:
                    level: info
                    path: /path/to/log/file
            """

            handler = logging.FileHandler(
                filename = get_option(key, 'filename', required=True), 
                mode = get_option(key, 'mode', 'a'), 
                encoding = get_option(key, 'encoding', None), 
                delay = get_option(key, 'delay', False),
            )

            handler.setFormatter(logging.Formatter(log_format))
        
        elif key == 'email':

            """
            === Example Configuration ===
            logging:
                - email:
                    level: warring
                    mailhost: example.com
                    fromaddr: admain@example.com
                    toaddrs: 
                        - warring@example.com
                        - admin@example.com
                    subject: "WARNING: Leonardo"
            """
            
            
            handler = logging.handlers.SMTPHandler(
                mailhost = get_option(key, 'mailhost', required=True),
                fromaddr = get_option(key, 'fromaddr', required=True),
                toaddrs = get_option(key, 'toaddrs', required=True),
                subject = get_option(key, 'subject', required=True),
                credentials = get_option(key, 'credentials', None),
                secure = get_option(key, 'secure', None),
            )

            handler.setFormatter(email_log_format)


        elif key == 'syslog':

            """
            === Example Configuration ===
            logging:
                - syslog:
                    level: error
                    host: localhost
                    port: 514
            """
            
            try:
                handler = logging.handlers.SysLogHandler(
                    (get_option(key, 'host', 'localhost'), 
                     int(get_option(key, 'port', '514'))),
                )
            except Exception:
                raise Exception("logging type `syslog` requires option"
                                "`port` with int value")

            handler.setFormatter(log_format)
             
        elif key == 'stdout':

            """
            === Example Configuration ===
            logging:
                - stdout:
                    level: debug
            """

            handler = logging.StreamHandler()
            handler.setFormatter(log_format)

        else:
            continue

        if level:
            handler.setLevel(level)

        app.logger.addHandler(handler)

else:
    # Add default handler
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_format)
    app.logger.addHandler(log_handler)

class LoggingException(Exception):

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        app.logger.exception(self.message)
