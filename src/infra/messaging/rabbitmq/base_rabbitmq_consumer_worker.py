from abc import ABC, abstractmethod
import aio_pika
import json


class BaseRabbitMQConsumerWorker(ABC):

    def __init__(self, rabbitmq_url: str, queue_name: str):
        self.__rabbitmq_url = rabbitmq_url
        self.__queue_name = queue_name


    async def start(self):
        connection = await aio_pika.connect_robust(self.__rabbitmq_url)

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(self.__queue_name, durable=True)


            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body)
                        await self.handle_message(payload)


    @abstractmethod
    async def handle_message(self, payload: dict):
        pass