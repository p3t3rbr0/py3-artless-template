from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from random import randint
from time import time
from typing import final

from django import setup as django_setup
from django.conf import settings
from django.template.loader import render_to_string
from jinja2 import Environment, FileSystemLoader, select_autoescape
from mako.template import Template

from artless_template import Tag as t
from artless_template import read_template

TEMPLATES_DIR: Path = Path(__file__).resolve().parent / "templates"

settings.configure(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["."],
            "APP_DIRS": False,
        },
    ]
)
django_setup()


jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), autoescape=select_autoescape()
)


def deltatime(func):
    """Measure execution time of decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time()
        retval = func(*args, **kwargs)
        delta = float(f"{time() - t0:.3f}")
        return retval, delta

    return wrapper


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


@deltatime
def test_artless_template():
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

    return read_template(TEMPLATES_DIR / "artless.html").render(**context)


@deltatime
def test_django_template():
    context = {
        "title": "Django template example",
        "header": "Users list",
        "users": users,
    }
    return render_to_string(TEMPLATES_DIR / "dtl.html", context)


@deltatime
def test_jinja2_template():
    template = jinja_env.get_template("jinja2.html")
    context = {
        "title": "Jinja2 template example",
        "header": "Users list",
        "users": users,
    }
    return template.render(**context)


@deltatime
def test_mako_template():
    template = Template(filename=str(TEMPLATES_DIR / "mako.html"))
    return template.render(
        title="Mako template example", header="Users list", users=users
    )


if __name__ == "__main__":
    results = {
        "artless": test_artless_template()[1],
        "dtl": test_django_template()[1],
        "jinja": test_jinja2_template()[1],
        "mako": test_mako_template()[1],
    }
    print(dict(sorted(results.items(), key=lambda x: x[1])))
