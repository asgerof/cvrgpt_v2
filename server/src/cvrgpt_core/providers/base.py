from abc import ABC, abstractmethod
from typing import List
from ..models import Company, Filing, Accounts, Event, EventFilter


class Provider(ABC):
    @abstractmethod
    def search_companies(self, q: str) -> List[Company]: ...
    @abstractmethod
    def get_company(self, cvr: str) -> Company: ...
    @abstractmethod
    def list_filings(self, cvr: str) -> List[Filing]: ...
    @abstractmethod
    def latest_accounts(self, cvr: str) -> Accounts: ...
    @abstractmethod
    def accounts_for_year(self, cvr: str, year: int) -> Accounts: ...


class EventsProvider(ABC):
    @abstractmethod
    def list_events(self, filters: EventFilter) -> List[Event]:
        """Return events across companies according to filters."""
        raise NotImplementedError
