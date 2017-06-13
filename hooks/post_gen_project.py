from pprint import pprint
from uuid import uuid4
import os
import subprocess
import sys
import re

from textwrap import dedent

WIN = sys.platform.startswith('win')

venv = 'env'
if WIN:
    venv_cmd = 'py -3 -m venv'
    venv_bin = os.path.join(venv, 'Scripts')
else:
    venv_cmd = 'python3 -m venv'
    venv_bin = os.path.join(venv, 'bin')

vars = dict(
    separator='=' * 79,
    venv=venv,
    venv_cmd=venv_cmd,
    pip_cmd=os.path.join(venv_bin, 'pip'),
    pytest_cmd=os.path.join(venv_bin, 'pytest'),
    pserve_cmd=os.path.join(venv_bin, 'pserve'),
    init_cmd=os.path.join(venv_bin, 'initialize_{{ cookiecutter.repo_name }}_db'),
)
msg = dedent(
    """
    %(separator)s
    Documentation: http://docs.pylonsproject.org/projects/pyramid/en/latest/
    Tutorials:     http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/
    Twitter:       https://twitter.com/PylonsProject
    Mailing List:  https://groups.google.com/forum/#!forum/pylons-discuss
    Welcome to Pyramid.  Sorry for the convenience.
    %(separator)s

    Change directory into your newly created project.
        cd {{ cookiecutter.repo_name }}

    Create a Python virtual environment.
        %(venv_cmd)s %(venv)s

    Upgrade packaging tools.
        %(pip_cmd)s install --upgrade pip setuptools

    Install the project in editable mode with its testing requirements.
        %(pip_cmd)s install -e ".[testing]"

    Configure the database:
        %(init_cmd)s development.ini

    Run your project's tests.
        %(pytest_cmd)s

    Run your project.
        %(pserve_cmd)s development.ini
    """ % vars)
print(msg)

def updated_zappa_settings(string):
    """
    Update the zappa settings file to create a unique
    uuid's where necessary.
    """
    # create a uuid to append to the project name
    uuid = re.match(r'(\w+)-', str(uuid4())).group(1)

    # the pattern we use to find the s3_bucket line
    pattern = re.compile(r'\"s3_bucket\"\:\s\"(\w+)(?!-)(?:\")')

    replace = lambda m: m.group(0)[:-1] + '-' + uuid + '"'
    return re.sub(pattern, replace, string)

with open('zappa_settings.json', 'r+') as settings:
    original_settings = settings.read()
    new_settings = updated_zappa_settings(original_settings)
    if new_settings:
        settings.seek(0)
        settings.write(new_settings)

