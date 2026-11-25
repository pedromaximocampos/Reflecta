# Reflecta demo deployment stack

This independent Terraform root prepares the first public Reflecta environment without changing the existing messaging stack.

```text
CloudFront frontend -> private S3 frontend bucket
                   \-> /api/* -> EC2:8000 (same-origin session cookies)
CloudFront API      -> EC2:8000 (direct diagnostics endpoint)
CloudFront covers   -> private S3 catalog-assets bucket
                            |
                            v
EC2: API + workers + Neo4j Community
                            |
              +-------------+-------------+
              |                           |
       encrypted EBS gp3          private RDS PostgreSQL
       persistent graph data      two database subnets
```

The EC2 host lives in a public subnet because it needs outbound internet access to OpenAI and AWS services. It has no general public application ingress: port 8000 accepts only the AWS-managed CloudFront origin-facing prefix list. Administration uses AWS Systems Manager Session Manager. RDS is not public.

Neo4j is deliberately kept on EC2 with a dedicated EBS volume. Fargate supports EBS, but a stateful graph database there adds service, volume, replacement, and recovery constraints that are unnecessary for this TCC deployment. The stateless API and workers can move to Fargate later while RDS, S3, CloudFront, SNS, and SQS remain unchanged.

## What this stack creates

- one VPC, two public subnets, and two isolated database subnets;
- one EC2 host with an Elastic IP, Session Manager, and no public SSH by default;
- one encrypted `gp3` EBS data volume mounted at `/srv/reflecta/neo4j`;
- one private, encrypted, single-AZ RDS PostgreSQL instance with one-day automated retention under the AWS Free Plan;
- RDS credentials generated and held by AWS Secrets Manager;
- one encrypted ECR repository with image scanning and retention of the 10 latest images;
- one application runtime secret whose values are populated outside Terraform;
- one CloudWatch Logs group with 14-day retention;
- private S3 buckets and CloudFront distributions for the frontend and catalog covers;
- an HTTPS CloudFront entry point for the API without an ALB;
- least-privilege hooks for existing S3, SNS, and SQS resources;
- an optional monthly AWS Budget with forecast and actual-cost alerts.

It does **not** deploy application containers yet. That is intentional: first review the infrastructure plan, then build/push the images and deploy the Compose production file through Session Manager.

## Covers, PDFs, and avatars

The catalog-assets bucket is separate from private work documents and user media. Only catalog assets are delivered through the public CloudFront URL. PDFs and avatars remain in their existing private buckets and continue to use authenticated, short-lived URLs. Configure `AWS_S3_CATALOG_ASSETS_BUCKET` and `AWS_CLOUDFRONT_CATALOG_ASSETS_BASE_URL` with this stack's outputs; when both are present, new covers use immutable CloudFront URLs. Existing cover objects must be copied from the works bucket before switching an existing database.

## Safe execution order

Do not run `apply` before the plan has been inspected.

Create the state backend through `infra/terraform/bootstrap/state` first. Copy `backend.hcl.example` to the ignored `backend.hcl`, replace the account placeholder, and initialize this root with `-backend-config=backend.hcl`. Existing local state must use `terraform init -migrate-state`, never a manual state-file copy.

```powershell
cd infra/terraform/stacks/demo
Copy-Item terraform.tfvars.example terraform.tfvars
aws login --profile reflecta-dev
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=reflecta-demo.tfplan
terraform show reflecta-demo.tfplan
```

Only after reviewing resource names, region, instance sizes, IAM permissions, and estimated cost:

```powershell
terraform apply reflecta-demo.tfplan
```

The local `terraform.tfvars`, state, and saved plan must never be committed.

## Operational notes

- `m7i-flex.large` is the Free Plan-eligible 8 GiB starting point for a recorded demo with Neo4j, API, and workers on one host. The account rejected `t3.large` as ineligible even with promotional credits.
- `db.t4g.micro`, one-day automated retention, and single-AZ RDS satisfy the current Free Plan limits. Take a manual snapshot before risky changes; production availability would require longer retention, Multi-AZ, and stricter deletion/final-snapshot settings.
- The Neo4j EBS volume is a separate Terraform resource. Back it up with snapshots before destructive work.
- This stack intentionally has no NAT Gateway or Application Load Balancer, avoiding two large fixed monthly costs for the first deployment.
- CloudFront distributions can take several minutes to finish provisioning.
- After apply, set the browser API URL to `${frontend_url}/api` and configure the API CORS origin with `frontend_url`; `api_base_url` remains useful for direct diagnostics.
- The browser build uses `${frontend_url}/api`; a CloudFront Function removes the prefix before forwarding to FastAPI, keeping refresh cookies same-origin.
- Before deploying containers, retrieve the RDS credentials through the instance role and run Alembic migrations exactly once.

## Later evolution to Fargate

The migration boundary is the stateless runtime only:

1. publish API and worker images to ECR;
2. create ECS task definitions and services;
3. allow their security group to reach RDS;
4. preserve Neo4j on EC2/EBS until a managed or clustered graph option is justified;
5. redirect the API CloudFront origin from EC2 to the new load-balanced service.

This avoids combining the first cloud deployment with an unnecessary stateful-container migration.
