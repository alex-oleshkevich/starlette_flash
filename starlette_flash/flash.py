from __future__ import annotations

import typing

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


class FlashBag:
    def __init__(self, messages: list[FlashMessage]):
        self._messages = messages

    def add(self, message: str, category: str) -> FlashBag:
        self._messages.append({"category": category, "message": str(message)})
        return self

    def get_by_category(self, category: FlashCategory | str) -> list[FlashMessage]:
        messages = [message for message in self._messages if message["category"] == category]
        self._messages = [message for message in self._messages if message["category"] != category]
        return messages

    def debug(self, message: str) -> FlashBag:
        self.add(message, FlashCategory.DEBUG)
        return self

    def info(self, message: str) -> FlashBag:
        self.add(message, FlashCategory.INFO)
        return self

    def success(self, message: str) -> FlashBag:
        self.add(message, FlashCategory.SUCCESS)
        return self

    def warning(self, message: str) -> FlashBag:
        self.add(message, FlashCategory.WARNING)
        return self

    def error(self, message: str) -> FlashBag:
        self.add(message, FlashCategory.ERROR)
        return self

    def all(self) -> list[FlashMessage]:
        return self._messages

    def consume(self) -> list[FlashMessage]:
        """Return all messages and empty the bag."""
        messages = self._messages.copy()
        self._messages.clear()
        return messages

    def clear(self) -> None:
        self._messages.clear()

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> typing.Iterator[FlashMessage]:
        return iter(self.consume())

    def __bool__(self) -> bool:
        return len(self) > 0


def flash(request: Request) -> FlashBag:
    """Get flash messages bag."""
    request.session.setdefault("flash_messages", [])
    return FlashBag(request.session["flash_messages"])


def get_messages_for_template(request: Request) -> list[FlashMessage]:
    """Consume and return all flash messages, suitable for template context processors."""
    return flash(request).consume()
