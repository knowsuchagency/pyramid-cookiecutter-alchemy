"""
Any functionality that's new or different from the base sqlalchemy cookie cutter template
will be tested in this module.
"""
from pathlib import Path
from . import (
    DEVELOPMENT_CONFIG_URI,
    dbsession,
    development_session
)
import pkg_resources
import pytest


def test_development_config_uri_exists():
    assert Path(DEVELOPMENT_CONFIG_URI).exists()


def test_distribution_package_has_development_config_uri():
    distribution = pkg_resources.get_distribution('{{ cookiecutter.repo_name }}')
    assert distribution.has_resource('development.ini')


def test_dbsession_raises_typeerror():
    with pytest.raises(TypeError):
        with dbsession([]) as session:
            assert True


def test_development_session():
    with development_session() as session:
        assert session
