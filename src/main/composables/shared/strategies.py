from src.application.ports.strategies.ibackoff_strategies import IBackoffStrategy
from src.infra.strategies.exponential_retry import ExponentialRetry


def get_exponential_backoff_strategy() -> IBackoffStrategy:
    return ExponentialRetry()
