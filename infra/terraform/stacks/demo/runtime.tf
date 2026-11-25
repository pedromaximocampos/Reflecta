resource "aws_ecr_repository" "app" {
  name                 = "${local.name_prefix}-app"
  image_tag_mutability = "IMMUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "${local.name_prefix}-app"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Retain the 10 most recent application images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_secretsmanager_secret" "app_runtime" {
  name                    = "${local.name_prefix}/application-runtime"
  description             = "Runtime credentials used by the Reflecta API and workers. Values are managed outside Terraform."
  recovery_window_in_days = 7

  tags = {
    Name = "${local.name_prefix}-application-runtime"
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/${var.project_name}/${var.environment}/application"
  retention_in_days = 14

  tags = {
    Name = "${local.name_prefix}-application"
  }
}
