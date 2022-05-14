import sqlite3
import unittest

from grantme import procedures, setup


class SingleUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        setup.setup_db(self.conn)
        self.me = "cook"

    def tearDown(self):
        self.conn.close()

    def check_emptyness(self):
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNone(exclusive)

    def test_acquire_and_revoke_shared(self):
        procedures.grant(self.me, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.me, shares)
        self.assertIsNone(exclusive)

        procedures.revoke(self.me, self.conn)
        self.check_emptyness()

    def test_acquire_and_revoke_exclusive(self):
        procedures.grant(self.me, False, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.me)

        procedures.revoke(self.me, self.conn)
        self.check_emptyness()

    def test_upgrade(self):
        procedures.grant(self.me, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.me, shares)
        self.assertIsNone(exclusive)

        procedures.grant(self.me, False, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.me)

        procedures.revoke(self.me, self.conn)
        self.check_emptyness()

    def test_no_downgrade(self):
        procedures.grant(self.me, False, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.me)

        procedures.grant(self.me, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.me)

        procedures.revoke(self.me, self.conn)
        self.check_emptyness()


if __name__ == "__main__":
    unittest.main()
