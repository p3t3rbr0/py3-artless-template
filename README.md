# artless-template

![Build Status](https://github.com/p3t3rbr0/py3-artless-template/actions/workflows/ci.yaml/badge.svg?branch=master)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/artless-template)
![PyPI Version](https://img.shields.io/pypi/v/artless-template)
[![Code Coverage](https://codecov.io/gh/p3t3rbr0/py3-artless-template/graph/badge.svg?token=S9JIKQL126)](https://codecov.io/gh/p3t3rbr0/py3-artless-template)
[![Maintainability](https://api.codeclimate.com/v1/badges/1002f19a39551c8fbb42/maintainability)](https://codeclimate.com/github/p3t3rbr0/py3-artless-template/maintainability)

Artless and small template library for server-side rendering.

Artless-template allows to generate HTML, using template files or/and natively Python objects. The library encourages approaches like HTMX and No-JS.

**Features**:
* Small and simple code base (less than 200 LOC).
* No third party dependencies (standart library only).

**Table of Contents**:
* [Install](#install)
* [Usage](#usage)
  * [Template and tags usage](#usage-tags)
  * [Template and components usage](#usage-components)
* [Performance](#performance)
* [Rodmap](#roadmap)

<a id="install"></a>
## Install

``` shellsession
$ pip install artless-template
```

<a id="usage"></a>
## Usage

Basically, you can create any tag with any name, attributes, text and child tags:

``` python
from artless_template import Tag as t

div = t("div")
print(div)
<div></div>

div = t("div", attrs={"class": "some-class"}, text="Some text")
print(div)
<div class="some-class">Some text</div>

div = t(
    "div",
    attrs={"class": "some-class"},
    text="Div text",
    children=[t(span, text="Span 1 text"), t(span, text="Span 2 text")]
)
print(div)
<div class="some-class"><span>Span 1 text</span><span>Span 2 text</span>Div text</div>

button = t("button", attrs={"onclick": "function() {alert('hello');}"}, text="Say Hello")
print(button)
<button onclick="function() {alert('hello');}">Say Hello</button>
```

<a id="usage-tags"></a>
### Template and tags usage

Create `templates/index.html` with contents:

``` html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>@title</title>
  </head>
  <body>
    <main>
        <section>
            <h1>@header</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                @users
            </table>
        </section>
    </main>
  </body>
</html>
```

``` python
from typing import final
from pathlib import Path
from random import randint
from dataclasses import dataclass
from artless_template import read_template, Tag as t

TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"

@final
@dataclass(frozen=True, slots=True, kw_only=True)
class UserModel:
    name: str
    email: str
    is_admin: bool


users = [
    UserModel(
        name=f"User_{_}", email=f"user_{_}@gmail.com", is_admin=bool(randint(0, 1))
    )
    for _ in range(10_000)
]


users_markup = t(
    "tbody",
    children=[
        t(
            "tr",
            children=[
                t("td", text=user.name),
                t("td", text=user.email),
                t("td", text="+" if user.is_admin else "-"),
            ],
        )
        for user in users
    ],
)

context = {
    "title": "Artless-template example",
    "header": "Users list",
    "users": users_markup,
}

template = read_template(TEMPLATES_DIR / "index.html").render(**context)
```

<a id="usage-components"></a>
### Template and components usage

``` html
<!DOCTYPE html>
<html lang="en">
  ...
  <body>
    <main>
      @main
    </main>
  </body>
</html>
```

``` python
from artless_template import read_template, Component, Tag as t

...

class UsersTableComponent:
    def __init__(self, count: int):
        self.users = [
            UserModel(
                name=f"User_{_}", email=f"user_{_}@gmail.com", is_admin=bool(randint(0, 1))
            )
            for _ in range(count)
        ]

    def view(self):
        return t(
            "table",
            children=[
                t(
                    "thead",
                    children=[
                        t(
                            "tr",
                            children=[
                                t("th", text="Name"),
                                t("th", text="Email"),
                                t("th", text="Admin"),
                            ]
                        )
                    ]
                ),
                t(
                    "tbody",
                    children=[
                        t(
                            "tr",
                            children=[
                                t("td", text=user.name),
                                t("td", text=user.email),
                                t("td", text="+" if user.is_admin else "-"),
                            ],
                        )
                        for user in self.users
                    ]
                )
            ]
        )

template = read_template(TEMPLATES_DIR / "index.html").render(main=UsersTableComponent(100500))
```

<a id="performance"></a>
## Performance

Performance comparison of the most popular template engines and artless-template library.
The benchmark render a HTML document with table of 10 thousand user models.

Run benchmark:

``` shellsession
$ python -m bemchmarks
```

Sorted results on i5 laptop (smaller is better):

``` python
{'mako': 0.009, 'jinja': 0.029, 'artless': 0.048, 'dtl': 0.157}
```

1. [Mako](https://www.makotemplates.org/) (0.009 sec.)
2. [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) (0.029 sec.)
3. **Artless-template (0.048 sec.)**
4. [Django templates](https://docs.djangoproject.com/en/5.0/ref/templates/) (0.157 sec.)

The performance of `artless-template` is better than the `Django template engine`, but worse than `Jinja2` and `Mako`.

<a id="roadmap"></a>
## Roadmap

- [x] Simplify the Tag constructor.
- [ ] Cythonize the module code.
- [ ] Create async version of `read_template()`.
- [ ] Write detailed documentation with Sphinx.
