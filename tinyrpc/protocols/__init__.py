#!/usr/bin/env python

from ..exc import *

class RPCRequest(object):
    unique_id = None
    """A unique ID to remember the request by. Protocol specific, may or
    may not be set. This value should only be set by
    :py:func:`~tinyrpc.RPCProtocol.create_request`.

    The ID allows client to receive responses out-of-order and still allocate
    them to the correct request.

    Only supported if the parent protocol has
    :py:attr:`~tinyrpc.RPCProtocol.supports_out_of_order` set to ``True``."""


    method = None
    """The name of the method to be called."""
    args = None
    """The positional arguments of the method call."""
    kwargs = None
    """The keyword arguments of the method call."""

    def error_respond(self, error):
        """Creates an error response.

        Create a response indicating that an error has occured.

        :param: An exception or a string describing the error.

        :return: A response or ``None`` to indicate that no error should be sent
        out.
        """
        raise RuntimeError('Not implemented')

    def respond(self, result):
        """Create a response.

        This creates and returns an instance of a protocol-specific subclass of
        :py:class:`~tinyrpc.RPCResponse`.

        :param result: Passed on to new response instance.

        :return: A response or ``None`` to indicate this request does not expect a
        response.
        """
        raise RuntimeError('Not implemented')

    def serialize(self):
        """Returns a serialization of the request.

        :return: A string to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCBatchRequest(list, RPCRequest):
    """Multiple requests batched together.

    A batch request is a subclass of :py:class:`list`. Protocols that support
    multiple requests in a single message use this to group them together.

    Handling a batch requests is done in any order, responses must be gathered
    in a batch response and be in the same order as their respective requests.

    Any item of a batch request is either a request or a subclass of
    :py:class:`~tinyrpc.RPCError`, which indicates that there has been an error
    in parsing the request.
    """
    pass


class RPCResponse(object):
    """RPC call response base class."""

    is_error = False
    """If true, the rpc call failed."""

    def serialize(self):
        """Returns a serialization of the response.

        :return: A reply to be passed on to a transport.
        """
        raise RuntimeError('Not implemented')


class RPCBatchResponse(list, RPCResponse):
    """Multiple response from a batch request. See
    :py:class:`~tinyrpc.RPCBatchRequest` on how to handle.

    Items in a batch response need to be either
    :py:class:`~tinyrpc.RCPResponse` instances or a subclass of
    :py:class:`Exception`. In the case of the latter, they should be
    automatically turned into response-instances through
    :py:func:`~tinyrpc.RPCProtocol.create_error_response`.
    """

    def create_batch_response(self):
        """Creates a response suitable for responding to this request.

        :return: An :py:class:`~tinyrpc.RPCBatchResponse` or ``None``, if no
        response is expected."""
        raise RuntimeError('Not implemented')

    def serialize(self):
        """Returns a serialization of the batch response."""
        raise RuntimeError('Not implemented')


class RPCErrorResponse(RPCResponse):
    is_error = True

    error = None
    """The error that has occured, an exception or a string."""


class RPCSuccessResponse(RPCResponse):
    is_error = False

    result = None
    """The rpc call's return value."""


class RPCProtocol(object):
    """Base class for all protocol implementations."""

    supports_out_of_order = False
    """If true, this protocol can receive responses out of order correctly.

    Note that this usually depends on the generation of unique_ids, the
    generation of these may or may not be thread safe, depending on the
    protocol. Ideally, only once instance of RPCProtocol should be used per
    client."""

    def create_request(self, method, args=None, kwargs=None, one_way=False):
        """Creates a new RPCRequest object.

        It is up to the implementing protocol whether or not ``args``,
        ``kwargs``, one of these, both at once or none of them are supported.

        :param method: The method name to invoke.
        :param args: The positional arguments to call the method with.
        :param kwargs: The keyword arguments to call the method with.
        :param one_way: The request is an update, i.e. it does not expect a
                        reply.
        :return: A new :py:class:`~tinyrpc.RPCRequest` instance.
        """
        raise RuntimeError('Not implemented')

    def create_error_response(self, error):
        """Creates an error response independent of a request.

        Usually, if an error occurs,
        :py:func:`~tinyrpc.RPCResponse.error_respond` should be called.
        If errors occur before an instance of :py:class:`~tinyrpc.RPCResponse`
        can be instantiated, use this function to generate a reply
        :param error: Exception or string.
        :return: A `~tinyrpc.RPCErrorResponse` instance.
        """
        raise RuntimeError('Not implemented')

    def parse_request(self, data):
        """Parses a request given as a string and returns an
        :py:class:`RPCRequest` instance.

        :return: An instanced request.
        """
        raise RuntimeError('Not implemented')

    def parse_reply(self, data):
        """Parses a reply and returns an :py:class:`RPCResponse` instance.

        :return: An instanced response.
        """
        raise RuntimeError('Not implemented')


class RPCBatchProtocol(RPCProtocol):
    def create_batch_request(self, requests=None):
        raise RuntimeError('Not implemented')
