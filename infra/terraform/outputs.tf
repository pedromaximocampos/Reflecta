output "integration_topic_arn" {
  description = "Value for AWS_SNS_ARN."
  value       = aws_sns_topic.integration_events.arn
}

output "consumer_queue_urls" {
  description = "Queue URLs consumed by the application workers."
  value       = { for name, queue in aws_sqs_queue.consumer : name => queue.id }
}

output "consumer_queue_arns" {
  description = "Queue ARNs used by IAM policies and event-source mappings."
  value       = { for name, queue in aws_sqs_queue.consumer : name => queue.arn }
}

output "dead_letter_queue_urls" {
  description = "DLQ URLs used for diagnostics and controlled redrive."
  value       = { for name, queue in aws_sqs_queue.dead_letter : name => queue.id }
}

output "application_environment" {
  description = "Non-secret application settings produced by this stack."
  value = {
    AWS_SNS_REGION                   = var.aws_region
    AWS_SNS_ARN                      = aws_sns_topic.integration_events.arn
    AWS_SQS_EMAILS_QUEUE_URL         = aws_sqs_queue.consumer["emails"].id
    AWS_SQS_WORK_INGESTIONS_QUEUE_URL = aws_sqs_queue.consumer["work_ingestions"].id
  }
}
