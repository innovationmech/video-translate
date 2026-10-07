"""Regression tests for embedding codebase names in the HTML explorer."""

import json
import runpy
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1] / ".agents/skills/codebase-visualizer/scripts/visualize.py"
)


class ParsedPage(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.tags = []
        self.text = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)

    def handle_data(self, data):
        self.text.append(data)


@pytest.mark.parametrize("location", ["root", "extension"])
def test_names_are_text_in_static_html(location, tmp_path):
    module = runpy.run_path(str(SCRIPT))
    name = '<img src=x onerror="alert(1)"> & 中文'
    extension = "." + name if location == "extension" else ".py"
    data = {"name": name if location == "root" else "project", "size": 5, "children": []}
    stats = {
        "files": 1,
        "dirs": 0,
        "extensions": Counter({extension: 1}),
        "ext_sizes": Counter({extension: 5}),
    }
    output = tmp_path / "map.html"
    module["generate_html"](data, stats, output)
    page = ParsedPage(output.read_text(encoding="utf-8"))
    assert "img" not in page.tags
    assert any(name in text for text in page.text)


def test_tree_data_cannot_close_inline_script(tmp_path):
    module = runpy.run_path(str(SCRIPT))
    name = '</script><img src=x onerror="alert(1)">'
    data = {"name": "project", "size": 0, "children": [{"name": name, "size": 0}]}
    stats = {"files": 1, "dirs": 0, "extensions": Counter(), "ext_sizes": Counter()}
    output = tmp_path / "map.html"
    module["generate_html"](data, stats, output)
    source = output.read_text(encoding="utf-8")
    assert "img" not in ParsedPage(source).tags
    serialized = source.split("const data = ", 1)[1].split(";\n", 1)[0]
    assert json.loads(serialized)["children"][0]["name"] == name
