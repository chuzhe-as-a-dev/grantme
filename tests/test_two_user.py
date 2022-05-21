import sqlite3
import unittest

from grantme import procedures, defs
from grantme.utils import errors
from grantme.procedures import Mode


class TwoUserTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row
        procedures.setup_db(self.conn)

        self.him = "cook"
        self.her = "julie"

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

    def assert_both(self, this, that):
        status = procedures.get_status(self.conn)
        self.assertIsNotNone(status)
        self.assertEqual(status.mode, Mode.SHARED)
        self.assertEqual(len(status.user_expires), 2)
        self.assertIn(this, status.user_expires)
        self.assertIn(that, status.user_expires)

    def test_sharing(self):
        procedures.grant(self.him, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        procedures.grant(self.her, Mode.SHARED, "1m", self.conn)
        self.assert_both(self.him, self.her)

        procedures.revoke(self.him, self.conn)
        self.assert_the_only(self.her, Mode.SHARED)

        procedures.revoke(self.her, self.conn)
        self.assert_emptiness()

    def test_unique_exclusive(self):
        procedures.grant(self.him, Mode.EXCLUSIVE, "1m", self.conn)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, Mode.SHARED, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.GRANT_FAILURE_CODE)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.GRANT_FAILURE_CODE)
        self.assert_the_only(self.him, Mode.EXCLUSIVE)

        procedures.revoke(self.him, self.conn)
        self.assert_emptiness()

    def test_rmw_like_deadlock(self):
        procedures.grant(self.him, Mode.SHARED, "1m", self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        procedures.grant(self.her, Mode.SHARED, "1m", self.conn)
        self.assert_both(self.him, self.her)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.her, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.UPGRADE_FAILURE_CODE)
        self.assert_both(self.him, self.her)

        with self.assertRaises(errors.RuntimeErrorWithMessageAndCode) as cm:
            procedures.grant(self.him, Mode.EXCLUSIVE, "1m", self.conn)
        the_exception = cm.exception
        self.assertEqual(the_exception.code, defs.Message.UPGRADE_FAILURE_CODE)
        self.assert_both(self.him, self.her)

        procedures.revoke(self.her, self.conn)
        self.assert_the_only(self.him, Mode.SHARED)

        procedures.revoke(self.him, self.conn)
        self.assert_emptiness()


if __name__ == "__main__":
    unittest.main()
