output "state_bucket_name" {
  description = "Private, versioned S3 bucket that stores Terraform state."
  value       = aws_s3_bucket.terraform_state.id
}

output "lock_table_name" {
  description = "DynamoDB table used for Terraform state locking."
  value       = aws_dynamodb_table.terraform_locks.name
}
