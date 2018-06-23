import logging
from urllib import parse
import grpc
from . import proto

class Client(object):

    """Defining property due to gRPC timeout being based on a C long type.
    Should really define this based on architecture.
    32-bit C long max value. "Infinity".
    """
    __C_MAX_LONG=2147483647

    def __init__(self, target, username, password, timeout=__C_MAX_LONG):
        """Initializes the gRPC client stub and defines authentication
        and timeout attributes. Timeout defaults to "infinity".
        """
        self.__client = self.__gen_client(target)
        self.username = username
        self.password = password
        self.timeout = timeout
    
    def __gen_target(self, target):
        """Parses and validates a supplied target URL for gRPC calls.
        Uses urllib to parse the netloc property from the URL.
        netloc property is, effectively, fqdn/hostname:port.
        This provides some level of URL validation and flexibility.
        Returns netloc property of target.
        """
        netloc_prefix = '//'
        if netloc_prefix not in target:
            target = netloc_prefix + target
        parsed_target = parse.urlparse(target)
        if not parsed_target.netloc:
            raise ValueError('Unable to parse netloc from supplied target URL!')
        if parsed_target.scheme:
            logging.debug('Scheme identified in target, ignoring and using netloc.')
        return parsed_target.netloc
    
    def __gen_metadata(self):
        """Generates expected gRPC call metadata."""
        return [
            ('user', self.username),
            ('password', self.password)
        ]
    
    def __gen_client(self, target, secure=False):
        """Instantiates and returns the NX-OS gRPC client stub
        over an insecure or secure channel. Validates target.
        """
        target = self.__gen_target(target)
        client = None
        if not secure:
            insecure_channel = grpc.insecure_channel(target)
            client = proto.gRPCConfigOperStub(insecure_channel)
        else:
            raise NotImplementedError('Secure channel not yet implemented!')
        return client

    
    def get_oper(self, datapath):
        """Adapted from IOS XR gRPC client for testing."""
        message = proto.GetOperArgs(YangPath=datapath)
        responses = self.__client.GetOper(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        output = ''
        error = ''
        for response in responses:
            output += response.yangjson
            error += response.errors
        return error, output
