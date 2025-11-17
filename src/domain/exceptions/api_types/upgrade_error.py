

class UpgradeRequired(Exception):
    """Exception raised when an upgrade is required."""

    def __init__(self, message="E necessario uma atualizacao para acessar o gas monitor"):
        super().__init__()
        self.message = message
        self.status_code = 426
        self.name = "Upgrade Required"
