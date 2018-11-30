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


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://mail.google.com/', "https://www.googleapis.com/auth/gmail.labels"]

def MakeLabel(label_name, mlv="show", llv="labelShow"):
    label = {"messageListVisibility" : mlv,
             "name" : label_name,
             "labelListView" : llv}
    return label

def CreateLabel(servicel, userId, label_object):
    try:
        label = servicel.users().labels().create(userId=userId, body=label_object).execute()
        print(label["id"])
        return label
    except errors.HttpError as error:
        print(f"An error occurred {error}")

def DeleteLabel(service, user_id, label_id):
    try:
        service.users().labels().delete(userId=user_id, id=label_id).execute()
        print(f"Label {label_id} deleted")
    except errors.HttpError as error:
        print(f"error: {error}")

def GetLabel(service, user_id, label_id):
    try:
        label = service.users().labels().get(userId=user_id, id=label_id).execute()
        #print(f"label {label.getName()} retrieved")
        print(label)
    except errors.HttpError as error:
        print(f"An error occurred {error}")

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
        print('An error occurred: %s' % error)

def MessageToJson(message, file_name):
    with open(f"./{file_name}.json", "w") as f:
        messageToJson = json.dumps(message, sort_keys=True, indent=4)
        f.write(messageToJson.replace("'", '""'))
        return messageToJson

def ParseEmail(message):
    sender = str(message["payload"]["headers"][16]["value"])
    date = str(message["payload"]["headers"][17]["value"])
    contentpre = (str(base64.urlsafe_b64decode(str.encode(message["payload"]["parts"][0]["body"]["data"])))).replace("\\r\\n", "\n")
    content = contentpre[2:len(contentpre)-1]
    parsedMessage = {"sender": sender, "date": date, "data": content}
    return parsedMessage

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    """labelname = str(input("name: ")) #Creates New Label
    #newlab = CreateLabel(service, "me", MakeLabel(labelname))"""

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(f"{labels.index(label)}) {label['name']}: {label['id']}")

    """idtodel = str(input("Id of label to delete: ")) #Deletes Existing Label
    DeleteLabel(service, "me", idtodel)"""

    #idtoget = str(input("Id to get: "))
    #GetLabel(service, "me", idtoget)

    #print(ListMessagesWithMatchingQuery(service, "me", "from:luigip2010@gmail.com"))

    #msg1 = GetMessage(service, "me", "167523bb6520bbba")

    messagesFromMe = ListMessagesWithMatchingQuery(service, "me", "from:luigip20101@gmail.com")

    msglist = []

    for x in messagesFromMe:
        msglist.append(GetMessage(service, "me", x["id"]))

    for m in msglist:
        print("\n\n{}) {}: {}".format(msglist.index(m), m["snippet"], m["id"]))

    parsedthing = ParseEmail(msglist[1])
    print(f'\n\nFrom: {parsedthing["sender"]}   {parsedthing["date"]}\n\n\n{parsedthing["data"]}')



if __name__ == '__main__':
    main()
# [END gmail_quickstart]
