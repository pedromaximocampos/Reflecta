import uuid
import jwt

from datetime import datetime, timedelta
from typing import Any
from src.modules.auth.application.ports.token.dto import GeneratedTokenDTO
from src.domain.exceptions.api_types import AuthError
from src.modules.auth.public.password_algorithm import PasswordAlgorithm
from src.modules.auth.application.ports.token.itoken_service import ITokenService
from src.modules.auth.domain.value_objects.token_jti import TokenJti
from src.modules.auth.public.user_id import UserId


class TokenServiceImpl(ITokenService):
    def __init__(self, jwt_secret: str, issuer: str = "individuum-api", algorithm = PasswordAlgorithm.HS256 ) -> None:
        self._jwt_secret = jwt_secret
        self._issuer = issuer
        self._algorithm = algorithm

    def generate_token(self, user_id: UserId, expires_in_seconds: int, now: datetime) -> GeneratedTokenDTO:
        jti = self._generate_jti()

        expiration = now + timedelta(seconds=expires_in_seconds)

        payload = {
            "sub": user_id.value,
            "jti": jti.value,
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
    def _generate_jti() -> TokenJti:
        return TokenJti(str(uuid.uuid4()))