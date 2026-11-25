resource "aws_route53_zone" "public" {
  count = local.custom_domain_enabled ? 1 : 0

  name    = local.custom_domain_name
  comment = "Public DNS for the ${local.name_prefix} environment"
}

resource "aws_acm_certificate" "custom" {
  count = local.custom_domain_enabled ? 1 : 0

  domain_name               = local.custom_domain_name
  subject_alternative_names = ["*.${local.custom_domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "acm_validation" {
  for_each = local.custom_domain_enabled ? {
    for option in aws_acm_certificate.custom[0].domain_validation_options : option.domain_name => {
      name   = option.resource_record_name
      record = option.resource_record_value
      type   = option.resource_record_type
    }
  } : {}

  allow_overwrite = true
  zone_id         = aws_route53_zone.public[0].zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 300
  records         = [each.value.record]
}

resource "aws_acm_certificate_validation" "custom" {
  count = var.enable_custom_domain_routing ? 1 : 0

  certificate_arn         = aws_acm_certificate.custom[0].arn
  validation_record_fqdns = [for record in aws_route53_record.acm_validation : record.fqdn]
}

resource "aws_sesv2_email_identity" "domain" {
  count = local.custom_domain_enabled ? 1 : 0

  email_identity = local.custom_domain_name

  dkim_signing_attributes {
    next_signing_key_length = "RSA_2048_BIT"
  }
}

resource "aws_route53_record" "ses_dkim" {
  count = local.custom_domain_enabled ? 3 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "${aws_sesv2_email_identity.domain[0].dkim_signing_attributes[0].tokens[count.index]}._domainkey.${local.custom_domain_name}"
  type    = "CNAME"
  ttl     = 300
  records = ["${aws_sesv2_email_identity.domain[0].dkim_signing_attributes[0].tokens[count.index]}.dkim.amazonses.com"]
}

resource "aws_ses_domain_mail_from" "domain" {
  count = local.custom_domain_enabled ? 1 : 0

  domain                 = local.custom_domain_name
  mail_from_domain       = "bounce.${local.custom_domain_name}"
  behavior_on_mx_failure = "UseDefaultValue"

  depends_on = [aws_sesv2_email_identity.domain]
}

resource "aws_route53_record" "ses_mail_from_mx" {
  count = local.custom_domain_enabled ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = aws_ses_domain_mail_from.domain[0].mail_from_domain
  type    = "MX"
  ttl     = 300
  records = ["10 feedback-smtp.${var.aws_region}.amazonses.com"]
}

resource "aws_route53_record" "ses_mail_from_spf" {
  count = local.custom_domain_enabled ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = aws_ses_domain_mail_from.domain[0].mail_from_domain
  type    = "TXT"
  ttl     = 300
  records = ["v=spf1 include:amazonses.com ~all"]
}

resource "aws_route53_record" "dmarc" {
  count = local.custom_domain_enabled ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "_dmarc.${local.custom_domain_name}"
  type    = "TXT"
  ttl     = 300
  records = ["v=DMARC1; p=none;"]
}

resource "aws_route53_record" "frontend_ipv4" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = local.custom_domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "frontend_ipv6" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = local.custom_domain_name
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www_ipv4" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "www.${local.custom_domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www_ipv6" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "www.${local.custom_domain_name}"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.frontend.domain_name
    zone_id                = aws_cloudfront_distribution.frontend.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "catalog_assets_ipv4" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "assets.${local.custom_domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.catalog_assets.domain_name
    zone_id                = aws_cloudfront_distribution.catalog_assets.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "catalog_assets_ipv6" {
  count = var.enable_custom_domain_routing ? 1 : 0

  zone_id = aws_route53_zone.public[0].zone_id
  name    = "assets.${local.custom_domain_name}"
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.catalog_assets.domain_name
    zone_id                = aws_cloudfront_distribution.catalog_assets.hosted_zone_id
    evaluate_target_health = false
  }
}
