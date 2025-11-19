import uuid
import jwt
from hashlib import sha256
from datetime import datetime, timedelta
from typing import Any
from src.application.services.token.dto import GeneratedTokenDTO
from src.domain.exceptions.api_types import AuthError
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from src.application.services.token.itoken_service import ITokenService


class TokenServiceImpl(ITokenService):
    def __init__(self, jwt_secret: str, issuer: str = "individuum-api", algorithm = PasswordAlgorithm.HS256 ) -> None:
        self._jwt_secret = jwt_secret
        self._issuer = issuer
        self._algorithm = algorithm

    def generate_token(self, user_id: str, expires_in_seconds: int, now: datetime) -> GeneratedTokenDTO:
        jti = self._generate_jti()

        expiration = now + timedelta(seconds=expires_in_seconds)

        payload = {
            "sub": user_id,
            "jti": jti,
            "iat": now,
            "exp": expiration,
            "iss": self._issuer,
        }


        token = jwt.encode(payload, self._jwt_secret, algorithm=self._algorithm)
        return GeneratedTokenDTO(
            token=token,
            jti=jti,
            expires_at=expiration,
        )

    def validate_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self._jwt_secret,
                algorithms=self._algorithm,
                issuer=self._issuer,
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["exp", "iat", "sub", "jti", "iss"],
                },
            )
            return payload
        except jwt.PyJWTError as e:
            raise AuthError("Credenciais invalidas") from e

    @staticmethod
    def _generate_jti() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def hash_jti(jti: str) -> str:
        return sha256(jti.encode()).hexdigest()
