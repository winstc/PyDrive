import httplib2
import os
import io
import config as cfg

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaIoBaseDownload
import googleapiclient.errors


SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'PyDrive'

DEFAULT_DOCUMENT_FORMAT = "application/vnd.oasis.opendocument.text"
DEFAULT_SPREADSHEET_FORMAT = "application/x-vnd.oasis.opendocument.spreadsheet"
DEFAULT_PRESENTATION_FORMAT = "application/vnd.oasis.opendocument.presentation"
DEFAULT_DRAWING_FORMAT = "image/jpeg"

class Client():

    def __init__(self):
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)

    def get_credentials(self):

        # Gets valid user credentials from storage.
        # If nothing has been stored, or if the stored credentials are invalid,
        # the OAuth2 flow is completed to obtain the new credentials.
        #
        # Returns:
        #    Credentials, the obtained credential.

        credential_dir = cfg.get_config_dir()
        credential_path = os.path.join(credential_dir,
                                       'PyDriveAuth.json')
        print(credential_dir)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def test(self):

        results = self.service.files().list(
            pageSize=100, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))

    def get_file_metadata(self, file_id):
        try:
            file = self.service.files().get(fileId=file_id).execute()
        except googleapiclient.errors.HttpError as err:
            if err.args[0]['status'] == '404':
                return None
            else:
                print(err)
        else:
            mime_type = file.get('mimeType')
            file_name = file.get('name')

            return {'id': file_id, 'name': file_name, 'mimeType': mime_type}

    def clone(self, file_id):
        file = self.get_file_metadata(file_id)
        mime_type = file['mimeType']
        file_name = file['name']

        if "application/vnd.google-apps" not in mime_type:
            request = self.service.files().get_media(fileId=file_id)
        else:
            if mime_type == "application/vnd.google-apps.document":
                download_mime_type = DEFAULT_DOCUMENT_FORMAT
            elif mime_type == "application/vnd.google-apps.spreadsheet":
                download_mime_type = DEFAULT_SPREADSHEET_FORMAT
            elif mime_type == "application/vnd.google-apps.presentation":
                download_mime_type = DEFAULT_PRESENTATION_FORMAT
            elif mime_type == "application/vnd.google-apps.drawing":
                download_mime_type = DEFAULT_DRAWING_FORMAT
            else:
                print("Bad Mime Type")
                return False
            request = self.service.files().export_media(fileId=file_id, mimeType=download_mime_type)

        fh = open(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def search(self, search_string):
        results = self.service.files().list(
            pageSize=100, q="name contains '{}'".format(search_string),
            fields="nextPageToken, files(id, name, mimeType)").execute()

        items = results.get('files', [])
        if items:
            return items
        else:
            meta = self.get_file_metadata(search_string)
            if meta:
                return [meta]
            else:
                return None


    def sync(self):
        response = self.service.changes().getStartPageToken().execute()
        print('Start token: %s' % response.get('startPageToken'))

        page_token = 85286   # response.get('startPageToken')
        while page_token is not None:
            response = self.service.changes().list(pageToken=page_token,
                                                spaces='drive').execute()
            for change in response.get('changes'):
                # Process change
                meta = self.get_file_metadata(change.get('fileId'))
                print('Change found for file: %s' % meta.get('name'))
            if 'newStartPageToken' in response:
                # Last page, save this token for the next polling interval
                saved_start_page_token = response.get('newStartPageToken')
            page_token = response.get('nextPageToken')

if __name__ == '__main__':

    c = Client()
    #c.clone("1Cdy8azKTyBhKOT6G_l2zeOxWulwSwnb951TWcDeqhAY")
    print(c.search("eng"))
    '''
    print("Search: ")
    items = c.search(input())
    for item in items:
        print('{0}.)  {1} ({2}) [{3}]'.format(items.index(item), item['name'], item['id'], item['mimeType']))
    print("Enter index to clone:")
    index = int(input())
    file = items[index]
    #c.clone(file['id'], file['name'], file['mimeType'])
   '''