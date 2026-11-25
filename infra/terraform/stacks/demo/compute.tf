resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.app_instance_type
  subnet_id     = aws_subnet.public[local.availability_zones[0]].id

  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.app.name
  key_name               = var.ec2_key_name

  disable_api_termination              = var.enable_instance_termination_protection
  instance_initiated_shutdown_behavior = "stop"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  root_block_device {
    encrypted             = true
    delete_on_termination = true
    volume_type           = "gp3"
    volume_size           = var.app_root_volume_size_gib
  }

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    neo4j_volume_id = replace(aws_ebs_volume.neo4j.id, "-", "")
  })

  user_data_replace_on_change = true

  tags = {
    Name = "${local.name_prefix}-app"
  }
}

resource "aws_eip" "app" {
  domain   = "vpc"
  instance = aws_instance.app.id

  tags = {
    Name = "${local.name_prefix}-app"
  }
}

resource "aws_ebs_volume" "neo4j" {
  availability_zone = local.availability_zones[0]
  type              = "gp3"
  size              = var.neo4j_volume_size_gib
  iops              = var.neo4j_volume_iops
  throughput        = var.neo4j_volume_throughput
  encrypted         = true

  tags = {
    Name = "${local.name_prefix}-neo4j-data"
    Role = "neo4j-data"
  }
}

resource "aws_volume_attachment" "neo4j" {
  device_name  = "/dev/sdf"
  volume_id    = aws_ebs_volume.neo4j.id
  instance_id  = aws_instance.app.id
  force_detach = false

  stop_instance_before_detaching = true
}
