from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RabbitMQConsumerConfig:
    url: str

    queue_name: str
    exchange_name: str
    routing_key: str

    retry_queue_name: str
    retry_routing_key: str

    dlx_queue_name: str
    dlx_routing_key: str
    dlx_exchange: str

    max_retries: int
    
    frontend_base_url: str

    ssl: bool = False


@dataclass(frozen=True, slots=True)
class RabbitMQPublisherConfig:
    url: str

    exchange_name: str
    routing_key: str
    queue_name: str

    frontend_base_url: str