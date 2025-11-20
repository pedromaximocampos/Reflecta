from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.value_objects.password_algorithm import PasswordAlgorithm
from hashlib import sha256

class JTIHasher(IHasherGenerator):

    def __init__(self, algorithm: str = PasswordAlgorithm.HS256):
        self.algorithm = algorithm

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        return self.generate_hash(plain_text) == hashed_text

    def generate_hash(self, plain_text: str) -> str:
        return sha256(plain_text.encode()).hexdigest()