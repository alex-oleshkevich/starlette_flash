import logging
import typing
from starlette.requests import Request

logger = logging.getLogger(__name__)


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

    def add(self, message: str, category: str) -> None:
        self._messages.append({"category": category, "message": str(message)})

    def get_by_category(self, category: FlashCategory | str) -> list[FlashMessage]:
        messages = [message for message in self._messages if message["category"] == category]
        self._messages = [message for message in self._messages if message["category"] != category]
        return messages

    def debug(self, message: str) -> None:
        self.add(message, FlashCategory.DEBUG)

    def info(self, message: str) -> None:
        self.add(message, FlashCategory.INFO)

    def success(self, message: str) -> None:
        self.add(message, FlashCategory.SUCCESS)

    def warning(self, message: str) -> None:
        self.add(message, FlashCategory.WARNING)

    def error(self, message: str) -> None:
        self.add(message, FlashCategory.ERROR)

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


def flash_processor(request: Request) -> dict[str, typing.Any]:
    """Flash message template context processor."""
    return {"flash_messages": flash(request)}
