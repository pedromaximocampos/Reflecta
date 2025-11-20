from dataclasses import dataclass



@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self):
        v = self.value.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError(f"Invalid email format: {self.value}")
        object.__setattr__(self, "value", v)