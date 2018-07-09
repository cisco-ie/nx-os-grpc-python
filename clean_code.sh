#!/usr/bin/env bash
pipenv run black --safe --verbose --exclude pb2 nxos_grpc
pipenv run pylint nxos_grpc/*.py
