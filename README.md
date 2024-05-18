# artless-template

Artless, small and simple template library for server-side rendering.

The project encourages approaches like HTMX and No-JS.

**Features**:

* Allows to generate HTML, using template files or/and natively (only Python).
* Small code base (less than 200 LOC).
* No third party dependencies (standart library only).

- [Install](#install)
- [Usage](#usage)
- [Performance](#performance)

<a id="install"></a>
## Install

``` shellsession
$ pip install artless-template
```

<a id="usage"></a>
## Usage

### Example with base layout template

Create `templates/index.html` with contents:

``` html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>$(title)</title>
  </head>
  <body>
    <main>
        <section>
            <h1>$(header)</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                $(users)
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
    None,
    None,
    [
        t(
            "tr",
            None,
            None,
            [
                t("td", None, user.name),
                t("td", None, user.email),
                t("td", None, "+" if user.is_admin else "-"),
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

template = read_template(TEMPLATES_DIR / "index.html").render(context)
```

### Usage more complex Components

``` html
<!DOCTYPE html>
<html lang="en">
  ...
  <body>
    <main>
      $(main)
    </main>
  </body>
</html>
```

``` python
from artless_template import read_template, Component, Tag as t

...

class UsersTableComponent:
    def __init__(self, count: int):
        self.user = [
            UserModel(
                name=f"User_{_}", email=f"user_{_}@gmail.com", is_admin=bool(randint(0, 1))
            )
            for _ in range(count)
        ]

    def view(self):
        return t(
            "table",
            None,
            None,
            [
                t(
                    "thead",
                    None,
                    None,
                    [
                        t(
                            "tr",
                            None,
                            None,
                            [
                                t("th", None, "Name"),
                                t("th", None, "Email"),
                                t("th", None, "Admin"),
                            ]
                        )
                    ]
                ),
                t(
                    "tbody",
                    None,
                    None,
                    [
                        t(
                            "tr",
                            None,
                            None,
                            [
                                t("td", None, user.name),
                                t("td", None, user.email),
                                t("td", None, "+" if user.is_admin else "-"),
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

Sorted results on my leptop (smaller is better):

``` python
{'mako': 0.011, 'jinja': 0.035, 'artless': 0.048, 'dtl': 0.158}
```

1. [Mako](https://www.makotemplates.org/) (0.011 sec.)
2. [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/) (0.035 sec.)
3. **Artless-template (0.048 sec.)**
4. [Django templates](https://docs.djangoproject.com/en/5.0/ref/templates/) (0.158 sec.)

The performance of `artless-template` is better than the `Django template engine`, but slightly worse than `Jinja2` and `Mako`.
