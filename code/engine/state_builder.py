from __future__ import annotations

import polars as pl

from models.profile import Profile
from models.event import FinancialEvent
from models.message import Message
from models.payment import PaymentOption
from models.image_ref import ImageReference
from models.state import FinancialState


class FinancialStateBuilder:
    """
    Converts Polars DataFrames into a FinancialState object.
    Factory Pattern implementation.
    """

    @staticmethod
    def _profile(df: pl.DataFrame) -> Profile:
        records = df.to_dicts()

        if len(records) != 1:
            raise ValueError(
                "FinancialState requires exactly one user profile."
            )

        return Profile(**records[0])

    @staticmethod
    def _events(df: pl.DataFrame) -> list[FinancialEvent]:
        return [FinancialEvent(**row) for row in df.to_dicts()]

    @staticmethod
    def _messages(df: pl.DataFrame) -> list[Message]:
        return [Message(**row) for row in df.to_dicts()]

    @staticmethod
    def _payments(df: pl.DataFrame) -> list[PaymentOption]:
        return [PaymentOption(**row) for row in df.to_dicts()]

    @staticmethod
    def _images(df: pl.DataFrame) -> list[ImageReference]:
        return [ImageReference(**row) for row in df.to_dicts()]

    def build(
        self,
        profile_df: pl.DataFrame,
        event_df: pl.DataFrame,
        message_df: pl.DataFrame,
        payment_df: pl.DataFrame,
        image_df: pl.DataFrame,
    ) -> FinancialState:

        return FinancialState(
            profile=self._profile(profile_df),
            events=self._events(event_df),
            messages=self._messages(message_df),
            payment_options=self._payments(payment_df),
            images=self._images(image_df),
        )