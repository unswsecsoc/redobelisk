# Red Obelisk CTF Scoreboard

A ctf scoreboard with writeups for training people to git gud.

## Dependencies
- python2.7
- pip

*optional*
- whatever virtualenv manager you want, e.g. pipenv, virtualenv etc.

## Installation

*Virtualenv*
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

*Pipenv*
```
pipenv shell
pipenv install
python manage.py runserver
```

## Deploying
- Get UWSGI, nginx, uwsgi-plugin-python
- fix uwsgi.ini to not suck
- symlink uwsgi.ini to /etc/uwsgi/sites-enabled

## Development

Fork and Pull request. Do it.
