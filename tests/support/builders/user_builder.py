from src.domain.entities.user import User, AuthCredentials
from src.domain.value_objects.email import Email
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.value_objects.user_id import UserId
from datetime import datetime, timezone
from tests.support.utils.id_utils import new_id

class UserBuilder:
    def __init__(self):
        self._id = UserId(new_id())
        self._email = Email("user@example.com")
        self._name = "John"
        self._surname = "Doe"
        self._username = "johndoe"
        self._date_of_birth = datetime(2000, 1, 1).date()
        self._avatar_url = None
        self._is_email_verified = True
        self._password_hash = PasswordHash(
            algorithm=PasswordAlgorithm("argon2"),
            hash="hashed_password",
            version=1,
        )
        self._created_at = datetime.now()
        self._last_login_at = None

    def with_email(self, email_str):
        self._email = Email(email_str)
        return self

    def unverified(self):
        self._is_email_verified = False
        return self

    def with_password_hash(self, pw_hash: PasswordHash):
        self._password_hash = pw_hash
        return self

    def with_id(self, id_str):
        self._id = UserId(id_str)
        return self

    def build(self):
        auth = AuthCredentials(password=self._password_hash, user_id=self._id, created_at=datetime.now(timezone.utc))
        return User(
            id=self._id,
            email=self._email,
            name=self._name,
            date_of_birth=self._date_of_birth,
            surname=self._surname,
            username=self._username,
            avatar_url=self._avatar_url,
            is_email_verified=self._is_email_verified,
            auth_credentials=auth,
            last_login_at=self._last_login_at,
            created_at=self._created_at,
        )
