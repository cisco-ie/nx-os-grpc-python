#!/usr/bin/env bash
PROTO_BASE_PATH=nxos_grpc/proto
for PROTO in "$PROTO_BASE_PATH"/*.proto
do
    echo "Generating $PROTO"
    pipenv run python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. $PROTO
done