#!/usr/bin/env bash
pipenv lock --pre --clear
pipenv --three install --dev --ignore-pipfile
pipenv run pip freeze > requirements.txt
