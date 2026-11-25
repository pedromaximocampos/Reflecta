output "vpc_id" {
  description = "Reflecta VPC identifier."
  value       = aws_vpc.this.id
}

output "app_instance_id" {
  description = "EC2 instance that runs the API, workers, and Neo4j."
  value       = aws_instance.app.id
}

output "app_elastic_ip" {
  description = "Stable public IP used only as the CloudFront API origin."
  value       = aws_eip.app.public_ip
}

output "neo4j_ebs_volume_id" {
  description = "Persistent encrypted EBS volume used by Neo4j."
  value       = aws_ebs_volume.neo4j.id
}

output "postgres_endpoint" {
  description = "Private RDS endpoint consumed by the application."
  value       = aws_db_instance.postgres.address
}

output "postgres_port" {
  description = "Private RDS PostgreSQL port."
  value       = aws_db_instance.postgres.port
}

output "postgres_master_secret_arn" {
  description = "Secrets Manager ARN containing the generated RDS credentials."
  value       = aws_db_instance.postgres.master_user_secret[0].secret_arn
  sensitive   = true
}

output "frontend_bucket_name" {
  description = "Private S3 bucket where the compiled frontend is uploaded."
  value       = aws_s3_bucket.frontend.id
}

output "frontend_url" {
  description = "HTTPS URL of the Reflecta frontend."
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "api_base_url" {
  description = "HTTPS URL of the Reflecta API."
  value       = "https://${aws_cloudfront_distribution.api.domain_name}"
}

output "catalog_assets_bucket_name" {
  description = "Private S3 bucket dedicated to catalog covers and other public catalog assets."
  value       = aws_s3_bucket.catalog_assets.id
}

output "catalog_assets_base_url" {
  description = "CloudFront base URL used to render catalog covers."
  value       = "https://${aws_cloudfront_distribution.catalog_assets.domain_name}"
}

output "ecr_repository_url" {
  description = "ECR repository used by the API and worker containers."
  value       = aws_ecr_repository.app.repository_url
}

output "application_runtime_secret_arn" {
  description = "Secrets Manager ARN read by the API and workers at deployment time."
  value       = aws_secretsmanager_secret.app_runtime.arn
  sensitive   = true
}

output "application_log_group_name" {
  description = "CloudWatch Logs group used by the API and worker containers."
  value       = aws_cloudwatch_log_group.app.name
}

output "session_manager_command" {
  description = "Command used to open a shell without exposing SSH."
  value       = "aws ssm start-session --target ${aws_instance.app.id} --region ${var.aws_region}${var.aws_profile == null ? "" : " --profile ${var.aws_profile}"}"
}

output "custom_domain_name" {
  description = "Configured public domain, or null when custom-domain support is disabled."
  value       = local.custom_domain_name
}

output "domain_delegation_name_servers" {
  description = "Authoritative Route 53 name servers that must be configured at the registrar."
  value       = local.custom_domain_enabled ? aws_route53_zone.public[0].name_servers : []
}

output "custom_frontend_url" {
  description = "Public custom URL after certificate validation and routing activation."
  value       = var.enable_custom_domain_routing ? "https://${local.custom_domain_name}" : null
}

output "ses_sender_email" {
  description = "Domain sender configured for the email Lambda after SES verification succeeds."
  value       = local.custom_domain_enabled ? "nao-responda@${local.custom_domain_name}" : null
}
