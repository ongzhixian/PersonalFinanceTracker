## BASE MESSAGE CLASSES

class Message(object):
    """Base class for all messages"""
    pass

class OperationResultMessage(Message):
    """Message to return result of some operation"""
    def __init__(self, operation_is_successful: bool, message: str | None = None, data_object: dict | list| None = None):
        self.is_success = operation_is_successful
        self.message = message
        self.data_object = data_object

    def __str__(self):
        return f"Operation is successful:{self.is_success}, Message:{self.message}, DataObject:{self.data_object}"

class ResponseMessage(Message):
    """Message use by endpoint to return response"""
    def __init__(self, status_code:int, body:str):
        self.statusCode = status_code
        self.body = body

    def to_dict(self):
        return {
            'statusCode': self.statusCode,
            'body': self.body
        }

    def __repr__(self):
        return self.to_dict()

    def __str__(self):
        return f"statusCode: {self.statusCode}, body: {self.body}"

# class DynamoDbMessage(Message):
#     def __map_from_dynamodb_attribute(self, att:dict):
#         for k, v in att.items():
#             match k:
#                 case 'S':
#                     return v
#                 case "N":
#                     return float(v)
#                 case _:
#                     print(f'Unhandled DynamoDb attribute {k}')
#                     return None
#         print('No DynamoDb attribute')
#         return None
#
#     def map_from_dynamodb_attribute(self, data:dict, field_name:str, default_value = None):
#         return self.__map_from_dynamodb_attribute(data[field_name]) if field_name in data else default_value
