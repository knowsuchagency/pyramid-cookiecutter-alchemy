from pyramid.config import Configurator
from configparser import ConfigParser
from functools import partial
from pathlib import Path


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.scan()
    return config.make_wsgi_app()


def zappa(config_uri, event, context, **vars):
    """
    Uses the settings in the configuration uri to bootstrap a wsgi application
    through our pyramid application. Zappa then uses that wsgi application
    to create a handler function for use with aws lambda. Event and context
    information are passed through aws to the handler function and it takes that
    information along with our wsgi application to return a response.
    
    :param config_uri: str
    :param event: aws event
    :param context: aws context
    :param vars: parameters that will be passed to the configuration file
    :return: response
    """
    config = ConfigParser()
    config.read(config_uri)
    settings = dict(config.items('app:main', vars=vars))
    wsgi_app = main(None, **settings)

    return wsgi_app(event, context)


zappa_dev = partial(zappa, 'development.ini', here=str(Path(__file__).parent))
zappa_prod = partial(zappa, 'production.ini')
