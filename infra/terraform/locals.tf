locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Repository  = "reflecta"
  }

  consumers = {
    emails = {
      queue_name                = coalesce(var.email_queue_name, "${var.project_name}-emails-${var.environment}")
      dlq_name                  = coalesce(var.email_dlq_name, "${var.project_name}-emails-dlq-${var.environment}")
      visibility_timeout_seconds = 60
      filter_policy = jsonencode({
        event_type = [{ prefix = "emails." }]
      })
    }

    work_ingestions = {
      queue_name                = coalesce(var.work_ingestion_queue_name, "${var.project_name}-work-ingestions-${var.environment}")
      dlq_name                  = coalesce(var.work_ingestion_dlq_name, "${var.project_name}-work-ingestions-dlq-${var.environment}")
      visibility_timeout_seconds = 300
      filter_policy = jsonencode({
        event_type = ["catalog.work_ingestion.requested"]
      })
    }
  }
}
