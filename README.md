# Starlette-Flash

Flash messages for Starlette framework.

![PyPI](https://img.shields.io/pypi/v/starlette_flash)
![CI](https://img.shields.io/github/actions/workflow/status/alex-oleshkevich/starlette_flash/qa.yml)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starlette_flash)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starlette_flash)
![PyPI - Downloads](https://img.shields.io/pypi/dm/starlette_flash)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starlette_flash)

## Installation

Install `starlette_flash` using pip or uv:

```bash
pip install starlette_flash
# or
uv add starlette_flash
```

## Quick start

See example application in [examples/](examples/) directory of this repository.

## Setup

Flash messages are stored in the session. Add `SessionMiddleware` to your app:

```python
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

app = Starlette(
    middleware=[Middleware(SessionMiddleware, secret_key="your-secret-key")],
)
```

## Flashing messages

To flash a message use the `flash` helper.

```python
from starlette_flash import flash


def index_view(request):
    flash(request).add('This is a message.', 'success')
```

### Using helpers

Shorthand helpers that set the category automatically:

- success
- error
- info
- warning
- debug

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('Saved.')
    flash(request).error('Something went wrong.')
    flash(request).info('Did you know?')
    flash(request).warning('Proceed with caution.')
    flash(request).debug('Value was 42.')
```

Helpers return `self`, so calls can be chained:

```python
flash(request).info('Step 1 done.').success('All steps complete.')
```

## Reading messages

To get all flash messages without removing them from the session, use `all()`:

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    messages = flash(request).all()
    print(messages)  # [{'category': 'success', 'message': 'This is a message.'}]
```

## Consuming messages

`consume()` returns all messages and clears the bag in one call:

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    messages = flash(request).consume()
    print(messages)  # [{'category': 'success', 'message': 'This is a message.'}]
    print(flash(request).all())  # [], messages have been consumed
```

Iterating the bag also consumes messages:

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    for message in flash(request):
        print(message)
    print(flash(request).all())  # [], messages have been consumed
```

## Template integration

`get_messages_for_template` is a convenience function that consumes and returns all messages,
suitable for use in Jinja2 globals or context processors:

```python
from starlette_flash import get_messages_for_template

templates.env.globals['get_flashed_messages'] = get_messages_for_template
```

Then in your template:

```jinja2
{% for message in get_flashed_messages(request) %}
    <div class="alert alert-{{ message.category }}">{{ message.message }}</div>
{% endfor %}
```
