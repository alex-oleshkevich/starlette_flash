import typing

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_flash.flash import FlashBag, FlashCategory, FlashMessage, flash, get_messages_for_template


class MarkedSession(dict[str, typing.Any]):
    def __init__(self) -> None:
        super().__init__()
        self.modified_calls = 0
        self.accessed_calls = 0

    def mark_modified(self) -> None:
        self.modified_calls += 1

    def mark_accessed(self) -> None:
        self.accessed_calls += 1


def test_flash_bag() -> None:
    messages: list[FlashMessage] = []
    bag = FlashBag(messages)
    bag.add("success", FlashCategory.SUCCESS)
    bag.success("success")
    bag.error("error")
    bag.warning("warning")
    bag.info("info")
    bag.debug("debug")
    assert len(bag) == 6
    assert bool(bag) is True

    bag.clear()
    assert len(bag) == 0
    assert bool(bag) is False


def test_flash_messages_by_category() -> None:
    bag = FlashBag([])
    bag.success("one")
    bag.error("two")

    assert bag.get_by_category(FlashCategory.SUCCESS) == [{"category": "success", "message": "one"}]
    assert len(bag.get_by_category(FlashCategory.SUCCESS)) == 0

    assert bag.get_by_category(FlashCategory.ERROR) == [{"category": "error", "message": "two"}]
    assert len(bag.get_by_category(FlashCategory.ERROR)) == 0


def test_returns_messages() -> None:
    bag = FlashBag(
        [
            {"category": "success", "message": "one"},
            {"category": "success", "message": "two"},
        ]
    )

    assert len(bag.all()) == 2
    assert len(bag) == 2


def test_consume() -> None:
    messages: list[FlashMessage] = [
        {"category": "success", "message": "one"},
        {"category": "success", "message": "two"},
    ]
    bag = FlashBag(messages)

    for _ in bag.consume():
        pass
    assert len(bag) == 0
    assert len(messages) == 0


def test_bag_is_iterable() -> None:
    bag = FlashBag(
        [
            {"category": "success", "message": "one"},
            {"category": "success", "message": "two"},
        ]
    )

    for _ in bag:
        pass
    assert len(bag) == 0


def test_fluent_chaining() -> None:
    bag = FlashBag([])
    assert bag.add("msg", FlashCategory.INFO) is bag
    result = bag.info("a").success("b").error("c").warning("d").debug("e")
    assert result is bag
    assert len(bag) == 6


def test_session_markers_are_used() -> None:
    session = MarkedSession()
    bag = FlashBag(session)

    bag.add("one", FlashCategory.INFO)
    assert session.modified_calls == 1

    assert bag.get_by_category(FlashCategory.INFO) == [{"category": "info", "message": "one"}]
    assert session.modified_calls == 2

    bag.success("two")
    assert session.modified_calls == 3

    assert bag.all() == [{"category": "success", "message": "two"}]
    assert session.accessed_calls == 1

    assert len(bag) == 1
    assert session.accessed_calls == 2

    assert bool(bag) is True
    assert session.accessed_calls == 4

    bag.clear()
    assert session.modified_calls == 4
    assert len(bag) == 0


def test_get_messages_for_template() -> None:
    def set_view(request: Request) -> JSONResponse:
        flash(request).success("hello")
        return JSONResponse({})

    def get_view(request: Request) -> JSONResponse:
        return JSONResponse({"messages": get_messages_for_template(request)})

    app = Starlette(
        routes=[Route("/set", set_view, methods=["post"]), Route("/get", get_view)],
        middleware=[Middleware(SessionMiddleware, secret_key="key", max_age=80000)],
    )
    client = TestClient(app)
    client.post("/set")
    response = client.get("/get")
    assert response.json()["messages"] == [{"category": "success", "message": "hello"}]
    response = client.get("/get")
    assert response.json()["messages"] == []


def test_starlette_integration() -> None:
    def set_view(request: Request) -> JSONResponse:
        flash(request).success("This is a message.")
        return JSONResponse({})

    def get_view(request: Request) -> JSONResponse:
        bag = flash(request)
        messages = [message for message in bag]
        return JSONResponse({"messages": messages})

    app = Starlette(
        routes=[Route("/set", set_view, methods=["get", "post"]), Route("/get", get_view)],
        middleware=[
            Middleware(SessionMiddleware, secret_key="key", max_age=80000),
        ],
    )
    client = TestClient(app)
    client.post("/set")

    response = client.get("/get")
    assert response.json()["messages"] == [{"category": "success", "message": "This is a message."}]

    # must be empty after reading messages
    response = client.get("/get")
    assert response.json()["messages"] == []
