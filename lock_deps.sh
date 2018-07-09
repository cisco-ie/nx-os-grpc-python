#!/usr/bin/env bash
pipenv lock --dev --clear
pipenv run pip freeze > requirements.txt
