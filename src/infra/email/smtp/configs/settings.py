from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SMTPSettings:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    frontend_domain: str
    app_name: str

    @property
    def from_address(self) -> str:
        return f"{self.app_name} <no-reply@{self.frontend_domain}>"