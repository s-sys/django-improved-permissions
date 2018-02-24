#!/bin/bash

isort -rc --skip .venv --skip migrations .
pylint --load-plugins=pylint_django improved_permissions/*.py
