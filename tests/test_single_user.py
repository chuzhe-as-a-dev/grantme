import sqlite3
import unittest

from grantme import procedures
from grantme.procedures import Mode


class SingleUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        procedures.setup_db(self.conn)

        self.me = "cook"

    def tearDown(self):
        self.conn.close()

    def assert_emptiness(self):
        status = procedures.get_status(self.conn)
        self.assertIsNone(status)

    def assert_the_only(self, who, mode):
        status = procedures.get_status(self.conn)
        self.assertIsNotNone(status)
        self.assertEqual(status.mode, mode)
        self.assertEqual(len(status.user_expires), 1)
        self.assertIn(who, status.user_expires)

    def test_acquire_and_revoke_shared(self):
        procedures.grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.SHARED)

        procedures.revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_acquire_and_revoke_exclusive(self):
        procedures.grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        procedures.revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_upgrade(self):
        procedures.grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.SHARED)

        procedures.grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        procedures.revoke(self.me, self.conn)
        self.assert_emptiness()

    def test_no_downgrade(self):
        procedures.grant(self.me, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        procedures.grant(self.me, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.me, Mode.EXCLUSIVE)

        procedures.revoke(self.me, self.conn)
        self.assert_emptiness()


if __name__ == "__main__":
    unittest.main()
