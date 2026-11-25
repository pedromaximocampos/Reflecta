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
  default     = "demo"

  validation {
    condition     = contains(["demo", "staging", "prod"], var.environment)
    error_message = "environment must be demo, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS Region used by the demo stack."
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Optional local AWS CLI profile. Workloads in AWS use IAM roles instead."
  type        = string
  default     = null
  nullable    = true
}

variable "vpc_cidr" {
  description = "IPv4 CIDR for the Reflecta VPC."
  type        = string
  default     = "10.42.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR."
  }
}

variable "app_instance_type" {
  description = "EC2 size for the API, workers, and Neo4j containers."
  type        = string
  default     = "t3.large"
}

variable "app_root_volume_size_gib" {
  description = "Size of the EC2 operating-system gp3 volume."
  type        = number
  default     = 20
}

variable "neo4j_volume_size_gib" {
  description = "Size of the dedicated encrypted gp3 volume used by Neo4j."
  type        = number
  default     = 40
}

variable "neo4j_volume_iops" {
  description = "Provisioned IOPS for the Neo4j gp3 volume."
  type        = number
  default     = 3000
}

variable "neo4j_volume_throughput" {
  description = "Provisioned throughput in MiB/s for the Neo4j gp3 volume."
  type        = number
  default     = 125
}

variable "enable_instance_termination_protection" {
  description = "Prevents accidental EC2 termination through the API."
  type        = bool
  default     = true
}

variable "ssh_ingress_cidrs" {
  description = "Optional trusted IPv4 CIDRs for SSH. Keep empty and use Session Manager."
  type        = list(string)
  default     = []
}

variable "ec2_key_name" {
  description = "Optional EC2 key pair. Session Manager is the default access path."
  type        = string
  default     = null
  nullable    = true
}

variable "postgres_db_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "reflecta"
}

variable "postgres_master_username" {
  description = "RDS master username. The password is generated and held by Secrets Manager."
  type        = string
  default     = "reflecta_admin"
  sensitive   = true
}

variable "postgres_engine_version" {
  description = "PostgreSQL major engine version."
  type        = string
  default     = "16"
}

variable "postgres_instance_class" {
  description = "RDS instance class for the demo environment."
  type        = string
  default     = "db.t4g.micro"
}

variable "postgres_allocated_storage_gib" {
  description = "Initial encrypted gp3 storage allocated to RDS."
  type        = number
  default     = 20
}

variable "postgres_max_allocated_storage_gib" {
  description = "Maximum storage after RDS autoscaling."
  type        = number
  default     = 100
}

variable "postgres_backup_retention_days" {
  description = "Automated RDS backup retention."
  type        = number
  default     = 7
}

variable "postgres_skip_final_snapshot" {
  description = "Demo convenience. Set false before treating the environment as durable production."
  type        = bool
  default     = true
}

variable "frontend_bucket_name" {
  description = "Optional globally unique override for the private frontend bucket."
  type        = string
  default     = null
  nullable    = true
}

variable "catalog_assets_bucket_name" {
  description = "Optional globally unique override for the private catalog-cover bucket."
  type        = string
  default     = null
  nullable    = true
}

variable "cloudfront_price_class" {
  description = "CloudFront edge-location price class used by the demo."
  type        = string
  default     = "PriceClass_100"

  validation {
    condition = contains([
      "PriceClass_100",
      "PriceClass_200",
      "PriceClass_All"
    ], var.cloudfront_price_class)
    error_message = "cloudfront_price_class must be PriceClass_100, PriceClass_200, or PriceClass_All."
  }
}

variable "application_s3_bucket_arns" {
  description = "Existing private S3 bucket ARNs that the application may access."
  type        = list(string)
  default     = []
}

variable "integration_topic_arn" {
  description = "Existing integration SNS topic ARN that the application may publish to."
  type        = string
  default     = null
  nullable    = true
}

variable "consumer_queue_arns" {
  description = "Existing SQS queue ARNs consumed by Reflecta workers."
  type        = list(string)
  default     = []
}

variable "enable_monthly_budget" {
  description = "Creates a monthly cost budget when an alert email is supplied."
  type        = bool
  default     = false
}

variable "monthly_budget_limit_usd" {
  description = "Monthly AWS cost limit used by the optional budget."
  type        = number
  default     = 100
}

variable "budget_alert_email" {
  description = "Email that receives budget alerts. Required when enable_monthly_budget is true."
  type        = string
  default     = null
  nullable    = true

  validation {
    condition = (
      !var.enable_monthly_budget ||
      (var.budget_alert_email != null && can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.budget_alert_email)))
    )
    error_message = "budget_alert_email must be a valid email when the monthly budget is enabled."
  }
}

variable "extra_tags" {
  description = "Additional tags merged into every supported AWS resource."
  type        = map(string)
  default     = {}
}
