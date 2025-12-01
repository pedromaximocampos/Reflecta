from datetime import date
from pydantic import BaseModel, EmailStr, field_validator, model_validator

class SignUpValidator(BaseModel):
    email: EmailStr
    username: str
    name: str
    surname: str
    date_of_birth: date
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username deve ter pelo menos 3 caracteres.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome não pode ser vazio.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres.")
        # se quiser, checks extras: número, letra maiúscula, etc.
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        today = date.today()
        if v >= today:
            raise ValueError("Data de nascimento deve ser no passado.")
        # se quiser regra de idade mínima, pode colocar aqui ou no domínio
        return v

    @model_validator(mode="after")
    def check_password_match(self):
        if self.password != self.password_confirm:
            raise ValueError("As senhas não conferem.")
        return self