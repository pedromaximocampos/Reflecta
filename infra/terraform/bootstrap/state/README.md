# Terraform state bootstrap

This root creates the private, versioned S3 bucket and DynamoDB lock table used by the Reflecta Terraform roots. It exists separately because a backend must exist before another root can migrate its state into it.

The committed `backend.hcl.example` contains placeholders. The real `backend.hcl`, local state, and plans are ignored by Git.

## Initial bootstrap

Initialize without a backend, apply the bucket/table, and then migrate this root's own state:

```powershell
terraform init -backend=false
terraform plan -out=bootstrap.tfplan
terraform apply bootstrap.tfplan
Copy-Item backend.hcl.example backend.hcl
# Replace AWS_ACCOUNT_ID locally.
terraform init -migrate-state -backend-config=backend.hcl
terraform plan
```

Both resources use `prevent_destroy`. Removing them requires an explicit code change and review; an ordinary destroy of another stack cannot delete the state backend.
