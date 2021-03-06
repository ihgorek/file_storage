import unittest

from app.api.register_and_login import Register


class TestLogIn(unittest.TestCase):
    def setUp(self):
        self.a = Register()


    def tearDown(self):
        del self.a

    def test_add_user(self):
        self.a.del_all()
        # True
        self.assertIs(self.a.add_user('1224', 'eva@eva.ru', 'eva123', '/'),
                      'ok')
        self.assertIs(self.a.add_user('admin', 'admin@admin.ru', 'admin', '/'),
                      'ok')
        # False
        self.assertEqual(self.a.add_user('admin', 'admin@admin.ru', 'admin', '/'),
                         'That username is already taken, please choose another')
        self.assertEqual(self.a.add_user('ad', 'aerd@ared.ru', 'admin123', '/'),
                         'Username is too short')
        self.assertEqual(self.a.add_user('adimin', '', 'admin223', '/'),
                         'Email address is too short, or incorrect')
        self.assertEqual(self.a.add_user('', '', '', ''),
                         'Username is too short')
        self.assertEqual(self.a.add_user('dearfriend', 'eva@eva.ru', '123456', '/'),
                         'This email is already in use.')

    def test_get_id_user(self):
        self.a.add_user('1224', 'eva@eva.ru', 'eva123', '/')
        self.a.add_user('admin', 'admin@admin.ru', 'admin', '/')
        # True
        self.assertIsInstance(self.a.get_id_user('admin'), int)
        self.assertIsInstance(self.a.get_id_user('1224'), int)
        #False
        self.assertIsInstance(self.a.get_id_user(''), str)
        self.assertIsInstance(self.a.get_id_user('random_name'), str)

    def test_del_user(self):
        # True
        self.assertEqual(self.a.del_user('admin'), 'admin has been deleted')
        self.assertEqual(self.a.del_user('1224'), '1224 has been deleted')
        # False
        self.assertEqual(self.a.del_user('admin'),
                         'This user does not exist')
        self.assertEqual(self.a.del_user(''),
                         'This user does not exist')



if __name__ == "__main__":
    unittest.main()
