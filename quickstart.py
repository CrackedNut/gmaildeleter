# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gmail_quickstart]
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import base64
import email
import json
from win10toast import ToastNotifier


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://mail.google.com/', "https://www.googleapis.com/auth/gmail.labels"]

def ListMessagesWithMatchingQuery(service, user_id, query=""):
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = service.users().messages().list(userId=user_id, q=query,
                                               pageToken=page_token).execute()
            messages.extend(response["messages"])
        return messages
    except errors.HttpError as error:
      print('An error occurred: %s' % error)

def GetMessage(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        #print(f"snippet: {message['snippet']}\n\n")
        return message
    except errors.HttpError as error:
        print(f"An error occurred {error}")

def TrashMessage(service, user_id, msg_id, x): #Change later to delete
    try:
        service.users().messages().trash(userId=user_id, id=msg_id).execute()
        print(f'Message with id: {msg_id} trashed successfully.')
        return x+1
    except errors.HttpError as error:
        print(f"An error occurred {error}")

def Auntenticate():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def main():
    service = Auntenticate()

    while True:
        toaster = ToastNotifier()
        sendermail = str(input("Sender: "))
        messagesFromMe = ListMessagesWithMatchingQuery(service, "me", f"from:{sendermail}")
        msglist = []

        for x in messagesFromMe:
            msglist.append(GetMessage(service, "me", x["id"]))
        toaster.show_toast(f"{len(msglist)} found")

        print("\n\n")

        for m in msglist:
            print("{}) {}: {}".format(msglist.index(m), m["snippet"], m["id"]))

        deleted = 0

        for m in msglist:
            deleted = TrashMessage(service, "me", m["id"], deleted)
        toaster.show_toast("Done!", f"{deleted} mails trashed")

if __name__ == '__main__':
    main()
# [END gmail_quickstart]
