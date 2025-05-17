# """
# Sections:
#     Base Entity classes
#         DynamoDbEntity
#     Base Repository classes
#         BaseRepositorya
# """
#
# # BASE ENTITY CLASSES
#
# class DynamoDbEntity(object):
#
#     @staticmethod
#     def dynamodb_null_value():
#         return {'NULL': True}
#
#     @staticmethod
#     def dynamodb_string_value(value):
#         return {'S': value}
#
#
# # BASE REPOSITORY CLASSES
#
# class BaseRepository(object):
#     pass
#     # def __list_tables(self):
#     #     response = dynamodb_client.list_tables()
#     #     return response
#     #
#     # def __create_inventory_item_table(self):
#     #     response = dynamodb_client.create_table(
#     #         TableName='hci_inventory_item',
#     #         AttributeDefinitions=[
#     #             {'AttributeType': 'S', 'AttributeName': 'item_code'},
#     #             {'AttributeType': 'S', 'AttributeName': 'item_description'},
#     #         ],
#     #         KeySchema=[
#     #             {'AttributeName': 'item_code', 'KeyType': 'HASH'},
#     #             {'AttributeName': 'item_description', 'KeyType': 'RANGE'},
#     #         ],
#     #         ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
#     #     )
#     #     print(response)
#     #
#     # def __delete_table(self, table_name: str):
#     #     response = dynamodb_client.delete_table(TableName=table_name)
#     #     print(response)
