locals {
  zip_output_path = "nhl-game-notifier.zip"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.repo_root_path}/notifier/"
  output_path = local.zip_output_path
}

resource "aws_lambda_function" "lambda_function" {
  filename         = local.zip_output_path
  function_name    = "${var.function_name}-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "notifier.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.6"
  memory_size      = "128"
  timeout          = "30"

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.sms_notifications.arn
    }
  }
}
