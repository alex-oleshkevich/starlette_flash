from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.routing import Route

from starlette_flash import flash
from starlette_flash.flash import FlashBag

HTML = """
<div>{messages}</div>
<form method="post">
    <label>Enter message <input type="text" name="message"></label>
    <button type="submit">Submit</button>
</form>
"""


def generate_messages(bag: FlashBag) -> str:
    HTML = """
    <ul>{messages}</ul>
    """
    lines = []
    for message in bag:
        lines.append(
            "<li>{category}: {message}</li".format(
                category=message["category"],
                message=message["message"],
            )
        )
    return HTML.format(messages=",".join(lines))


async def index_view(request: Request) -> Response:
    messages = flash(request)

    if request.method == "POST":
        data = await request.form()
        messages.success(str(data["message"]))
        return RedirectResponse("/", 302)

    message_html = generate_messages(messages)
    return HTMLResponse(HTML.format(messages=message_html))


app = Starlette(
    debug=True,
    routes=[Route("/", index_view, methods=["get", "post"])],
    middleware=[Middleware(SessionMiddleware, secret_key="key!")],
)
