from django.test import TestCase
from django.contrib.auth.hashers import make_password, check_password
# Create your tests here.
class UserTest(TestCase):
    def test_generate_password(self):
        encrypt = make_password('1')
        print(encrypt)
        self.assertTrue(check_password('1', encrypt))
