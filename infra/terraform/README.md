# Reflecta AWS messaging with Terraform

This root module describes the first Infrastructure as Code slice of Reflecta:

```text
PostgreSQL Outbox
        |
        v
SNS integration topic
        |
        +--> SQS emails ----------> email DLQ
        |
        +--> SQS work ingestions -> work-ingestion DLQ
```

Each SNS subscription filters the `event_type` message attribute. The producer publishes once to the integration topic; each consumer owns its queue, retry boundary, and DLQ.

## What this stack manages

- one standard SNS integration topic;
- one standard SQS queue per consumer;
- one DLQ per consumer;
- redrive after the configured receive limit;
- queue policies restricted to the SNS service and this topic ARN;
- raw SNS message delivery;
- subscription filtering through `MessageAttributes`;
- server-side encryption managed by SQS.

Lambda, SES, S3, databases, networking, and application deployment are intentionally outside this first slice.

## Safety before the first command

The development resources may already exist because they were created manually. Terraform configuration alone does not adopt them. Running `apply` before import can produce name conflicts or unintended changes.

Use this order:

```powershell
cd infra/terraform
Copy-Item terraform.tfvars.example terraform.tfvars
aws sso login --profile reflecta-dev
terraform init
terraform fmt -check -recursive
terraform validate
```

Then copy the required examples from `imports.tf.example` to `imports.local.tf`, replace placeholders locally, and run:

```powershell
terraform plan -out=reflecta.tfplan
terraform show reflecta.tfplan
```

Only run `terraform apply reflecta.tfplan` after the import actions and every proposed infrastructure change have been reviewed. This repository does not apply infrastructure automatically.

## Important files

| File | Purpose |
| --- | --- |
| `versions.tf` | Terraform and AWS provider constraints |
| `providers.tf` | AWS Region, local profile, and default tags |
| `variables.tf` | Inputs and validation rules |
| `locals.tf` | Naming, tags, consumers, and SNS filters |
| `messaging.tf` | SNS, SQS, DLQ, policies, subscriptions, and redrive |
| `outputs.tf` | ARNs and queue URLs consumed by the application |
| `imports.tf.example` | Safe template for adopting manually created resources |

## State and credentials

- `.tfstate`, plans, `.terraform/`, local variable files, and local import blocks are ignored by Git.
- The provider uses the normal AWS credential chain. `aws_profile` is only a local convenience; workloads running in AWS should use IAM roles.
- The provider lock file should be committed after `terraform init`.
- A shared or production environment should use protected remote state and locking instead of local state.
- Terraform state is operational data and can contain sensitive values even when the HCL source does not.

## Cost boundary

Terraform itself does not add AWS cost. Cost comes from the resources it creates and their use. SNS and SQS are request-based services; always inspect the plan, remain within the intended environment, and configure billing alerts separately.
