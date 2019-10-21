resource "aws_sns_topic" "sms_notifications" {
  name = "${var.function_name}-sms-notifications-${var.environment}"
}
