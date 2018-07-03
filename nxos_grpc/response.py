"""Generic response wrapper class.
All responses follow the same data return format,
so generalizing the data return structure. Formalizes
the requirement to consume chunks until the object is fully
formed, and then when finalized exposes dict reprs of the
YangData and Errors data.
TODO: Simplify?
"""
import json


def build_response(reqid, response_stream):
    r"""Build a gRPCResponse from response stream.

    Parameters
    ----------
    reqid : { 0, +inf }
        The request ID to indicate to the device.
    response_stream : object
        gRPC response stream to consume and assemble.
    
    Returns
    -------
    response_obj : object
        Response object with ReqID, YangData, and Errors fields.

    Raises
    ------
    Exception
        Response stream ReqIDs do not match.
    
    Notes
    -----
    gRPCResponse does not serialize YangData or Errors with strict
    JSON parsing (carriage returns etc.). This could present some issues.
    """
    response_obj = gRPCResponse(reqid)
    for response in response_stream:
        response_obj.add_data(
            response.ReqID,
            response.YangData,
            response.Errors
        )
    response_obj.finalize()
    return response_obj

class gRPCResponse(object):
    """Response wrapper. Fields accessible via dict or attribute access.

    Attributes
    ----------
    req_id || ReqID
    yang_data || YangData
    errors || Errors

    Methods
    -------
    add_data(...)
        Add both YangData and Errors raw data.
    add_yang_data(...)
        Add raw YangData to existing parsed chunks.
    add_errors(...)
        Add raw Errors to existing parsed chunks.
    finalize()
        Parse raw data into dicts for easier Pythonic usage.
    as_dict_raw()
        Raw data in dict form.
    as_dict()
        dict-ified data in dict form.
    """

    def __init__(self, ReqID):
        self.req_id = ReqID
        self.ReqID = self.req_id
        self.yang_data = None
        self.YangData = self.yang_data
        self.errors = None
        self.Errors = self.errors
        self.__finalized = False
        self.__yang_data_raw = ''
        self.__errors_raw = ''
    
    def __getitem__(self, key):
        allowed_keys = {'ReqID', 'YangData', 'Errors'}
        if key not in allowed_keys:
            raise Exception('Key not allowed for dict-like access!')
        if not self.__finalized:
            raise Exception('Must finalize before dict representation!')
        return self.__dict__[key]
    
    def __repr__(self):
        return json.dumps(
            self.as_dict_raw()
        )
    
    def __check_req_id(self, req_id):
        if req_id != self.req_id:
            raise Exception('ReqIDs in response stream do not match!')
    
    def add_data(self, req_id, yang_data, errors):
        self.add_yang_data(req_id, yang_data)
        self.add_errors(req_id, errors)
    
    def add_yang_data(self, req_id, data):
        self.__check_req_id(req_id)
        self.__yang_data_raw += data
    
    def add_errors(self, req_id, errors):
        self.__check_req_id(req_id)
        self.__errors_raw += errors
    
    def finalize(self):
        self.yang_data = json.loads(self.__yang_data_raw, strict=False) if self.__yang_data_raw else None
        self.YangData = self.yang_data
        self.errors = json.loads(self.__errors_raw, strict=False) if self.__errors_raw else None
        self.Errors = self.errors
        self.__finalized = True
    
    def as_dict_raw(self):
        return {
            'ReqID': self.req_id,
            'YangData': self.__yang_data_raw,
            'Errors': self.__errors_raw
        }
    
    def as_dict(self):
        if not self.__finalized:
            raise Exception('Must finalize before dict representation!')
        return {
            'ReqID': self.req_id,
            'YangData': self.yang_data,
            'Errors': self.errors
        }
