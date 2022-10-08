# Starlette-Flash

Flash messages for Starlette framework.

![PyPI](https://img.shields.io/pypi/v/starlette_flash)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/starlette_flash/Lint)
![GitHub](https://img.shields.io/github/license/alex-oleshkevich/starlette_flash)
![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/starlette_flash)
![PyPI - Downloads](https://img.shields.io/pypi/dm/starlette_flash)
![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/starlette_flash)

## Installation

Install `starlette_flash` using PIP or poetry:

```bash
pip install starlette_flash
# or
poetry add starlette_flash
```

## Quick start

See example application in [examples/](examples/) directory of this repository.

## Setup

You must install SessionMiddleware to use flash messages.

## Flashing messages

To flash a message use `flash` helper.

```python
from starlette_flash import flash


def index_view(request):
    flash(request).add('This is a message.', 'success')

```

### Using helpers

There are several predefined helpers exists which automatically set the category:

- success
- error
- info
- debug

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')
    flash(request).error('This is a message.')
    flash(request).info('This is a message.')
    flash(request).debug('This is a message.')

```

## Reading messages

To get current flash messages without removing them from session, use `all` method:

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    messages = flash(request).all()
    print(messages)  # {'category': 'success', 'message': 'This is a message.'}

```

## Consuming messages

You can read messages one by one and then clear the storage by using `consume` method.

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    messages = []
    for message in flash(request).consume():
        messages.append(message)
    print(messages)  # {'category': 'success', 'message': 'This is a message.'}
    print(flash(request).all())  # empty, messages has been consumed

```

You can iterate the flash bag to consume messages as well:

```python
from starlette_flash import flash


def index_view(request):
    flash(request).success('This is a message.')

    messages = []
    for message in flash(request):
        messages.append(message)
    print(messages)  # {'category': 'success', 'message': 'This is a message.'}
    print(flash(request).all())  # empty, messages has been consumed

```
