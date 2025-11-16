import ulid



class ULIDGenerator:


    @staticmethod
    def generate_ulid() -> str:
        """Generate a new ULID and return it as a string."""
        return str(ulid.new())