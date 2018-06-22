#!/usr/bin/env bash
python -m grpc_tools.protoc --proto_path=. --python_out=nx-os-grpc-python/proto --grpc_python_out=nx-os-grpc-python/proto nxos_grpc.proto
