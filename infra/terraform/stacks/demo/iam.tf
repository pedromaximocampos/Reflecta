resource "aws_iam_role" "app" {
  name = "${local.name_prefix}-app"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

data "aws_iam_policy_document" "app_runtime" {
  statement {
    sid       = "ReadRdsMasterSecret"
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_db_instance.postgres.master_user_secret[0].secret_arn]
  }

  statement {
    sid       = "ReadApplicationRuntimeSecret"
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.app_runtime.arn]
  }

  statement {
    sid    = "AccessCatalogAssetsBucket"
    effect = "Allow"
    actions = [
      "s3:GetBucketLocation",
      "s3:ListBucket"
    ]
    resources = [aws_s3_bucket.catalog_assets.arn]
  }

  statement {
    sid    = "ManageCatalogAssets"
    effect = "Allow"
    actions = [
      "s3:AbortMultipartUpload",
      "s3:DeleteObject",
      "s3:GetObject",
      "s3:ListMultipartUploadParts",
      "s3:PutObject"
    ]
    resources = ["${aws_s3_bucket.catalog_assets.arn}/*"]
  }

  dynamic "statement" {
    for_each = length(var.application_s3_bucket_arns) > 0 ? [1] : []
    content {
      sid    = "AccessApplicationBuckets"
      effect = "Allow"
      actions = [
        "s3:GetBucketLocation",
        "s3:ListBucket"
      ]
      resources = var.application_s3_bucket_arns
    }
  }

  dynamic "statement" {
    for_each = length(var.application_s3_bucket_arns) > 0 ? [1] : []
    content {
      sid    = "AccessApplicationObjects"
      effect = "Allow"
      actions = [
        "s3:AbortMultipartUpload",
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:ListMultipartUploadParts",
        "s3:PutObject"
      ]
      resources = local.application_bucket_object_arns
    }
  }

  dynamic "statement" {
    for_each = var.integration_topic_arn != null ? [1] : []
    content {
      sid       = "PublishIntegrationEvents"
      effect    = "Allow"
      actions   = ["sns:Publish"]
      resources = [var.integration_topic_arn]
    }
  }

  dynamic "statement" {
    for_each = length(var.consumer_queue_arns) > 0 ? [1] : []
    content {
      sid    = "ConsumeApplicationQueues"
      effect = "Allow"
      actions = [
        "sqs:ChangeMessageVisibility",
        "sqs:DeleteMessage",
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl",
        "sqs:ReceiveMessage"
      ]
      resources = var.consumer_queue_arns
    }
  }
}

resource "aws_iam_role_policy" "app_runtime" {
  name   = "${local.name_prefix}-runtime"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_runtime.json
}

resource "aws_iam_instance_profile" "app" {
  name = "${local.name_prefix}-app"
  role = aws_iam_role.app.name
}
