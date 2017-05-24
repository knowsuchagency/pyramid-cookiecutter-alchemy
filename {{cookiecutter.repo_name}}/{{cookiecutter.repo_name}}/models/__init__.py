from functools import singledispatch, partial
from contextlib import contextmanager
from pathlib import Path

from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import sessionmaker

import pkg_resources
import transaction
import zope.sqlalchemy

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .mymodel import MyModel  # noqa

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

DEVELOPMENT_CONFIG_URI = pkg_resources. \
    get_distribution('{{ cookiecutter.repo_name }}').get_resource_filename(
    pkg_resources.ResourceManager(),
    'development.ini'
)


@contextmanager
@singledispatch
def dbsession(arg):
    """
    A context manager that allows us to connect to the database
    given pastedeploy settings.

    i.e.

    from pyramid.paster import get_appsettings
    import mytest.models as models

    config_uri = '/path/to/mytest/development.ini'
    settings = get_appsettings(config_uri)
    with models.dbsession(settings) as session:
        ... do stuff

    """
    raise TypeError(f"No handler function registered for object of type {type(arg)}")


@dbsession.register(dict)
def _(settings):
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)
    with transaction.manager:
        session = get_tm_session(session_factory, transaction.manager)
        yield session


@dbsession.register(str)
def _(config_uri):
    """
    Given a path to a configuration file, yield a dbsession.

    i.e.

    import pyramid_project.models as models

    config_uri = '/path/to/{{ cookiecutter.repo_name }}/development.ini'
    with models.dbsession(config_uri) as session:
        ... do stuff
    """
    path = Path(config_uri)
    settings = get_appsettings(str(path.absolute()))
    with dbsession(settings) as session:
        yield session


# default context manager for use during development
development_session = partial(dbsession, DEVELOPMENT_CONFIG_URI)


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('{{ cookiecutter.repo_name }}.models')``.

    """
    settings = config.get_settings()

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )
