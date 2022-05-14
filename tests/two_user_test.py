import sqlite3
import unittest

from grantme import procedures, setup, defs
from grantme.utils import errors


class TwoUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        setup.setup_db(self.conn)
        self.him = "cook"
        self.her = "julie"

    def tearDown(self):
        self.conn.close()

    def check_emptyness(self):
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNone(exclusive)

    def test_sharing(self):
        procedures.grant(self.him, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.him, shares)
        self.assertIsNone(exclusive)

        procedures.grant(self.her, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 2)
        self.assertIn(self.her, shares)
        self.assertIsNone(exclusive)

        procedures.revoke(self.him, self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.her, shares)
        self.assertIsNone(exclusive)

        procedures.revoke(self.her, self.conn)
        self.check_emptyness()

    def test_unique_exclusive(self):
        procedures.grant(self.him, False, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.him)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, True, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.GRANT_FAILURE_CODE)

        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.him)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, False, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.GRANT_FAILURE_CODE)

        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 0)
        self.assertIsNotNone(exclusive)
        self.assertEqual(exclusive[0], self.him)

        procedures.revoke(self.him, self.conn)
        self.check_emptyness()

    def test_rmw_like_deadlock(self):
        procedures.grant(self.him, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.him, shares)
        self.assertIsNone(exclusive)

        procedures.grant(self.her, True, "1m", self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 2)
        self.assertIn(self.him, shares)
        self.assertIn(self.her, shares)
        self.assertIsNone(exclusive)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, False, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.UPGRADE_FAILURE_CODE)

        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 2)
        self.assertIn(self.him, shares)
        self.assertIn(self.her, shares)
        self.assertIsNone(exclusive)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.him, False, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.UPGRADE_FAILURE_CODE)

        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 2)
        self.assertIn(self.him, shares)
        self.assertIn(self.her, shares)
        self.assertIsNone(exclusive)

        procedures.revoke(self.her, self.conn)
        shares, exclusive = procedures.granted(self.conn)
        self.assertEqual(len(shares), 1)
        self.assertIn(self.him, shares)
        self.assertIsNone(exclusive)

        procedures.revoke(self.him, self.conn)
        self.check_emptyness()


if __name__ == "__main__":
    unittest.main()
