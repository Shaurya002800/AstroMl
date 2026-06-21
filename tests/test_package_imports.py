import importlib
import unittest


class PackageImportTests(unittest.TestCase):
    def test_service_modules_import_from_package_context(self):
        modules = [
            "src.report",
            "src.api",
            "src.operational_status",
            "src.backup",
            "src.legacy_migration",
            "src.interpretation.interpret",
        ]

        for module in modules:
            with self.subTest(module=module):
                importlib.import_module(module)


if __name__ == "__main__":
    unittest.main()
