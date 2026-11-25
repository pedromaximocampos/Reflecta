resource "aws_db_instance" "postgres" {
  identifier = "${local.name_prefix}-postgres"

  engine         = "postgres"
  engine_version = var.postgres_engine_version
  instance_class = var.postgres_instance_class

  db_name                     = var.postgres_db_name
  username                    = var.postgres_master_username
  manage_master_user_password = true
  port                        = 5432

  allocated_storage     = var.postgres_allocated_storage_gib
  max_allocated_storage = var.postgres_max_allocated_storage_gib
  storage_type          = "gp3"
  storage_encrypted     = true

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.postgres.id]
  publicly_accessible    = false
  multi_az               = false

  backup_retention_period = var.postgres_backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  delete_automated_backups   = false
  deletion_protection        = var.environment == "prod"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  skip_final_snapshot       = var.postgres_skip_final_snapshot
  final_snapshot_identifier = var.postgres_skip_final_snapshot ? null : "${local.name_prefix}-postgres-final"

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}
