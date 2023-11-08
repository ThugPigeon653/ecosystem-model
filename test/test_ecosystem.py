import sys
print(sys.path)
import unittest
import sqlite3
from unittest.mock import patch
from src.ecosystem import Pregnancy
from src.db_connection import Connection

class TestPregnancy(unittest.TestCase):
    def setUp(self):
        self.test_conn = sqlite3.connect(':memory:')
        self.test_cursor = self.test_conn.cursor()
        self.test_cursor.execute('''
            CREATE TABLE animals (
                id INTEGER PRIMARY KEY,
                weight INTEGER,
                birth_rate INTEGER
            )
        ''')
        self.test_cursor.execute('INSERT INTO animals (id, weight, birth_rate) VALUES (1, 100, 5)')
        self.real_connection = Connection.get_connection()
        Connection.get_connection = lambda: self.test_conn

    def tearDown(self):
        Connection.get_connection = self.real_connection
        self.test_conn.close()

    @patch('src.ecosystem.Pregnancy.conn')
    def test_insert_pregnancy(self, mock_conn):
        pregnancy = Pregnancy()
        result = pregnancy.insert_pregnancy(1, 2, 100)
        self.test_cursor.execute('SELECT * FROM pregnancy WHERE mother_id = 1')
        row = self.test_cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(result, 1)

if __name__ == '__main':
    unittest.main()
