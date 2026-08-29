from datetime import timedelta
from typing import Protocol



class IBackoffStrategy(Protocol):


    def next_delay_in_seconds(self, attempts: int) ->  timedelta:
       """
       Strategy para ser injetados em workers (principalmente mensageria) para lidar com delays de retry quando uma
       mensagem possivelmente falha
       :param attempts: numero de tentativas utilizado para calcular o delay
       :return: timedelta em segundos para ser adicionado
       """
       ...