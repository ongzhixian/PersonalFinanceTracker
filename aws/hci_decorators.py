"""Common HCI decorators
"""

import json
import pdb

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

def dump_api_gateway_event_context(event:dict, context):
    ''' Prints the event and context that AWS API Gateway receives
    Args:
        event (dict): The ID of the item to retrieve.
        context (str, optional): An optional query parameter.
    Returns:
        response (dict): object with status code and text message
    '''
    print("[event]", event)
    print("[context]", context)
    return {
        'statusCode': 200,
        'body': json.dumps('Successful HTTP')
    }

@my_decorator
@endpoint_url('/hci-blazer', 'GET')
def test_endpoint_url_decorator(event:dict, context):
    print('TEST test_endpoint decorator')
    dump_api_gateway_event_context(event, context)

if __name__ == '__main__':
    test_endpoint_url_decorator({}, None)