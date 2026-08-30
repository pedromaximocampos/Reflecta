from typing import Protocol


class IHasherGenerator(Protocol):
    """Contrato para geração e verificação de hashes."""

    def generate_hash(self, plain_text: str) -> str:
        """Gera um hash a partir do texto simples fornecido."""
        raise NotImplementedError

    def verify_hash(self, plain_text: str, hashed_text: str) -> bool:
        """Verifica se o texto simples corresponde ao hash fornecido."""
        raise NotImplementedError