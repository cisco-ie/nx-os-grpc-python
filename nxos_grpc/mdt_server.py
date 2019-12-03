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


def create_mdt_server(
    insecure_addresses=["[::]:50051"], secure_addresses=[], max_workers=10
):
    """Utility method to start up a gRPC server receiving NX-OS MDT.
    Derived from gRPC Basics - Python documentation.
    https://grpc.io/docs/tutorials/basic/python/

    Parameters
    ----------
    insecure_addresses : list, optional
        A list of strings which are IP:port(s) to serve without security.
        This or secure_addresses must be specified.
    secure_addresses : list, optional
        A list of tuples which are (address, server_credential) to serve with security.
        This or insecure_addresses must be specified.
    max_workers : int, optional
        The number of concurrent workers to handle RPCs.

    Returns
    -------
    grpc_server : gRPC Server
        The gRPC server instance spun up for usage.
        Used to start/stop server.
    mdt_server : MDTServer
        The MDTServer instance.
        Used to add callbacks to handle messages.
    """
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    mdt_server = MDTServer()
    proto.add_gRPCMdtDialoutServicer_to_server(mdt_server, grpc_server)
    for address in insecure_addresses:
        grpc_server.add_insecure_port(address)
    for address, credential in secure_addresses:
        grpc_server.add_secure_port(address, credential)
    grpc_server.start()
    return grpc_server, mdt_server


class MDTServer(proto.gRPCMdtDialoutServicer):
    """NX-OS gRPC MDT dialout server implementation.

    Data is propagated to interested parties via callbacks.

    Methods
    -------
    add_callback(...)
        Add a function signature to be called per message for handling.

    Examples
    --------
    >>> from nxos_grpc import create_mdt_server
    >>> grpc_server, mdt_server = create_mdt_server()
    >>> def nothing_much(message):
    ...   print(message)
    >>> mdt_server.add_callback(nothing_much)
    ...
    """

    def __init__(self):
        """Initializes the MDTServer object and internal state items.
        """
        # Uncertain if we need a lock, but concurrency
        self.__chunk_map_lock = Lock()
        # Map to store all our chunks
        self.__chunk_map = {}
        # Callbacks we've been provided
        self.__callbacks = []

    def add_callback(self, func):
        """Add a callback to handle each MDT message.

        Parameters
        ----------
        func : function
            The function signature to be called for callback.
        """
        self.__callbacks.append(func)

    def MdtDialout(self, request_iterator, context):
        """Services the MDT messages from NX-OS."""
        for message_chunk in request_iterator:
            telemetry_pb = self.__assemble_telemetry_pb(message_chunk)
            if telemetry_pb is not None:
                for callback in self.__callbacks:
                    callback(telemetry_pb)
            yield proto.MdtDialoutArgs(ReqId=message_chunk.ReqId)

    def __assemble_telemetry_pb(self, message_chunk):
        """Handles NX-OS telemetry chunking.
        Stores chunked messages in self.__chunk_map and returns
        fully assembled messages once they match the specified totalSize.
        """
        message = None
        if len(message_chunk.data) < message_chunk.totalSize:
            # Need to begin storing to reassemble
            with self.__chunk_map_lock:
                if message_chunk.ReqId in self.__chunk_map:
                    self.__chunk_map[message.ReqId] += message_chunk.data
                else:
                    self.__chunk_map[message.ReqId] = message_chunk.data
                if (
                    len(self.__chunk_map[message_chunk.ReqId])
                    == message_chunk.totalSize
                ):
                    message = proto.Telemetry()
                    message.ParseFromString(self.__chunk_map.pop(message_chunk.ReqId))
                elif (
                    len(self.__chunk_map[message_chunk.ReqId]) > message_chunk.totalSize
                ):
                    raise Exception(
                        "Message %s assembly (%i) is larger than totalSize (%i)!"
                        % (
                            str(message_chunk.ReqId),
                            len(self.__chunk_map[message_chunk.ReqId]),
                            message_chunk.totalSize,
                        )
                    )
        elif (
            message_chunk.totalSize
            and len(message_chunk.data) > message_chunk.totalSize
        ):
            raise Exception(
                "Message %s chunk (%i) is larger than totalSize (%i)!"
                % (
                    str(message_chunk.ReqId),
                    len(message_chunk.data),
                    message_chunk.totalSize,
                )
            )
        else:
            # message_chunk is a complete telemetry message
            message = proto.Telemetry()
            message.ParseFromString(message_chunk.data)
        return message
