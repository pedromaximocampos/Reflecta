variable "project_name" {
  description = "Lowercase project identifier used in AWS resource names."
  type        = string
  default     = "reflecta"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "project_name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment suffix."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be dev, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS Region where SNS and SQS resources are managed."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Optional local AWS CLI profile. Leave null on AWS and use an IAM role."
  type        = string
  default     = null
  nullable    = true
}

variable "email_queue_name" {
  description = "Optional override used when importing an existing email queue."
  type        = string
  default     = null
  nullable    = true
}

variable "email_dlq_name" {
  description = "Optional override used when importing an existing email DLQ."
  type        = string
  default     = null
  nullable    = true
}

variable "work_ingestion_queue_name" {
  description = "Optional override used when importing an existing work-ingestion queue."
  type        = string
  default     = null
  nullable    = true
}

variable "work_ingestion_dlq_name" {
  description = "Optional override used when importing an existing work-ingestion DLQ."
  type        = string
  default     = null
  nullable    = true
}

variable "max_receive_count" {
  description = "Number of failed receives before SQS moves a message to its DLQ."
  type        = number
  default     = 5

  validation {
    condition     = var.max_receive_count >= 1 && var.max_receive_count <= 1000
    error_message = "max_receive_count must be between 1 and 1000."
  }
}

variable "message_retention_seconds" {
  description = "Retention period for messages in the main queues."
  type        = number
  default     = 345600

  validation {
    condition     = var.message_retention_seconds >= 60 && var.message_retention_seconds <= 1209600
    error_message = "message_retention_seconds must be between 60 seconds and 14 days."
  }
}

variable "dlq_retention_seconds" {
  description = "Retention period for failed messages in the DLQs."
  type        = number
  default     = 1209600

  validation {
    condition     = var.dlq_retention_seconds >= 60 && var.dlq_retention_seconds <= 1209600
    error_message = "dlq_retention_seconds must be between 60 seconds and 14 days."
  }
}
