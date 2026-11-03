resource "aws_sns_topic" "integration_events" {
  name = "${var.project_name}-integration-events-${var.environment}"
}

resource "aws_sqs_queue" "dead_letter" {
  for_each = local.consumers

  name                      = each.value.dlq_name
  message_retention_seconds = var.dlq_retention_seconds
  sqs_managed_sse_enabled   = true

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.consumer[each.key].arn]
  })
}

resource "aws_sqs_queue" "consumer" {
  for_each = local.consumers

  name                       = each.value.queue_name
  message_retention_seconds  = var.message_retention_seconds
  receive_wait_time_seconds  = 20
  visibility_timeout_seconds = each.value.visibility_timeout_seconds
  sqs_managed_sse_enabled    = true
}

resource "aws_sqs_queue_redrive_policy" "consumer" {
  for_each = local.consumers

  queue_url = aws_sqs_queue.consumer[each.key].id
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dead_letter[each.key].arn
    maxReceiveCount     = var.max_receive_count
  })
}

data "aws_iam_policy_document" "allow_sns_to_queue" {
  for_each = local.consumers

  statement {
    sid    = "AllowIntegrationTopicToSend"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.consumer[each.key].arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.integration_events.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "allow_sns_to_queue" {
  for_each = local.consumers

  queue_url = aws_sqs_queue.consumer[each.key].id
  policy    = data.aws_iam_policy_document.allow_sns_to_queue[each.key].json
}

resource "aws_sns_topic_subscription" "consumer" {
  for_each = local.consumers

  topic_arn            = aws_sns_topic.integration_events.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.consumer[each.key].arn
  raw_message_delivery = true
  filter_policy_scope  = "MessageAttributes"
  filter_policy        = each.value.filter_policy

  depends_on = [aws_sqs_queue_policy.allow_sns_to_queue]
}
