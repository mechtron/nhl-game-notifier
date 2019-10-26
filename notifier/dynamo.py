import csv
import datetime
import os
import sys
import uuid

import boto3


DYNAMODB_CLIENT = boto3.client('dynamodb')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')


def get_users_csv():
    print("Retrieving user list from CSV..")
    users = []
    with open(os.path.join(sys.path[0], 'users.csv')) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=',')
        for row in reader:
            user = dict()
            for col in reader.fieldnames:
                user[col] = row[col]
            users.append(user)
    return users


def get_users():
    print("Retrieving user list from DynamoDB..")
    users = []
    response = DYNAMODB_CLIENT.scan(
        TableName=DYNAMODB_TABLE_NAME,
        Select="ALL_ATTRIBUTES",
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    for user in response["Items"]:
        users.append(dict(
            Id=user["Id"]["S"],
            SmsNumber=user["SmsNumber"]["S"],
            SmsNumberIsSubscribed=user["SmsNumberIsSubscribed"]["BOOL"],
            FavouriteTeam=user["FavouriteTeam"]["S"],
            MinutesToNotifyBeforeGameStart=(
                int(user["MinutesToNotifyBeforeGameStart"]["N"])
            ),
            LastNotified=(
                datetime.datetime.fromtimestamp(int(user["LastNotified"]["N"]))
            ),
        ))
    print("{} users successfully loaded".format(len(users)))
    return users


def create_user(**kwargs):
    response = DYNAMODB_CLIENT.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item={
            "Id": {
                "S": str(uuid.uuid4())[:8],
            },
            "SmsNumber": {
                "S": kwargs["sms_number"],
            },
            "SmsNumberIsSubscribed": {
                "BOOL": False,
            },
            "FavouriteTeam": {
                "S": kwargs["team"],
            },
            "MinutesToNotifyBeforeGameStart": {
                "N": kwargs["minutes_to_notify_before"],
            },
            "LastNotified": {
                "N": "0",
            },
        }
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print("New user successfully created")


def delete_user(user_id):
    response = DYNAMODB_CLIENT.delete_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"Id": {"S": user_id}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print("User with ID {} was successfully deleted".format(user_id))
