#!/bin/bash

rm -rf cover
isort -rc --skip .venv --skip migrations .
pylint --load-plugins=pylint_django **/*.py
coverage erase
coverage run manage.py test --failfast
coverage report
coverage html
