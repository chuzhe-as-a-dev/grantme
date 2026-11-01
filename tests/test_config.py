import tempfile
import unittest
from pathlib import Path

from grantme.utils.config import DEFAULT_DATA_DIR, read_data_dir


class ConfigTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.conf = Path(self.tmp.name) / "grantme.conf"

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file(self):
        self.assertEqual(read_data_dir(self.conf, "host"), Path(DEFAULT_DATA_DIR))

    def test_default_and_host_sections(self):
        self.conf.write_text(
            "[default]\ndata_dir = /data/default\n\n[host2]\ndata_dir = /data/host2\n"
        )
        self.assertEqual(read_data_dir(self.conf, "host1"), Path("/data/default"))
        self.assertEqual(read_data_dir(self.conf, "host2"), Path("/data/host2"))

    def test_example_file(self):
        example = Path(__file__).resolve().parent.parent / "bin" / "grantme.conf.example"
        self.assertEqual(read_data_dir(example, "host"), Path(DEFAULT_DATA_DIR))


if __name__ == "__main__":
    unittest.main()
