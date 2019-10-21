import os

import boto3


SNS_CLIENT = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')


def get_sns_topic_subscriptions(sns_topic_arn):
    response = SNS_CLIENT.list_subscriptions_by_topic(
        TopicArn=sns_topic_arn,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    return response["Subscriptions"]


def subscribe_sms_number_to_sns_topic(sms_number, sns_topic):
    response = SNS_CLIENT.subscribe(
        TopicArn=sns_topic,
        Protocol='sms',
        Endpoint=sms_number,
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def subscribe_sms_number_if_not_already_subscribed(sms_number):
    existing_subscriptions = get_sns_topic_subscriptions(SNS_TOPIC_ARN)
    for subscription in existing_subscriptions:
        if sms_number in subscription["Endpoint"]:
            return
    subscribe_sms_number_to_sns_topic(sms_number, SNS_TOPIC_ARN)


def send_sms_notification(sms_number, message):
    subscribe_sms_number_if_not_already_subscribed(sms_number)
    response = SNS_CLIENT.publish(
        PhoneNumber=sms_number,
        Message=message,
    )
    assert "MessageId" in response
