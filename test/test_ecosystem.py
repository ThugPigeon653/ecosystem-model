import unittest
from unittest.mock import patch
import src.ecosystem as eco

class TestPregnancy(unittest.TestCase):
    def setUp(self):
        eco.initialize(True)

    def test_insert_pregnancy(self):
        pregnancy = eco.Pregnancy()
        result = pregnancy.insert_pregnancy(1, 2, 100)
        print(result)

if __name__ == '__main__':
    unittest.main()
