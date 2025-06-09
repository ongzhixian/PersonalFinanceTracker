import json
import mimetypes
import os.path
from base64 import urlsafe_b64encode, urlsafe_b64decode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.message import EmailMessage


class GmailApi(object):
    """
    See: https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.html
    """
    # If modifying these scopes, delete the file oauth_credentials file.
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
              "https://www.googleapis.com/auth/gmail.compose"]
    OAUTH_CREDENTIALS_FILE_NAME = 'google_oauth_credentials_token.json'

    def get_profile(self, user_id: str ='me'):
        """
        { # Profile for a Gmail user.
          "emailAddress": "A String", # The user's email address.
          "historyId": "A String", # The ID of the mailbox's current history record.
          "messagesTotal": 42, # The total number of messages in the mailbox.
          "threadsTotal": 42, # The total number of threads in the mailbox.
        }
        """
        oauth_credentials = self._get_oauth_credentials()
        try:  # Call the Gmail API
            service = build("gmail", "v1", credentials=oauth_credentials)
            profile = service.users().getProfile(userId=user_id).execute()
            return profile

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    def get_labels(self, user_id: str ='me'):
        oauth_credentials = self._get_oauth_credentials()
        try:
            # Call the Gmail API
            service = build("gmail", "v1", credentials=oauth_credentials)
            results = service.users().labels().list(userId=user_id).execute()
            labels = results.get("labels", [])

            if not labels:
                print("No labels found.")
                return
            print("Labels:")
            for label in labels:
                print(label["name"])

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f"An error occurred: {error}")

    def get_label(self, label_name: str, user_id: str ='me'):
        oauth_credentials = self._get_oauth_credentials()
        try:
            service = build("gmail", "v1", credentials=oauth_credentials)
            profile = service.users().labels().get(userId=user_id,id=label_name).execute()
            return profile
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_message_list(self, user_id: str ='me', label_id_list=None):
        oauth_credentials = self._get_oauth_credentials()
        message_list = []
        try:
            service = build("gmail", "v1", credentials=oauth_credentials)
            list_response = service.users().messages().list(userId=user_id, labelIds=label_id_list).execute()
            message_list.extend(list_response['messages'])

            while 'nextPageToken' in list_response:
                next_page_token = list_response['nextPageToken']
                result_size_estimate = list_response['resultSizeEstimate']
                print('next_page_token: %s, result_size_estimate: %s' % (next_page_token, result_size_estimate))
                list_response = service.users().messages().list(userId=user_id, labelIds=label_id_list, pageToken=next_page_token).execute()
                message_list.extend(list_response['messages'])

            return message_list
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_message(self, message_id: str, user_id: str ='me'):
        oauth_credentials = self._get_oauth_credentials()
        
        try:
            service = build("gmail", "v1", credentials=oauth_credentials)
            response = service.users().messages().get(userId = user_id, id = message_id).execute()
            return response
        except HttpError as error:
            print(f"An error occurred: {error}")

    def create_draft(self):
        """Create and insert a draft email.
        Print the returned draft's message and id.
        Returns: Draft object, including draft id and message meta data.

        Load pre-authorized user credentials from the environment.
        TODO(developer) - See https://developers.google.com/identity
        for guides on implementing OAuth2 for the application.
        """
        oauth_credentials = self._get_oauth_credentials()
        try:
            service = build("gmail", "v1", credentials=oauth_credentials)

            message = EmailMessage()
            
            message["To"] = "zhixian@hotmail.com"
            message["From"] = "overxianz@gmail.com"
            message["Subject"] = "Automated draft"

            message.set_content("This is automated draft mail")


             # Add attachment(s) if any
            attachment_filename = "photo.jpg"
            # guessing the MIME type
            type_subtype, _ = mimetypes.guess_type(attachment_filename)
            maintype, subtype = type_subtype.split("/")

            with open(attachment_filename, "rb") as fp:
                attachment_data = fp.read()
            message.add_attachment(attachment_data, maintype, subtype)


            # encoded message
            encoded_message = urlsafe_b64encode(message.as_bytes()).decode()

            # create_message = {"message": {"raw": encoded_message}}
            # draft = (
            #     service.users()
            #     .drafts()
            #     .create(userId="me", body=create_message)
            #     .execute()
            # )
            # print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
            # return draft

            create_message = {"raw": encoded_message}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')

        except HttpError as error:
            print(f"An error occurred: {error}")
            draft = None

        


    def _get_oauth_credentials(self):
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        oauth_credentials = None
        # The oauth credentials file stores the user's access and refresh tokens.
        # It is created automatically when the authorization flow completes for the first time.
        oauth_credentials_file_path = f'./{GmailApi.OAUTH_CREDENTIALS_FILE_NAME}'
        if os.path.exists(oauth_credentials_file_path):
            oauth_credentials = Credentials.from_authorized_user_file(
                oauth_credentials_file_path, GmailApi.SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not oauth_credentials or not oauth_credentials.valid:
            if oauth_credentials and oauth_credentials.expired and oauth_credentials.refresh_token:
                oauth_credentials.refresh(Request())
            else:
                google_oauth_credentials_file_path = self._get_google_oauth_credentials_file_path()
                flow = InstalledAppFlow.from_client_secrets_file(
                    google_oauth_credentials_file_path, GmailApi.SCOPES
                )
                oauth_credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(oauth_credentials_file_path, "w", encoding='utf8') as out_file:
                out_file.write(oauth_credentials.to_json())

        return oauth_credentials

    def _get_google_oauth_credentials_file_path(self):
        user_secrets_id = 'tech-notes-press'
        file_name = 'hci_blazer_quickstart_credentials.json'
        file_path = os.path.expandvars(f'%APPDATA%/Microsoft/UserSecrets/{user_secrets_id}/{file_name}')
        return file_path

    def _uri_b64encode(s):
        return urlsafe_b64encode(s).strip('=')

    def _uri_b64decode(s):
        return urlsafe_b64decode(s + '=' * (4 - len(s) % 4))

def main():
    gmail_api = GmailApi()
    gmail_profile = gmail_api.get_profile()
    print('gmail_profile: %s\n' % gmail_profile)
    
    # gmail_api.get_labels()

    # inbox_details = gmail_api.get_label(label_name='INBOX', user_id='overxianz@gmail.com')
    # print('inbox_details: %s\n' % inbox_details)

    # LIST MESSAGES
    # message_list = gmail_api.get_message_list(label_id_list=['INBOX'])
    # print('message_list: %s\n' % len(message_list))
    # first_message = message_list[1]
    # last_message = message_list[-1]
    # print('first_message: %s' % first_message)
    # print('last_message: %s' % last_message)

    # 
    # message = gmail_api.get_message(message_id=first_message['id'])
    # message_part = message['payload']['parts'][1]
    # message_data = message_part['body']['data']
    # msg = urlsafe_b64decode(message_data + '=' * (4 - len(message_data) % 4))
    # # print('msg: %s\n' % msg)
    # with open('message.html', 'w', encoding='utf8') as out_file:
    #     out_file.write(msg.decode('utf8'))

    gmail_api.create_draft()


if __name__ == "__main__":
    main()
