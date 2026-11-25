variable "project_name" {
  description = "Lowercase project identifier used in AWS resource names."
  type        = string
  default     = "reflecta"
}

variable "aws_region" {
  description = "AWS Region that stores the Terraform state and lock table."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile used only while running Terraform locally."
  type        = string
  default     = null
  nullable    = true
}
