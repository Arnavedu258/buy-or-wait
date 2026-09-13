from pydantic import BaseModel

from .profile import Profile
from .event import FinancialEvent
from .message import Message
from .payment import PaymentOption
from .image_ref import ImageReference


class FinancialState(BaseModel):
    """
    Complete financial snapshot of one user.
    This object is passed to the Forecast Engine.
    """

    profile: Profile

    events: list[FinancialEvent]

    messages: list[Message]

    payment_options: list[PaymentOption]

    images: list[ImageReference]