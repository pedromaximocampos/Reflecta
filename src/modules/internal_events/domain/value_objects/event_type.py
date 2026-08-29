from dataclasses import dataclass


@dataclass(frozen=True)
class EventType:
    value: str

    def __post_init__(self):
        v = self.value.strip()
        if not v:
            raise ValueError("EventName cannot be empty")
        if "." not in v:
            raise ValueError("EventName must be '<domain>.<use-case>.<action>'. Ex.: emails.send_email.requested")

        object.__setattr__(self, "value", v)

    @property
    def domain(self) -> str:
        return self.value.split(".", 1)[0]