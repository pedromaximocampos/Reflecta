# AWS application deployment

This directory contains only the versioned runtime topology. `.env.prod` is generated on the EC2 host from AWS Secrets Manager and must never be committed. The ECR image reference uses an immutable Git commit tag.

Deployment order:

1. create/update infrastructure through `infra/terraform/stacks/demo`;
2. publish the backend image to ECR using an immutable commit tag;
3. write runtime credentials directly to Secrets Manager;
4. render `/srv/reflecta/app/.env.prod` on EC2 through its instance role;
5. start Neo4j and run PostgreSQL and Neo4j migrations once;
6. start the API and three active workers;
7. build the frontend with the CloudFront API URL and synchronize `frontend/dist` to the private frontend bucket;
8. invalidate the frontend CloudFront distribution and run the smoke checks.

The legacy RabbitMQ email workers are intentionally absent. Production email delivery continues through the existing SNS, SQS, and Lambda path.
