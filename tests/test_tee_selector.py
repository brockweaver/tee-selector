# test_math_utils.py
import unittest
from tee_selector import add

class TestMathUtils(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == "__main__":
    unittest.main()