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

def endpoint_url(relative_path:str, http_method:str):
    """A decorator that does nothing"""
    def endpoint_url_decorator(func, relative_path = relative_path, http_method = http_method):
        def endpoint_url_decorator_wrapper(*args, **kwargs):
            print(http_method, relative_path, func.__name__)
            return func(*args, **kwargs)
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

    # def response(self, http_code:int, body_text:str) -> dict:
    #     return {
    #         'statusCode': http_code,
    #         'body': json.dumps(body_text)
    #     }

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
        self.DataObject = data_object
        self.ErrorMessage = error_message
        self.is_invalid = self.DataObject is None

    def __str__(self):
        return f"is_invalid:{not self.is_invalid}, ErrorMessage:{self.ErrorMessage}, DataObject:{self.DataObject}"

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


# Example

@my_decorator
@endpoint_url('/hci-blazer', 'GET')
def test_endpoint_url_decorator(event:dict, context):
    print('TEST test_endpoint decorator')
    dump_api_gateway_event_context(event, context)

if __name__ == '__main__':
    test_endpoint_url_decorator({}, None)