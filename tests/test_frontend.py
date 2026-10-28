"""Frontend-only refactor contracts, independent of disposable browser captures."""
import collections
import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTRACT = json.loads((ROOT / "docs/frontend-contract.json").read_text(encoding="utf-8"))
CONVERSION = json.loads((ROOT / "docs/frontend-conversion.json").read_text(encoding="utf-8"))
CONSOLIDATED = json.loads((ROOT / "docs/frontend-consolidation.json").read_text(encoding="utf-8"))["files"]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.classes = set()
        self.inline = []

    def handle_starttag(self, tag, attrs):
        self.elements.append(json.dumps([tag, sorted((k, v) for k, v in attrs if k != "class")], ensure_ascii=False))
        for key, value in attrs:
            if key == "style" or tag == "style":
                self.inline.append((tag, key))
            if key == "class":
                value = re.sub(r"{%.*?%}|{{.*?}}", " ", value or "", flags=re.S)
                self.classes.update(value.split())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


class FrontendTests(unittest.TestCase):
    def test_backend_dependencies_and_pitch_detection_unchanged(self):
        expected = dict(CONVERSION["backend"])
        for path in ("requirements.txt", "assets/js/tuner/tuner_pitch.js",
                     "assets/js/chatbot/chatbot_api.js", "assets/js/chatbot/chatbot.js",
                     "assets/js/account/account.js", "assets/js/shared/app.js", "assets/js/shared/theme.js"):
            expected[path] = CONTRACT["original_files"][path]
        for relative, digest in expected.items():
            with self.subTest(file=relative):
                self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), digest)

    def test_original_files_and_non_class_dom_contract_preserved(self):
        for relative in CONTRACT["original_files"]:
            current = CONSOLIDATED.get(relative, relative)
            self.assertTrue((ROOT / current).is_file(), f"Original content missing: {relative} -> {current}")
        actual = collections.Counter()
        for path in (ROOT / "templates").rglob("*.html"):
            parser = Markup()
            parser.feed(path.read_text(encoding="utf-8"))
            actual.update(parser.elements)
        # Includes may change file boundaries, but all original tags, SVG
        # geometry, form attributes, IDs, data hooks and Jinja values remain.
        self.assertEqual(dict(sorted(actual.items())), CONTRACT["original_elements"])

    def test_catalog_and_search_filter_have_one_html_and_css_file_each(self):
        for module in ("catalog", "search_filter"):
            for folder, extension in (("templates", "html"), ("assets/css", "css")):
                directory = ROOT / folder / module
                self.assertEqual(sorted(p.name for p in directory.glob(f"*.{extension}")),
                                 [f"{module}.{extension}"])
            sheet = (ROOT / f"assets/css/{module}/{module}.css").read_text(encoding="utf-8")
            self.assertNotIn("@import", sheet)
            self.assertIn("SECTION:", sheet)
        for previous, current in CONSOLIDATED.items():
            self.assertFalse((ROOT / previous).exists(), previous)
            self.assertTrue((ROOT / current).is_file(), current)

    def test_no_utility_or_inline_component_styling(self):
        utilities = set(CONVERSION["utility_tokens"])
        for path in (ROOT / "templates").rglob("*.html"):
            with self.subTest(template=path):
                parser = Markup()
                parser.feed(path.read_text(encoding="utf-8"))
                self.assertEqual(parser.classes & utilities, set())
                self.assertFalse(any(":" in name for name in parser.classes), parser.classes)
                self.assertEqual(parser.inline, [])
        for path in (ROOT / "assets/css").rglob("*.css"):
            with self.subTest(css=path):
                source = path.read_text(encoding="utf-8")
                self.assertNotRegex(source, r"(?i)tailwind|--tw-|@apply\b|@config\b|@layer\s+(?:utilities|components|base)")
                self.assertNotIn("\\:", source)
                self.assertNotIn("--ui-", source, "Use ordinary CSS values instead of generated styling variables")
                self.assertNotIn(":is(.dark *)", source, "Use the readable .dark .component theme selector")
        for path in (ROOT / "assets/js").rglob("*.js"):
            with self.subTest(js=path):
                source = path.read_text(encoding="utf-8")
                self.assertNotRegex(source, r"\.style(?:\.|\[)|setAttribute\([\"']style[\"']")
                self.assertNotRegex(source, r"\b(?:dark|hover|focus|sm|md|lg|xl):(?:bg|text|border|grid|flex|underline)")

    def test_component_pairs_comments_and_css_import_graph(self):
        imports = {}
        for path in (ROOT / "assets/css").rglob("*.css"):
            source = path.read_text(encoding="utf-8")
            self.assertIn("COMPONENT:", source, str(path))
            references = re.findall(r"@import\s+url\([\"']([^\"']+)[\"']\)", source)
            local = [str((path.parent / ref).resolve()) for ref in references if not ref.startswith(("https:", "http:", "data:", "//"))]
            self.assertEqual(len(local), len(set(local)), f"Duplicate import: {path}")
            for target in local:
                self.assertTrue(Path(target).is_file(), f"Missing CSS import: {path} -> {target}")
            imports[str(path.resolve())] = local
        def visit(path, ancestors):
            self.assertNotIn(path, ancestors, f"CSS import cycle: {path}")
            for child in imports[path]:
                visit(child, ancestors + [path])
        for path in imports:
            visit(path, [])
        for path in (ROOT / "templates").rglob("*.html"):
            relative = path.relative_to(ROOT).as_posix()
            sheet = ROOT / relative.replace("templates/", "assets/css/").replace(".html", ".css")
            self.assertTrue(sheet.is_file(), f"Missing matching stylesheet: {relative}")
            source = path.read_text(encoding="utf-8")
            self.assertTrue(source.startswith("<!-- MODULE:"), relative)
            self.assertIn(sheet.relative_to(ROOT).as_posix(), source)
            self.assertIn("JS:", source)
        # Even composition-only sheets are wired so students can add their
        # component rules without first diagnosing a missing import.
        loaded = set()
        for module in ("shared", "account", "admin", "auth", "catalog", "chatbot", "landing", "lessons", "search_filter", "tuner"):
            entry = str((ROOT / f"assets/css/{module}/{module}.css").resolve())
            def collect(path):
                loaded.add(path)
                for child in imports[path]:
                    collect(child)
            collect(entry)
        self.assertEqual(loaded, set(imports))


if __name__ == "__main__":
    unittest.main()
