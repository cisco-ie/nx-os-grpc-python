"""NX-OS gRPC Python wrapper library.
Function usage derived from example NX-OS client from BU (thanks! :)).
TODO: Write session state management wrapper.
TODO: Exception classes.
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

    def __init__(self, target, username, password, timeout=__C_MAX_LONG,
            credentials=None, credentials_from_file=True, tls_server_override=None
        ):
        """Initializes the gRPC client stub and defines authentication and timeout attributes.

        Parameters
        ----------
        target : str
            The host[:port] to issue gRPC requests against.
        username : str
        password : str
        timeout : { 0, Maximum C Integer Value }, optional
            Timeout for request which sets a deadline for return.
        credentials : str, optional
            PEM file path or PEM file contents.
        tls_server_override : str, optional
            TLS server name if desired.
        credentials_from_file : { True, False }, optional
            Indicates that credentials is a file path.
        
        Notes
        -----
        Client building might be revisited.
        """
        self.__client = self.__gen_client(
            target,
            credentials=self.__gen_creds(
                credentials, credentials_from_file
            ),
            options=(('grpc.ssl_target_name_override', tls_server_override,),)
                if tls_server_override else None
        )
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
    
    def __gen_client(self, target, credentials=None, options=None):
        """Instantiates and returns the NX-OS gRPC client stub
        over an insecure or secure channel. Validates target.
        """
        target = self.__gen_target(target)
        client = None
        if not credentials:
            insecure_channel = grpc.insecure_channel(target)
            client = proto.gRPCConfigOperStub(insecure_channel)
        else:
            channel_creds = grpc.ssl_channel_credentials(credentials)
            secure_channel = grpc.secure_channel(target, channel_creds, options)
            client = proto.gRPCConfigOperStub(secure_channel)
        return client
    
    def __gen_creds(self, creds, creds_from_file=False):
        """Generate credentials either by reading credentials from
        the specified file or return the original creds specified.
        """
        ret_creds = None
        if creds_from_file:
            with open(creds, 'rb') as cred_fd:
                ret_creds = cred_fd.read()
        else:
            ret_creds = creds
        return ret_creds

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

    def get_oper(self, yang_path, namespace=None, request_id=0, path_is_payload=False):
        r"""Get operational data from device.

        Parameters
        ----------
        yang_path : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.
        path_is_payload : { True, False }, optional
            Indicates that the yang_path parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        if not path_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yang_path is not payload.')
            yang_path = self.__parse_xpath_to_json(yang_path, namespace)
        message = proto.GetOperArgs(ReqID=request_id, YangPath=yang_path)
        responses = self.__client.GetOper(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def get(self, yang_path, namespace=None, request_id=0, path_is_payload=False):
        r"""Get configuration and operational data from device.

        Parameters
        ----------
        yang_path : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.
        path_is_payload : { True, False }, optional
            Indicates that the yang_path parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        if not path_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yangpath is not payload.')
            yang_path = self.__parse_xpath_to_json(yang_path, namespace)
        message = proto.GetArgs(ReqID=request_id, YangPath=yang_path)
        responses = self.__client.Get(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def get_config(self, yang_path, namespace=None, request_id=0,
            source='running', path_is_payload=False
        ):
        r"""Get configuration data from device.

        Parameters
        ----------
        yang_path : str
            YANG XPath which locates the datapoints.
        namespace : str, optional
            YANG namespace applicable to the specified XPath.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.
        source : { 'running', ? }, optional
            Source to retrieve configuration from.
        path_is_payload : { True, False }, optional
            Indicates that the yang_path parameter contains a preformed JSON
            payload and should not be parsed into JSON as an XPath.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        
        Notes
        -----
        Need to verify whether source param may be something other than running.
        """
        if not path_is_payload:
            if not namespace:
                raise Exception('Must include namespace if yang_path is not payload.')
            yang_path = self.__parse_xpath_to_json(yang_path, namespace)
        message = proto.GetConfigArgs(ReqID=request_id, Source=source, YangPath=yang_path)
        responses = self.__client.GetConfig(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def edit_config(self, yang_path,
            operation='merge', default_operation='merge', session_id=0,
            request_id=0, target='running', error_operation='roll-back'
        ):
        r"""Writes the specified YANG data subset to the target datastore.

        Parameters
        ----------
        yang_path : str
            JSON-encoded YANG data to be edited.
        operation : { 'merge', 'create', 'replace', 'delete', 'remove' }, optional
            Operation to perform on the configuration datastore.
        default_operation : { 'merge', 'replace', 'none' }, optional
            Default operation while traversing the configuration tree.
        session_id : { 0, +inf }, optional
            Unique session ID acquired from start_session.
            0 indicates stateless operation.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.
        target : { 'running' }, optional
            Target datastore. Only 'running' is supported.
        error_operation : { 'roll-back', 'stop', 'continue' }, optional
            Action to be preformed in the event of an error.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        message = proto.EditConfigArgs(
            YangPath=yang_path, Operation=operation, SessionID=session_id, ReqID=request_id,
            Target=target, DefOp=default_operation, ErrorOp=error_operation)
        responses = self.__client.EditConfig(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def start_session(self, request_id=0):
        r"""Starts a new session acquiring a session ID.

        Parameters
        ----------
        request_id : int, optional
            The request ID to indicate to the device.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        message = proto.SessionArgs(ReqID=request_id)
        responses = self.__client.StartSession(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def close_session(self, session_id, request_id=0):
        r"""Requests graceful termination of a session.

        Parameters
        ----------
        session_id : { 0, +inf }
            Unique session ID acquired from starting a session.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.

        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        """
        message = proto.CloseSessionArgs(ReqID=request_id, SessionID=session_id)
        responses = self.__client.CloseSession(message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)

    def kill_session(self, session_id, session_id_to_kill, request_id=0):
        r"""Forces the closing of a session.

        Parameters
        ----------
        session_id : { 0, +inf }
            Unique session ID acquired from starting a session.
        session_id_to_kill : { 0, +inf }
            Unique session ID to kill.
        request_id : { 0, +inf }, optional
            The request ID to indicate to the device.
        
        Returns
        -------
        response : gRPCResponse
            Response wrapper object with ReqID, YangData, and Errors fields.
        
        Notes
        -----
        Not verified on whether we need to open a new session to kill a session.
        """
        message = proto.KillArgs(
            ReqID=request_id,
            SessionID=session_id,
            SessionIDToKill=session_id_to_kill
        )
        responses = self.__client.KillSession(
            message,
            timeout=self.timeout,
            metadata=self.__gen_metadata()
        )
        return build_response(request_id, responses)
