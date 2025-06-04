"""
Sections:
    Base Entity classes
        DynamoDbEntity
    Base Repository classes
        BaseRepository
"""

# BASE ENTITY CLASSES

class DynamoDbEntity(object):

    @staticmethod
    def dynamodb_null_value():
        return {'NULL': True}

    @staticmethod
    def dynamodb_string_value(value:str):
        return {'S': value}

    @staticmethod
    def dynamodb_number_value(value: str):
        return {'N': value}

    @staticmethod
    def dynamodb_boolean_value(value:bool):
        return {'B': value}

    @staticmethod
    def __map_from_dynamodb_attribute(att:dict):
        for k, v in att.items():
            match k:
                case 'S':
                    return v
                case 'N':
                    return float(v)
                case 'NULL':
                    return None if v == True else v
                case _:
                    print(f'Unhandled DynamoDb attribute {k}')
                    return None
        print('No DynamoDb attribute')
        return None

    def map_from_dynamodb_attribute(self, data:dict, field_name:str, default_value = None):
        return self.__map_from_dynamodb_attribute(data[field_name]) if field_name in data else default_value

    @staticmethod
    def get_dynamodb_attribute_value(data:dict, field_name:str, default_value = None):
        return DynamoDbEntity.__map_from_dynamodb_attribute(data[field_name]) if field_name in data else default_value


# BASE REPOSITORY CLASSES

class BaseRepository(object):
    pass
    # def __list_tables(self):
    #     response = dynamodb_client.list_tables()
    #     return response
    #
    # def __create_inventory_item_table(self):
    #     response = dynamodb_client.create_table(
    #         TableName='hci_inventory_item',
    #         AttributeDefinitions=[
    #             {'AttributeType': 'S', 'AttributeName': 'item_code'},
    #             {'AttributeType': 'S', 'AttributeName': 'item_description'},
    #         ],
    #         KeySchema=[
    #             {'AttributeName': 'item_code', 'KeyType': 'HASH'},
    #             {'AttributeName': 'item_description', 'KeyType': 'RANGE'},
    #         ],
    #         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    #     )
    #     print(response)
    #
    # def __delete_table(self, table_name: str):
    #     response = dynamodb_client.delete_table(TableName=table_name)
    #     print(response)
