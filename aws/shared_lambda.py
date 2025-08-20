"""Shared lambda module
Decorators:
    1. endpoint_url
    1. my_decorator
Functions:
    1. dump_api_gateway_event_context
Classes:
    1.
Examples
"""

import json
from shared_messages import OperationResultMessage, ResponseMessage

# Decorators

def endpoint_url(relative_path:str, http_method:str, required_roles:list[str]|None = None):
    """A decorator that does nothing"""
    def endpoint_url_decorator(func, relative_path = relative_path, http_method = http_method, required_roles = required_roles):
        def endpoint_url_decorator_wrapper(*args, **kwargs):
            print(http_method, relative_path, func.__name__, required_roles)
            return func(*args, **kwargs)
        endpoint_url_decorator_wrapper.__is_endpoint_url_decorator__ = True
        endpoint_url_decorator_wrapper.__name__ = func.__name__ # Preserve function name
        endpoint_url_decorator_wrapper.__doc__ = func.__doc__   # Preserve docstring
        return endpoint_url_decorator_wrapper
    return endpoint_url_decorator


def endpoint_url_prototype(relative_path:str, http_method:str, required_roles:list[str]|None = None):
    """A decorator that does nothing"""
    def endpoint_url_decorator(func, relative_path = relative_path, http_method = http_method, required_roles = required_roles):
        def endpoint_url_decorator_wrapper(*args, **kwargs):
            print(http_method, relative_path, func.__name__, required_roles)
            pdb.set_trace()
            return func(*args, **kwargs)
        endpoint_url_decorator_wrapper.__is_endpoint_url_decorator__ = True
        endpoint_url_decorator_wrapper.__name__ = func.__name__ # Preserve function name
        endpoint_url_decorator_wrapper.__doc__ = func.__doc__   # Preserve docstring
        return endpoint_url_decorator_wrapper
    return endpoint_url_decorator


def my_decorator(func):
    """An example decorator that does nothing
    Showcase a decorator that does not take parameters.
    """
    def wrapper(*args, **kwargs):
        print("Something before the function runs.")
        func(*args, **kwargs)
    return wrapper


# Functions

def dump_api_gateway_event_context(event:dict, context):
    """ Prints the event and context that AWS API Gateway receives
    Args:
        event (dict): The ID of the item to retrieve.
        context (str, optional): An optional query parameter.
    Returns:
        response (dict): object with status code and text message
    """
    print("[event]", event)
    print("[context]", context)
    return {
        'statusCode': 200,
        'body': json.dumps('Successful HTTP')
    }

# Classes

class EndpointResponse(object):
    """Encapsulates logic endpoint outgoing responses"""
    def __init__(self):
        self.HTTP_OK_CODE = 200
        self.HTTP_BAD_REQUEST_CODE = 400
        self.HTTP_FORBIDDEN = 401
        self.HTTP_BAD_GATEWAY = 502

    # def response(self, http_code:int, body_text:str) -> dict:
    #     return {
    #         'statusCode': http_code,
    #         'body': json.dumps(body_text)
    #     }

    def bad_gateway(self, upstream_operation_result_message:OperationResultMessage) -> dict:
        return ResponseMessage(
            self.HTTP_BAD_REQUEST_CODE,
            json.dumps(upstream_operation_result_message.__dict__)).to_dict()

    def forbidden(self) -> dict:
        return ResponseMessage(
            self.HTTP_FORBIDDEN,
            body='').to_dict()

    def bad_request(self, text_message:str) -> dict:
        return ResponseMessage(
            self.HTTP_BAD_REQUEST_CODE,
            json.dumps(OperationResultMessage(False, text_message).__dict__)).to_dict()

    def ok(self, is_success:bool, return_message:str) -> dict:
        return ResponseMessage(
            self.HTTP_OK_CODE,
            json.dumps(OperationResultMessage(is_success, return_message).__dict__)).to_dict()

    def data(self, operation_result_message:OperationResultMessage) -> dict:
        return ResponseMessage(
            self.HTTP_OK_CODE,
            json.dumps(operation_result_message.__dict__)
        ).to_dict()


class EventBodyJson(object):
    """Parsed result of an API Gateway event body"""
    def __init__(self, data_object:dict|None = None, error_message:str|None = None):
        """
        Args:
            data_object (dict|none): Data object result of parsing event object
            error_message (str|none): An error message to indicate where parsing failed
        """
        self.data_object = data_object
        self.error_message = error_message
        self.is_invalid = self.data_object is None

    def __str__(self):
        return f"is_invalid:{self.is_invalid}, ErrorMessage:{self.error_message}, DataObject:{self.data_object}"

    @staticmethod
    def get_event_body_json(event: dict):
        """Parses an API Gateway event object to return EventJsonBody
        Args:
            event (dict): Event object received from API Gateway
        Returns:
            EventBodyJson: Result from parsing event arg
        """
        if 'body' not in event:
            return EventBodyJson(error_message='`body` not found in context')
        try:
            return EventBodyJson(data_object=json.loads(event['body']))
        except json.decoder.JSONDecodeError:
            return EventBodyJson(error_message='`body` is invalid json')


class EventHeadersJson(object):
    def __init__(self, data_object: dict | None = None):
        self.data_object = data_object

    @staticmethod
    def get_event_headers_json(event: dict):
        """Parses an API Gateway event object to return EventJsonBody
        Args:
            event (dict): Event object received from API Gateway
        Returns:
            EventHeadersJson: Result from parsing event arg
        """
        if 'headers' not in event:
            return EventHeadersJson(error_message='`headers` not found in context')
        try:
            return EventHeadersJson(data_object=json.loads(event['headers']))
        except json.decoder.JSONDecodeError:
            return EventHeadersJson(error_message='`headers` is invalid json')

    def get_authorization_header(event):
        if 'headers' not in event:
            return None
        try:
            json_obj = event['headers']
            return json_obj['authorization'] if 'authorization' in json_obj else None
        except json.decoder.JSONDecodeError:
            return None


class EventQueryStringParametersJson(object):
    """Parsed result of an API Gateway event queryStringParameters"""
    def __init__(self, data_object:dict|None = None, error_message:str|None = None):
        """
        Args:
            data_object (dict|none): Data object result of parsing event object
            error_message (str|none): An error message to indicate where parsing failed
        """
        self.data_object = data_object
        self.error_message = error_message
        self.is_valid = self.data_object is not None

    def __str__(self):
        return f"is_invalid:{self.is_invalid}, ErrorMessage:{self.error_message}, DataObject:{self.data_object}"

    @staticmethod
    def get_event_query_string_parameters_json(event: dict):
        """Parses an API Gateway event object to return EventQueryStringParametersJson
        Args:
            event (dict): Event object received from API Gateway
        Returns:
            EventQueryStringParametersJson: Result from parsing event arg
        """
        if 'queryStringParameters' not in event:
            return EventQueryStringParametersJson(error_message='`queryStringParameters` not found in context')
        try:
            return EventQueryStringParametersJson(data_object=event['queryStringParameters'])
        except json.decoder.JSONDecodeError:
            return EventQueryStringParametersJson(error_message='`queryStringParameters` is invalid json')

class EventPathParametersJson(object):
    """Parsed result of an API Gateway event pathParameters"""
    def __init__(self, data_object:dict|None = None, error_message:str|None = None):
        """
        Args:
            data_object (dict|none): Data object result of parsing event object
            error_message (str|none): An error message to indicate where parsing failed
        """
        self.data_object = data_object
        self.error_message = error_message
        self.is_valid = self.data_object is not None

    def __str__(self):
        return f"is_invalid:{self.is_invalid}, ErrorMessage:{self.error_message}, DataObject:{self.data_object}"

    @staticmethod
    def get_event_path_parameters_json(event: dict):
        """Parses an API Gateway event object to return EventPathParametersJson
        Args:
            event (dict): Event object received from API Gateway
        Returns:
            EventPathParametersJson: Result from parsing event arg
        """
        if 'pathParameters' not in event:
            return EventPathParametersJson(error_message='`pathParameters` not found in context')
        try:
            return EventPathParametersJson(data_object=event['pathParameters'])
        except json.decoder.JSONDecodeError:
            return EventPathParametersJson(error_message='`pathParameters` is invalid json')

# Example

@my_decorator
@endpoint_url_prototype('/hci-blazer', 'GET', ['requireRole1', 'requireRole2'])
def test_endpoint_url_decorator(event:dict, context):
    print('TEST test_endpoint decorator')
    dump_api_gateway_event_context(event, context)

if __name__ == '__main__':
    test_endpoint_url_decorator({}, None)