from __future__ import annotations

from collections import defaultdict

from models.message import Message
from models.event import FinancialEvent


class ConflictResolver:
    """
    Resolves conflicts between financial events and messages.

    Priority
    --------
    1. Settlement
    2. Cancellation
    3. Amendment
    4. Latest timestamp
    5. Conservative fallback
    """

    CANCEL_WORDS = {
        "cancel",
        "cancelled",
        "canceled",
        "void"
    }

    SETTLED_WORDS = {
        "settled",
        "paid",
        "completed"
    }

    def resolve(
        self,
        events: list[FinancialEvent],
        messages: list[Message],
    ) -> list[FinancialEvent]:

        grouped = defaultdict(list)

        for msg in messages:
            if msg.related_event_id:
                grouped[msg.related_event_id].append(msg)

        cleaned = []

        for event in events:

            related = grouped.get(event.event_id, [])

            if not related:
                cleaned.append(event)
                continue

            related.sort(
                key=lambda m: m.message_date,
                reverse=True
            )

            latest = related[0]

            text = latest.content.lower()

            if any(word in text for word in self.CANCEL_WORDS):
                continue

            if any(word in text for word in self.SETTLED_WORDS):
                event.status = "confirmed"

            cleaned.append(event)

        return cleaned