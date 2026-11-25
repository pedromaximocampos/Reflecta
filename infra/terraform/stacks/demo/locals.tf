locals {
  name_prefix = "${var.project_name}-${var.environment}"

  availability_zones = slice(data.aws_availability_zones.available.names, 0, 2)

  public_subnet_cidrs = [
    for index in range(2) : cidrsubnet(var.vpc_cidr, 8, index)
  ]

  database_subnet_cidrs = [
    for index in range(2) : cidrsubnet(var.vpc_cidr, 8, index + 10)
  ]

  frontend_bucket_name = coalesce(
    var.frontend_bucket_name,
    "${local.name_prefix}-frontend-${data.aws_caller_identity.current.account_id}"
  )

  catalog_assets_bucket_name = coalesce(
    var.catalog_assets_bucket_name,
    "${local.name_prefix}-catalog-assets-${data.aws_caller_identity.current.account_id}"
  )

  application_bucket_object_arns = [
    for bucket_arn in var.application_s3_bucket_arns : "${bucket_arn}/*"
  ]

  has_application_permissions = (
    length(var.application_s3_bucket_arns) > 0 ||
    var.integration_topic_arn != null ||
    length(var.consumer_queue_arns) > 0
  )

  custom_domain_enabled = var.custom_domain_name != null
  custom_domain_name    = local.custom_domain_enabled ? trimsuffix(lower(var.custom_domain_name), ".") : null

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Repository  = "Individuum_MVP"
    },
    var.extra_tags
  )
}
