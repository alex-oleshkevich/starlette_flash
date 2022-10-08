import jinja2
import os.path
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from starlette_flash import flash

this_dir = os.path.abspath(os.path.dirname(__file__))
templates = Jinja2Templates(
    os.path.join(this_dir, "templates"),
    loader=jinja2.ChoiceLoader(
        [
            jinja2.PackageLoader(__name__),
            jinja2.PackageLoader("starlette_flash"),
        ]
    ),
)


async def index_view(request: Request) -> Response:
    messages = flash(request)

    if request.method == "POST":
        data = await request.form()
        messages.add(str(data["message"]), str(data["category"]))
        return RedirectResponse("/", 302)

    return templates.TemplateResponse("index.html", {"request": request, "flash_messages": messages})


app = Starlette(
    debug=True,
    routes=[Route("/", index_view, methods=["get", "post"])],
    middleware=[Middleware(SessionMiddleware, secret_key="key!")],
)
