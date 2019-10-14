import os

import boto3


# SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:634076224864:NhlGameNotifier"


def send_sms_notification(sms_number, message):
    sns_client = boto3.client('sns')
    response = sns_client.publish(
        # TopicArn=SNS_TOPIC_ARN,
        PhoneNumber=sms_number,
        Message=message,
    )
    assert "MessageId" in response
