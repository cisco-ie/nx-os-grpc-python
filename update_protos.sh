#!/usr/bin/env bash
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. nxos_grpc/proto/nxos_grpc.proto
