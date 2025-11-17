

class UniqueViolation(Exception):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Unique constraint violated for {field} with value {value}")