import base64
import hashlib
import hmac


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def recoverable_share_token(share_id: str, secret: str) -> str:
    """Derive an owner-recoverable bearer token without persisting it in clear text."""
    if not secret:
        raise ValueError("A share token secret is required.")
    digest = hmac.new(
        secret.encode(),
        f"reflecta:context-share:{share_id}".encode(),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

