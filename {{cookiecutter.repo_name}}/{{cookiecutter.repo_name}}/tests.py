from pyramid import testing

import transaction
import pytest


def dummy_request(dbsession):
    return testing.DummyRequest(dbsession=dbsession)


@pytest.fixture()
def config():
    with testing.testConfig(settings={'sqlalchemy.url': 'sqlite:///:memory:'}) as cfg:
        cfg.include('{{ cookiecutter.project_name }}.models')
        yield cfg


@pytest.fixture()
def settings(config):
    return config.get_settings()


@pytest.fixture()
def engine(settings):
    from .models import get_engine
    return get_engine(settings)


@pytest.fixture()
def session(engine):
    from .models import get_session_factory, get_tm_session
    session_factory = get_session_factory(engine)

    return get_tm_session(session_factory, transaction.manager)


@pytest.fixture()
def request(session, engine):
    """
    Use this fixture when you need a request object where the
    database has been initialized.
    """
    from .models.meta import Base
    Base.metadata.create_all(engine)

    yield testing.DummyRequest(dbsession=session)

    testing.tearDown()
    transaction.abort()
    Base.metadata.drop_all(engine)


def test_passing_home_view(request):
    from .models import MyModel

    model = MyModel(name='one', value=55)
    request.dbsession.add(model)

    from .views.default import home
    info = home(request)
    assert info['one'].name == 'one'
    assert info['project'] == '{{ cookiecutter.project_name }}'


def test_failing_home_view(session):
    """
    This should fail because the database will not have been initialized.
    """
    from .views.default import home
    info = home(dummy_request(session))
    assert info.status_int == 500
