resource "aws_dynamodb_table" "dynamodb_table" {
  name           = "${var.function_name}-${var.environment}"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "Id"

  attribute {
    name = "Id"
    type = "S"
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
  }
}
