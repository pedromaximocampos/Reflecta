from src.modules.internal_events.application.ports.strategies.ibackoff_strategies import IBackoffStrategy
from src.modules.internal_events.infrastructure.strategies.exponential_retry import ExponentialRetry


def get_exponential_backoff_strategy() -> IBackoffStrategy:
    return ExponentialRetry()
