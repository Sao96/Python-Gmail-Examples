import base64
import pickle
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def connect():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def searchEmail(service, query):
    # First request to get the ids of emails matching query, for a mximum of 5
    googleRes = service.users().messages().list(
        userId='me',
        includeSpamTrash=None,
        labelIds=None,
        maxResults=5,
        pageToken=None,
        q=query
    ).execute()
    foundMessages = googleRes.get('messages', [])
    # for each found message, we will make a get request for the full email
    # from the id we found for each message
    for foundMsg in foundMessages:
        msgData = service.users().messages().get(
            userId='me', id=foundMsg['id'], format='full').execute()
        date = msgData["internalDate"]
        headers = msgData["payload"]["headers"]
        # header contents are stored in an array of dict objects
        subject = [hdr["value"] for hdr in headers if hdr["name"] == "Subject"]
        data = ""
        if "data" in msgData["payload"]["body"]:
            data = base64.urlsafe_b64decode(msgData["payload"]["body"]["data"])
        # convert the retrieved time from milliseconds to current date
        print(datetime.datetime.fromtimestamp(int(date)/1000))
        print("\n")
        print(subject)
        print(data[:min(400, len(data))])
        print("\n****************"*3)


if __name__ == '__main__':
    service = connect()
    while True:
        print("Enter a search query: ")
        searchEmail(service, input())
