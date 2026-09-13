from .loader import DatasetLoader


class BaseRepository:

    def __init__(self, loader: DatasetLoader | None = None):
        self.loader = loader or DatasetLoader()


class ProfileRepository(BaseRepository):

    def all(self):
        return self.loader.load("financial_profiles.csv")


class RequestRepository(BaseRepository):

    def all(self):
        return self.loader.load("requests.csv")


class EventRepository(BaseRepository):

    def all(self):
        return self.loader.load("financial_events.csv")


class MessageRepository(BaseRepository):

    def all(self):
        return self.loader.load("messages.csv")


class ImageRepository(BaseRepository):

    def all(self):
        return self.loader.load("images.csv")


class PaymentRepository(BaseRepository):

    def all(self):
        return self.loader.load("request_payment_options.csv")


class ExchangeRepository(BaseRepository):

    def all(self):
        return self.loader.load("exchange_rates.csv")