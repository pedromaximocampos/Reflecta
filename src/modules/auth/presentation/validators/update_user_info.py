from datetime import date

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class UpdateUserInfoValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=200)
    surname: str | None = Field(default=None, max_length=200)
    date_of_birth: date | None = None
    avatar_url: AnyHttpUrl | None = None

    @field_validator("name", "surname")
    @classmethod
    def validate_person_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("O campo não pode ser vazio.")
        return normalized

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is not None and value >= date.today():
            raise ValueError("Data de nascimento deve ser no passado.")
        return value

    @model_validator(mode="after")
    def validate_partial_update(self):
        if not self.model_fields_set:
            raise ValueError("Informe ao menos um campo para atualização.")

        null_fields = [
            field_name
            for field_name in self.model_fields_set
            if getattr(self, field_name) is None
        ]
        if null_fields:
            raise ValueError(
                "Campos enviados não podem ser nulos: " + ", ".join(sorted(null_fields))
            )
        return self


class UpdateUserInfoResponseValidator(BaseModel):
    user_id: str
    name: str
    surname: str
    date_of_birth: date
    avatar_url: str | None = None
