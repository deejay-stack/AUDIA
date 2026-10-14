"""Current component migration: route identity, source preservation, and imports."""
import hashlib
import json
import re
import unittest
from pathlib import Path

from app import app

ROOT = Path(__file__).resolve().parent.parent
BASELINE = json.loads((ROOT / "docs/components/before.json").read_text(encoding="utf-8"))
MIGRATION = json.loads((ROOT / "docs/components/migration.json").read_text(encoding="utf-8"))


class StructureTests(unittest.TestCase):
    def test_exact_route_and_blueprint_contract(self):
        routes = sorted([
            {"endpoint": rule.endpoint, "methods": sorted(rule.methods), "rule": rule.rule}
            for rule in app.url_map.iter_rules()
        ], key=lambda rule: (rule["endpoint"], rule["rule"], rule["methods"]))
        self.assertEqual(routes, BASELINE["routes"])
        self.assertEqual(list(app.blueprints), BASELINE["blueprints"])
        self.assertEqual(len({id(blueprint) for blueprint in app.blueprints.values()}), 7)

    def test_original_files_and_logic_preserved(self):
        # Undo only the recorded imports, filenames, and extracted component
        # wiring. All other original bytes, including current user edits, match.
        for old, metadata in BASELINE["files"].items():
            with self.subTest(file=old):
                target = MIGRATION["moves"].get(old, old)
                path = ROOT / target
                self.assertTrue(path.is_file(), f"Missing source: {target}")
                if old in MIGRATION["moves"]:
                    self.assertFalse((ROOT / old).is_file(), f"Duplicate old source: {old}")
                raw = path.read_bytes()
                if target in MIGRATION["rewrites"]:
                    original = raw.decode("utf-8")
                    for change in reversed(MIGRATION["rewrites"][target]):
                        self.assertIn(change["after"], original, f"Missing component wiring: {target}")
                        original = original.replace(change["after"], change["before"], change["count"])
                    raw = original.encode("utf-8")
                self.assertEqual(hashlib.sha256(raw).hexdigest(), metadata["sha256"],
                                 f"Source changed outside the component migration: {target}")
        # Extracted markup, rules, handlers and their integration scaffolding
        # also remain the exact versions exercised by the migration checks.
        for target, expected in MIGRATION["new_runtime_files"].items():
            with self.subTest(component=target):
                self.assertEqual(hashlib.sha256((ROOT / target).read_bytes()).hexdigest(), expected)

    def test_template_and_browser_import_paths(self):
        for feature in ("catalog", "search_filter", "chatbot", "tuner", "lessons"):
            for folder, suffix in (("modules", "py"), ("templates", "html"), ("assets/css", "css")):
                self.assertTrue((ROOT / folder / feature / f"{feature}.{suffix}").is_file())
        for name in app.jinja_env.list_templates():
            app.jinja_env.get_template(name)
        for folder, extension, pattern in [
            ("assets/js", "*.js", r'(?:from\s*|import\s*\()\s*[\'\"](\.[^\'\"]+)[\'\"]'),
            ("assets/css", "*.css", r'@import\s+url\([\'\"]([^\'\"]+)[\'\"]\)'),
        ]:
            for path in (ROOT / folder).rglob(extension):
                for reference in re.findall(pattern, path.read_text(encoding="utf-8")):
                    if reference.startswith(("https://", "http://", "//", "data:")):
                        continue
                    self.assertTrue((path.parent / reference).resolve().is_file(), f"{path}: {reference}")


if __name__ == "__main__":
    unittest.main()
