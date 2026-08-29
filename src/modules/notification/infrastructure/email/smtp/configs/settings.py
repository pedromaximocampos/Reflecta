from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SMTPSettings:
    server: str
    port: int
    username: str
    password: str
    frontend_domain: str
    app_name: str
    use_ssl: bool

    @property
    def from_address(self) -> str:
        return f"individuum.mvp.app.adm@gmail.com"