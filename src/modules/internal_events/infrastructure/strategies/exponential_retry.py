from datetime import timedelta

from src.modules.internal_events.application.ports.strategies.ibackoff_strategies import IBackoffStrategy


class ExponentialRetry(IBackoffStrategy):


    def next_delay_in_seconds(self, attempts: int) ->  timedelta:
        time_int = min(300, 2 **attempts * 5)
        return timedelta(seconds=time_int)