resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${local.name_prefix}-vpc"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${local.name_prefix}-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = {
    for index, az in local.availability_zones : az => {
      index = index
      cidr  = local.public_subnet_cidrs[index]
    }
  }

  vpc_id                  = aws_vpc.this.id
  availability_zone       = each.key
  cidr_block              = each.value.cidr
  map_public_ip_on_launch = false

  tags = {
    Name = "${local.name_prefix}-public-${each.value.index + 1}"
    Tier = "public"
  }
}

resource "aws_subnet" "database" {
  for_each = {
    for index, az in local.availability_zones : az => {
      index = index
      cidr  = local.database_subnet_cidrs[index]
    }
  }

  vpc_id            = aws_vpc.this.id
  availability_zone = each.key
  cidr_block        = each.value.cidr

  tags = {
    Name = "${local.name_prefix}-database-${each.value.index + 1}"
    Tier = "database"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "${local.name_prefix}-public"
  }
}

resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_db_subnet_group" "postgres" {
  name       = "${local.name_prefix}-postgres"
  subnet_ids = [for subnet in aws_subnet.database : subnet.id]

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}
