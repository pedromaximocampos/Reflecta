from datetime import datetime, timedelta, timezone

import pytest

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.value_objects.event_type import EventType
from src.modules.internal_events.domain.value_objects.outbox_status import OutboxStatus
from src.modules.internal_events.infrastructure.messaging.routing.event_router import EventRouter
from src.modules.internal_events.infrastructure.messaging.workers.outbox_dispatcher_worker import OutboxDispatcherWorker


class PublisherFake:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False
        self.published: list[OutboxEvent] = []

    async def start(self) -> None:
        self.started = True

    async def publish(self, event: OutboxEvent) -> None:
        self.published.append(event)

    def sync_publish(self, event: OutboxEvent) -> None:
        self.published.append(event)

    async def stop(self) -> None:
        self.stopped = True


class OutboxRepositoryFake:
    def __init__(self, events: list[OutboxEvent]) -> None:
        self.events = events
        self.sent: list[OutboxEvent] = []
        self.failed: list[OutboxEvent] = []

    async def claim_pending(self, batch_limit: int, attempts_limit: int) -> list[OutboxEvent]:
        return self.events[:batch_limit]

    async def mark_sent(self, event: OutboxEvent) -> None:
        self.sent.append(event)

    async def mark_failed(self, event: OutboxEvent) -> None:
        self.failed.append(event)


class UnitOfWorkFake:
    def __init__(self, repository: OutboxRepositoryFake) -> None:
        self.outbox_repository = repository
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def commit(self) -> None:
        self.commits += 1


class ClockFake:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class BackoffFake:
    def next_delay_in_seconds(self, attempts: int) -> timedelta:
        return timedelta(seconds=5)


@pytest.mark.asyncio
async def test_event_router_uses_specific_rabbitmq_publisher_for_each_event() -> None:
    verification_publisher = PublisherFake()
    password_reset_publisher = PublisherFake()
    router = EventRouter({
        "emails.verification.requested": verification_publisher,
        "emails.password_reset.requested": password_reset_publisher,
    })

    await router.start()

    assert router.resolve_publisher(EventType("emails.verification.requested")) is verification_publisher
    assert router.resolve_publisher(EventType("emails.password_reset.requested")) is password_reset_publisher
    assert verification_publisher.started is True
    assert password_reset_publisher.started is True

    await router.stop()

    assert verification_publisher.stopped is True
    assert password_reset_publisher.stopped is True


@pytest.mark.asyncio
async def test_dispatch_once_publishes_event_and_marks_it_as_sent() -> None:
    now = datetime(2026, 8, 30, tzinfo=timezone.utc)
    event = OutboxEvent(
        id="01K00000000000000000000000",
        event_type=EventType("emails.verification.requested"),
        payload={"user_email": "user@example.com", "raw_code": "code"},
        event_occurred_at=now,
        created_at=now,
    )
    publisher = PublisherFake()
    repository = OutboxRepositoryFake([event])
    unit_of_work = UnitOfWorkFake(repository)
    worker = OutboxDispatcherWorker(
        event_router=EventRouter({event.event_type.value: publisher}),
        uow=unit_of_work,
        batch_limit=10,
        attempts_limit=5,
        system_clock=ClockFake(now),
        backoff_strategy=BackoffFake(),
    )

    dispatched = await worker.dispatch_once()

    assert dispatched == 1
    assert publisher.published == [event]
    assert repository.sent == [event]
    assert repository.failed == []
    assert event.status is OutboxStatus.SENT
    assert event.sent_at == now
    assert unit_of_work.commits == 2
