"""Artless, small and simple template library for server-side rendering."""

__author__ = "Peter Bro"
__version__ = "0.1.0"
__license__ = "MIT"
__all__ = ["Component", "Template", "Tag", "read_template"]


from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Mapping, Optional, Protocol, Sequence, runtime_checkable

# Void tags (https://developer.mozilla.org/en-US/docs/Glossary/Void_element),
# without closing scope.
_VOID_TAGS: dict[str, bool] = {
    "area": True,
    "base": True,
    "br": True,
    "col": True,
    "embed": True,
    "hr": True,
    "img": True,
    "input": True,
    "link": True,
    "meta": True,
    "source": True,
    "track": True,
    "wbr": True,
}


class Tag:
    """Virtual tag implementation."""

    __slots__ = ("name", "attrs", "text", "children", "parent", "__weakref__")

    def __init__(
        self,
        name: str,
        /,
        attrs: Optional[Mapping[str, str]] = None,
        text: str = "",
        children: Optional[Sequence["Tag"]] = None,
    ) -> None:
        """Initialize a Tag object.

        Args:
            name: Name of the tag.
            attrs: Optional dict with a tag attributes (id, class, data-*, etc).
            text: Optional text fo the tag.
            children: Optional sequence with a child tags.
        """
        self.name = name.lower()
        self.attrs = attrs
        self.text: str = text
        self.children = []

        self.parent: Optional["Tag"] = None

        if children:
            for child in children:
                child.parent = self
                self.children.append(child)

    def __str__(self) -> str:
        """String representation of a tag."""
        return self._render()

    def __repr__(self) -> str:
        """Tag service representation of a tag."""
        return (
            f"Tag(name={self.name!r}, attrs={self.attrs!r}, "
            f"text={self.text!r}, children={self.children!r})"
        )

    @property
    def is_parent(self) -> bool:
        """Property indicating that tag has children."""
        return bool(self.children)

    @property
    def is_leaf(self) -> bool:
        """Property indicating that tag hasn't children."""
        return not bool(self.children)

    def add_child(self, tag: "Tag") -> "Tag":
        """Add tag as a child to the current tag."""
        tag.parent = self
        self.children.append(tag)
        return self

    def _render(self) -> str:
        """Render the object into an html-tag representation."""
        tag = f"<{self.name}"

        if self.attrs:
            for name, value in self.attrs.items():
                tag += f' {name}="{value}"'

        if self.name in _VOID_TAGS:
            tag += " />"
            return tag

        tag += ">"

        for child in self.children:
            tag += child._render()

        if self.text:
            tag += self.text

        tag += f"</{self.name}>"

        return tag


@runtime_checkable
class Component(Protocol):
    """More complex tags composition tied to common logic and/or state.

    The component object can be passed as is to template substitution as a context.
    """

    def view(self) -> Tag:
        """Required method for any component.

        Returns:
            Tag object.
        """
        pass


ContextT = Mapping[str, str | int | float | bool | None | datetime | Tag | Component]


class Template:
    """String based template.

    Works on principle of replacing substrings in a string.
    """

    __slots__ = ("template", "__weakref__")

    def __init__(self, template: str) -> None:
        """Initialize a Template object.

        Args:
            template: Template content, with markup for data substitution.
        """
        self.template = template

    def render(self, context: ContextT) -> str:
        """Render the template by substituting context data.

        Args:
            context: Dict with context substitution.

        Returns:
            Rendered template as a string.
        """
        if not context:
            return self.template

        for key, value in context.items():
            replacement = f"$({key})"
            value = str(value.view()) if isinstance(value, Component) else str(value)
            self.template = self.template.replace(replacement, value)

        return self.template


@lru_cache()
def read_template(filename: str | Path) -> Template:
    """Read template from file.

    Args:
        filename: Path to file.

    Returns:
        Template instance.
    """
    with open(filename, "r") as fh:
        return Template(fh.read())
