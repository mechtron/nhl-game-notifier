import csv
import os
import sys
import uuid

import boto3


DYNAMODB_CLIENT = boto3.client('dynamodb')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')


def get_users():
    print("Retrieving user list..")
    users = []
    with open(os.path.join(sys.path[0], 'users.csv')) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            user = dict()
            for col in reader.fieldnames:
                user[col] = row[col]
            users.append(user)
    print("{} users successfully loaded".format(len(users)))
    return users


def create_user(**kwargs):
    DYNAMODB_CLIENT.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item={
            "Id": {
                "S": str(uuid.uuid4())[:8],
            },
            "SmsNumber": {
                "S": kwargs["sms_number"],
            },
            "SmsNumberIsSubscribed": {
                "BOOL": kwargs["sms_is_subscribed"],
            },
            "FavouriteTeam": {
                "S": kwargs["favourite_team"],
            },
            "MinutesToNotifyBeforeGameStart": {
                "N": kwargs["minutes_to_notify_before"],
            },
            "LastNotified": {
                "N": kwargs["last_notified"],
            },
        }
    )
