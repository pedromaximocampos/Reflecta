resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app"
  description = "CloudFront and optional administrative access to Reflecta"
  vpc_id      = aws_vpc.this.id

  ingress {
    description     = "API traffic from CloudFront origin-facing addresses"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront_origin_facing.id]
  }

  dynamic "ingress" {
    for_each = length(var.ssh_ingress_cidrs) > 0 ? [1] : []
    content {
      description = "Optional restricted SSH access"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = var.ssh_ingress_cidrs
    }
  }

  egress {
    description = "Application outbound access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-app"
  }
}

resource "aws_security_group" "postgres" {
  name        = "${local.name_prefix}-postgres"
  description = "PostgreSQL access only from the Reflecta application host"
  vpc_id      = aws_vpc.this.id

  ingress {
    description     = "PostgreSQL from application"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    description = "Stateful response traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}
