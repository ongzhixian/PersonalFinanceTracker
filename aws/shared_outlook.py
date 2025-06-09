import asyncio
import os
import json


# from azure.identity.aio import ClientSecretCredential
from azure.identity import DeviceCodeCredential, AuthenticationRecord, TokenCachePersistenceOptions
from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError

import pdb

class OutlookApi(object):
    SCOPES = ['User.Read', 'Mail.Read', 'Mail.Send', 'Tasks.ReadWrite']
    AUTHENTICATION_RECORD_FILE_NAME = 'msal_authentication_record.json'

    def __init__(self):
        """
        DeviceCodeCredential
        See: https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.devicecodecredential?view=azure-python
        """
        client_id = '357dbf37-6fe6-46a2-a4d3-22afbb62c923'
        msal_authentication_record = self._get_authentication_record()
        application_cache_persistence_options = TokenCachePersistenceOptions(name="my_application")

        device_code_credential = DeviceCodeCredential(
            client_id = client_id, tenant_id = "common",
            cache_persistence_options = application_cache_persistence_options,
            authentication_record=msal_authentication_record,
            disable_automatic_authentication = True)

        # We use msal_authentication_record as aa mechanism to check if device has been authenticated before.
        # While this is strictly speaking not technically accurate, it is acceptable because of the way MS oauth work.
        if msal_authentication_record is None:
            authentication_record = device_code_credential.authenticate(scopes=OutlookApi.SCOPES)
            self._save_authentication_record(authentication_record)

        self.access_token =  device_code_credential.get_token(*OutlookApi.SCOPES, tenant_id='common')
        self.msgraph_client = GraphServiceClient(device_code_credential, scopes=OutlookApi.SCOPES)

    def _get_authentication_record(self):
        msal_authentication_record_file_path = f'./{OutlookApi.AUTHENTICATION_RECORD_FILE_NAME}'
        if os.path.exists(msal_authentication_record_file_path):
            with open(msal_authentication_record_file_path, 'r', encoding='utf8') as in_file:
                auth_record_data = in_file.read()
                return AuthenticationRecord.deserialize(auth_record_data)
        return None

    def _save_authentication_record(self, authentication_record):
        msal_authentication_record_file_path = f'./{OutlookApi.AUTHENTICATION_RECORD_FILE_NAME}'
        with open(msal_authentication_record_file_path, 'w', encoding='utf8') as out_file:
            out_file.write(authentication_record.serialize())

    # GET /users/{id | userPrincipalName}
    async def get_user(self):
        try:
            # 3 methods of getting user info:
            # See: https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=python
            # Method 1:
            user = await self.msgraph_client.users.by_user_id('userID').get()
            # Method 2:
            # user = await self.msgraph_client.me.get()
            # Method 3:
            # from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
            # from kiota_abstractions.base_request_configuration import RequestConfiguration
            # query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            #     select=['displayName', 'mail', 'userPrincipalName']
            # )
            # request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            #     query_parameters=query_params
            # )
            # user = await self.msgraph_client.me.get(request_configuration=request_config)
            # print(user.user_principal_name, user.display_name, user.id)
        except APIError as e:
            print(f'Error: {e.error.message}')

    async def get_inbox(self):
        from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder

        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters= query_params
        )

        messages = await self.msgraph_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages

    def _print_messages(self, message_page):
        if message_page and message_page.value:
            # Output each message's details
            for message in message_page.value:
                print('Message:', message.subject)
                if (
                        message.from_ and
                        message.from_.email_address
                ):
                    print('  From:', message.from_.email_address.name or 'NONE')
                else:
                    print('  From: NONE')
                print('  Status:', 'Read' if message.is_read else 'Unread')
                print('  Received:', message.received_date_time)

            # If @odata.nextLink is present
            more_available = message_page.odata_next_link is not None
            print('\nMore messages available?', more_available, '\n')

    async def send_mail(self, subject: str, body: str, recipient: str):
        from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
        from msgraph.generated.models.message import Message
        from msgraph.generated.models.item_body import ItemBody
        from msgraph.generated.models.body_type import BodyType
        from msgraph.generated.models.recipient import Recipient
        from msgraph.generated.models.email_address import EmailAddress

        message = Message()
        message.subject = subject

        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = body

        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = recipient
        message.to_recipients = []
        message.to_recipients.append(to_recipient)

        request_body = SendMailPostRequestBody()
        request_body.message = message

        await self.msgraph_client.me.send_mail.post(body=request_body)

    async def get_meta_task_lists(self):
        # result = await self.msgraph_client.me.todo.lists.by_todo_task_list_id('todoTaskList-id').tasks.get()
        response = await self.msgraph_client.me.todo.lists.get()
        for meta_task_list in response.value:
            print(f'{meta_task_list.display_name:<30}, {meta_task_list.id}')
        # print(response)

    async def get_task_list(self, task_list_id):
        response = await self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks.get()
        for todo_task in response.value:
            print(f'{todo_task.title:<30}, {todo_task.id}')

    async def add_task(self, task_list_id):
        # response = await self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks.get()
        # for todo_task in response.value:
        #     print(todo_task.title)
        from msgraph.generated.models.todo_task import TodoTask
        from msgraph.generated.models.linked_resource import LinkedResource
        # To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
        request_body = TodoTask(
            title = "A new task",
            categories = [
                "Important",
            ],
            linked_resources = [
                LinkedResource(
                    web_url = "http://microsoft.com",
                    application_name = "Microsoft",
                    display_name = "Microsoft",
                ),
            ],
        )
        # tasks = self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks
        result = await self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks.post(request_body)

    async def update_task_due_date(self, task_list_id, task_id):
        """
        https://learn.microsoft.com/en-us/graph/api/todotask-update?view=graph-rest-1.0&tabs=python
        :return:
        """
        from msgraph.generated.models.todo_task import TodoTask
        from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
        # To initialize your graph_client, see https://learn.microsoft.com/en-us/graph/sdks/create-client?from=snippets&tabs=python
        request_body = TodoTask(
            due_date_time=DateTimeTimeZone(
                date_time="2020-07-25T16:00:00",
                time_zone="Eastern Standard Time",
            ),
        )

        result = await self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks.by_todo_task_id(task_id).patch(request_body)


    async def get_task(self, task_list_id, task_id):
        """
        https://learn.microsoft.com/en-us/graph/api/todotask-update?view=graph-rest-1.0&tabs=python
        :return:
        """
        result = await self.msgraph_client.me.todo.lists.by_todo_task_list_id(task_list_id).tasks.by_todo_task_id(task_id).get()

        # Serialize result using Kiota (https://pypi.org/project/microsoft-kiota-serialization-json/)
        # from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter
        # writer = JsonSerializationWriter()
        # result.serialize(writer)        # Serialize the object
        # serialized_data = writer.writer #  Get the serialized data (for JSON, this would be a dictionary)
        # print(json.dumps(serialized_data, indent=4))

        # Using JsonSerializationWriterFactory example
        from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
        writer = JsonSerializationWriterFactory().get_serialization_writer('application/json')
        result.serialize(writer=writer)
        # writer.get_serialized_content() # return bytes
        print(json.dumps(writer.writer, indent=4))


async def main():
    outlook_api = OutlookApi()
    # await outlook_api.get_user()

    # message_page = await outlook_api.get_inbox()
    # outlook_api._print_messages(message_page)

    # await outlook_api.send_mail('Testing Microsoft Graph', 'Hello world!', 'overxianz@gmail.com')
    # print('Mail sent.\n')

    # await outlook_api.get_meta_task_lists()

    task_list_id = 'AQMkADAwATExADhlOC0yOWM5LTVlMGItMDACLTAwCgAuAAADuHKU05PoUU_qJzmvhfprswEApVTMkOsFVEeI82ZdygHiigAAAN4R5h8AAAA='
    # await outlook_api.get_task_list(task_list_id)

    # await outlook_api.add_task(task_list_id)

    task_id = 'AQMkADAwATExADhlOC0yOWM5LTVlMGItMDACLTAwCgBGAAADuHKU05PoUU_qJzmvhfprswcApVTMkOsFVEeI82ZdygHiigAAAN4R5h8AAAClVMyQ6wVUR4jzZl3KAeKKAAgwfD37AAAA'
    # await outlook_api.update_task_due_date(task_list_id, task_id)

    await outlook_api.get_task(task_list_id, task_id)


if __name__ == "__main__":
    # Run main
    asyncio.run(main())
