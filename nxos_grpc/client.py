"""NX-OS gRPC Python wrapper library.
Function usage derived from example NX-OS client from BU (thanks! :)).
"""
import logging
import json
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

    def get_oper(self, datapath, namespace=None, reqid=0, datapath_is_payload=False):
        r"""Get operational data from device.

        Parameters
        ----------
        datapath : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        reqid : { 0, +inf }, optional
            The request ID to indicate to the device.
        datapath_is_payload : { True, False }, optional
            Indicates that the datapath variable contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        res_reqid : int
            The request ID returned in the response.
        res_yangdata : { dict, None }
            The JSON-formed response data parsed into dict.
        res_errors : { dict, None }
            The JSON-formed response errors parsed into dict.
        
        Raises
        ------
        Exception
            When request IDs do not match in request return chunks.
        
        Notes
        -----
        Decodes JSON data without strict parsing rules. May present some difficulties.
        """
        if not datapath_is_payload:
            if not namespace:
                raise Exception('Must include namespace if datapath is not payload.')
            datapath = self.__parse_xpath_to_json(datapath, namespace)
        message = proto.GetOperArgs(ReqID=reqid, YangPath=datapath)
        responses = self.__client.GetOper(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        res_reqid = None
        res_yangdata = ''
        res_errors = ''
        for response in responses:
            if res_reqid is None:
                res_reqid = response.ReqID
            elif res_reqid != response.ReqID:
                raise Exception('ReqIDs in response stream do not match!')
            res_yangdata += response.YangData
            res_errors += response.Errors
        res_yangdata = json.loads(res_yangdata, strict=False) if res_yangdata else None
        res_errors = json.loads(res_errors, strict=False) if res_errors else None
        return res_reqid, res_yangdata, res_errors
