"""NX-OS gRPC Python wrapper library.
Function usage derived from example NX-OS client from BU (thanks! :)).
"""
import logging
import json
from urllib import parse
import grpc
from .response import build_response
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
        self.timeout = int(timeout)
    
    def __gen_target(self, target, netloc_prefix='//', default_port=50051):
        """Parses and validates a supplied target URL for gRPC calls.
        Uses urllib to parse the netloc property from the URL.
        netloc property is, effectively, fqdn/hostname:port.
        This provides some level of URL validation and flexibility.
        Returns netloc property of target.
        """
        if netloc_prefix not in target:
            target = netloc_prefix + target
        parsed_target = parse.urlparse(target)
        if not parsed_target.netloc:
            raise ValueError('Unable to parse netloc from target URL %s!', target)
        if parsed_target.scheme:
            logging.debug('Scheme identified in target, ignoring and using netloc.')
        target_netloc = parsed_target.netloc
        if parsed_target.port is None:
            ported_target = '%s:%i' % (parsed_target.hostname, default_port)
            logging.debug('No target port detected, reassembled to %s.', ported_target)
            target_netloc = self.__gen_target(ported_target)
        return target_netloc
    
    def __gen_metadata(self):
        """Generates expected gRPC call metadata."""
        return [
            ('username', self.username),
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

    def __parse_xpath_to_json(self, xpath, namespace):
        """Parses an XPath to JSON representation, and appends
        namespace into the JSON request.
        """
        xpath_dict = {}
        xpath_split = xpath.split('/')
        first = True
        for element in reversed(xpath_split):
            if first:
                xpath_dict[element] = {}
                first = False
            else:
                xpath_dict = {element: xpath_dict}
        xpath_dict['namespace'] = namespace
        return json.dumps(xpath_dict)

    def get_oper(self, yangpath, namespace=None, reqid=0, yangpath_is_payload=False):
        r"""Get operational data from device.

        Parameters
        ----------
        yangpath : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        reqid : { 0, +inf }, optional
            The request ID to indicate to the device.
        yangpath_is_payload : { True, False }, optional
            Indicates that the yangpath parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        if not yangpath_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yangpath is not payload.')
            yangpath = self.__parse_xpath_to_json(yangpath, namespace)
        message = proto.GetOperArgs(ReqID=reqid, YangPath=yangpath)
        responses = self.__client.GetOper(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(reqid, responses)

    def get(self, yangpath, namespace=None, reqid=0, yangpath_is_payload=False):
        r"""Get configuration and operational data from device.

        Parameters
        ----------
        yangpath : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        reqid : { 0, +inf }, optional
            The request ID to indicate to the device.
        yangpath_is_payload : { True, False }, optional
            Indicates that the yangpath parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        if not yangpath_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yangpath is not payload.')
            yangpath = self.__parse_xpath_to_json(yangpath, namespace)
        message = proto.GetArgs(ReqID=reqid, YangPath=yangpath)
        responses = self.__client.Get(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(reqid, responses)

    def get_config(self, yangpath, namespace=None, reqid=0, source='running', yangpath_is_payload=False):
        r"""Get configuration data from device.

        Parameters
        ----------
        yangpath : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        reqid : { 0, +inf }, optional
            The request ID to indicate to the device.
        source : { 'running', ? }, optional
            Source to retrieve configuration from.
        yangpath_is_payload : { True, False }, optional
            Indicates that the yangpath parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        if not yangpath_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yangpath is not payload.')
            yangpath = self.__parse_xpath_to_json(yangpath, namespace)
        message = proto.GetConfigArgs(ReqID=reqid, Source=source, YangPath=yangpath)
        responses = self.__client.GetConfig(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(reqid, responses)
