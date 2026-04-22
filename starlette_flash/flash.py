import typing
from typing import TypeGuard

from starlette.requests import Request


class FlashCategory:
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class FlashMessage(typing.TypedDict):
    category: str
    message: str


class SessionMarkers(typing.Protocol):
    def mark_modified(self) -> None: ...
    def mark_accessed(self) -> None: ...


class SessionStorage(typing.Protocol):
    def __getitem__(self, key: str) -> typing.Any: ...
    def __setitem__(self, key: str, value: typing.Any) -> None: ...
    def setdefault(self, key: str, default: list[FlashMessage]) -> list[FlashMessage]: ...


class MarkedSession(SessionStorage, SessionMarkers, typing.Protocol):
    pass


def has_session_markers(session: SessionStorage) -> TypeGuard[MarkedSession]:
    return hasattr(session, "mark_modified") and hasattr(session, "mark_accessed")


class FlashBag:
    def __init__(
        self,
        session: list[FlashMessage] | dict[str, typing.Any] | None = None,
        key: str = "flash_messages",
    ):
        self._key = key
        self._session: SessionStorage = session if isinstance(session, dict) else {}
        self._session.setdefault(key, session if isinstance(session, list) else [])

    @property
    def _messages(self) -> list[FlashMessage]:
        return typing.cast(list[FlashMessage], self._session[self._key])

    @_messages.setter
    def _messages(self, value: list[FlashMessage]) -> None:
        self._session[self._key] = value

    def add(self, message: str, category: str) -> "FlashBag":
        if has_session_markers(self._session):
            self._session.mark_modified()
        self._messages.append({"category": category, "message": str(message)})
        return self

    def get_by_category(self, category: FlashCategory | str) -> list[FlashMessage]:
        if has_session_markers(self._session):
            self._session.mark_modified()
        messages = [message for message in self._messages if message["category"] == category]
        self._messages = [message for message in self._messages if message["category"] != category]
        return messages

    def debug(self, message: str) -> "FlashBag":
        self.add(message, FlashCategory.DEBUG)
        return self

    def info(self, message: str) -> "FlashBag":
        self.add(message, FlashCategory.INFO)
        return self

    def success(self, message: str) -> "FlashBag":
        self.add(message, FlashCategory.SUCCESS)
        return self

    def warning(self, message: str) -> "FlashBag":
        self.add(message, FlashCategory.WARNING)
        return self

    def error(self, message: str) -> "FlashBag":
        self.add(message, FlashCategory.ERROR)
        return self

    def all(self) -> list[FlashMessage]:
        if has_session_markers(self._session):
            self._session.mark_accessed()
        return self._messages.copy()

    def consume(self) -> list[FlashMessage]:
        """Return all messages and empty the bag."""
        messages = self._messages.copy()
        self.clear()
        return messages

    def clear(self) -> None:
        if has_session_markers(self._session):
            self._session.mark_modified()
        self._messages.clear()

    def __len__(self) -> int:
        if has_session_markers(self._session):
            self._session.mark_accessed()
        return len(self._messages)

    def __iter__(self) -> typing.Iterator[FlashMessage]:
        return iter(self.consume())

    def __bool__(self) -> bool:
        if has_session_markers(self._session):
            self._session.mark_accessed()
        return len(self) > 0


def flash(request: Request) -> FlashBag:
    """Get flash messages bag."""
    return FlashBag(request.session)


def get_messages_for_template(request: Request) -> list[FlashMessage]:
    """Consume and return all flash messages, suitable for template context processors."""
    return flash(request).consume()
