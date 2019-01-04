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
"""Generic response wrapper class.
All responses follow the same data return format,
so generalizing the data return structure. Formalizes
the requirement to consume chunks until the object is fully
formed, and then when finalized exposes dict reprs of the
YangData and Errors data.
TODO: Simplify?
"""
import json
import logging


def build_response(reqid, response_stream):
    """Build a gRPCResponse from response stream.

    Parameters
    ----------
    reqid : uint
        The request ID to indicate to the device.
    response_stream : object, iterable
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
        response_obj.add_data(response.ReqID, response.YangData, response.Errors)
    try:
        response_obj.finalize()
    except json.decoder.JSONDecodeError:
        logging.exception('Error finalizing response JSON! Returning potentially un-finalized elements.')
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
        self.__yang_data_raw = ""
        self.__errors_raw = ""

    def __getitem__(self, key):
        """Enable usage of attribute-like access like original data structure."""
        allowed_keys = {"ReqID", "YangData", "Errors"}
        if key not in allowed_keys:
            raise Exception("Key not allowed for dict-like access!")
        if not self.__finalized:
            raise Exception("Must finalize before dict representation!")
        return self.__dict__[key]

    def __repr__(self):
        """JSON dump raw data in instance."""
        return json.dumps(self.as_dict_raw())

    def __check_req_id(self, req_id):
        """Ensures that ReqIDs are consistent per message/chunk."""
        if req_id != self.req_id:
            raise Exception("ReqIDs in response stream do not match!")

    def add_data(self, req_id, yang_data, errors):
        """Adds both yang_data and errors to raw data."""
        self.add_yang_data(req_id, yang_data)
        self.add_errors(req_id, errors)

    def add_yang_data(self, req_id, data):
        self.__check_req_id(req_id)
        self.__yang_data_raw += data

    def add_errors(self, req_id, errors):
        self.__check_req_id(req_id)
        self.__errors_raw += errors

    def finalize(self):
        """Serialize raw, received data to Python dicts."""
        self.yang_data = (
            json.loads(self.__yang_data_raw, strict=False)
            if self.__yang_data_raw
            else None
        )
        self.YangData = self.yang_data
        self.errors = (
            json.loads(self.__errors_raw, strict=False) if self.__errors_raw else None
        )
        self.Errors = self.errors
        self.__finalized = True

    def as_dict_raw(self):
        """Returns the raw data representations."""
        return {
            "ReqID": self.req_id,
            "YangData": self.__yang_data_raw,
            "Errors": self.__errors_raw,
        }

    def as_dict(self):
        """Returns the dict-ified data representations."""
        if not self.__finalized:
            raise Exception("Must finalize before dict representation!")
        return {"ReqID": self.req_id, "YangData": self.yang_data, "Errors": self.errors}
