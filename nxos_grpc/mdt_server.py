"""Copyright 2019 Cisco Systems

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
"""NX-OS gRPC Python MDT dialout server."""

from concurrent import futures
from threading import Lock
import grpc
from . import proto

def create_server(insecure_addresses=['[::]:50051'], secure_addresses=[], max_workers=10, block=True):
    """Derived from gRPC Python basic tutorial
    secure_addresses wants a list of tuples of address and credentials
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    proto.add_gRPCMdtDialoutServicer_to_server(MDTServer(), server)
    for address in insecure_addresses:
        server.add_insecure_port(address)
    for address, credential in secure_addresses:
        server.add_secure_port(address, credential)
    server.start()
    return server


class MDTServer(proto.gRPCMdtDialoutServicer):
    """NX-OS gRPC MDT dialout server implementation."""

    def __init__(self):
        # Uncertain if we need a lock, but concurrency
        self.__chunk_map_lock = Lock()
        # Map to store all our chunks
        self.__chunk_map = {}
        self.__callbacks = []
    
    def __assemble_telemetry_pb(self, message_chunk):
        message = None
        if len(message_chunk.data) < message_chunk.totalSize:
            with self.__chunk_map_lock:
                if message_chunk.ReqId in self.__chunk_map:
                    self.__chunk_map[message.ReqId] += message_chunk.data
                else:
                    self.__chunk_map[message.ReqId] = message_chunk.data
                if len(self.__chunk_map[message_chunk.ReqId]) == message_chunk.totalSize:
                    message = proto.Telemetry()
                    message.ParseFromString(self.__chunk_map.pop(message_chunk.ReqId))
                elif len(self.__chunk_map[message_chunk.ReqId]) > message_chunk.totalSize:
                    raise Exception('Assembly for %s in progress is larger than stated totalSize!' % str(message_chunk.ReqId))
        elif len(message_chunk.data) > message_chunk.totalSize:
            raise Exception('Message chunk is larger than total message size!')
        else:
            message = proto.Telemetry()
            message.ParseFromString(message_chunk.data)
        return message
    
    def add_callback(self, function):
        self.__callbacks.append(function)

    def MdtDialout(self, request_iterator, context):
        for message_chunk in request_iterator:
            telemetry_pb = self.__assemble_telemetry_pb(message_chunk)
            if telemetry_pb is not None:
                for callback in self.__callbacks:
                    callback(telemetry_pb)
            yield proto.MdtDialoutArgs(ReqId=message_chunk.ReqId)
