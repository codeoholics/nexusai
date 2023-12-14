from unittest import TestCase
from resourcereader import get_absolute_path_from_resources


class Test(TestCase):
    def test_get_absolute_path_from_resources(self):
        res = get_absolute_path_from_resources('my_file.txt')
        print(res)
        self.assertIn('resources/my_file.txt', res)
