from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1gnYaAyPMTZj4_i_e0MrHVIXZtSgDMegBZfPZFsaAQjs'
SAMPLE_RANGE_NAME = 'Form Responses 1!A2:G'

class Person:
    def __init__(self, name):
        self.name = name
        self.choices = {}
        self.points = 0

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
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

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    sid = Person("Siddharth")
    omkar = Person("Omkar")
    gaurav = Person("Gaurav")
    maqsood = Person("Maqsood")

    personDict = {}
    personDict["Siddharth"] = sid
    personDict["Omkar"] = omkar
    personDict["Gaurav"] = gaurav
    personDict["Maqsood"] = maqsood

    with open('results.json') as f:
        data = json.load(f)

    if not values:
        print('No data found.')
    else:
        for row in values:
            person = row[1]
            match_number = row[2].split()[0]
            winnerGuess = row[3]
            momGuess = row[4]
            highScorerGuess = row[5]
            highWicketsGuess = row[6]

            submissionDate = row[0].split()[0].split("/")[1]
            submissionTime = row[0].split()[1].split(":")[0]

            if int(match_number) > 11:
                continue

            match_date = data['results'][int(match_number) - 1]['date']
            match_time = data['results'][int(match_number) - 1]['time']

            if (int(submissionDate) == match_date) and (int(submissionTime) >= match_time):
                print("Skipped %s" % (person))
                continue

            personDict[person].choices[match_number] = []
            personDict[person].choices[match_number].append(winnerGuess.lower())
            personDict[person].choices[match_number].append(momGuess.lower())
            personDict[person].choices[match_number].append(highScorerGuess.lower())
            personDict[person].choices[match_number].append(highWicketsGuess.lower())

    for result in data['results']:
        match_number = result['id']

        for person in personDict.values():
            if match_number in person.choices.keys():
                choicesList = person.choices[match_number]

                if choicesList[1] in result['mom']:
                    person.points += 10

                if result['winner'] in choicesList[0]:
                    person.points += 10

                for bowler in result['highwickets']:
                    if choicesList[3] in bowler:
                        person.points += 10

                for batsmen in result['highscorer']:
                    if choicesList[2] in batsmen:
                        person.points += 10


    for person in personDict.values():
        print('%s, %s' % (person.name, person.points))


if __name__ == '__main__':
    main()