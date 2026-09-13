from __future__ import annotations

import json
import logging
import logging.handlers
import queue
import sys
import threading
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path

# ==========================================================
# Context Variables (Thread Safe)
# ==========================================================

TRACE_ID: ContextVar[str] = ContextVar(
    "trace_id",
    default="-",
)

REQUEST_ID: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


# ==========================================================
# Correlation Context
# ==========================================================

class LogContext:

    @staticmethod
    def new_trace() -> str:
        trace = uuid.uuid4().hex[:16]
        TRACE_ID.set(trace)
        return trace

    @staticmethod
    def set_request(request_id: str):
        REQUEST_ID.set(request_id)

    @staticmethod
    def trace() -> str:
        return TRACE_ID.get()

    @staticmethod
    def request() -> str:
        return REQUEST_ID.get()


# ==========================================================
# JSON Formatter
# ==========================================================

class JsonFormatter(logging.Formatter):

    def format(self, record):

        payload = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),

            "level": record.levelname,

            "service": record.name,

            "thread": threading.current_thread().name,

            "trace_id": LogContext.trace(),

            "request_id": LogContext.request(),

            "message": record.getMessage(),
        }

        if hasattr(record, "latency_ms"):
            payload["latency_ms"] = record.latency_ms

        if hasattr(record, "confidence"):
            payload["confidence"] = record.confidence

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


# ==========================================================
# Logger Factory
# ==========================================================

class LoggerFactory:

    _configured = False

    _queue: queue.Queue = queue.Queue(-1)

    _listener = None

    @classmethod
    def create(cls, name: str):

        logger = logging.getLogger(name)

        if cls._configured:
            return logger

        logger.setLevel(logging.INFO)

        logs = Path("logs")

        logs.mkdir(exist_ok=True)

        file_handler = (
            logging.handlers.RotatingFileHandler(
                logs / "application.log",
                maxBytes=5_000_000,
                backupCount=5,
                encoding="utf-8",
            )
        )

        file_handler.setFormatter(JsonFormatter())

        console = logging.StreamHandler(sys.stdout)

        console.setFormatter(JsonFormatter())

        queue_handler = logging.handlers.QueueHandler(
            cls._queue
        )

        logger.addHandler(queue_handler)

        cls._listener = logging.handlers.QueueListener(
            cls._queue,
            file_handler,
            console,
            respect_handler_level=True,
        )

        cls._listener.start()

        cls._configured = True

        return logger


# ==========================================================
# Public API
# ==========================================================

def get_logger(name: str):
    return LoggerFactory.create(name)