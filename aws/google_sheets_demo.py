import os
from apiclient import discovery
from google.oauth2 import service_account

class GoogleSheet(object):
    def __init__(self, google_sheet_id):
        self.google_sheet_id = google_sheet_id
        self.service = self.__get_google_sheets_service()

    def __get_google_sheets_service(self):
        scopes = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        secret_file = os.path.join(os.getcwd(), 'hci-blazer-lambda-client-key.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        return service

    def append_to_sheet(self, sheet_name, values_to_append):
        try:
            range_to_append = f"{sheet_name}"
            body = {
                'values': values_to_append
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.google_sheet_id,
                range=range_to_append,
                valueInputOption='USER_ENTERED',  # or 'RAW'
                insertDataOption='INSERT_ROWS',  # Inserts new rows for the data
                body=body
            ).execute()
            print(f"{result.get('updates').get('updatedCells')} cells appended.")
            print(f"Appended to range: {result.get('updates').get('updatedRange')}")
            return result
        # except HttpError as error:
        #     print(f"An API error occurred: {error}")
        #     print(f"Details: {error.resp.status}, {error._get_reason()}")
        #     return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

# def get_google_sheets_service():
#     secret_file = os.path.join(os.getcwd(), 'hci-blazer-lambda-client-key.json')
#     credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
#     service = discovery.build('sheets', 'v4', credentials=credentials)
#     return service

def append_to_sheet(service, spreadsheet_id, sheet_name, values_to_append):
    try:
        # The range where the data will be appended.
        # Using just the sheet name (e.g., 'Sheet1') tells the API to find the
        # first empty row after the last row containing data in that sheet.
        # You can also use A1 notation like 'Sheet1!A:Z' to be more specific
        # about the columns the API should consider when finding the "table".
        range_to_append = f"{sheet_name}"

        body = {
            'values': values_to_append
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_to_append,
            valueInputOption='USER_ENTERED',  # or 'RAW'
            insertDataOption='INSERT_ROWS', # Inserts new rows for the data
            body=body
        ).execute()
        print(f"{result.get('updates').get('updatedCells')} cells appended.")
        print(f"Appended to range: {result.get('updates').get('updatedRange')}")
        return result
    # except HttpError as error:
    #     print(f"An API error occurred: {error}")
    #     print(f"Details: {error.resp.status}, {error._get_reason()}")
    #     return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

try:
    spreadsheet_id = '1IeETC6g8xqipia0SnrMsXOxN14SONPZxmJVOWx_rHgY'
    sheet_name = 'Outstanding'
    data_to_add = [
        # ['New Data A1', 'New Data B1', 'New Data C1'],
        # ['Another Row 1', 'Another Row 2']
        ['item 1', 'Some student', '2025-05-10', '2025-05-24']
    ]

    google_sheet = GoogleSheet(spreadsheet_id)
    google_sheet.append_to_sheet(sheet_name, data_to_add)

    # service = get_google_sheets_service()
    # #service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, body=data, range=range_name, valueInputOption='USER_ENTERED').execute()
    # append_to_sheet(service, spreadsheet_id, sheet_name, data_to_add)



except OSError as e:
    print(e)
