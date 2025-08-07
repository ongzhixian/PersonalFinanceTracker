import pdb
import inspect
import ucm

from shared_lambda import endpoint_url

#
# def ensure_list(value):
#     """
#     Ensure that the input value is a list. If it is not, convert it to a list.
#     If the input is None, return an empty list.
#     :param value: The input value to check.
#     :return: A list containing the input value or an empty list if the input is None.
#     """
#     if value is None:
#         return []
#     elif isinstance(value, list):
#         return value
#     else:
#         return [value]
def ensure_has_header(request, request_headers) -> dict:
    if 'headers' not in request:
        raise 'No headers error'
    request_headers=request['headers']
    return request_headers


def main2():
    request = {
        'headers': {
            'authorization': 'bearer sometoken'
        }
    }
    request_headers = None
    request_headers = ensure_has_header(request, request_headers)
    print('request_headers', request_headers)


def main():

    functions = inspect.getmembers(ucm, inspect.isfunction)

    for name, func in functions:
        has_is_decorator = hasattr(func, "__is_decorator__")
        has_is_endpoint_url_decorator = hasattr(func, "__is_endpoint_url_decorator__")
        if has_is_endpoint_url_decorator:
            print("Function: %s, is_decorated: %s|%s" % (name, has_is_endpoint_url_decorator, has_is_decorator))
        else:
            print("** Plain function: %s" % (name))

if __name__ == "__main__":
    main()