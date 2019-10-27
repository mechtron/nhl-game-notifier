import csv
from datetime import datetime
import os
import sys
import uuid

import boto3


DYNAMODB_CLIENT = boto3.client('dynamodb')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')


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
            id=user["Id"]["S"],
            sms_number=user["SmsNumber"]["S"],
            sms_number_subscribed=user["SmsNumberIsSubscribed"]["BOOL"],
            team=user["FavouriteTeam"]["S"],
            minutes_to_notify_before_game=(
                int(user["MinutesToNotifyBeforeGameStart"]["N"])
            ),
            last_notified=(
                datetime.fromtimestamp(int(user["LastNotified"]["N"]))
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


def update_user_sns_subscription_status(user_id, status):
    response = DYNAMODB_CLIENT.update_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"Id": {"S": user_id}},
        UpdateExpression="SET SmsNumberIsSubscribed = :value",
        ExpressionAttributeValues={":value": {"BOOL": status}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print(
        "User with ID {user_id} SNS subscription "
        "status updated to {new_status}".format(
            user_id=user_id,
            new_status=status,
        )
    )


def update_user_last_notified_date(user_id, epoch_time):
    response = DYNAMODB_CLIENT.update_item(
        TableName=DYNAMODB_TABLE_NAME,
        Key={"Id": {"S": user_id}},
        UpdateExpression="SET LastNotified = :value",
        ExpressionAttributeValues={":value": {"N": str(epoch_time)}},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] is 200
    print(
        "User with ID {user_id} LastNotified updated to {new_date}".format(
            user_id=user_id,
            new_date=epoch_time,
        )
    )
