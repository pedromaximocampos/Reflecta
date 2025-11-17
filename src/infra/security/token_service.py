from src.domain.ports.security.itoken_service import ITokenService
import jwt

import uuid
from datetime import datetime, timezone, timedelta

from hashlib import sha256

class TokenServiceImpl(ITokenService):


    def generate_token(self, user_id: str, expires_in_seconds: int) -> str:
        salt = self.get_salt_token(subject)

        payload = {
            "sub": subject,
            "jti": salt,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=expires_in),
            "iss": "gmon-service",
        }
        token = jwt.encode(payload, self._jwt_secret, algorithm="HS256")

        return token

    def validate_token(self, token: str) -> str:
        try:
            return jwt.decode(
                token,
                self._jwt_secret,
                algorithms=["HS256"],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "sub", "jti", "iss"]
                }
            )

        except Exception as e:
            raise e

    def __init__(self, jwt_secret: str) -> None:
        self._jwt_secret = jwt_secret


    @classmethod
    def get_salt_token(cls, subject: str) -> str:
        """Gera um salt único para o token."""
        unique_id = str(uuid.uuid4())
        timestamp = str(int(datetime.now(timezone.utc).timestamp()))

        unique_id = sha256(
            f"{subject}:{unique_id}:{timestamp}:".encode()
        ).hexdigest()

        return unique_id