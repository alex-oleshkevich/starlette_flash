from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_flash.flash import FlashBag, FlashCategory, FlashMessage, flash


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
