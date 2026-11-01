import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


LAUNCHER = Path(__file__).resolve().parent.parent / "bin" / "grantme"


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = dict(os.environ, GRANTME_DIR=str(Path(self.tmp.name) / "grantme"))

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(LAUNCHER), *args],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

    def test_missing_db(self):
        result = self.run_cli("--status")
        self.assertEqual(result.returncode, 255)
        self.assertIn("--init", result.stdout)
        self.assertFalse(Path(self.env["GRANTME_DIR"]).exists())

    def test_init_twice(self):
        for _ in range(2):
            result = self.run_cli("--init")
            self.assertEqual(result.returncode, 0, result.stdout)

        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_grant_list_revoke(self):
        self.run_cli("--init")

        result = self.run_cli("--mode", "shared", "--duration", "1w2d")
        self.assertEqual(result.returncode, 0, result.stdout)

        result = self.run_cli("--list")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(self.env.get("USER", ""), result.stdout)

        result = self.run_cli("--revoke")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_bad_duration(self):
        self.run_cli("--init")

        result = self.run_cli("--mode", "shared", "--duration", "abc")
        self.assertEqual(result.returncode, 255)
        self.assertIn("Could not parse", result.stdout)
        self.assertNotIn("Traceback", result.stdout)


if __name__ == "__main__":
    unittest.main()
