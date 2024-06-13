from unittest import TestCase
from unittest.mock import mock_open, patch

from artless_template import (
    _VOID_TAGS,
    Component,
    Tag,
    Template,
    read_template,
)


class TestConstants(TestCase):
    def test_package_constants(self):
        expected_tags = [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "source",
            "track",
            "wbr",
        ]
        self.assertEqual(list(sorted(_VOID_TAGS.keys())), expected_tags)


class TestTemplate(TestCase):
    def setUp(self):
        self.content = (
            "<html><head><title>@title</title></head><body><h1>@header</h1></body></html>"
        )
        self.template = Template(self.content)

    def test_class_attributes(self):
        expected_slots = ("template", "__weakref__")
        self.assertEqual(Template.__slots__, expected_slots)

    def test_render_with_regular_context(self):
        context = {"title": "Test title", "header": "Test"}
        expected_result = (
            "<html><head><title>Test title</title></head><body><h1>Test</h1></body></html>"
        )

        result = self.template.render(**context)

        self.assertEqual(result, expected_result)

    def test_render_without_empty_context(self):
        result = self.template.render()
        self.assertEqual(result, self.content)

    def test_render_context_with_component(self):
        class SomeComponent(Component):
            def view(self):
                return Tag("div", None, "Div text")

        template = Template("<html><head><title></title></head><body>@body</body></html>")
        result = template.render(body=SomeComponent())

        self.assertEqual(
            result, "<html><head><title></title></head><body><div>Div text</div></body></html>"
        )


class TestReadTemplate(TestCase):
    def setUp(self):
        self.file_content = (
            "<html><head><title>@title</title></head><body><h1>@header</h1></body></html>"
        )
        self.fake_open = mock_open(read_data=self.file_content)

    def test_read_template(self):
        with patch("builtins.open", self.fake_open) as mock_file:
            template = read_template("templates/index.html")

        mock_file.assert_called_once_with("templates/index.html", "r")

        self.assertIsInstance(template, Template)
        self.assertEqual(template.template, self.file_content)


class TestTag(TestCase):
    def setUp(self):
        self.test_cases = [
            # Only tag name
            (["div", None, None], "<div></div>"),
            # Only name and attributes
            (["div", {"id": "superblock"}, None], '<div id="superblock"></div>'),
            # Only name and text
            (["div", None, "Test"], "<div>Test</div>"),
            # Name, attributes and text
            (["div", {"id": "superblock"}, "Test"], '<div id="superblock">Test</div>'),
            # Name, more attributes and text
            (
                [
                    "div",
                    {"id": "some-id", "class": "some-class", "data-field": "some data field"},
                    "Some text",
                ],
                '<div id="some-id" class="some-class" data-field="some data field">Some text</div>',
            ),
            # Name, attributes, text and children
            (
                [
                    "div",
                    {"class": "parent"},
                    "Parent text",
                    [
                        Tag(
                            "div",
                            {"class": "child"},
                            "Child text",
                            [Tag("span", None, "Span text")],
                        )
                    ],
                ],
                (
                    '<div class="parent"><div class="child"><span>Span text</span>'
                    "Child text</div>Parent text</div>"
                ),
            ),
            # Void tag
            (["br"], "<br />"),
            # Void tag with attributes
            (
                ["area", {"data-url": "https://www.w3.org/"}],
                '<area data-url="https://www.w3.org/" />',
            ),
            # Void tag with text
            (["area", None, "Text that will not be shown"], "<area />"),
            # Void tag with children
            (["area", None, None, [Tag("span")]], "<area />"),
        ]

    def test_render_tags(self):
        for args, expected in self.test_cases:
            with self.subTest(args=args, expected=expected):
                self.assertEqual(str(Tag(*args)), expected)

    def test_repr(self):
        tag = Tag("div", {"id": "superblock"}, "Div text", [Tag("span", None, "Span text")])
        self.assertEqual(
            tag.__repr__(),
            (
                "Tag(name='div', attrs={'id': 'superblock'}, text='Div text', "
                "children=[Tag(name='span', attrs=None, text='Span text', children=[])])"
            ),
        )

    def test_add_child(self):
        tag = Tag("div")

        self.assertEqual(len(tag.children), 0)
        self.assertEqual(str(tag), "<div></div>")

        tag.add_child(Tag("span"))

        self.assertEqual(len(tag.children), 1)
        self.assertEqual(str(tag), "<div><span></span></div>")

    def test_is_parent(self):
        tag = Tag("div")
        self.assertFalse(tag.is_parent)

        tag.add_child(Tag("span"))
        self.assertTrue(tag.is_parent)

    def test_is_leaf(self):
        tag = Tag("div")
        self.assertTrue(tag.is_leaf)

        tag.add_child(Tag("span"))
        self.assertFalse(tag.is_leaf)
